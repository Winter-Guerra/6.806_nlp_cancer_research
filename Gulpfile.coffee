# This is a gulpfile for the sources dir

gulp = require('gulp')
dedupe = require('./gulp-dedupe')
count = require('gulp-count')
flatten = require('gulp-flatten')

gulp.task 'countSources', () ->
  stream = gulp.src([ 'sources/raw/**/*.md' ])
  .pipe(flatten())
  .pipe(dedupe())
  .pipe(count('## data files copied'))
  .pipe(gulp.dest('./sources/deduped'))
  return stream

