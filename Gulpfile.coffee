# This is a gulpfile for the sources dir

gulp = require('gulp')
dedupe = require('./gulp-dedupe')
count = require('gulp-count')
flatten = require('gulp-flatten')
run = require('gulp-run') # For the stream tokenizer
rename = require("gulp-rename")
replace = require('gulp-replace')
tap = require('gulp-tap')
natural = require('natural')
yaml = require('js-yaml')
math = require('mathjs')
crypto = require('crypto')
fs = require('fs-extra')
path = require 'path'
clusterfck = require("clusterfck")

gulp.task 'countSources', () ->
	stream = gulp.src([ 'sources/raw/**/*.md' ])
	.pipe(flatten())
	.pipe(dedupe())
	.pipe(count('## data files copied'))
	.pipe(gulp.dest('./sources/deduped'))
	return stream

	# Let's tokenize our summary dataset by sentence
gulp.task 'tokenizeSummary', () ->
	
	stream = gulp.src([ 'sources/raw/*Summary/**/*.md' ])
	.pipe(dedupe())

	# Fix the naming scheme
	.pipe(rename( (path) ->
		path.basename = path.dirname
		path.dirname = './'
		path.extname = '.yaml'
		return path
	))
	.pipe(flatten())

	# For debugging
	.pipe(count('## summaries read'))

	# remove all paragraphs before ## xxx breast cancer-related
	.pipe( replace(/[\s\S]*^## .*cancer-related.*/mg, '') )

	# Remove all paragraphs after the following headings
	.pipe(replace(/^## [\s\S]*/mg, ''))

	# Remove all remaining headings
	.pipe(replace(/^#.*/mg, ''))

	# Do a sanity check that all files have at least 1 sentence in them
	.pipe(
		tap (file) ->
			if file.contents.toString().length < 100
				console.error "ERR: #{file.path} does not have enough characters in the tokenized summary"
		)
	
	# Tokenize the sentence
	.pipe(run('python3 sentence_tokenizer.py', {silent:true})) # This generates yaml files of each sentence of the summaries
	
	# Save the output
	.pipe(gulp.dest('./build/summaries')) # Save this to a temp directory so that we can check the output of the tokenizer

	return stream

# This will use tf-idf to match all the summary sentences with the best match in our corpus  
gulp.task 'generateTrainingClassifications', (cb) ->

	TfIdf = natural.TfIdf
	tfidf = new TfIdf()

	# First, let's make our corpus.
	stream = gulp.src([ 'sources/deduped/*.md' ])

	.pipe( 
		tap (file) ->
			# console.log file.path.toString()
			tfidf.addDocument(file.contents.toString(), file.path.toString())

	)

	# Our corpus has been filled. Let's start doing lookups
	.on 'end', () ->

		stream = gulp.src([ './build/summaries/*.yaml' ])

		.pipe(
			tap (file) ->
				# read YAML file
				sentences = yaml.safeLoad( file.contents.toString() )

				# file.contents = '' 

				# Iterate through every sentence in the yaml
				rankings = []
				output = 
					'sentences': sentences
					'documentRankings': {}

				for i in [0...tfidf.documents.length]
					documentRanking = ( tfidf.tfidf(sentence, i) for sentence in sentences )

					# Check that this document vector is not all zeros
					# continue if Math.max.apply(Math, documentRanking) is 0

					documentPath = tfidf.documents[i].__key
					output['documentRankings'][i] = documentRanking


				# Append the sentence to the yaml file in ./build/classifications
				file.contents = new Buffer yaml.safeDump(output)
				return file.contents
		)
		.pipe( gulp.dest('./build/trainingClassifications') )
		.on('end', cb)

	.on	'error', (err) ->
		console.error err


# Let's make a table of what the content of a file is and what bins the file belongs to.
gulp.task 'createHashTable', () ->

	hashTable = {}

	stream = gulp.src(['sources/raw/badFoods/**/*.md', 'sources/raw/recommendedFoods/**/*.md'])

	.pipe(
		tap (file) ->
			# Find the bin that the file should be in
			[unused..., bin, unused ] = file.path.split('/')
			# bin = file.base

			fileHash = crypto.createHash('md5').update(file.contents).digest("hex").toString()

			# Now, append the bin to the binary dictionary of the files
			if not hashTable[fileHash]?
				hashTable[fileHash] = [bin]
			else
				hashTable[fileHash].push(bin) if bin not in hashTable[fileHash]

			return 
		)
	.on	'end', () ->

		# Now, write out the hash table
		# console.log hashTable

		console.log Object.keys(hashTable).length

		# Save the hash table
		yamlData = yaml.safeDump(hashTable)
		fs.outputFileSync('./sources/hashTable.yaml', yamlData)

	return stream

gulp.task 'createFileIndexedHashTable', () ->

	hashTable = yaml.safeLoad(fs.readFileSync('./sources/hashTable.yaml'))
	i = 0
	indexedHashTable = {}


	stream = gulp.src([ 'sources/deduped/*.md' ])
	.pipe(
		tap (file) =>
			# Find the bin that the file should be in

			fileHash = crypto.createHash('md5').update(file.contents).digest("hex").toString()

			# Find the tags that go with this file
			tagData =
				hash: fileHash
				tags: hashTable[fileHash]

			indexedHashTable[i] = tagData
			i += 1
			return 
	)
	.on 'end', () ->

		# Save the hash table
		console.log indexedHashTable
		yamlData = yaml.safeDump(indexedHashTable)
		fs.outputFileSync('./sources/indexedHashTable.yaml', yamlData)



	return stream
	

# Collapses the feature vectors in each section yaml, 
gulp.task 'collapseBinData', () ->

	indexedHashTable = yaml.safeLoad(fs.readFileSync './sources/indexedHashTable.yaml' )
	hashTable = yaml.safeLoad(fs.readFileSync './sources/hashTable.yaml' )

	stream = gulp.src(['build/trainingClassifications/*.yaml'])

	.pipe(
		tap (file) ->
			# Read the feature vector from the yaml.
			data = yaml.safeLoad( file.contents.toString() )
			sentences = data['sentences']
			documentRankings = data['documentRankings']

			# Figure out what category we are looking at
			category = path.basename file.path, '.yaml'

			# each outer array signifies a document. Let's take the tf-idf sum of each document
			documentTFIDFValues = ( 0 for i in [0...Object.keys(documentRankings).length])
			# console.log documentTFIDFValues
			for docNum, docScore of documentRankings
				documentTFIDFValues[parseInt(docNum)] = math.sum(docScore) 
			# console.log documentTFIDFValues

			# Let's build our bucket by looking for the expected number of results.

			# Let's see how many documents we should have in the bucket
			shouldHave = math.sum( ( 1 for hash, categoryList of hashTable when category in categoryList) )

			
			bucket = ( {docScore:0, docNum:0} for i in [0...shouldHave])
			for docScore, i in documentTFIDFValues
				if docScore > bucket[0].docScore
					bucket.push({docScore, docNum:i})
					bucket.sort (a,b) ->
						if a.docScore > b.docScore
							return 1
						else if a.docScore < b.docScore
							return -1
						else 
							return 0
					bucket.shift()

			console.log bucket
			

			console.log "Category: #{category}, bucket length: #{bucket.length} docs in the bucket."

			

			# Let's compute how many of the documents in the bucket actually should be there.
			actuallyHave = 0
			for doc in bucket
				{docNum, docScore} = doc
				actuallyHave += 1 if category in indexedHashTable[docNum]['tags']

			console.log "I correctly filed away #{actuallyHave} out of #{shouldHave} files that were supposed to be in the bucket. Error is #{actuallyHave/shouldHave}"
	)

	return stream

		



