from shovel import task

import os
import glob
# Import C yaml bindings
import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

import nltk.data
import sys
import string

def trainPunktArticles():
	pass

def tokenizeDocuments(fileIterator):
	''' This will split a text document (supplied as yaml) into sentences. '''

	# Setup the tokenizer
	sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')

	outputFiles = {}

	# read in cleaned and deduped articles
	for f in fileIterator:

		# Get information about the file
		with open(f) as _f:
			fileData = yaml.load(_f, Loader=Loader)

		# Tokenize
		# save the sentences in an array
		sentences = sent_detector.tokenize(fileData['text'].strip())

		# Output the new document
		fileData['text'] = sentences

		# Save the document
		outputFiles[f] = fileData

	# print(outputFiles)

	return outputFiles

def stemDocuments(fileIterator):
	''' This will take a list of yaml documents and output a list of stemmed sentences with all relevant data. '''

	# Setup the stemmer
	from nltk.stem.snowball import EnglishStemmer
	from nltk import word_tokenize
	from nltk.corpus import stopwords
	stemmer = EnglishStemmer()
	stopWords = stopwords.words('english')

	outputList = []

	# read in articles
	for f in fileIterator:

		# Get information about the file
		with open(f) as _f:
			fileData = yaml.load(_f, Loader=Loader)

		sentences = fileData['text']

		for sentence in sentences:

			# Clean the punctuation out of the sentence
			cleanedSentence = ''.join([char if char not in string.punctuation else ' ' for char in sentence])

			# Tokenize words out of the sentence (excluding stopwords)
			tokenizedSentence = [word for word in word_tokenize(cleanedSentence) if word not in stopWords ]

			# Remove punctuation
			# tokenizedSentence = []

			# Stem the words using snowball
			stemmedTokenizedSentence = [stemmer.stem(word) for word in tokenizedSentence]

			# Save the tokenized stemmed sentence as a string separated by whitespace (scikit learn likes this format).
			outputSentence = " ".join(stemmedTokenizedSentence)

			# Now, make an entry in the output list
			listEntry = { key:value for key,value in fileData.items() if key != 'text' }
			listEntry['sentence'] = outputSentence
			listEntry['originalSentence'] = sentence

			outputList.append(listEntry)

	return outputList


@task
def tokenizeArticleSentences():
	'''This works on tokenizing sentences from our input article data.'''

	docs = tokenizeDocuments(glob.glob("./sources/cleaned_deduped/*.yaml"))

	# Save the documents
	for filePath, fileData in docs.items():

		# Output the newly tokenized file
		newFileName = filePath.replace('cleaned_deduped','tokenizedArticles')
		
		with open(newFileName, 'w') as _f:
			output = yaml.dump(fileData, Dumper=Dumper)
			_f.write(output)

@task
def tokenizeSummarySentences():
	'''This works on tokenizing sentences from our input summary data.'''
	
	docs = tokenizeDocuments(glob.glob("./sources/cleanedSummaries/*.yaml"))

	# Save the documents
	for filePath, fileData in docs.items():

		# Output the newly tokenized file
		newFileName = filePath.replace('cleanedSummaries','tokenizedSummaries')
		
		with open(newFileName, 'w') as _f:
			output = yaml.dump(fileData, Dumper=Dumper)
			_f.write(output)

@task
def aggregateAndStemCorpus():

	fileData = stemDocuments(glob.glob("./sources/tokenizedArticles/*.yaml"))

	# Save the tokenized corpus
	with open('./sources/stemmedCorpus.yaml', 'w') as _f:
			output = yaml.dump(fileData, Dumper=Dumper)
			_f.write(output)


