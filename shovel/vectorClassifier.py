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

######### CONFIGURATION
d = 200 # The dimensionality of the thing


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

		model = models.Doc2Vec(documents, size=d, window=8, min_count=5, workers=4)
		# model = models.Word2Vec(corpus, size=100, window=5, min_count=5, workers=4)

		# Trim unneeded memory
		# model.init_sims(replace=True)

		# Save the model
		model.save(modelFilename)

	else:
		model = models.Doc2Vec.load(modelFilename)

	# Check that word associations work
	print(model.most_similar(positive=['cancer']))
	print(model.most_similar(positive=['angiogenesis']))

	print(model.most_similar(positive=['green','tea']))

	# print(model.most_similar(positive=['cure']))


	# Check that document associations work
	print(model.docvecs.most_similar(1))

def makeDocumentVectors():



	# Import word vector model
	modelFilename = './training_data/corpus.model'
	model = models.Doc2Vec.load(modelFilename)
	# Trim unneeded memory
	# model.init_sims(replace=True)

	# Make a list of documents
	sources = [(1, './training_data/100_datapoints/+1/*.md'), (-1,'./training_data/100_datapoints/-1/*.md')]
	documents = []

	# Get the source files and lable them all
	for (label, source) in sources:
		_docs = [(label, file) for file in glob.glob(source)]
		documents.extend(_docs)

	# Find the size of the final vector
	size


	for doc in documents:

		# Read in the document as a list of tokenized words and punctuation
		document_word_list = []
		with open(doc) as f:
			document_word_list = f.read().split(' ')

		# Make a vector using Word2Vec
		documentVector = model.infer_vector(document_word_list)

		# Append this vector to a large vector




	return (X)

def trainClassifier(documentVectors):
	''' This uses document vectors to train a scikit classifier. '''
