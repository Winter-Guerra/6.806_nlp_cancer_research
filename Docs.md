

## Database Keys

* `{PMID}:URL` -> holds the file path that belongs to this PMID.
  * Ex: `/mnt/ephemeral0/xml/Genome_Announc/Genome_Announc_2014_Sep_25_2(5)_e00942-14.nxml`

* `summary_abstract_1:{PMID}` -> holds a text string of a few sentences from the document, grabbed from the abstract.
  * EX: `"Fruit quality is a very complex trait that is affected by both genetic and non-genetic factors. Generally, low temperature (LT) is used to delay fruit senescence and maintain fruit quality during post-harvest storage but the molecular mechanisms involved are poorly understood. Hirado Buntan Pummelo (HBP; "`

* `conn:{PMID}` -> Is a hashtable that holds keys of the form `{PMID} -> {cross_reference_count}`. This is used to form  the connection graph training data.
  * EX: `$hgetall "conn:18371199" -> ("16704839", "1") ("18617994", "1") ("17067369", "1") ....`

* `'linked_articles'` ->
* `'review-article'` ->
* `article_types` ->
* `linked_summarized_article_1` ->
* 'holdout_PMIDs'
* 'training_PMIDs'
