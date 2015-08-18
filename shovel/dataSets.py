# File for dealing with training and test sets

from . import query
from . import process

import multiprocessing
import json
import sys
import string

# For templating
from pybars import Compiler
compiler = Compiler()
# Get templates
templates = {}
with open('./templates/trainingData.handlebars') as f:
	templates['trainingData'] = f.read()
# Compile the templates
templater = {key: compiler.compile(template) for key,template in templates.items()}

# import gensim
from gensim import corpora, similarities, models
import sklearn
from sklearn.feature_extraction.text import CountVectorizer
from sklearn import svm
import numpy as np

import redis
import pickle
# Connect to the cache
r = redis.StrictRedis(host='localhost', port=6379, db=0)

# Import snowball stemmer
from nltk.stem.snowball import EnglishStemmer
stemmer = EnglishStemmer()

# Import stopwords list
from nltk.corpus import stopwords

# Startup word2vec
modelFilename = './training_data/corpus.model'
model = models.Word2Vec.load(modelFilename)

def pruneSentenceVocab(sentence, model):
	return ' '.join([word for word in sentence.split() if word in model])

def locateStringObjInDoc(searchString, doc):

	for paragraphObj in doc.rawParagraphList:
		paragraph = paragraphObj['paragraph']
		if paragraph != None:
			index = paragraph.find(searchString)

			if index != -1:

				# Then, create a results object
				resultsObj = {key:val for key, val in paragraphObj.items()}
				del resultsObj['paragraph']
				resultsObj['sentence'] = searchString

				yield resultsObj

class TrainingSet():

	def __init__(self, trainingSetPath):
		self.trainingSetDir = './training_data'
		self.trainingSetPath = self.trainingSetDir + trainingSetPath

	def createTrainingSet(self):
		threads = 4

		# Let's create the positive training set (I.E. set of important sentences).

		# Get list of foods
		foodList = []
		with open('./foodList.txt') as f:
			foodList = f.read().split('\n')

		# Grab our query results
		# queryObjects = [query.Query(foodList[0]), query.Query(foodList[1])]
		# queryObjects = [query.Query(subject) for subject in foodList]

		pool = multiprocessing.Pool(threads)
		queryObjects = pool.map(query.Query, foodList)

		context = {
			'query': queryObjects
		}

		# Print out our unannotated dataset to a file for human annotation
		html = templater['trainingData'](context)
		# Output the rendered html
		with open(self.trainingSetPath, 'w') as f:
			f.write(html)

	def readTrainingSet(self):

		# Let's read the training set
		trainingSet = []
		with open(self.trainingSetPath) as f:
			trainingSet = f.read().split('\n')

		# Iterate through all lines of the training set
		# Remove all empty lines
		trainingSet = [line for line in trainingSet if len(line) >0]
		# Remove all commented lines
		trainingSet = [line for line in trainingSet if line[0] is not '#']


		dictionaryOfArticleURLs = {}
		currentQuery = None
		currentURL = None

		# Let's populate our dictionary of URLs and their associated significant sentences and related query subjects
		for dataElement in trainingSet:
			# Let's create a data object from the line
			try:
				dataObj = json.loads(dataElement)
			except Exception as e:
				print("ERR parsing {}".format(dataElement))

				raise e
			# Let's check to see if this is the start of a new query
			if dataObj.get('QuerySubj', None) != None:
				currentQuery = dataObj['QuerySubj']

			# Let's check if this is the start of a new URL document
			elif dataObj.get('URL', None) != None:
				currentURL = dataObj['URL']

			# Then this must be a sentence object
			else:

				sentence = dataObj['s']
				correlation = dataObj['correlation']


				# Make the sentence vector
				sentenceVector = (sentence, currentQuery, correlation)

				# NOTE: This still allows "Article not relevant." sentences to go through for negative training.
				# NOTE: This also still allows s: null blank sentences to go through to show that the document has not been trained on.

				# We should log this sentence vector
				sentenceList = dictionaryOfArticleURLs.get(currentURL, [])
				sentenceList.append(sentenceVector)
				dictionaryOfArticleURLs[currentURL] = sentenceList

				# Db Object schema:
				# {
				#	URL: [(sentence, currentQuery, correlation)]
				# }

		# Now, we are done logging all of our sentences into our training database.
		# Let's save this object into our database

		serializedTrainingDataset = json.dumps(dictionaryOfArticleURLs)
		r.set('positiveTrainingDataset', serializedTrainingDataset)

		print(serializedTrainingDataset)

	def generateSentenceTokenizedCorpus(self):
		threads = 4

		# Let's grab the serializedTrainingDataset from DB
		serializedTrainingDataset = json.loads(r.get('positiveTrainingDataset').decode("utf-8"))

		# Get list of URLs
		urlList = serializedTrainingDataset.keys()

		# process URLs into documents using a generator
		pool = multiprocessing.Pool(threads)
		# documentIteratorList = pool.imap(process.Document, urlList)
		documentIteratorList = map(process.Document, urlList)

		# Let's open up the output file
		with open(self.trainingSetDir + '/corpus.txt', 'w') as f:

			# Let's output the tokenized sentence list to the file

			for doc in documentIteratorList:
				# print(doc.stemmedSentences)
				stemmedSentenceObjects = doc.stemmedSentences
				for sentenceObj in stemmedSentenceObjects:
					sentence = sentenceObj['sentence']
				#
					f.write(sentence + '\n')

		# Done!

	def generatePositiveDictionaryVector(self):
		output = []

		# Let's grab the serializedTrainingDataset from DB
		serializedTrainingDataset = json.loads(r.get('positiveTrainingDataset').decode("utf-8"))

		for URL, sentenceObjList in serializedTrainingDataset.items():

			# This is the training object.
			for targetSentence, currentQuery, correlation in sentenceObjList:

				# Check if we should use this as a positive training vector
				if targetSentence != None and targetSentence != '' and targetSentence != "Article not relevant.":

					# Process the document
					doc = process.Document(URL)
					stemmedSentenceObjects = list(doc.stemmedSentences)

					# Look for the FIRST location of the string in the document (should eventually be all)
					results = list(locateStringObjInDoc(targetSentence, doc))

					if len(results) == 0:
						print("ERR: Did not find result for string {}.".format(targetSentence))
					else:
						# Add the results vector to our output vector
						output.extend(results)
						# print(output)

					# Log the feature vector of the located string.

		# Log the created list of positive feature vectors to the DB
		r.set('positiveDictionaryFeatureset', json.dumps(output))
		print(output)




if __name__ == '__main__':
	trainingSet = TrainingSet("/positiveDataset.txt")
	# trainingSet.createTrainingSet()
	# trainingSet.readTrainingSet()
	# trainingSet.generateSentenceTokenizedCorpus()
	trainingSet.generatePositiveDictionaryVector()