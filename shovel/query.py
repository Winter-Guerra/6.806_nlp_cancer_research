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
# from bs4 import BeautifulSoup
# import re

from pws import Google
from urllib.parse import urlparse

def getWebpageFromResults(response, idx):
	url = response['results'][int(idx)]['link'].split('&')[0]
	webpageContent = "<!-- URL:" + url + '-->' + requests.get(url).text
	return webpageContent


@task
def run(query, numberResults, showAbstract=False, save=False):

	response = Google.search(query, numberResults)

	for idx, result in enumerate(response['results']):
		if not save:
			print("Page title:", result['link_text'])
			print("Snippet:", result['link_info'])
			print('Website:', urlparse(result['link']).hostname)
			print('Reference:', idx)
			print("Related Queries:", result.get('related_queries',''))

		if showAbstract:
			webpageContent = getWebpageFromResults(response, idx)
			# Now, find the abstract in the content
			from prep import getDocumentFeatures, getParagraphsWithTag
			document = getDocumentFeatures(webpageContent)

			# Save the document
			result['text'] = document

			# Print the abstract
			if not save:
				print(getParagraphsWithTag(document, 'abstract'))
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


	# Show the text.
	print(webpageContent)

	return webpageContent
