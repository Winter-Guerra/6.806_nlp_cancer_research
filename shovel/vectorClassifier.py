# This file runs the word vector classifier

from shovel import task

import glob
import random
import os
from bs4 import BeautifulSoup
import re
import requests
# Import C yaml bindings
import yaml
try:
	from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
	from yaml import Loader, Dumper

# import gensim
from gensim import corpora, similarities, models

@task
def analyzeCorpus(loadSavedData = False):

	corpusFilename = './training_data/corpus.txt'
	modelFilename = './training_data/corpus.model'

	model = None
	if not loadSavedData:

		print("Training")

		# Import the sentence corpus document
		corpus = []
		with open('./training_data/corpus.txt') as f:
			sentences = f.read().split('\n')
			# Tokenize the sentences
			for sentence in sentences:
				corpus.append(sentence.split(' '))

		# Make document vector model using the corpus
		documents = models.doc2vec.TaggedLineDocument(corpusFilename)

		model = models.Doc2Vec(documents, size=200, window=8, min_count=5, workers=4)
		# model = models.Word2Vec(corpus, size=100, window=5, min_count=5, workers=4)

		# Trim unneeded memory
		# model.init_sims(replace=True)

		# Save the model
		model.save(modelFilename)

	else:
		model = models.Doc2Vec.load(modelFilename)

	# Check that word associations work
	print(model.most_similar(positive=['cancer']))

	print(model.most_similar(positive=['cure']))


	# Check that document associations work
	print(model.docvecs.most_similar(1))

def makeDocumentVectors():

	# Import word vector model
	modelFilename = './training_data/corpus.model'
	model = models.Word2Vec.load(modelFilename)
	# Trim unneeded memory
	model.init_sims(replace=True)

	# Make a list of documents
	sources = ['./training_data/100_datapoints/+1/*.md', './training_data/100_datapoints/-1/*.md']
	documents = []
	# documents.extend(glob.glob(source)) for source in sources
	#
	# for doc in documents:
	# 	# Make a vector using Word2Vec




	return (X)

def trainClassifier(documentVectors):
	''' This uses document vectors to train a scikit classifier. '''
