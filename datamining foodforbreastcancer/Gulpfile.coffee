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
YAML = require('libyaml') # The better yaml
math = require('mathjs')
crypto = require('crypto')
fs = require('fs-extra')
path = require 'path'
clusterfck = require("clusterfck")
buffer = require 'vinyl-buffer'
util = require('util')
{wait, repeat, doAndRepeat, waitUntil} = require 'wait'
prat = require('prat')
promise = require 'bluebird'
lazypipe = require('lazypipe')

# Init libraries
natural.PorterStemmer.attach()


# Helper methods
convertFilepath = (filepath) ->
	filepath = filepath.replace(/tokenized_deduped/, "deduped")
	filepath = filepath.replace(/.yaml/, ".md")
	return filepath

getTitle = (text) ->
	titleList = /^# .*/m.exec(text)
	title = titleList[titleList.length-1]
	title = title[2..]
	return title


cleanData = lazypipe()
	# Let's remove sub headings from the sources (these cannot count as sentences)
	.pipe(replace, /^##+.*/mg, '')
	# Let's remove underlines 
	.pipe(replace, /_/g, '')
	# Let's remove asterisks  
	.pipe(replace, /\*/g, '')
	# Let's remove all apostrophies
	.pipe(replace, /\'/g, '')
	# Let's remove all quotation marks
	.pipe(replace, /\"/g, '')
	# Let's lazily remove all square parenthesis
	.pipe(replace, /\[.*?\]/g, '')
	# Let's lazily remove all stuff inside of parenthesis.
	.pipe(replace, /\(.*?\)/g, '')
	# Let's make all paragraph breaks 2 linebreaks, not more.
	.pipe(replace, /\n\s*\n+/g, '\n\n')
	# Move periods back to closest word
	.pipe(replace, /\s*\./g, '.')
	# Move commas back to closest word
	.pipe(replace, /\s*\,/g, ',')
	# Let's keep all ascii and killall unicode
	.pipe(replace, /[^\x00-\x7F]/g,'')
	# Remove some more crap
	.pipe(replace, /\&lt/,'')

removeTitle = lazypipe()
	# Let's remove the title from the source (these cannot count as sentences)
	.pipe(replace, /^#+.*/mg, '')


gulp.task 'dedupeSources', () ->
	stream = gulp.src([ 'sources/raw/**/*.md' ])
	.pipe(flatten())
	.pipe(dedupe())
	.pipe(count('## data files copied'))
	.pipe(gulp.dest('./sources/deduped'))
	return stream

gulp.task 'cleanSummaries', () ->
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
	# .pipe( replace(/[\s\S]*^## .*cancer-related.*/mg, '') )
	# Remove all paragraphs after the following headings
	# .pipe(replace(/^## [\s\S]*/mg, ''))

	# Remove all remaining headings
	.pipe(replace(/^#.*/mg, ''))

	# Now, do some other default text cleaning
	.pipe(cleanData())
	.pipe(removeTitle())

	# Now save the new text file as a yaml file
	.pipe(
		tap (file) ->

			# Figure out the tag


			objData = {
				tags: path.basename(file.path, '.yaml')
				filePath: file.path
				text: file.contents.toString()
			}

			file.contents = new Buffer YAML.stringify(objData)
			
		)
	# Save the output
	.pipe(gulp.dest('./sources/cleanedSummaries'))

	return stream



gulp.task 'cleanCorpus', () ->

	hashTable = yaml.safeLoad(fs.readFileSync('./sources/dedupedPathIndexedHashTable.yaml'))

	stream = gulp.src(['./sources/deduped/*.md'])

	.pipe(cleanData())
	 
	.pipe(
		tap (file) ->

			text = file.contents.toString()

			# save the title
			title = getTitle(text)

			# Remove the title from the data
			text = text.replace(/^# .*/mg, '')

			# Get hash
			filePathHash = crypto.createHash('md5').update(file.path).digest("hex").toString()

			# Get other file data (like tags)
			metadata = hashTable[filePathHash]


			objData = {
				title: title
				pathHash: filePathHash
				tags: metadata['tags']
				filePath: metadata['filePath']
				text: text
			}

			file.contents = new Buffer YAML.stringify(objData)
		)
	.pipe(rename( (path) ->
		path.extname = '.yaml'
		return path
	))
	.pipe(gulp.dest('./sources/cleaned_deduped'))

	return stream


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

gulp.task 'createDedupedPathIndexedHashTable', () ->

	hashTable = yaml.safeLoad(fs.readFileSync('./sources/hashTable.yaml'))
	indexedHashTable = {}


	stream = gulp.src([ 'sources/deduped/*.md' ])
	.pipe(
		tap (file) =>
			# Find the bin that the file should be in

			fileHash = crypto.createHash('md5').update(file.contents).digest("hex").toString()
			filePathHash = crypto.createHash('md5').update(file.path).digest("hex").toString()

			# Find the tags that go with this file
			tagData =
				hash: fileHash
				tags: hashTable[fileHash]
				filePath: file.path

			indexedHashTable[filePathHash] = tagData
			return 
	)
	.on 'end', () ->

		# Save the hash table
		console.log indexedHashTable
		yamlData = yaml.safeDump(indexedHashTable)
		fs.outputFileSync('./sources/dedupedPathIndexedHashTable.yaml', yamlData)



	return stream
	

# Collapses the feature vectors in each section yaml, 
gulp.task 'collapseBinData',['generateTrainingClassifications'], () ->

	indexedHashTable = yaml.safeLoad(fs.readFileSync './sources/indexedHashTable.yaml' )
	hashTable = yaml.safeLoad(fs.readFileSync './sources/hashTable.yaml' )

	stream = gulp.src(['./sources/trainingClassifications/*.yaml'])

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

		


