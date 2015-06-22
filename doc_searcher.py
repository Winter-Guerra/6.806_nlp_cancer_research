import yaml
import sklearn
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
import scipy
import numpy
import os
import glob
import matplotlib.pyplot as plt

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
	bigram_vectorizer = CountVectorizer(ngram_range=(1, 2), token_pattern=r'\b\w+\b', min_df=5, stop_words="english")

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

		# Now, 

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

		print("Acc", accuracy, "Linked sentences", totalLinkedSentences, "totalSentences",totalSentences, "docs with summaries", len(totalDocsWithSummaries))

		# Plot the probability distribution
		# plt.plot(numpy.linspace(0,n, n), relationMatrix[1,:])

	# Calculate the total accuracy
	print("Total accuracy", totalLinkedSentences/totalSentences)



if __name__ == '__main__':
	(tfidf, transformer, bigram_vectorizer, pathHashes) = getTfidf()
	analyzeSummaries(tfidf, transformer, bigram_vectorizer, pathHashes)



