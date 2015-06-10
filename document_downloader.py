# This script will look through each folder in our source list download the article associated with it.

# THIS SCRIPT REQUIRES Python3 and Pip3


import json
import requests
import html2text
import re

markdown = html2text.HTML2Text()
markdown.ignore_links = True
markdown.ignore_images = True
# markdown.images_to_alt = True # No, because this does not completely remove the crap
markdown.body_width = 0

downloadedArticles = {}
pendingURLs = []

# Pages with subscriptions and PDF downloads
whitelistedPages = {
	"onlinelibrary.wiley.com": "http://onlinelibrary.wiley.com/doi/{}/full",
	"pubs.acs.org": "http://pubs.acs.org/doi/full/{}",
	"link.springer.com" : "http://link.springer.com/article/{}/fulltext.html",
	"online.liebertpub.com": "http://online.liebertpub.com/doi/full/{}"
}

# Pages with 

# For each folder, loop through the links and try to download them or load them from the cache

def getArticle(URL):

	# Check if we already have the article

	if URL in downloadedArticles:
		print("Got URL from cache")
		return downloadedArticles[URL]

	# else, we should download the article
	else:
		page = requests.get(URL)

		if page.ok:

			# Check if the article has a DOI
			potentialDOI = URL.split('dx.doi.org/')[-1]
			DOI = potentialDOI if (potentialDOI is not URL and len(potentialDOI) is not 0) else None


			# Let's figure out where our target page lives
			targetAddress = page.url

			# Now, let's download and translate the page
			articleAddress = None

			for website, template in whitelistedPages.items():
				if website in targetAddress:
					articleAddress = template.format(DOI)
					# print("using template", "website", articleAddress)
			
			if articleAddress is None:
				print("I do not know how to convert and download {}".format(targetAddress))
				pendingURLs.append(targetAddress)

			else :
				# Download the html file
				page = requests.get(articleAddress)


		# MUST ADD RESULT TO DATABASE
		if page.ok:
			downloadedArticles[URL] = page.text
			return page.text
		else:
			return None


def convertPageToMarkdown(htmlPage):

	# Convert page to markdown
	markdownPage = markdown.handle(htmlPage)
	# print(markdownPage)
	

	# Get the title
	match = re.search("(^#\s.*\n)", markdownPage, flags=re.IGNORECASE|re.MULTILINE)
	title = match.group(1)
	# print(title)


	# Remove all text before abstract and after reference section 
	match = re.search("(^#+ abstract[\s\S]*)\s#+ reference", markdownPage, flags=re.IGNORECASE|re.MULTILINE)
	# print(match)
	article = match.group(1) # The highlighted selector

	cleanArticle = title + '\n' +  article

	# Now, clean the article from unneeded lines of lists

	# Clean out images
	cleanArticle = re.sub(r'^\s*\*.*\n', '', cleanArticle,  flags=re.IGNORECASE|re.MULTILINE)

	return cleanArticle


def test():

	# Let's test that the page getter works for whitelisted pages
	# getArticle("http://dx.doi.org/10.1021/jf5053546") # good!

	page = getArticle("http://dx.doi.org/10.1021/jf5053546") # good!
	# print(page)

	article = convertPageToMarkdown(page)
	print(article)


	# Check that it crashes on bad pages
	# print getArticle("http://link.springer.com/article/10.1007%2Fs11626-013-9681-6") # good!

	# print("PENDING URLS")
	# print(pendingURLs)

def scrape():

	# Walk through the directory tree

	directories = ['']




if __name__ == '__main__':
	test()






