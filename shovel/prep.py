
from shovel import task

import glob
from bs4 import BeautifulSoup
import re
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
def getFullPubmedArticle(html):
	fullArticle = ''
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



def getDocumentFeatures(html):
	# Run the text through bs4 to prettify it
	soup = BeautifulSoup(html, 'html5lib')

	# Start extracting data and compiling it into a document
	doc = [
		{'paragraph': getTagText(soup.title), 'treeLocation': ['title']}
	]



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
				paragraphText = getTagText(tag)

				# Check that the paragraph has text
				if paragraphText is not None:
					paragraphEntry = {
						'paragraph': paragraphText,
						'treeLocation': paragraphLocation
					}

					# print(paragraphEntry)

					# save the paragraph in the document
					doc.append(paragraphEntry)



	print(doc)


	return doc

def getParagraphsWithTag(document, tag):

	output = []
	for paragraphEntry in document:
		if tag in paragraphEntry['treeLocation']:
			output.append(paragraphEntry)
	return output


@task
def createParagraphFeatures(destination):
	''' This function will convert all documents in the current folder into yaml docs. Then, it will output them to a destination folder. '''

	for file in glob.iglob('./*.html'):
		# Open the html file
		html = ''
		with open(file, 'r') as f:
			html = f.read()

		document = getDocumentFeatures(html)
