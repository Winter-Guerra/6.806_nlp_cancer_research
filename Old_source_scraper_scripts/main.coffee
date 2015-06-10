# The main test script

request = require('superagent')
jf = require('jsonfile')
# Make the new jsons pretty
jf.spaces = 4
fs = require('fs-extra')
_ = require("underscore")



QueryString = (inputURL) ->
	escapedURL = encodeURIComponent(inputURL)
	URL =  "https://api.import.io/store/connector/_magic?url=#{ escapedURL }&js=false&_apikey=60bf0d6f-5c74-45ee-9594-2e74b98bf9f2%3ALT9v0eC%2BcTtecmABCyCuR%2BM%2FCQL%2BshA5Egd98L4EcskAO7%2BG7MT9fUQZrHJhcxZpOkAnXBlOVaOWRjD2wbT9Ag%3D%3D"
	return URL

sanitizeResults = (jsonResponse) ->
	results = jsonResponse.tables[0].results

	# Go through each article listing and change the "link/_text" field to "Title"
	for article in results
		title = article['link/_text']
		delete article['link/_text']
		article['title'] = title

	return results


# Find the json representation of the list of articles in the URL

getAndSaveData = (title, URL) ->

	request.get( QueryString( URL ) )
		.accept('application/json')
		.end (err, res) ->
			if (res.ok)

				# Get the results
				jsonResponse = res.body

				if not jsonResponse.tables?
					# Then we have a small problem
					console.error "No files found for #{title}"

				else
					results = sanitizeResults(jsonResponse)

					# Log the jsonfile to disk
					fs.emptyDirSync("./sources/badFoods/#{title}")

					jf.writeFileSync("./sources/badFoods/#{title}/article-list.json", results)

				# Append the 

throttledQuery = _.throttle getAndSaveData, 1000



# RUN THE SCRIPT ON ALL THE DATA WE HAVE
goodFoods = fs.readJsonSync('./sources/badFoods.json')

linkList = goodFoods['links']





for link in linkList

	[unused, ..., title] = link.split('/')
	console.log title
	getAndSaveData( title, link)




# getAndSaveData("Dry Beans", "http://foodforbreastcancer.com/foods/dry-beans")


