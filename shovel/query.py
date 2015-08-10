# This file is a task runner for running knowledge queries against google.
# Import C yaml bindings
import yaml
try:
	from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
	from yaml import Loader, Dumper
import json
# from shovel import task
# import scraper
import sys
import os
# from bs4 import BeautifulSoup
# import re

from .google import Google
from urllib.parse import urlparse

from . import process
from . import scraper
# from shovel import scraper

import multiprocessing
import mistune

# For templating
from pybars import Compiler
compiler = Compiler()
# Get templates
templates = {}
with open('./templates/index.handlebars') as f:
	templates['index'] = f.read()
with open('./templates/food_entry.handlebars') as f:
	templates['food_entry'] = f.read()


# Compile the templates
templater = {key: compiler.compile(template) for key,template in templates.items()}

def getURLFromResults(response, idx):
	return response['results'][int(idx)]['link'].split('&')[0]

def getWebpageFromResults(response, idx):
	url = getURLFromResults(response, idx)
	webpageContent = "<!-- URL:" + url + '-->' + scraper.get(url).text
	return webpageContent


# @task
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
			webpageContent = process.getFullArticle(URL)
			document = process.Document(webpageContent)

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

# @task
def view(query, idx):
	''' This function can be used to grab HTML webpages using the search function. '''

	response = Google.search(query, int(idx)+1)

	webpageContent = getWebpageFromResults(response, idx)

# @task
def test():
	url = 'http://www.ncbi.nlm.nih.gov/pubmed/23349849'
	webpageContent = getFullArticle(url)

	document = getDocumentFeatures(webpageContent)

	# print(getParagraphsWithTags(document, ['abstract']))

# @task
def getDocuments(query, numberResults, includeReference=False, separator='\n'):

	output = []
	seenConclusions = set()

	response = Google.search(query, numberResults)

	for idx, result in enumerate(response['results']):


		URL = getURLFromResults(response, idx)
		# Now, find the abstract in the content
		fullURL = process.getFullArticleLink(URL)
		document = process.Document(fullURL)

		# Ignore documents without conclusions
		if document.conclusion is None:
			continue

		# Ignore documents that we have already seen before
		if document.conclusion is not None and document.conclusion not in seenConclusions:
			seenConclusions.add(document.conclusion)
			# Append this document to our list of output documents
			output.append(document)
			print(document.conclusion)

	return output

def dedupeDocuments(documents):
	from more_itertools import unique_everseen

	# Let's get the sentences from the data
	sentences = data.split('\n')

	dedupedSentences = list(unique_everseen(sentences))

	outputFileData = '\n\n'.join(dedupedSentences)

	return outputFileData

def saveSummary(food):
	numberResults = 40

	queryString = "breast cancer {} site:ncbi.nlm.nih.gov".format(food)
	documents = getDocuments(queryString, numberResults, includeReference=True, separator='\n\n')

	# Let's dedupe the documents based on conclusions
	# conclusionString = dedupeLines(conclusionString)

	context={
		'title': "{} and its effects on breast cancer".format(food.capitalize()),
		'command': "$shovel3 query.concatConclusions '{}' {} includeReference=True".format( queryString, numberResults),
		'documents': documents
	}

	# Render the page
	html = templater['food_entry'](context)

	# Output the rendered html
	with open("./dist/summaries/{}.html".format(food), 'w') as f:
		f.write(html)

	print("Done with {}".format(food))

	return html

# @task
def getFoodListQuery():
	threads = 6

	# Get list of foods
	foodList = []
	with open('./foodList.txt') as f:
		foodList = f.read().split('\n')

	pool = multiprocessing.Pool(threads)
	pool.map(saveSummary, foodList)

# @task
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

	#Start templating the index page
	context={
		'title': "List of summaries by food",
		'foods': sortedFoods
	}

	print(context)

	# Render the webpage
	html = templater['index'](context)
	# Save the webpage

	with open('./dist/index.html', 'w') as f:
		f.write(html)

if __name__ == '__main__':
	getFoodListQuery()
	# generateFoodListIndexPage()
