###!
# gulp-dedupe, https://github.com/hoho/gulp-dedupe
# (c) 2014 Marat Abdullin, MIT license
###

'use strict'
through = require('through')
gutil = require('gulp-util')
PluginError = gutil.PluginError
path = require('path')
defaults = require('lodash.defaults')

module.exports = (options) ->
  filesMap = {}

  bufferContents = (file) ->
    if file.isNull()
      return
    if file.isStream()
      return @emit('error', new PluginError('gulp-dedupe', 'Streaming not supported'))
    
    if filesMap[file.contents.toString()]?
      # We have a duplicate. Do nothing.
      return
    else
      filesMap[file.contents.toString()] = true
      @emit 'data', file
    return

  endStream = ->
    @emit 'end'
    return

  options = defaults(options or {},
    error: false
    same: true
    diff: false)
  through bufferContents, endStream

# ---
# generated by js2coffee 2.0.4