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
natural = require('natural')
tokenizer = new natural.WordPunctTokenizer()

cleanData = lazypipe()
	# Let's remove title headings from the sources (these cannot count as sentences)
	.pipe(replace, /^#+.*/mg, '')
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
	# Remove commas and other punctuation that is not [.,?:]
	.pipe(replace, /[;/]/g, ' ')
	# Make everything single spaced
	.pipe(replace, /\s+/g, ' ')


removeTitle = lazypipe()
	# Let's remove the title from the source (these cannot count as sentences)
	.pipe(replace, /^#+.*/mg, '')

gulp.task 'separateData', () ->


	# gulp.src(['/Users/winterg/Dropbox (MIT)/Development_Workspace/UROP/datamining foodforbreastcancer/sources/raw/badFoods/**/*.md'])
	# .pipe(flatten())
	# .pipe(dedupe())
	# .pipe(gulp.dest('./training_data/-1/'))


	gulp.src(['/Users/winterg/Dropbox (MIT)/Development_Workspace/UROP/datamining foodforbreastcancer/sources/raw/recommendedFoods/**/*.md'])
	.pipe(flatten())
	.pipe(dedupe())
	.pipe(gulp.dest('./training_data/+1/'))

gulp.task 'pruneOutNegatives', (cb) ->

	# Make dictionary
	dict = {}

	stream = gulp.src(['/Users/winterg/Dropbox (MIT)/Development_Workspace/UROP/training_data/-1/*.md', '/Users/winterg/Dropbox (MIT)/Development_Workspace/UROP/training_data/0/*.md'])
	.pipe(
		tap (file) ->
			# Get the file contents
			dict[file.contents.toString()] = true
		)

	.on 'end', () ->
		# Now, start the second stream
		gulp.src(['/Users/winterg/Dropbox (MIT)/Development_Workspace/UROP/training_data/+1/*.md'])
		.pipe(
			tap (file) ->
				if not dict[file.contents.toString()]?
					# console.log file.contents.toString()
					return file
				else
					console.log "None!"
					fs.unlinkSync(file.path)
					# return null
			)
		.pipe(gulp.dest('/Users/winterg/Dropbox (MIT)/Development_Workspace/UROP/training_data/+1_sorted/'))
		.on 'end', cb

	return

gulp.task 'concatDocumentCorpusWithWhitespaceTokenization', () ->

	corpus = []

	stream = gulp.src(['/Users/winterg/Dropbox (MIT)/Development_Workspace/UROP/datamining foodforbreastcancer/sources/deduped/*.md'])

	.pipe(cleanData())

	.pipe(
		tap (file) ->
			# Get the data from the file
			fileData = file.contents.toString().toLowerCase()

			# Tokenize the document
			fileData = tokenizer.tokenize(fileData).join(' ')

			# Append document to output file
			corpus.push(fileData)
	)
	.on 'end', () ->
		# Write the corpus to disk
		fs.outputFileSync('./training_data/corpus.txt', corpus.join('\n'))

	return stream
