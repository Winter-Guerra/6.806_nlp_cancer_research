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

	# Remove headings
	.pipe(replace(/^#.*/mg, ''))
	
	# Tokenize the sentence
	.pipe(run('python3 sentence_tokenizer.py', {silent:true})) # This generates yaml files of each sentence of the summaries
	
	# Save the output
	.pipe(gulp.dest('./build/summaries')) # Save this to a temp directory so that we can check the output of the tokenizer

	return stream

# This will use tf-idf to match all the summary sentences with the best match in our corpus  
gulp.task 'generateTrainingClassifications', () ->

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

	.on	'error', (err) ->
		console.error err

# This task will take the sentences output from the summaries and pair them with a specific sentence from 
gulp.task 'mapSentenceClassificationsToOriginalFiles', () ->



		



