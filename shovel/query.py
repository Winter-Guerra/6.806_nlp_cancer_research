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
import time
import random
from bs4 import BeautifulSoup

from .google import Google
from urllib.parse import urlparse, parse_qs

from . import process
from . import scraper
# from shovel import scraper

import multiprocessing
import mistune

import redis
import pickle
# Start talking to our cache server (redis)
r = redis.StrictRedis(host='localhost', port=6379, db=0)

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

def findDeployDirectory():
	# Find our working directory
	sortedFolderList = sorted(os.listdir("./dist/"), reverse=True)
	deployDirectory = "./dist/" + sortedFolderList[0]
	return deployDirectory


# This class takes a subject and finds a bunch of documents relating to the subject.
class Query():

	def __init__(self, subj):

		self.numberResults = 40
		self.subj = subj
		self.queryString = self.getQueryString()
		self.documentURLs = self.getDocumentURLs()
		self.documents = self.getDocuments()

		self.saveDocumentURLsInCache()

	def getQueryString(self):
		return "breast cancer {} site:ncbi.nlm.nih.gov".format(self.subj)

	def queryCacheKey(self):
		return "query:{}:documentURLs".format(self.subj)

	def saveDocumentURLsInCache(self):
		# Save the document URLs in the cache so that they can be accessed faster later
		if not r.exists(self.queryCacheKey()) and len(self.documents) > 0:
			documentURLs = [document.URL for document in self.documents]
			r.sadd(self.queryCacheKey(), *documentURLs)


	def getDocumentURLs(self):
		# Check if we already have this in the cache
		documentURLs = list( r.smembers(self.queryCacheKey()) )
		documentURLs = [url.decode("utf-8") for url in documentURLs]

		if len(documentURLs) is 0:
			# Then, we need to find the document URLs from query
			response = Google.search(self.queryString, self.numberResults)

			for idx, result in enumerate(response['results']):
				documentURLs.append( self.getURLFromResults(response, idx) )

		return documentURLs

	def getDocuments(self):
		return [process.Document(URL) for URL in self.documentURLs]

	def getURLFromResults(self, response, idx):
		rawLink = response['results'][int(idx)]['link']

		# Default behavior
		url = rawLink.split('&')[0]

		# Check if the URL is coming in the form of the weird google redirect link
		urlComponents = urlparse(rawLink, 'http')

		if len(urlComponents.query) > 0:
			queryComponents = parse_qs(urlComponents.query)

			urlArray = queryComponents.get('url', [])
			if len(urlArray) > 0:
				url = urlArray[0]

		return url

def saveSummary(food):
	numberResults = 40

	deployDirectory = findDeployDirectory()

	query = Query(food)

	# Let's only show the documents that have conclusions
	documents = [document for document in query.documents if document.conclusion]

	# Let's sort the documents in order of conclusion length. I.E. shortest->longest
	documents = sorted(documents, key=lambda doc: len(doc.conclusion))


	context={
		'title': "{} and its effects on breast cancer".format(food.capitalize()),
		'documents': documents
	}

	# Do not save the file if it returned zero results since this could be due to an error.
	if len(query.documents) is 0:
		return None

	# Render the page
	html = templater['food_entry'](context)

	# Output the rendered html
	with open(deployDirectory+"/summaries/{}.html".format(food), 'w') as f:
		f.write(html)

	print("Done with {}".format(food))

	return html


def getFoodListQuery():
	threads = 4

	# Get list of foods
	foodList = []
	with open('./foodList.txt') as f:
		foodList = f.read().split('\n')

	deployDirectory = findDeployDirectory()

	# Comb out foods where we already have data on them
	dedupedFoodList = [food for food in foodList if not os.path.isfile( deployDirectory+"/summaries/{}.html".format(food) ) ]
	# dedupedFoodList = foodList

	print("Gathering data on the following foods")
	print(dedupedFoodList)


	pool = multiprocessing.Pool(threads)
	pool.map(saveSummary, dedupedFoodList)

# @task
def generateFoodListIndexPage():
	# Get list of foods
	foodList = []
	with open('./foodList.txt') as f:
		foodList = f.read().split('\n')


	# Count how many citations each food has by looking at the number of outermost list elements
	def findFileCitationCount(file):
		try:
			with open(file) as f:
				html = f.read()

				# Parse the html page
				soup = BeautifulSoup(html, 'html5lib')
				outerList = soup.ul
				numberCitations = len(outerList.contents)-1


				return numberCitations
		except Exception as e:
			print(e)
			return 0

	deployDirectory = findDeployDirectory()

	fileLengths = [findFileCitationCount(deployDirectory+"/summaries/{}.html".format(food)) for food in foodList ]

	sortedFoods = [ {'food': x[0], 'numberCitations': x[1]} for x in sorted(zip(foodList, fileLengths), key=lambda x:x[1], reverse=True)]

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

	with open(deployDirectory+'/index.html', 'w') as f:
		f.write(html)


if __name__ == '__main__':
	# getFoodListQuery()
	generateFoodListIndexPage()
