# This file is a task runner for running knowledge queries against google.
import yaml
from shovel import task
import requests
from bs4 import BeautifulSoup
import re

from pws import Google
from urllib.parse import urlparse

@task
def run(query, numberResults):
	
	response = Google.search(query, numberResults)

	for idx, result in enumerate(response['results']):
		print("Page title:", result['link_text'])
		print("Snippet:", result['link_info'])
		print('Website:', urlparse(result['link']).hostname)
		print('Reference:', idx)
		print("Related Queries:", result.get('related_queries',''))
		print('---------------------------')

@task
def get(query, resultNumber):

	response = Google.search(query, int(resultNumber)+1)

	url = response['results'][int(resultNumber)]['link'].split('&')[0]

	print("<!--", url, '-->')

	# Download the page
	r = requests.get(url)

	# Run the text through bs4 to prettify it
	soup = BeautifulSoup(r.text, 'html5lib')

	print("Title:", soup.title.string)

	text = soup.find_all('p')
	for paragraph in text:
		if paragraph.string is not None:

			# Find the title of the paragraph
			paragraphTitle = ''
			for sibling in paragraph.find_previous_siblings(re.compile("^h")):
				# print(sibling)
				paragraphTitle = sibling.string


			if paragraphTitle is not '':
				print("Paragraph Title:", paragraphTitle)
				print(paragraph.string)
				print('')
	# print(soup.find_all('p'))


	# Print the text of the page onscreen
	# print(r.text)


