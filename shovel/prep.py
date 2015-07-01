
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


def getDocumentFeatures(html):
	# Run the text through bs4 to prettify it
	soup = BeautifulSoup(html, 'html5lib')

	# Start extracting data and compiling it into a document
	document = {
		'title':soup.title.string
	}

	print("Title:", document['title'])

	# Let's find all paragraphs
	text = soup.find_all('p')
	for paragraph in text:

		if paragraph.string is not None:

			# Find a comma separated list of headings that shows the paragraph's place in the tree.
			tree = []

			for parent in reversed(list(paragraph.parents)):
				# Check if there is a sibling here that is a heading
				for sibling in parent.find_previous_siblings(re.compile("^h[^1]")):
					if sibling.string is not None:
						tree.append(removePunctuation(sibling.string.strip().lower()))

			for sibling in paragraph.find_previous_siblings(re.compile("^h")):
				if sibling.string is not None:
					tree.append(removePunctuation(sibling.string.strip().lower()))
					break

			# Check that the paragraph has a title
			if len(tree) is not 0:

				# Save the paragraph
				paragraphList = document.get(tuple(tree), [])
				paragraphList.append(paragraph.string)
				document[tuple(tree)] = paragraphList
				# Print debug info
				# print(document['paragraphs'][-1])
				print('')

	return document

def getParagraphsWithTag(document, tag):

	output = {}
	for key, val in document.items():
		if tag in key:
			output[key] = val
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
