# Winter@csail.mit.edu, June 2015.
from shovel import task

# Import C yaml bindings
import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

import sklearn
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
import scipy
import numpy
import os
import glob
import matplotlib.pyplot as plt

class Document():
	def __init__(self, relationMatrix, indexOffset, corpus):
		# This will create a document.
		self.relationMatrix = relationMatrix.flatten()
		self.indexOffset = indexOffset
		self.corpus = corpus

	def getOriginalSentence(self, i):
		return self.corpus[i+self.indexOffset]['originalSentence']

	def getWeighting(self, i):
		return repr(self.relationMatrix[i])

	def getKImportantSentences(self, k):
		# Minimize k based on size of matrix
		matrix = self.relationMatrix
		k = min(len(matrix), k)

		# This will make an array of k indices. Unsorted, but will be the largest K.
		ind = numpy.argpartition(matrix, -k)[-k:]

		# Now, sort the list and return the indices
		indexofindex = numpy.argsort(matrix[ind])
		# print( indexofindex)
		result = ind[indexofindex]
		# print(result)
		return result

class Analyzer():
	def __init__(self):

		# Init files
		print("Loading corpus file")

		with open("./sources/stemmedCorpus.yaml") as f: 
			self.corpus = yaml.load(f, Loader=Loader)

		print("Loading hash dictionary")
		with open("./sources/dedupedPathIndexedHashTable.yaml") as f: 
			self.pathIndexedHashTable = yaml.load(f, Loader=Loader)

		print("Extracting sentences")
		self.sentences = [ str(element['sentence']) for element in self.corpus]
		self.pathHashes = [ str(element['pathHash']) for element in self.corpus]
		self.tags = [ str(element['tags']) for element in self.corpus]
		self.originalSentences = [ str(element['originalSentence']) for element in self.corpus]


	def getTfidf(self):

		print("Finding bigrams")
		# Convert sentence to bigram

		n = len(self.sentences)
		# Let us discount words that are not present in 10% of articles
		mindf = int(0.1*n)
		# Let us discount words that appear in almost all articles
		maxdf = int(0.9*n)

		self.bigram_vectorizer = CountVectorizer(ngram_range=(1, 2), binary=True, analyzer=str.split)

		print("Finding count vector")
		# Get our count vector of bigram occurances
		X = self.bigram_vectorizer.fit_transform(self.sentences)

		# print(X.shape)

		# Now, let us make tf-idf vectors from this.

		self.idftransformer = TfidfTransformer()

		print("Finding tf-idf")
		self.tfidf = self.idftransformer.fit_transform(X)


	# This should use a pathhash to look up what tag a hash belongs to:
	def belongsToTag(self, hsh, tag):
		correctTags = self.pathIndexedHashTable.get(hsh, {'tags':[]})['tags']
		return (tag in correctTags)

	# This function is useful for matrix ops
	def indexBelongsToTag(self, index, tag):
		# get the hash

		# print(index)
		# print(len(pathHashes))
		hsh = self.pathHashes[index]
		return self.belongsToTag(hsh, tag)


# This function should load all summaries by tag
	def analyzeSummaries(self):

		print("Reading summaries")
		# Find the filenames of the summaries
		files = glob.glob("./sources/tokenizedStemmedSummaries/*.yaml")
		# print(files)

		totalAccuracy = 0
		totalLinkedSentences = 0
		totalSentences = 0
		totalDocsWithSummaries = {}

		numSummaries = len(files)

		outputRelationMatrix = None

		for f in files:

			# Load the summary file
			fileData = []
			with open(f) as _f: 
				fileData = yaml.load(_f, Loader=Loader)


			# Get the sentences and make sure that it is a string
			sentenceList = [element['sentence'] for element in fileData]

			# Get the tag
			tag = fileData[0]['tags']

			# Find the dimensions of the arrays we will be using
			s = len(sentenceList)
			(n,d) = self.tfidf.shape

			# print(sentenceList) #works!

			# Now, turn each sentence into tfidf vector
			countMatrix = self.bigram_vectorizer.transform(sentenceList)
			summaryTfidf = self.idftransformer.transform(countMatrix)

			# print(summaryTfidf.shape)

			# Now, dot product the feature vectors to get a matrix that is (sxn). I.E. connecting every summary sentence with every other sentence.

			# print("Multiplication: ", summaryTfidf.shape, tfidf.transpose().shape)
			# This is the cosine similarity step
			relationMatrix = summaryTfidf.dot( self.tfidf.transpose())

			# Normalize the relation matrix such that it becomes a probability distribution
			relationMatrix = scipy.sparse.csr_matrix( relationMatrix/relationMatrix.sum(axis=1) )

			# print(relationMatrix.shape)

			# Now, reduce the matrix such that the index of the highest column for each row is output into a (sx1) matrix.

			resultVector = numpy.argmax(relationMatrix.toarray(), axis=1) # sx1
			# print(resultVector)

			# Now, figure out if each element is correct in classification or not.
			classify = numpy.vectorize(lambda x: tag in self.tags[x] )
			binaryClassification = classify(resultVector).reshape(s,1)

			# Now, figure out what the error is
			accuracy = numpy.sum(binaryClassification, axis=0)/s

			# Now, update the total accuracy
			totalAccuracy += accuracy

			# We should check how many linked sentences we have from the summaries.
			totalLinkedSentences += numpy.sum(binaryClassification, axis=0)
			totalSentences += s

			# We should keep track of how many documents have at least 1 sentence strongly associated with them.
			def addDocument(x):
				# print(x)
				if tag in self.tags[x]: 
					totalDocsWithSummaries[x] = 1 


			logDocuments = numpy.vectorize(addDocument)
			logDocuments(resultVector)

			# print("Acc", accuracy, "Linked sentences", totalLinkedSentences, "totalSentences",totalSentences, "docs with summaries", len(totalDocsWithSummaries))

			# Update the overall relation matrix
			if outputRelationMatrix is not None:
				outputRelationMatrix = scipy.sparse.vstack([outputRelationMatrix, relationMatrix])
			else:
				outputRelationMatrix = relationMatrix

		# Calculate the total accuracy
		print("Total accuracy", totalLinkedSentences/totalSentences)

		self.relationMatrix = outputRelationMatrix


# This will take a (s,n) document and output a (1,w) document where w=number of documents in our corpus.
	def splitRelationMatrixByDocument(self, debug=False):
		'''
		>>> x = [1,1,1,3,4,5,5]
		>>> Analyzer().splitRelationMatrixByDocument(x)
		Making list of relation matrices for each document
		[(3, 1), (4, 3), (5, 4), (7, 5)]
		'''

		print("Making list of relation matrices for each document")
		
		if debug:
			self.pathHashes = debug

		# print(pathHashes)

		transitions = []
		for i in range(1, len(self.pathHashes)):
			if self.pathHashes[i-1] != self.pathHashes[i]:
				transitions.append( (i, self.pathHashes[i-1]) )

		transitions.append( (len(self.pathHashes), self.pathHashes[-1]) )

		if debug:
			print(transitions)
			return

		# Now, we must squash the matrix into (1,n)
		relationMatrix = self.relationMatrix.sum(axis=0) # This will be in dense format

		outputMatrixDict = {}

		leftBound = 0
		for lastIndexOfDocument, hsh in transitions:
			
			slicedMatrix = relationMatrix[0,leftBound:lastIndexOfDocument]
			# Normalize the new matrix
			subMatrix = numpy.array(slicedMatrix/slicedMatrix.sum())

			# Make the document
			doc = Document(subMatrix, leftBound, self.corpus)

			outputMatrixDict[hsh] = doc


			leftBound = lastIndexOfDocument

		# Now, output the new list of matrices
		self.documentDict = outputMatrixDict
		return 


	def prettyPrintRelationMatrixList(self):
		k = 5

		print("Printing summary of results")

		# Let us go through each document and output its top results.
		for hsh, doc in self.pathIndexedHashTable.items():
			print("--------------------------------------------")
			print("Path Hash:", hsh)
			print("File:", doc['filePath'])
			print("Bucket:", doc['tags'])


			# Get the relation matrix
			# index = indexLookupTable[hsh]
			document = self.documentDict[hsh]
			# print( relationMatrix.shape)

			# Now, get the top 5 index results of sentences for the matrix (1,n[x])
			indices = document.getKImportantSentences(k)

			# Package the sentence data that correspond to these indices
			# print(relationMatrix[0])
			sentenceList = [ {'sentence': document.getOriginalSentence(i), 'weighting': document.getWeighting(i)} for i in reversed(indices)]

			# Print the results to stdio
			outputData = yaml.dump(sentenceList, Dumper=Dumper)
			print(outputData)

@task
def runDoctest():
	import doctest
	doctest.testmod()


@task
def run(verbose=False):

	analyzer = Analyzer()

	# REAL PROG STARTS HERE
	analyzer.getTfidf()

	analyzer.analyzeSummaries()

	# Now, let's try to process the resulting sentence distribution for each document
	analyzer.splitRelationMatrixByDocument()

	if verbose:
		# Let's prettyprint the file data
		analyzer.prettyPrintRelationMatrixList()




