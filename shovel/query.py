# This file is a task runner for running knowledge queries against google.
# Import C yaml bindings
import yaml
try:
	from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
	from yaml import Loader, Dumper
import json
from shovel import task
import requests
import sys
import os
# from bs4 import BeautifulSoup
# import re

from pws import Google
from urllib.parse import urlparse

import prep

import multiprocessing
import mistune

def getURLFromResults(response, idx):
	return response['results'][int(idx)]['link'].split('&')[0]

def getWebpageFromResults(response, idx):
	url = getURLFromResults(response, idx)
	webpageContent = "<!-- URL:" + url + '-->' + requests.get(url).text
	return webpageContent


@task
def run(query, numberResults, showAbstract=True, save=False):

	response = Google.search(query, numberResults)

	for idx, result in enumerate(response['results']):
		if not save:
			print("Page title:", result['link_text'])
			print("Snippet:", result['link_info'])
			print('Website:', urlparse(result['link']).hostname)
			print('Reference:', idx)
			print("Related Queries:", result.get('related_queries',''))

		if showAbstract:
			URL = getURLFromResults(response, idx)
			# Now, find the abstract in the content
			webpageContent = prep.getFullArticle(URL)
			document = prep.Document(webpageContent)

			# Save the document
			result['text'] = document

			# Print the abstract
			if not save:
				print(document.getParagraphsWithTags(['abstract']))
				# print(getParagraphsWithTag(document, ['abstract']))
				print('---------------------------')

	if save:
		# We want to output a json file with the results
		# print(response['results'])
		outputText = json.dumps(response['results'], sort_keys=True, indent=4, separators=(',', ': '))
		# Print the text to stdio
		sys.stdout.write(outputText)

	return

@task
def view(query, idx):
	''' This function can be used to grab HTML webpages using the search function. '''

	response = Google.search(query, int(idx)+1)

	webpageContent = getWebpageFromResults(response, idx)

@task
def test():
	url = 'http://www.ncbi.nlm.nih.gov/pubmed/23349849'
	webpageContent = getFullArticle(url)

	document = getDocumentFeatures(webpageContent)

	# print(getParagraphsWithTags(document, ['abstract']))

@task
def concatConclusions(query, numberResults, includeReference=False, separator='\n'):

	output = ''

	response = Google.search(query, numberResults)

	for idx, result in enumerate(response['results']):

		URL = getURLFromResults(response, idx)
		# Now, find the abstract in the content
		webpageContent = prep.getFullArticle(URL)
		document = prep.Document(webpageContent)

		# Check if the document has a conclusion
		conclusions = document.getParagraphsWithTags( ['abstract', 'conclusions']) \
			+ document.getParagraphsWithTags( ['abstract', 'conclusion'])

		# Ignore documents without conclusions
		if len(conclusions) is 0:
			continue

		for conclusion in conclusions:
			newData = conclusion['paragraph'].replace('\n', '')
			output = output + newData
			print(newData)

		if includeReference:
			# Print the reference
			ref = document.getTextReference()
			output = output + ref
			print(ref)

			# print('----')

		# Get ready for new article conclusion
		output = output + separator

	return output

def dedupeLines(data):
	from more_itertools import unique_everseen

	# Let's get the sentences from the data
	sentences = data.split('\n')

	dedupedSentences = list(unique_everseen(sentences))

	outputFileData = '\n\n'.join(dedupedSentences)

	return outputFileData

def saveSummary(food):
	numberResults = 40

	queryString = "breast cancer {} site:ncbi.nlm.nih.gov".format(food)
	conclusionString = concatConclusions(queryString, numberResults, includeReference=True, separator='\n\n')

	# Let's dedupe the conclusions
	conclusionString = dedupeLines(conclusionString)

	# Now, save the conclusions in a markdown file
	markdownSource = """# {} and Breast Cancer\
\n\n\
	Summary generated using: $shovel3 query.concatConclusions '{}' {} includeReference=True\n\n\
{}""".format(food.capitalize(), queryString, numberResults, conclusionString)

	# Render the markdown
	html = mistune.markdown(markdownSource)

	# Output the rendered markdown to html
	with open("./dist/summaries/{}.html".format(food), 'w') as f:
		f.write(html)

	print("Done with {}".format(food))

	return html

@task
def getFoodListQuery():
	threads = 2

	# Get list of foods
	foodList = []
	with open('./foodList.txt') as f:
		foodList = f.read().split('\n')

	pool = multiprocessing.Pool(threads)
	pool.map(saveSummary, foodList)

@task
def generateFoodListIndexPage():
	# Get list of foods
	foodList = []
	with open('./foodList.txt') as f:
		foodList = f.read().split('\n')

	# Figure out which food has the most info (by linecount)
	def findFileLineCount(file):
		try:
			with open(file) as f:
				lines = f.read().split('<p>')
				return len(lines)
		except Exception as e:
			return 0

	fileLengths = [findFileLineCount("./dist/summaries/{}.html".format(food)) for food in foodList ]

	sortedFoods = [ x[0] for x in sorted(zip(foodList, fileLengths), key=lambda x:x[1], reverse=True) ]

	print(sortedFoods)

	# Start making the markdown document
	markdownSource = """
# List of summaries by food\n\n"""

	for food in sortedFoods:
		markdownSource = markdownSource + "* [{}](./summaries/{}.html)\n".format(food.capitalize(), food)

	# Render the markdown
	html = mistune.markdown(markdownSource)

	with open('./dist/index.html', 'w') as f:
		f.write(html)

# if __name__ == '__main__':
	# generateFoodListIndexPage()
