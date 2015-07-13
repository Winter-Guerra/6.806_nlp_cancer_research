
from shovel import task

import glob
import random
import os
from bs4 import BeautifulSoup
import datetime
import re
import requests
# Import C yaml bindings
import yaml
try:
	from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
	from yaml import Loader, Dumper

def removePunctuation(s):
	s = re.sub(r'[^\w\s]','',s)
	return s

def getTagText(tag):
	if tag.text is None:
		return None
	else:
		return removePunctuation(tag.text.strip().lower())

# @TODO ####################################
def getPMCID(html):
	PMCID = ''
	return PMCID

# @TODO ####################################
def getFullArticle(URL):
	''' Look at a webpage and check if we can find a better version of the webpage. This happens by looking for "read full text" link tags '''

	landingPage = requests.get(URL).text

	fullArticle = landingPage

	soup = BeautifulSoup(landingPage, 'html5lib')

	# Find the div that holds free links
	links = soup.select('div.icons.portlet a[free_status="free"]')
	# print(links)

	if len(links) > 0:
		fullLink = links[-1]['href']
		# print(fullLink)
		fullArticle = requests.get(fullLink).text

	return fullArticle

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
			lastIndexOfTree = len(self.tree)-delta
			# Slice out old parts of tree
			self.tree = self.tree[:lastIndexOfTree]

			# Replace the current endpoint of the tree with the last tag
			self.tree[-1] = tagText


class Document():

	def __init__(self, html):

		self.paragraphList = []
		self.citation = {
			"datePublishedRaw": None,
			"journal": None
		}
		self.DOI = None

		# Get document from HTML
		self.initParagraphList(html)
		self.getDOI(html)
		self.getCitationDetailsFromDOI()


	def initParagraphList(self, html):
		# Run the text through bs4 to prettify it
		soup = BeautifulSoup(html, 'html5lib')

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



	def getDOI(self, html):
		# Run the text through bs4 to prettify it
		soup = BeautifulSoup(html, 'html5lib')

		# Find the citation data container
		doiList = soup.select('div [class="cit"]')
		self.DOI = None # For scope
		if len(doiList) > 0:

			doiContainer = doiList[0].text if (len(doiList) > 0) else ''

			# Now find the DOI from the raw text
			match = re.search("doi: (.*)\. ", doiContainer)
			if match is not None:
				self.DOI = match.group(1)

	def getCitationDetailsFromDOI(self):
		journal = None
		datePublishedRaw = None

		if self.DOI is not None:
			rawCitationData = requests.get("http://api.crossref.org/works/{DOI}".format(DOI=self.DOI)).json()['message']
			journal = rawCitationData['container-title'][0]
			datePublishedRaw = rawCitationData['deposited']['timestamp']

		self.citation = {
			"datePublishedRaw": datePublishedRaw,
			"journal": journal
		}


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



@task
def createParagraphFeatures(destination):
	''' This function will convert all documents in the current folder into yaml docs. Then, it will output them to a destination folder. '''

	for file in glob.iglob('./*.html'):
		# Open the html file
		html = ''
		with open(file, 'r') as f:
			html = f.read()

		document = Document(html)

@task
def reduceTo100Files(directory, probability):
	for file in glob.iglob(directory+'*.md'):

		shouldDelete = (random.random() <= float(probability))

		if shouldDelete:
			os.remove(file)
