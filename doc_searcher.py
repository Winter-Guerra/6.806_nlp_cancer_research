import yaml
import sklearn
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import normalize
import scipy
import numpy
from numpy import linalg as LA
import os
import glob
import math

# Init files
print("Loading corpus file")

corpus = []
with open("./sources/stemmedCorpus.yaml") as f: 
	corpus = yaml.load(f, Loader=yaml.CLoader)

print("Loading hash dictionary")
pathIndexedHashTable = {}
with open("./sources/dedupedPathIndexedHashTable.yaml") as f: 
	pathIndexedHashTable = yaml.load(f, Loader=yaml.CLoader)

def getTfidf():

	
	print("Extracting sentences")
	sentences = [ str(element['sentence']) for element in corpus]
	pathHashes = [ str(element['pathHash']) for element in corpus]
	# print(len(pathHashes))

	# print(sentences)

	print("Finding bigrams")
	# Convert sentence to bigram
	bigram_vectorizer = CountVectorizer(ngram_range=(1, 1), token_pattern=r'\b\w+\b', min_df=5, stop_words="english")

	print("Finding count vector")
	# Get our count vector of bigram occurances
	X = bigram_vectorizer.fit_transform(sentences)

	# print(X.shape)

	# Now, let us make tf-idf vectors from this.

	idftransformer = TfidfTransformer(norm='l2')

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

	numSummaries = len(files)

	for f in files:
		# Find tag
		filePath = os.path.join(rootDir, f)

		basename = os.path.basename(filePath)
		filename = os.path.splitext(basename)[0]
		tag = filename

		# Load the summary file to get the set of sentences that we need to check against our corpus
		_sentenceList = []
		with open(f) as _f: 
			_sentenceList = yaml.load(_f, Loader=yaml.CLoader)


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

		# This is the cosine similarity step
		relationMatix = summaryTfidf.dot( tfidf.T)

		# Normalize the matrix
		relationMatix = scipy.sparse.csr_matrix( relationMatix/relationMatix.sum(axis=1) )

		# Let's do a soft classification
		correctClassification = scipy.sparse.csr_matrix( [[1 if indexBelongsToTag(i, pathHashes, tag) else 0] for i in range(n)])

		# Now, let's calculate the new soft classification accuracy
		print(relationMatix.shape, correctClassification.shape)
		
		# Make the soft classifications
		# correctColumns = correctClassification.nonzero()[0]
		softClassification = relationMatix.dot(correctClassification)
		# print(softClassification)

		# Now, add all rows, then add all columns and divide by s to get the accuracy.
		accuracy = softClassification.sum()/s

		# Now, update the total accuracy
		totalAccuracy += accuracy

		# print(accuracy)

	# Calculate the total accuracy
	print("Total accuracy", totalAccuracy/numSummaries)



if __name__ == '__main__':
	(tfidf, transformer, bigram_vectorizer, pathHashes) = getTfidf()
	analyzeSummaries(tfidf, transformer, bigram_vectorizer, pathHashes)



