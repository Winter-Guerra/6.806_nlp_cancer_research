
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

# @TODO ####################################
def getPMCID(html):
	PMCID = ''
	return PMCID

# @TODO ####################################
def getFullPubmedArticle(html):
	fullArticle = ''
	return fullArticle

class documentHeirarchy():
	def __init__(self, firstHeaderTag):
		# Figure out what tag level is this first tag. This should be our "base level"
		self.baseTagLevel = self.getTagLevel(firstHeaderTag)

		self.tree = [self.getTagText(firstHeaderTag)]

	def getState(self):
		return self.tree

	def getTreeDepth(self):
		if len(self.tree) is 0:
			return None # This should never happen
		else:
			return (len(self.tree)+self.baseTagLevel-1)

	def getTagLevel(self, headerTag):
		match = re.search("h(\d)", headerTag.name)
		tagLevel = int(match.group(1))
		return tagLevel

	def getTagText(self, headerTag):
		text = headerTag.string
		if text is None:
			return None
		else:
			return removePunctuation( text.strip() )

	def updateState(headerTag):
		# Figure out what tag level we are at
		tagLevel = self.getTagLevel(headerTag)
		tagText = self.getTagText(headerTag)

		# If this tag is same depth as our current tag
		if self.getTreeDepth() == tagLevel:
			self.tree[-1] = tagText
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
	document = [
		{'paragraph': soup.title.string.strip(), 'treeLocation': ['title']}
	]



	# Find the interleaved combinations of headers and text
	paragraphsAndHeaders = soup.find_all(['p', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8', 'h9'])

	print(paragraphsAndHeaders)


	return document

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
