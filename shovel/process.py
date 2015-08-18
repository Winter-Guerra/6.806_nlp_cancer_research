
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
import string
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



# Initialize the sentence tokenizer
import nltk.data
sentence_detector = nltk.data.load('tokenizers/punkt/english.pickle')

# Import snowball stemmer
from nltk.stem.snowball import EnglishStemmer
stemmer = EnglishStemmer()

# Import stopwords list
from nltk.corpus import stopwords


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

		self.paragraphList = Document.clean(self.getParagraphList()) # List
		# self.sentences = list(self.getSentences()) # Generator
		self.stemmedSentences = list(self.getStemmedSentences()) # Generator

		# Turned off for speed.
		# self.citation = self.getCitationDetails()
		# self.humanReadableCitation = Document.getHumanReadableCitation(self.citation)
		# self.conclusion = self.getConclusion()

		# Find the document title
		# self.title = getTagText(self.soup.title)

	def clean(paragraphList):
		''' This is a static method that will take in a paragraph list and clean out numbers, brackets, hyphens, numbers, etc. However, it will not clean out punctuation because that is needed for the sentence tokenizer. '''

		for paragraphObj in paragraphList:
			paragraph = paragraphObj['paragraph']

			# Remove all forms of parenthesis, numbering
			cleanedParagraph = paragraph.translate( {ord(i):None for i in '\t0123456789()[]{}' } )

			# Hypens should be turned into spaces
			cleanedParagraph = cleanedParagraph.translate( {ord(i):' ' for i in '-' } )

			# Make the paragraph text lowercase
			cleanedParagraph = cleanedParagraph.lower()

			paragraphObj['paragraph'] = cleanedParagraph.lower()

		return paragraphList

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


	def getParagraphList(self):
		output = []

		# Run the text through bs4 to prettify it
		soup = self.soup

		# Get the paragraph title
		# output.append(
		# 	{'paragraph': getTagText(soup.title), 'treeLocation': ['title']}
		# )

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
						output.append(paragraphEntry)

		return output

	def getCitationDetails(self):
		output = {}
		soup = self.soup

		# All of the citation information in PMC articles is contained in <meta> tags that have names that start with name="citation_xxx"

		metatags = soup.find_all('meta', {'name':re.compile("citation_.*")})
		# print(metatags)

		# Now, let's scape off the data from the metatags
		for metatag in metatags:
			key = ' '.join( metatag['name'].split('_')[1:] )
			value = metatag['content']

			# Save the metatag data
			output[key] = value

		return output

	def getHumanReadableCitation(citation):
		# Our citation should be of the form:
		# Journal, earliest published date

		# Check to see if we have a citation_
		if len(citation.keys())>0:

			# Find the closest tags
			journal = citation.get(Document.getClosestKeyToString(citation, 'journal'), '')
			publishedDate = citation.get(Document.getClosestKeyToString(citation, 'date'), '')

			humanReadableCitation = "{}. Published {}.".format(journal, publishedDate)
			return humanReadableCitation

	def getClosestKeyToString( obj, targetKey):
		''' This is mainly used for getting humanReadableCitations from the citation metadata. Uses fuzzy selection to get results. '''

		keys = obj.keys()
		similarityRatios = [difflib.SequenceMatcher(a=key.lower(), b=targetKey).ratio() for key in keys ]

		mostSimilarObject = max(zip(similarityRatios, keys), key=lambda x: x[0])

		return mostSimilarObject[1]


	def getSentences(self):
		''' This is a generator that spits out the text of the document. '''

		# Let's walk through the paragraphs of the text and tokenize the paragraphs into text
		for paragraphObj in self.paragraphList:

			paragraph = paragraphObj['paragraph']

			if paragraph is not None:

				newSentences = sentence_detector.tokenize(paragraph)

				for sentence in newSentences:
					yield sentence


	def getTokenizedSentenceFromParagraph(paragraph):
		# Tokenize paragraph into sentences
		sentences = sentence_detector.tokenize(paragraph)

		for sentence in sentences:
			# remove punctuation
			sentence = sentence.translate( {ord(i):None for i in string.punctuation+'\r\n\t' } )

			tokenizedSentence = sentence.split()

			# remove stop words
			tokenizedSentence = [word for word in tokenizedSentence if word not in stopwords.words('english')]

			yield tokenizedSentence


	def getStemmedSentences(self):
		''' This will return a generator list of stemmed sentence objects using the snowball stemmer '''
		output = []

		for paragraphObj in self.paragraphList:
			paragraph = paragraphObj['paragraph']

			# Tokenize paragraph into sentences
			sentences = Document.getTokenizedSentenceFromParagraph(paragraph)

			for tokenizedSentence in sentences:

				words = tokenizedSentence
				stemmedWords = [stemmer.stem(word) for word in words]

				stemmedSentence = ' '.join(stemmedWords)

				# Copy the paragraph obj
				newSentenceObj = {key:val for key,val in paragraphObj.items()}
				del newSentenceObj['paragraph']

				newSentenceObj['sentence'] = stemmedSentence

				# Yield this sentence obj
				# yield newSentenceObj
				output.append(newSentenceObj)

		return output

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

		if len(tmpConclusions) > 0:
			return ' '.join([conclusion['paragraph'] for conclusion in conclusions]).replace('/n', '')
