# This script will look through each folder in our source list download the article associated with it.

# THIS SCRIPT REQUIRES Python3 and Pip3


import json
import yaml
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
# 	document.saveMarkdownOnly( './sources/recommendedfoodsSummary/apples')


def getJSONFromDirectory(directory):

	with open("{}/article-list.json".format(directory)) as data_file:    
		data = json.load(data_file)
	return data

# This file should only be once
def fixPending_URL_JSON(directory):

	# Find the json file for the directory.

	objData = None # For scope


	try:
		with open("{}/pending-URLs-to-scrape.json".format(directory), 'r+') as f:    
			
			# Get the file from the data
			lines = f.readlines()
			f.seek(0)
			# print(lines)

			# Check if the jsonfile is a valid json file
			try:
				data = json.load(f)
				objData = data
			
			except:
				# Fix the json file by replacing all '' with ""

				
				lines = [re.sub("\'", '\"', line) for line in lines]
				
				jsonString = "".join(lines)
				objData = json.loads(jsonString)

	except IOError:
		pass # Handle missing files gracefully

	if objData is not None:
		# Then we need to write the new file and delete the old file
		with open("{}/pending-URLs-to-scrape.yaml".format(directory), 'w') as f: 
			yaml.dump(objData, f)

		# If that completed successfully, delete the old file
		os.remove("{}/pending-URLs-to-scrape.json".format(directory))


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
		pool = Pool(processes=2) # depends on available cores
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

	# directoryList = [ './sources/badFoodsSummary/adzuki-beans', './sources/badFoodsSummary/alcohol', './sources/badFoodsSummary/almonds', './sources/badFoodsSummary/avocados', './sources/badFoodsSummary/bacon', './sources/badFoodsSummary/basil', './sources/badFoodsSummary/beef', './sources/badFoodsSummary/brown-rice', './sources/badFoodsSummary/butter', './sources/badFoodsSummary/cheese', './sources/badFoodsSummary/coffee', './sources/badFoodsSummary/corn-oil', './sources/badFoodsSummary/escargot', './sources/badFoodsSummary/ginger', './sources/badFoodsSummary/herring-and-sardines', './sources/badFoodsSummary/lamb', './sources/badFoodsSummary/lavender', './sources/badFoodsSummary/mackerel', './sources/badFoodsSummary/milk', './sources/badFoodsSummary/mushrooms', './sources/badFoodsSummary/mustard', './sources/badFoodsSummary/papaya', './sources/badFoodsSummary/peanuts', './sources/badFoodsSummary/pork', './sources/badFoodsSummary/potatoes', './sources/badFoodsSummary/rhubarb', './sources/badFoodsSummary/safflower-oil', './sources/badFoodsSummary/saffron', './sources/badFoodsSummary/sage', './sources/badFoodsSummary/salt', './sources/badFoodsSummary/shellfish', './sources/badFoodsSummary/soy-protein-isolate', './sources/badFoodsSummary/soybean-oil', './sources/badFoodsSummary/soybean-paste', './sources/badFoodsSummary/sugar', './sources/badFoodsSummary/sunflower-oil', './sources/badFoodsSummary/yerba-mate', './sources/recommendedFoodsSummary/apples', './sources/recommendedFoodsSummary/artichokes', './sources/recommendedFoodsSummary/basil', './sources/recommendedFoodsSummary/bell-peppers', './sources/recommendedFoodsSummary/black-pepper', './sources/recommendedFoodsSummary/blackberries', './sources/recommendedFoodsSummary/blueberries', './sources/recommendedFoodsSummary/boysenberries', './sources/recommendedFoodsSummary/broccoli', './sources/recommendedFoodsSummary/brown-rice', './sources/recommendedFoodsSummary/brussels-sprouts', './sources/recommendedFoodsSummary/buckwheat', './sources/recommendedFoodsSummary/cabbage', './sources/recommendedFoodsSummary/canola-oil', './sources/recommendedFoodsSummary/carrots', './sources/recommendedFoodsSummary/cauliflower', './sources/recommendedFoodsSummary/celery', './sources/recommendedFoodsSummary/cherries', './sources/recommendedFoodsSummary/chicken', './sources/recommendedFoodsSummary/coffee', './sources/recommendedFoodsSummary/cranberries', './sources/recommendedFoodsSummary/cucumbers', './sources/recommendedFoodsSummary/currants', './sources/recommendedFoodsSummary/Dry Beans', './sources/recommendedFoodsSummary/dry-beans', './sources/recommendedFoodsSummary/flaxseed', './sources/recommendedFoodsSummary/ginger', './sources/recommendedFoodsSummary/grapes', './sources/recommendedFoodsSummary/green-tea', './sources/recommendedFoodsSummary/greens', './sources/recommendedFoodsSummary/herring-and-sardines', './sources/recommendedFoodsSummary/honey', './sources/recommendedFoodsSummary/horseradish', './sources/recommendedFoodsSummary/hot-peppers', './sources/recommendedFoodsSummary/kale', './sources/recommendedFoodsSummary/kefir', './sources/recommendedFoodsSummary/lake-trout', './sources/recommendedFoodsSummary/lettuce', './sources/recommendedFoodsSummary/low-fat-yogurt', './sources/recommendedFoodsSummary/mackerel', './sources/recommendedFoodsSummary/mushrooms', './sources/recommendedFoodsSummary/mustard', './sources/recommendedFoodsSummary/olives-and-olive-oil', './sources/recommendedFoodsSummary/onions-and-garlic', './sources/recommendedFoodsSummary/parsley', './sources/recommendedFoodsSummary/pomegranates', './sources/recommendedFoodsSummary/pumpkins', './sources/recommendedFoodsSummary/raspberries', './sources/recommendedFoodsSummary/saffron', './sources/recommendedFoodsSummary/salmon', './sources/recommendedFoodsSummary/seaweed', './sources/recommendedFoodsSummary/soybeans', './sources/recommendedFoodsSummary/spinach', './sources/recommendedFoodsSummary/tofu', './sources/recommendedFoodsSummary/tomatoes', './sources/recommendedFoodsSummary/turmeric', './sources/recommendedFoodsSummary/turnips-and-turnip-greens', './sources/recommendedFoodsSummary/walnuts', './sources/recommendedFoodsSummary/watercress', './sources/recommendedFoodsSummary/watermelon', './sources/recommendedFoodsSummary/zucchini']

	# Let's download summaries for each folder

	directoryList = [ './sources/raw/badFoodsSummary/adzuki-beans', './sources/raw/badFoodsSummary/alcohol', './sources/raw/badFoodsSummary/almonds', './sources/raw/badFoodsSummary/avocados', './sources/raw/badFoodsSummary/bacon', './sources/raw/badFoodsSummary/basil', './sources/raw/badFoodsSummary/beef', './sources/raw/badFoodsSummary/brown-rice', './sources/raw/badFoodsSummary/butter', './sources/raw/badFoodsSummary/cheese', './sources/raw/badFoodsSummary/coffee', './sources/raw/badFoodsSummary/corn-oil', './sources/raw/badFoodsSummary/escargot', './sources/raw/badFoodsSummary/ginger', './sources/raw/badFoodsSummary/herring-and-sardines', './sources/raw/badFoodsSummary/lamb', './sources/raw/badFoodsSummary/lavender', './sources/raw/badFoodsSummary/mackerel', './sources/raw/badFoodsSummary/milk', './sources/raw/badFoodsSummary/mushrooms', './sources/raw/badFoodsSummary/mustard', './sources/raw/badFoodsSummary/papaya', './sources/raw/badFoodsSummary/peanuts', './sources/raw/badFoodsSummary/pork', './sources/raw/badFoodsSummary/potatoes', './sources/raw/badFoodsSummary/rhubarb', './sources/raw/badFoodsSummary/safflower-oil', './sources/raw/badFoodsSummary/saffron', './sources/raw/badFoodsSummary/sage', './sources/raw/badFoodsSummary/salt', './sources/raw/badFoodsSummary/shellfish', './sources/raw/badFoodsSummary/soy-protein-isolate', './sources/raw/badFoodsSummary/soybean-oil', './sources/raw/badFoodsSummary/soybean-paste', './sources/raw/badFoodsSummary/sugar', './sources/raw/badFoodsSummary/sunflower-oil', './sources/raw/badFoodsSummary/yerba-mate', './sources/raw/recommendedFoodsSummary/apples', './sources/raw/recommendedFoodsSummary/artichokes', './sources/raw/recommendedFoodsSummary/basil', './sources/raw/recommendedFoodsSummary/bell-peppers', './sources/raw/recommendedFoodsSummary/black-pepper', './sources/raw/recommendedFoodsSummary/blackberries', './sources/raw/recommendedFoodsSummary/blueberries', './sources/raw/recommendedFoodsSummary/boysenberries', './sources/raw/recommendedFoodsSummary/broccoli', './sources/raw/recommendedFoodsSummary/brown-rice', './sources/raw/recommendedFoodsSummary/brussels-sprouts', './sources/raw/recommendedFoodsSummary/buckwheat', './sources/raw/recommendedFoodsSummary/cabbage', './sources/raw/recommendedFoodsSummary/canola-oil', './sources/raw/recommendedFoodsSummary/carrots', './sources/raw/recommendedFoodsSummary/cauliflower', './sources/raw/recommendedFoodsSummary/celery', './sources/raw/recommendedFoodsSummary/cherries', './sources/raw/recommendedFoodsSummary/chicken', './sources/raw/recommendedFoodsSummary/coffee', './sources/raw/recommendedFoodsSummary/cranberries', './sources/raw/recommendedFoodsSummary/cucumbers', './sources/raw/recommendedFoodsSummary/currants', './sources/raw/recommendedFoodsSummary/dry-beans', './sources/raw/recommendedFoodsSummary/flaxseed', './sources/raw/recommendedFoodsSummary/ginger', './sources/raw/recommendedFoodsSummary/grapes', './sources/raw/recommendedFoodsSummary/green-tea', './sources/raw/recommendedFoodsSummary/greens', './sources/raw/recommendedFoodsSummary/herring-and-sardines', './sources/raw/recommendedFoodsSummary/honey', './sources/raw/recommendedFoodsSummary/horseradish', './sources/raw/recommendedFoodsSummary/hot-peppers', './sources/raw/recommendedFoodsSummary/kale', './sources/raw/recommendedFoodsSummary/kefir', './sources/raw/recommendedFoodsSummary/lake-trout', './sources/raw/recommendedFoodsSummary/lettuce', './sources/raw/recommendedFoodsSummary/low-fat-yogurt', './sources/raw/recommendedFoodsSummary/mackerel', './sources/raw/recommendedFoodsSummary/mushrooms', './sources/raw/recommendedFoodsSummary/mustard', './sources/raw/recommendedFoodsSummary/olives-and-olive-oil', './sources/raw/recommendedFoodsSummary/onions-and-garlic', './sources/raw/recommendedFoodsSummary/parsley', './sources/raw/recommendedFoodsSummary/pomegranates', './sources/raw/recommendedFoodsSummary/pumpkins', './sources/raw/recommendedFoodsSummary/raspberries', './sources/raw/recommendedFoodsSummary/saffron', './sources/raw/recommendedFoodsSummary/salmon', './sources/raw/recommendedFoodsSummary/seaweed', './sources/raw/recommendedFoodsSummary/soybeans', './sources/raw/recommendedFoodsSummary/spinach', './sources/raw/recommendedFoodsSummary/tofu', './sources/raw/recommendedFoodsSummary/tomatoes', './sources/raw/recommendedFoodsSummary/turmeric', './sources/raw/recommendedFoodsSummary/turnips-and-turnip-greens', './sources/raw/recommendedFoodsSummary/walnuts', './sources/raw/recommendedFoodsSummary/watercress', './sources/raw/recommendedFoodsSummary/watermelon', './sources/raw/recommendedFoodsSummary/zucchini']

	for folder in directoryList:

		foodType = folder.split('/')[-1]

		print("Scraping summary for {}".format(foodType))

		URL = "http://foodforbreastcancer.com/foods/{}".format(foodType)
		
		page = requests.get(URL)
		
		# format the page in markdown
		markdownPage = markdown.handle(page.text)

		# Save the page
		filename = "{}/summary.md".format(folder)

		# CLean the file
		# Remove tables
		markdownPage = re.sub(r'<table[\s\S]+?</table>', '', markdownPage,  flags=re.IGNORECASE|re.MULTILINE)

		# Remove asterisks
		markdownPage = re.sub(r'\*', '', markdownPage,  flags=re.IGNORECASE|re.MULTILINE)

		# Remove header
		markdownPage = re.sub(r'[\s\S]*# Food for Breast Cancer', '', markdownPage,  flags=re.IGNORECASE)

		# Remove footer
		markdownPage = re.sub(r'## Selected[\s\S]*', '', markdownPage,  flags=re.IGNORECASE)

		# Remove tags list
		markdownPage = re.sub(r'Tags:.*', '', markdownPage,  flags=re.IGNORECASE|re.MULTILINE)

		with open( filename, 'w') as outfile:
			outfile.write(markdownPage)





