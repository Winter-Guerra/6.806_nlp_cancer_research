
# from shovel import task

import glob
import random
import os
from bs4 import BeautifulSoup
import datetime
import difflib
import re
# Import C yaml bindings
import yaml
try:
	from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
	from yaml import Loader, Dumper

from . import scraper
import requests

import redis
import pickle
# Connect to the cache
r = redis.StrictRedis(host='localhost', port=6379, db=0)


def removePunctuation(s):
	s = re.sub(r'[^\w\s]','',s)
	return s

def getTagText(tag):
	if tag is None:
		return None
	else:
		if tag.text is None:
			return None
		else:
			return removePunctuation(tag.text.strip().lower())

# @TODO ####################################
def getPMCID(html):
	PMCID = ''
	return PMCID

# @TODO ####################################


class DocumentHeirarchy():
	''' This class keeps track of where we are in the document heirarchy as we parse the document. '''
	def __init__(self):
		''' This will be initialized later '''
		self.baseTagLevel = None
		self.tree = None

	def initHeirarchy(self, firstHeaderTag):
		# Figure out what tag level is this first tag. This should be our "base level"
		self.baseTagLevel = self.getTagLevel(firstHeaderTag)

		self.tree = [getTagText(firstHeaderTag)]


	def getState(self):
		return self.tree

	def hasHeirarchy(self):
		return (self.getState() is not None)

	def getTreeDepth(self):
		return (len(self.tree)+self.baseTagLevel-1)

	def getTagLevel(self, headerTag):
		match = re.search("h(\d)", headerTag.name)
		tagLevel = int(match.group(1))
		return tagLevel

	def update(self, headerTag):
		# Check if we have a heirarchy to update. Otherwise, init the heirarchy.
		if not self.hasHeirarchy():
			self.initHeirarchy(headerTag)

		# Figure out what tag level we are at
		tagLevel = self.getTagLevel(headerTag)
		tagText = getTagText(headerTag)
		# print(headerTag.name)

		# If this tag is same depth as our current tag
		if self.getTreeDepth() == tagLevel:
			self.tree[-1] = tagText
			# print(self.tree[-1])
		elif self.getTreeDepth() < tagLevel:
			self.tree.append(tagText)
		# Tag is smaller than current depth
		else:
			delta = self.getTreeDepth() - tagLevel
			lastIndexOfTree = max(0, len(self.tree)-delta)
			# Slice out old parts of tree
			self.tree = self.tree[:lastIndexOfTree]

			# Replace the current endpoint of the tree with the last tag
			if len(self.tree) is 0:
				# Then, we have a tag that should actually be our base tag
				self.initHeirarchy(headerTag)

			# Otherwise, just replace the tag
			else:
				self.tree[-1] = tagText




class Document():

	def __init__(self, URL):

		self.URL = URL
		self.html = scraper.get(URL).text
		self.soup = BeautifulSoup(self.html, 'html5lib')

		# Make sure that we have the correct article
		self.ensureHasFullArticle()

		self.paragraphList = []
		self.citation = {} # This dict will be populated with more terms later.
		self.humanReadableCitation = ''

		self.conclusion = None

		# Process document from HTML
		self.initParagraphList()
		self.getCitationDetails()
		self.getHumanReadableCitation()
		self.getConclusion()

	def ensureHasFullArticle(self):
		''' Look at a webpage and check if we can find a better version of the webpage. This happens by looking for "read full text" link tags '''

		# Find the div that holds free links
		links = self.soup.select('div.icons.portlet a')

		# Let's check if there is a better version of the webpage
		if len(links) > 0:

			# Let's find the available urls
			URLs = [tag['href'] for tag in links]
			# Let's favor NIH links over other links
			NIHLinks = [url for url in URLs if 'ncbi.nlm.nih.gov' in url]
			sortedURLS = NIHLinks + URLs
			# Pick the best URL from the sorted list
			URL = URLs[0]

			# Now, save this better version of the webpage
			self.URL = URL
			self.html = scraper.get(URL).text
			self.soup = BeautifulSoup(self.html, 'html5lib')


	def initParagraphList(self):
		# Run the text through bs4 to prettify it
		soup = self.soup

		# Get the paragraph title
		self.paragraphList.append(
			{'paragraph': getTagText(soup.title), 'treeLocation': ['title']}
		)

		# Find the interleaved combinations of headers and text
		headerTags = ['h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8', 'h9']
		paragraphTags = ['p']
		paragraphsAndHeaders = soup.find_all( headerTags + paragraphTags )

		# Let's start parsing the document heirarchy
		heirarchy = DocumentHeirarchy()

		for tag in paragraphsAndHeaders:

			# Check if the tag is a header tag
			if tag.name in headerTags:
				# print(tag)
				heirarchy.update(tag)
				# print(heirarchy.getState())

			else:
				# We must have a paragraph tag
				if heirarchy.hasHeirarchy():

					# The paragraph location list needs to be copied. Otherwise, the saved location will be overwritten.
					paragraphLocation = list(heirarchy.getState())
					paragraphText = tag.text

					# Check that the paragraph has text
					if paragraphText is not None:
						paragraphEntry = {
							'paragraph': paragraphText,
							'treeLocation': paragraphLocation
						}

						# print(paragraphEntry)

						# save the paragraph in the document
						self.paragraphList.append(paragraphEntry)

	def getCitationDetails(self):
		soup = self.soup

		# All of the citation information in PMC articles is contained in <meta> tags that have names that start with name="citation_xxx"

		metatags = soup.find_all('meta', {'name':re.compile("citation_.*")})
		# print(metatags)

		# Now, let's scape off the data from the metatags
		for metatag in metatags:
			key = ' '.join( metatag['name'].split('_')[1:] )
			value = metatag['content']

			# Save the metatag data
			self.citation[key] = value

	def getHumanReadableCitation(self):
		# Our citation should be of the form:
		# Journal, earliest published date

		# Check to see if we have a citation_
		if len(self.citation.keys())>0:

			# Find the closest tags
			journal = self.citation.get(self.getClosestKeyToString(self.citation, 'journal'), '')
			publishedDate = self.citation.get(self.getClosestKeyToString(self.citation, 'date'), '')

			self.humanReadableCitation = "{}. Published {}.".format(journal, publishedDate)

	def getClosestKeyToString(self, obj, targetKey):
		keys = obj.keys()
		similarityRatios = [difflib.SequenceMatcher(a=key.lower(), b=targetKey).ratio() for key in keys ]

		mostSimilarObject = max(zip(similarityRatios, keys), key=lambda x: x[0])

		return mostSimilarObject[1]





	def getParagraphsWithTags(self, tags):

		tagSet = set(tags)

		output = []
		for paragraphEntry in self.paragraphList:
			treeSet = set(paragraphEntry['treeLocation'])

			if tagSet.issubset(treeSet):
				output.append(paragraphEntry)
		return output

	def getPrettyPublishingDate(self):
		output = None

		timestamp = self.citation['datePublishedRaw'] # To turn a millis timestamp to unix epoch

		if timestamp is not None:
			# print(timestamp)

			# To turn a millis timestamp to unix epoch
			dt = datetime.datetime.fromtimestamp(timestamp/1000)
			output = dt.strftime("%m/%d/%y")
		return output

	def getTextReference(self):
		return "Citation: Journal:{}, Date:{}".format(self.citation['journal'], self.getPrettyPublishingDate())

	def getConclusion(self):
		conclusions = self.getParagraphsWithTags( ['abstract', 'conclusions']) \
			+ self.getParagraphsWithTags( ['abstract', 'conclusion'])

		if len(conclusions) > 0:
			self.conclusion = ' '.join([conclusion['paragraph'] for conclusion in conclusions]).replace('/n', '')
			# print(self.conclusion)



# @task
def createParagraphFeatures(destination):
	''' This function will convert all documents in the current folder into yaml docs. Then, it will output them to a destination folder. '''

	for file in glob.iglob('./*.html'):
		# Open the html file
		html = ''
		with open(file, 'r') as f:
			html = f.read()

		document = Document(html)
