# This file runs the word vector classifier

# from shovel import task

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
import sklearn
from sklearn.feature_extraction.text import CountVectorizer
from sklearn import svm
import numpy as np

from . import process

import redis
import pickle
# Connect to the cache
r = redis.StrictRedis(host='localhost', port=6379, db=0)

# Import snowball stemmer
from nltk.stem.snowball import EnglishStemmer
stemmer = EnglishStemmer()

######### CONFIGURATION
d = 200 # The dimensionality of the vectors


# @task
def analyzeCorpus(loadSavedData = False):

	corpusFilename = './training_data/corpus.txt'
	modelFilename = './training_data/corpus.model'

	model = None
	if not loadSavedData:

		print("Training")

		# Make document vector model using the corpus
		# documents = models.doc2vec.TaggedLineDocument(corpusFilename)
		sentences = models.word2vec.LineSentence(corpusFilename)

		# model = models.Doc2Vec(documents, size=d, window=8, min_count=5, workers=4)
		model = models.Word2Vec(sentences, size=d, window=8, min_count=5, workers=4)

		# Save the model
		model.save(modelFilename)

	else:
		model = models.Word2Vec.load(modelFilename)


	# Check that word associations work
	wordList = ['caffeine', 'cancer', 'angiogenesis', 'green', 'tea' ]
	for word in wordList:
		stemmedWord = stemmer.stem(word)

		print(word, ': ', model.most_similar(positive=[stemmedWord]))


# def makeTrainingVectors():
#
# 	# Let's grab the serializedTrainingDataset from DB
# 	serializedTrainingDataset = json.loads(r.get('positiveTrainingDataset').decode("utf-8"))
#
# 	# Let's walk through the URLs, grab the sentences, and turn them into vectors
# 	for URL in serializedTrainingDataset.keys():
#
# 		document = process.Document(URL)
# 		sentenceObjList = serializedTrainingDataset[URL]
#
# 		for sentence in sentenceObjList:



# @task
def runSVMClassifier():

	# Instantiate the scikit unigram/bigram vectorizer
	# Note: This vectorizer expects the sentence to be tokenized
	bigram_vectorizer = CountVectorizer(ngram_range=(1, 2), binary=True, analyzer=str.split)

	############
	# Train the bigram vectorizer
	############

	sentences = []
	with open('./training_data/corpus.txt') as f:
		sentences = f.read().split('\n')

	bigram_vectorizer.fit(sentences)

	###########
	# Train SVM
	###########

	# Load the corpus. Each line in the corpus is a new snippet.
	sentences = []
	with open('./training_data/trainingSet.txt') as f:
		sentences = f.read().split('\n')

	# Make the feature vectors
	X = bigram_vectorizer.transform(sentences)

	# Import the training lables for the training set
	y = []
	with open('./training_data/trainingLabels.txt') as f:
		y = np.array([ int(lable) for lable in f.read().split('\n')])

	# Train the SVM
	classifier = svm.SVC()
	classifier.fit(X, y)

	######################
	# Find training error
	######################
	# Classify test set using SVM
	y_predicted = classifier.predict(X)

	# Calculate the classifier accuracy on the test set
	diffArray = (y_predicted == y)
	totalRight = sum(diffArray)
	accuracy = totalRight/float(len(totalRight))
	print("Training accuracy", accuracy)

	######################
	# Use the trained SVM to classify the test set
	######################

	# Get test set
	sentences = []
	with open('./training_data/testSet.txt') as f:
		sentences = f.read().split('\n')

	X = bigram_vectorizer.transform(sentences)

	# GEt test set lables
	y = []
	with open('./training_data/testLables.txt') as f:
		y = np.array([ int(lable) for lable in f.read().split('\n')])

	# Classify test set using SVM
	y_predicted = classifier.predict(X)

	# Calculate the classifier accuracy on the test set
	diffArray = (y_predicted == y)
	totalRight = sum(diffArray)
	accuracy = totalRight/float(len(totalRight))
	print("Test accuracy", accuracy)

if __name__ == '__main__':
	analyzeCorpus()
