# TODO for 7/24/2015

## Let's work on finding concluding sentences

* Convert markdown article to a bunch of sentences that have connection to the title of the article and also have tree heirarchy.

* Convert markdown articles into feature vectors of sentences.
  * Each feature vector has:
    * Overlap with query
    * Encode location in tree
    * Bag of words of sentence

## plan
  * Rerun spider by downloading each article into a jason file of paragraphs, separated by document and also separated by query.

queries:
  "tomato":
    [
    article:
      [
      [['abstract', 'results'], "sentence text", +1]
      ]
    ]
