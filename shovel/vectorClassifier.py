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

@task
def analyzeCorpus(loadSavedData = True):

	modelFilename = './training_data/corpus.model'

	# import gensim
	from gensim import corpora, similarities, models

	model = None
	if not loadSavedData:

		# Import the sentence corpus document
		corpus = []
		with open('./training_data/corpus.txt') as f:
			sentences = f.read().split('\n')
			# Tokenize the sentences
			for sentence in sentences:
				corpus.append(sentence.split(' '))

		model = models.Word2Vec(corpus, size=100, window=5, min_count=5, workers=4)

		# Save the model
		model.save(modelFilename)

	else:
		model = models.Word2Vec.load(modelFilename)


	print(model.most_similar(positive=['cancer']))

	print(model.most_similar(positive=['cure']))
