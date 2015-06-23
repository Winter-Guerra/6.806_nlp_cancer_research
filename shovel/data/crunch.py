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
	def __init__(self, relationMatrix, indexOffset):
		# This will create a document.
		self.relationMatrix = relationMatrix.flatten()
		self.indexOffset = indexOffset

	def getOriginalSentence(self, i):
		return corpus[i+self.indexOffset]['originalSentence']

	def getWeighting(self, i):
		return repr(self.relationMatrix[i])

	def getKImportantSentences(self, k):
		# Minimize k based on size of matrix
		matrix = self.relationMatrix
		k = min(len(matrix), k)

		ind = numpy.argpartition(matrix, -k)[-k:] # This will make an array of k indices. Unsorted, but will be the largest K.

		# Now, sort the list and return the indices
		indexofindex = numpy.argsort(matrix[ind])
		# print( indexofindex)
		result = ind[indexofindex]
		# print(result)
		return result


def getTfidf():

	# print(len(pathHashes))

	# print(sentences)

	print("Finding bigrams")
	# Convert sentence to bigram
	bigram_vectorizer = CountVectorizer(ngram_range=(1, 1), token_pattern=r'\b\w+\b', min_df=10, stop_words="english")

	print("Finding count vector")
	# Get our count vector of bigram occurances
	X = bigram_vectorizer.fit_transform(sentences)

	# print(X.shape)

	# Now, let us make tf-idf vectors from this.

	idftransformer = TfidfTransformer()

	print("Finding tf-idf")
	tfidf = idftransformer.fit_transform(X)

	# print(tfidf.shape)

	return (tfidf, idftransformer, bigram_vectorizer, pathHashes)

# This should use a pathhash to look up what tag a hash belongs to:
def belongsToTag(hsh, tag):
	correctTags = pathIndexedHashTable.get(hsh, {'tags':[]})['tags']
	return (tag in correctTags)

# This function is useful for matrix ops
def indexBelongsToTag(index, pathHashes, tag):
	# get the hash

	# print(index)
	# print(len(pathHashes))
	hsh = pathHashes[index]
	return belongsToTag(hsh, tag)


# This function should load all summaries by tag
def analyzeSummaries(tfidf, idftransformer, bigram_vectorizer, pathHashes):

	print("Reading summaries")

	rootDir = "/Users/winterg/Dropbox (MIT)/Development_Workspace/UROP/sources"
	os.chdir(rootDir)

	# Find the filenames of the summaries
	files = glob.glob("tokenizedStemmedSummaries/*.yaml")
	# print(files)

	totalAccuracy = 0
	totalLinkedSentences = 0
	totalSentences = 0
	totalDocsWithSummaries = {}

	numSummaries = len(files)

	outputRelationMatrix = None

	for f in files:
		# Find tag
		filePath = os.path.join(rootDir, f)

		basename = os.path.basename(filePath)
		filename = os.path.splitext(basename)[0]
		tag = filename

		# Load the summary file to get the set of sentences that we need to check against our corpus
		_sentenceList = []
		with open(f) as _f: 
			_sentenceList = yaml.load(_f, Loader=Loader)


		# Force all of array to be string elements
		_sentenceList = [map(str, sentence) for sentence in _sentenceList]

		# Turn the tokenized sentence we loaded into a string
		sentenceList = [" ".join(sentence) for sentence in _sentenceList]

		# Find the dimensions of the arrays we will be using
		s = len(sentenceList)
		(n,d) = tfidf.shape

		# print(sentenceList) #works!

		# Now, turn each sentence into tfidf vector
		countMatrix = bigram_vectorizer.transform(sentenceList)
		summaryTfidf = idftransformer.transform(countMatrix)

		# print(summaryTfidf.shape)

		# Now, dot product the feature vectors to get a matrix that is (sxn). I.E. connecting every summary sentence with every other sentence.

		# print("Multiplication: ", summaryTfidf.shape, tfidf.transpose().shape)
		# This is the cosine similarity step
		relationMatrix = summaryTfidf.dot( tfidf.transpose())

		# Normalize the relation matrix such that it becomes a probability distribution
		relationMatrix = scipy.sparse.csr_matrix( relationMatrix/relationMatrix.sum(axis=1) )

		# print(relationMatrix.shape)

		# Now, reduce the matrix such that the index of the highest column for each row is output into a (sx1) matrix.

		resultVector = numpy.argmax(relationMatrix.toarray(), axis=1) # sx1
		# print(resultVector)

		# Now, figure out if each element is correct in classification or not.
		classify = numpy.vectorize(lambda x: indexBelongsToTag(x, pathHashes, tag) )
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
			if indexBelongsToTag(x, pathHashes, tag): 
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

	os.chdir('../')
	return outputRelationMatrix


# This will take a (s,n) document and output a (1,w) document where w=number of documents in our corpus.
def splitRelationMatrixByDocument(relationMatrix, pathHashes, debug=False):
	'''
	>>> x = [1,1,1,3,4,5,5]
	>>> splitRelationMatrixByDocument(x,x, True)
	Making list of relation matrices for each document
	[(3, 1), (4, 3), (5, 4), (7, 5)]
	'''

	print("Making list of relation matrices for each document")
	
	if debug:
		pathHashes = relationMatrix

	# print(pathHashes)

	transitions = []
	for i in range(1, len(pathHashes)):
		if pathHashes[i-1] != pathHashes[i]:
			transitions.append( (i, pathHashes[i-1]) )

	transitions.append( (len(pathHashes), pathHashes[-1]) )

	if debug:
		return transitions

	# Now, we must squash the matrix into (1,n)
	relationMatrix = relationMatrix.sum(axis=0) # This will be in dense format

	outputMatrixDict = {}

	leftBound = 0
	for lastIndexOfDocument, hsh in transitions:
		
		slicedMatrix = relationMatrix[0,leftBound:lastIndexOfDocument]
		# Normalize the new matrix
		subMatrix = numpy.array(slicedMatrix/slicedMatrix.sum())

		# Make the document
		doc = Document(subMatrix, leftBound)

		outputMatrixDict[hsh] = doc


		leftBound = lastIndexOfDocument

	# Now, output the new list of matrices
	return outputMatrixDict


def prettyPrintRelationMatrixList(documentDict):
	k = 5

	print("Printing summary of results")

	# Let us go through each document and output its top results.
	for hsh, doc in pathIndexedHashTable.items():
		print("--------------------------------------------")
		print("Path Hash:", hsh)
		print("File:", doc['filePath'])
		print("Bucket:", doc['tags'])


		# Get the relation matrix
		# index = indexLookupTable[hsh]
		document = documentDict[hsh]
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
def crunchData():

	# Init files
	print("Loading corpus file")

	corpus = []
	with open("./sources/stemmedCorpus.yaml") as f: 
		corpus = yaml.load(f, Loader=Loader)

	print("Loading hash dictionary")
	pathIndexedHashTable = {}
	with open("./sources/dedupedPathIndexedHashTable.yaml") as f: 
		pathIndexedHashTable = yaml.load(f, Loader=Loader)

	print("Extracting sentences")
	sentences = [ str(element['sentence']) for element in corpus]
	pathHashes = [ str(element['pathHash']) for element in corpus]

	# REAL PROG STARTS HERE

	(tfidf, transformer, bigram_vectorizer, pathHashes) = getTfidf()
	relationMatrix = analyzeSummaries(tfidf, transformer, bigram_vectorizer, pathHashes)

	# Now, let's try to process the resulting sentence distribution for each document
	outputMatrixList = splitRelationMatrixByDocument(relationMatrix, pathHashes=pathHashes)

	# Let's prettyprint the file data
	prettyPrintRelationMatrixList(outputMatrixList)




