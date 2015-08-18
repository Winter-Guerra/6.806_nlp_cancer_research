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

		# Startup word2vec
		modelFilename = './training_data/corpus.model'
		model = models.Word2Vec.load(modelFilename)

		# Let's grab the serializedTrainingDataset from DB
		serializedTrainingDataset = json.loads(r.get('positiveTrainingDataset').decode("utf-8"))

		for URL, sentenceObjList in serializedTrainingDataset:

			doc = process.Document(URL)
			stemmedSentenceObjects = list(doc.stemmedSentences)

			for sentence, currentQuery, correlation in sentenceObjList:

				# Stem the sentence that we have
				# Remove all forms of parenthesis, numbering, punctuation
				cleanedSentence = sentence.translate( {ord(i):None for i in string.punctuation+'\t0123456789()[]{}' } )
				# Hypens should be turned into spaces
				cleanedSentence = cleanedSentence.translate( {ord(i):' ' for i in '-' } )
				# Make the paragraph text lowercase
				cleanedSentence = cleanedSentence.lower()

				targetWords = [stemmer.stem(word) for word in cleanedSentence.split() if word not in stopwords.words('english')]

				# Now, we iterate through all sentences in the document and select the best match using
				sentenceMatchPercentage = [ model.n_similarity(targetWords, possibleMatch['sentence'].split()) for possibleMatch in stemmedSentenceObjects ] 	




				# find all sentences in the document that match this sentence.

				# Pick the closest match.



if __name__ == '__main__':
	trainingSet = TrainingSet("/positiveDataset.txt")
	# trainingSet.createTrainingSet()
	# trainingSet.readTrainingSet()
	trainingSet.generateSentenceTokenizedCorpus()
