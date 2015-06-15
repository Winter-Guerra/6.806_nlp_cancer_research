# This is a gulpfile for the sources dir

gulp = require('gulp')
dedupe = require('./gulp-dedupe')
count = require('gulp-count')
flatten = require('gulp-flatten')
run = require('gulp-run') # For the stream tokenizer
rename = require("gulp-rename")
replace = require('gulp-replace')

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
