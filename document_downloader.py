# This script will look through each folder in our source list download the article associated with it.

# THIS SCRIPT REQUIRES Python3 and Pip3


import json
import requests
import html2text
import re
import urllib.request
import string

valid_chars = "-_ %s%s" % (string.ascii_letters, string.digits)

markdown = html2text.HTML2Text()
markdown.ignore_links = True
markdown.ignore_images = True
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
	"www.mdpi.com":
		{'root': "{}/htm", 'key':'landingPage'}
}

class Document:

	def __init__(self, entryURL):
		self.info = {
			'entryURL': entryURL
		}

		self.info['DOI'] = self.getDOI()
		self.info['landingPage'] =  self.getLandingPageURL()
		self.info['articleURL'] = self.findArticleURL()

		self.info['articleHTML'] = self.getArticle()
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
				print("I do not know how to convert and download {}".format(landingPageURL), file=sys.stderr)
				pendingURLs.append(landingPageURL)

				# Return the entry link since there is probably some info there
				outputURL = landingPageURL

		# Request failed because link is busted
		else:
			# We got a broken link
			print("We got a broken entry link {}".format(landingPageURL), file=sys.stderr)


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
		match = re.search("(^#\s.*\n)", markdownPage, flags=re.IGNORECASE|re.MULTILINE)
		title = match.group(1)

		# Remove all text before abstract and after reference section 
		match = re.search("(^#+ abstract[\s\S]*)\s#+ reference", markdownPage, flags=re.IGNORECASE|re.MULTILINE)
		# print(match)
		article = match.group(1) # The highlighted selector

		cleanArticle = title + '\n' +  article

		# Clean out unordered lists and horizontal rules
		cleanArticle = re.sub(r'^\s*\*.*\n', '', cleanArticle,  flags=re.IGNORECASE|re.MULTILINE)

		# Clean out ordered lists

		return cleanArticle

	def saveDocument(self, directory):

		objectToSave = self.info

		# Let's make the name of the file the title
		filename = self.getFilenameRoot()

		with open( "{}/{}.json".format(directory, filename) , 'w') as outfile:
			json.dump(objectToSave, outfile)

		return

	def getFilenameRoot(self):

		# Let's make the name of the file a title
		match = re.search("(^#\s.*\n)", self.info['markdown'], flags=re.IGNORECASE|re.MULTILINE)
		title = match.group(1)

		return ''.join(c for c in title if c in valid_chars)



	def saveMarkdownOnly(self, directory):

		# Let's make the name of the file the title
		filename = self.getFilenameRoot()
		articleText = self.info['markdown']

		with open( "{}/{}.md".format(directory, filename) , 'w') as outfile:
			outfile.write(articleText)

		return


def test():

	# Let's test that the page getter works for whitelisted pages
	URL = "http://dx.doi.org/10.1021/jf5053546" # good!

	# URL = "http://dx.doi.org/10.3390/antiox2030181" # ERROR


	document = Document(URL) # good!
	# print(page)
	document.saveMarkdownOnly( './sources/recommendedfoods/apples')



def scrape():

	# Walk through the directory tree

	directories = ['']




if __name__ == '__main__':
	test()






