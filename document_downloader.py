# This script will look through each folder in our source list download the article associated with it.

# THIS SCRIPT REQUIRES Python3 and Pip3


import json
import requests
import html2text
import re
import urllib.request
import string
import sys
import os

valid_chars = "-_ %s%s" % (string.ascii_letters, string.digits)

markdown = html2text.HTML2Text()
markdown.ignore_links = True
markdown.ignore_images = True
markdown.bypass_tables = True
# markdown.images_to_alt = True # No, because this does not completely remove the crap
markdown.body_width = 0

downloadedArticles = {}
pendingURLs = []

# Pages with subscriptions and PDF downloads
whitelistedPages = {
	"onlinelibrary.wiley.com": 
		{"root": "http://onlinelibrary.wiley.com/doi/{}/full", "key": "DOI"},
	"pubs.acs.org": 
		{'root': "http://pubs.acs.org/doi/full/{}", 'key':"DOI"},
	"link.springer.com" : 
		{"root": "http://link.springer.com/article/{}/fulltext.html", 'key':'DOI'},
	"online.liebertpub.com": 
		{'root': "http://online.liebertpub.com/doi/full/{}", 'key':'DOI'},
	"mdpi.com":
		{'root': "{}/htm", 'key':'landingPage'},
	"tandfonline.com":
		{'root': "http://www.tandfonline.com/doi/full/{}", 'key':'DOI'}
}

# These are pages where we must scrape what we can from the landing page.
silentPages = [
	"www.actahort.org", "www.sciencedirect.com", "cancerjournal.net", "informahealthcare.com", "informahealthcare.com", "ncbi.nlm.nih.gov/pubmed" 
]

def isSilentPage(URL):

	# Check if the URL belongs to a silent page
	output = False
	for rootURL in silentPages:
		output = (rootURL in URL) or output

	return output

class Document:

	def __init__(self, entryURL, title=None):
		print("Scraping document: ", entryURL)

		self.info = {
			'entryURL': entryURL,
			'title': title
		}

		self.info['DOI'] = self.getDOI()
		self.info['landingPage'] =  self.getLandingPageURL()
		self.info['articleURL'] = self.findArticleURL()

		self.info['articleHTML'] = self.getArticle()

		# print(self.info)
		self.info['markdown'] = self.getMarkdown()

		# print(self.info)

	def getDOI(self):

		# Check if the article has a DOI
		entryURL = self.info['entryURL']

		potentialDOI = entryURL.split('dx.doi.org/')[-1]
		DOI = potentialDOI if (potentialDOI is not entryURL and len(potentialDOI) is not 0) else None

		return DOI

	def getLandingPageURL(self):
		entryPage = requests.get( self.info['entryURL'] )
		return entryPage.url if entryPage.ok else self.info['entryURL']


	def findArticleURL(self):

		landingPageURL = self.info['landingPage']

		entryPage = requests.get( landingPageURL )

		outputURL = None

		if entryPage.ok:

			# Now, let's download and translate the page
			for website, template in whitelistedPages.items():
				if website in landingPageURL:

					# format final URL from template list
					neededInfo = self.info[ template['key'] ]
					outputURL = template['root'].format(neededInfo)
			
			if outputURL is None:

				# Do we already know about this problem? If not, tell me about it.
				if not isSilentPage(landingPageURL):
					print("I do not know how to convert and download {}".format(landingPageURL), file=sys.stderr)
					pendingURLs.append( self.info['entryURL'] )

				# Return the entry link since there is probably some info there
				outputURL = landingPageURL

		# Request failed because link is busted
		else:
			# We got a broken link
			print("We got a broken entry link {}".format(landingPageURL), file=sys.stderr)
			pendingURLs.append( self.info['entryURL'] )


		return outputURL



	# For each folder, loop through the links and try to download them or load them from the cache
	def getArticle(self):

		# Check if we already have the article
		entryURL = self.info['entryURL']

		if entryURL in downloadedArticles:
			print("Got entryURL from cache")
			return downloadedArticles[entryURL]

		# else, we should download the article
		else:
			# Get the article's address
			articleAddress = self.info['articleURL']

			if articleAddress is not None:
				page = requests.get(articleAddress)


			# MUST ADD RESULT TO DATABASE
				if page.ok:
					downloadedArticles[entryURL] = page.text
		
			return downloadedArticles.get(entryURL, "")


	def getMarkdown(self):

		# Convert page to markdown
		htmlPage = self.info['articleHTML']
		markdownPage = markdown.handle(htmlPage)
		# print("Markdown: ", markdownPage)
		
		# Get the title
		title = self.info['title']
		if title is None:
			match = re.search("(^#\s.*\n)", markdownPage, flags=re.IGNORECASE|re.MULTILINE)
			title = match.group(1) if match is not None else ""
			self.info['title'] = title
		else:
			title = "# {}\n".format(title)

		# Select all text before abstract and after reference section 
		match = re.search("(^#+ abstract[\s\S]*)\n#+ reference", markdownPage, flags=re.IGNORECASE|re.MULTILINE)
		# print(match)
		article = match.group(1) if match is not None else "" # The highlighted selector

		# Check if the article was actually selected, else select only the abstract
		if match is None:
			match = re.search("(^#+ abstract[\s\S]+?)\n\n", markdownPage, flags=re.IGNORECASE|re.MULTILINE)
			article = match.group(1) if match is not None else "" # The highlighted section

		cleanArticle = title + '\n' +  article

		# Clean out unordered lists
		cleanArticle = re.sub(r'^\s*\*\s+.+\n', '', cleanArticle,  flags=re.IGNORECASE|re.MULTILINE)

		# Clean out horizontal rules
		cleanArticle = re.sub(r'^\*\*\*\n', '', cleanArticle,  flags=re.IGNORECASE|re.MULTILINE)

		# Remove all remaining asterisks (might be emphasis marks)
		cleanArticle = re.sub(r'\*', '', cleanArticle,  flags=re.IGNORECASE|re.MULTILINE)

		# Remove all html tables
		cleanArticle = re.sub(r'<table[\s\S]+?</table>', '', cleanArticle,  flags=re.IGNORECASE|re.MULTILINE)

		# Clean out ordered lists (Note: This works since all things that look like ordered lists are already escaped)
		cleanArticle = re.sub(r'\n\s*[0-9]+\..*', '', cleanArticle,  flags=re.IGNORECASE|re.MULTILINE)

		# Remove all lines of words that are too short and obviously not paragraphs or headings
		cleanArticle = re.sub(r'((?!^#)^.{1,80}\n)', '', cleanArticle,  flags=re.IGNORECASE|re.MULTILINE)

		return cleanArticle

	def ok(self):

		# Do a quick sanity check of the document
		return (len(self.info['markdown']) > 500) # Documents are usually bigger than 500 characters (for the abstract)

	def saveDocument(self, directory):

		# Check document okay
		if not self.ok():
			URL = self.info['entryURL']
			print("ERROR parsing {}".format(URL), file=sys.stderr)
			if URL not in pendingURLs:
				pendingURLs.append(URL)
			return


		objectToSave = self.info

		# Let's make the name of the file the title
		filename = self.getFilenameRoot()

		with open( "{}/{}.json".format(directory, filename) , 'w') as outfile:
			json.dump(objectToSave, outfile)
		return

	def getFilenameRoot(self):

		# Let's make the name of the file a title
		title = self.info['title']
		proposedFilename = ''.join(c for c in title if c in valid_chars)

		return proposedFilename[:120] if len(proposedFilename)>120 else proposedFilename



	def saveMarkdownOnly(self, directory):

		# Check document okay
		if not self.ok():
			URL = self.info['entryURL']
			print("ERROR parsing {}".format(URL), file=sys.stderr)
			if URL not in pendingURLs:
				pendingURLs.append(URL)
			return

		# Let's make the name of the file the title
		filename = self.getFilenameRoot()
		articleText = self.info['markdown']

		with open( "{}/{}.md".format(directory, filename) , 'w') as outfile:
			outfile.write(articleText)

		return

def savePendingList(directory):
	# Let's make the name of the file the title
	filename = 'pending-URLs-to-scrape'
	articleText = str(pendingURLs)

	with open( "{}/{}.json".format(directory, filename) , 'w') as outfile:
		outfile.write(articleText)
	return

# def test():

# 	# Let's test that the page getter works for whitelisted pages
# 	# URL = "http://dx.doi.org/10.1021/jf5053546" # good!

# 	URL = "http://dx.doi.org/10.3390/antiox2030181" # ERROR


# 	document = Document(URL, title='Phenolic Compounds in Apple (Malus x domestica Borkh.): Compounds Characterization and Stability during Postharvest and after Processing') # good!
# 	# print(page)
# 	document.saveMarkdownOnly( './sources/recommendedfoods/apples')


def getJSONFromDirectory(directory):

	with open("{}/article-list.json".format(directory)) as data_file:    
		data = json.load(data_file)
	return data

def scrape(directory, articleList=None):

	print("#####################################")
	print("Scraping: ", directory)

	if articleList is None:
		articleList = getJSONFromDirectory(directory)

	for item in articleList:
		url = item['link']
		titleName = item['title']

		# Now, let's get and save the document
		document = Document(url, title=titleName)
		document.saveMarkdownOnly(directory)

	print( "Pending URLs:", pendingURLs)

	savePendingList(directory)

def parallel_function(f):
	def easy_parallize(f, sequence):
		""" assumes f takes sequence as input, easy w/ Python's scope """
		from multiprocessing import Pool
		pool = Pool(processes=4) # depends on available cores
		result = pool.map(f, sequence) # for i in sequence: result[i] = f(i)
		cleaned = [x for x in result if not x is None] # getting results
		cleaned = asarray(cleaned)
		pool.close() # not optimal! but easy
		pool.join()
		return cleaned
	from functools import partial
	return partial(easy_parallize, f)



if __name__ == '__main__':
	# scrape()

	# Scrape all

	directoryList = [ './sources/badFoods/adzuki-beans', './sources/badFoods/alcohol', './sources/badFoods/almonds', './sources/badFoods/avocados', './sources/badFoods/bacon', './sources/badFoods/basil', './sources/badFoods/beef', './sources/badFoods/brown-rice', './sources/badFoods/butter', './sources/badFoods/cheese', './sources/badFoods/coffee', './sources/badFoods/corn-oil', './sources/badFoods/escargot', './sources/badFoods/ginger', './sources/badFoods/herring-and-sardines', './sources/badFoods/lamb', './sources/badFoods/lavender', './sources/badFoods/mackerel', './sources/badFoods/milk', './sources/badFoods/mushrooms', './sources/badFoods/mustard', './sources/badFoods/papaya', './sources/badFoods/peanuts', './sources/badFoods/pork', './sources/badFoods/potatoes', './sources/badFoods/rhubarb', './sources/badFoods/safflower-oil', './sources/badFoods/saffron', './sources/badFoods/sage', './sources/badFoods/salt', './sources/badFoods/shellfish', './sources/badFoods/soy-protein-isolate', './sources/badFoods/soybean-oil', './sources/badFoods/soybean-paste', './sources/badFoods/sugar', './sources/badFoods/sunflower-oil', './sources/badFoods/yerba-mate', './sources/recommendedFoods/apples', './sources/recommendedFoods/artichokes', './sources/recommendedFoods/basil', './sources/recommendedFoods/bell-peppers', './sources/recommendedFoods/black-pepper', './sources/recommendedFoods/blackberries', './sources/recommendedFoods/blueberries', './sources/recommendedFoods/boysenberries', './sources/recommendedFoods/broccoli', './sources/recommendedFoods/brown-rice', './sources/recommendedFoods/brussels-sprouts', './sources/recommendedFoods/buckwheat', './sources/recommendedFoods/cabbage', './sources/recommendedFoods/canola-oil', './sources/recommendedFoods/carrots', './sources/recommendedFoods/cauliflower', './sources/recommendedFoods/celery', './sources/recommendedFoods/cherries', './sources/recommendedFoods/chicken', './sources/recommendedFoods/coffee', './sources/recommendedFoods/cranberries', './sources/recommendedFoods/cucumbers', './sources/recommendedFoods/currants', './sources/recommendedFoods/Dry Beans', './sources/recommendedFoods/dry-beans', './sources/recommendedFoods/flaxseed', './sources/recommendedFoods/ginger', './sources/recommendedFoods/grapes', './sources/recommendedFoods/green-tea', './sources/recommendedFoods/greens', './sources/recommendedFoods/herring-and-sardines', './sources/recommendedFoods/honey', './sources/recommendedFoods/horseradish', './sources/recommendedFoods/hot-peppers', './sources/recommendedFoods/kale', './sources/recommendedFoods/kefir', './sources/recommendedFoods/lake-trout', './sources/recommendedFoods/lettuce', './sources/recommendedFoods/low-fat-yogurt', './sources/recommendedFoods/mackerel', './sources/recommendedFoods/mushrooms', './sources/recommendedFoods/mustard', './sources/recommendedFoods/olives-and-olive-oil', './sources/recommendedFoods/onions-and-garlic', './sources/recommendedFoods/parsley', './sources/recommendedFoods/pomegranates', './sources/recommendedFoods/pumpkins', './sources/recommendedFoods/raspberries', './sources/recommendedFoods/saffron', './sources/recommendedFoods/salmon', './sources/recommendedFoods/seaweed', './sources/recommendedFoods/soybeans', './sources/recommendedFoods/spinach', './sources/recommendedFoods/tofu', './sources/recommendedFoods/tomatoes', './sources/recommendedFoods/turmeric', './sources/recommendedFoods/turnips-and-turnip-greens', './sources/recommendedFoods/walnuts', './sources/recommendedFoods/watercress', './sources/recommendedFoods/watermelon', './sources/recommendedFoods/zucchini']

	scrape.parallel = parallel_function(scrape)
	result = scrape.parallel(directoryList)

	# for path in directoryList:
	# 	scrape(directory=path)






