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


@task
def tokenizeArticleSentences():
	'''This works on tokenizing sentences from our input article data.'''

	# Setup the tokenizer
	sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')

	# read in cleaned and deduped articles
	for f in glob.glob("./sources/cleaned_deduped/*.yaml"):

		# Get information about the file
		with open(f) as _f:
			fileData = yaml.load(_f, Loader=Loader)


		# Tokenize
		# save the sentences in an array
		sentences = sent_detector.tokenize(fileData['text'].strip())

		# Output the newly tokenized file
		newFileName = f.replace('cleaned_deduped','tokenized_deduped_articles')
		with open(newFileName, 'w') as _f:
			output = yaml.dump(sentences, Dumper=Dumper)
			_f.write(output)

@task
def tokenizeSummarySentences():
	'''This works on tokenizing sentences from our input summary data.'''
	pass

