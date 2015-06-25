from shovel import task

import os
import glob
# Import C yaml bindings
import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

import nltk.data
import sys

def trainPunktArticles():
	pass

def tokenizeDocuments(fileIterator):
	''' This will split a text document (supplied as yaml) into sentences. '''

	# Setup the tokenizer
	sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')

	outputFiles = {}

	# read in cleaned and deduped articles
	for f in fileIterator:

		# Get information about the file
		with open(f) as _f:
			fileData = yaml.load(_f, Loader=Loader)

		# pathHash = fileData['pathHash']


		# Tokenize
		# save the sentences in an array
		sentences = sent_detector.tokenize(fileData['text'].strip())

		# Output the new document
		fileData['text'] = sentences

		# Save the document
		outputFiles[f] = fileData

	# print(outputFiles)

	return outputFiles


@task
def tokenizeArticleSentences():
	'''This works on tokenizing sentences from our input article data.'''

	docs = tokenizeDocuments(glob.glob("./sources/cleaned_deduped/*.yaml"))

	# Save the documents
	for filePath, fileData in docs.items():

		# Output the newly tokenized file
		newFileName = filePath.replace('cleaned_deduped','tokenizedArticles')
		
		with open(newFileName, 'w') as _f:
			output = yaml.dump(fileData, Dumper=Dumper)
			_f.write(output)

@task
def tokenizeSummarySentences():
	'''This works on tokenizing sentences from our input summary data.'''
	
	docs = tokenizeDocuments(glob.glob("./sources/cleanedSummaries/*.yaml"))

	# Save the documents
	for filePath, fileData in docs.items():

		# Output the newly tokenized file
		newFileName = filePath.replace('cleanedSummaries','tokenizedSummaries')
		
		with open(newFileName, 'w') as _f:
			output = yaml.dump(fileData, Dumper=Dumper)
			_f.write(output)

