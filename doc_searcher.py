import yaml
import sklearn
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
import numpy
import os
import glob

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
	bigram_vectorizer = CountVectorizer(ngram_range=(1, 2), token_pattern=r'\b\w+\b', min_df=1)

	print("Finding count vector")
	# Get our count vector of bigram occurances
	X = bigram_vectorizer.fit_transform(sentences)

	# print(X.shape)

	# Now, let us make tf-idf vectors from this.

	transformer = TfidfTransformer()

	print("Finding tf-idf")
	tfidf = transformer.fit_transform(X)

	# print(tfidf.shape)

	return (tfidf, transformer, bigram_vectorizer, pathHashes)

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
def analyzeSummaries(tfidf, transformer, bigram_vectorizer, pathHashes):

	print("Reading summaries")

	rootDir = "/Users/winterg/Dropbox (MIT)/Development_Workspace/UROP/sources"
	os.chdir(rootDir)

	# Find the filenames of the summaries
	files = glob.glob("tokenizedStemmedSummaries/*.yaml")
	# print(files)

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

		# print(sentenceList) #works!

		# Now, turn each sentence into tfidf vector
		countMatrix = bigram_vectorizer.transform(sentenceList)
		summaryTfidf = transformer.transform(countMatrix)

		# print(summaryTfidf.shape)

		# Now, dot product the feature vectors to get a matrix that is (sxn). I.E. connecting every summary sentence with every other sentence.

		# print("Multiplication: ", summaryTfidf.shape, tfidf.transpose().shape)
		relationMatix = summaryTfidf.dot( tfidf.transpose())

		# print(relationMatix.shape)

		# Now, reduce the matrix such that the index of the highest column for each row is output into a (sx1) matrix.

		resultVector = numpy.argmax(relationMatix.toarray(), axis=1) # sx1
		# print(resultVector)

		# Now, figure out if each element is correct in classification or not.
		classify = numpy.vectorize(lambda x: indexBelongsToTag(x, pathHashes, tag))
		binaryClassification = classify(resultVector)

		# Now, figure out what the error is
		accuracy = numpy.sum(binaryClassification, axis=1)/binaryClassification.shape[0]
		print(accuracy)



if __name__ == '__main__':
	(tfidf, transformer, bigram_vectorizer, pathHashes) = getTfidf()
	analyzeSummaries(tfidf, transformer, bigram_vectorizer, pathHashes)



