
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


def getDocumentFeatures(html):
	# Run the text through bs4 to prettify it
	soup = BeautifulSoup(html, 'html5lib')

	# Start extracting data and compiling it into a document
	document = [
		{'paragraph': soup.title.string.strip(), 'treeLocation': ['title']}
	]

	# print("Title:", document['title'])

	# Let's find all paragraphs
	text = soup.find_all('p')
	for paragraph in text:

		if paragraph.string is not None:

			# Find a comma separated list of headings that shows the paragraph's place in the tree.
			tree = []

			for parent in reversed(list(paragraph.parents)):

				# Check if there is a sibling here that is a heading
				# print(parent.previous_siblings)
				for sibling in parent.find_previous_siblings(re.compile("^h[2-9]")):
					# print(sibling)
					if sibling.string is not None:
						tree.append(removePunctuation(sibling.string.strip().lower()))
						break

			for sibling in paragraph.find_previous_siblings(re.compile("^h[2-9]")):
				if sibling.string is not None:
					tree.append(removePunctuation(sibling.string.strip().lower()))
					break

			# Check that the paragraph has a title
			if len(tree) is not 0:

				# Save the paragraph in the paragraph list
				paragraphEntry = {
					'paragraph': paragraph.string.strip(),
					'treeLocation': tree
				}
				document.append(paragraphEntry)
				# Print debug info
				# print(document['paragraphs'][-1])
				# print('')

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
