

# [Link to dataset](http://nlp-dataset-6806-2015.s3.amazonaws.com/list.html)

## Dataset Information

The dataset for my [fall 2015 6.806 MIT research project](https://github.com/Winter-Guerra/6.806_nlp_cancer_research) can be found at [this Amazon S3 bucket.](http://nlp-dataset-6806-2015.s3.amazonaws.com/list.html)

Below is a listing of all of the directories in this dataset and their file sizes.

```bash
.
├── [ 16K]  lost+found
├── [8.0G]  neural_net_training_data
│   ├── [1.0G]  testing.hdf5
│   ├── [3.8G]  training.hdf5
│   └── [3.1G]  word2vec_models
├── [94G]  pubmed_files
│   ├── [17G]  cited_xml_files
│   └── [77G]  full_xml_dataset
└── [448M]  redis_memory_cache
    ├── [321M]  dump.rdb
    └── [127M]  temp-9201.rdb
```

### Dataset Folders

On a high level, the dataset has the following structure:

```bash
.
├── [8.0G]  neural_net_training_data
```

This folder contains training and testing data `(*.hdf5)` that were created using citation cross linking across the Pubmed Open Access dataset. Each file holds a giant tuple list of the form (X1, X2, Y) where X1 is a vector embedding of a document, X2 is another vector embedding of a document, and Y is a continuous label between [0,1] that states how 'good' the document similarity is based on citation cross linking.

```bash
│   ├── [1.0G]  testing.hdf5
│   ├── [3.8G]  training.hdf5
│   └── [3.1G]  word2vec_models
```

The `word2vec_models` folder contains a word2vec model from [bio.nlplab.org](http://bio.nlplab.org/) that has been trained on the NIH's PubMed and PMC datasets. This model is used to create the embedded representations of the documents in the dataset for use in the `neural_net_training_data` files used to train the neural network.

```bash
├── [94G]  pubmed_files
│   ├── [17G]  cited_xml_files
│   └── [77G]  full_xml_dataset
```

Here we have both the [full NIH Open Access dataset](http://www.ncbi.nlm.nih.gov/pmc/tools/openftlist/) and a smaller subset of the Open Access dataset that only includes `research-article` documents that were cited in at least 1 `review-article` document. The `cited_xml_files` folder contains the subset of the data that is actually interesting to my research, and is thus compiled into the `neural_net_training_data` folder.

```bash
└── [448M]  redis_memory_cache
    ├── [321M]  dump.rdb
    └── [127M]  temp-9201.rdb
```

Here we have the data from my research's [in-memory Redis cache](http://redis.io/). This database is very lightweight and contains meta-information on all of the relevant articles in the NIH Open Access dataset. For more information on what information is stored in this database, please look at the section in this [readme concerning the database structure.](#article-metadata-database)


## Article Metadata Database

## Metadata parsed from documents

* `article_types` -> This contains a list of all of the article types found in the full Open Access dataset.
  * Ex: `[ 'review-article', 'research-article', 'retraction', etc.]`
* `{article-type}` (I.E `'research-article'`) -> Holds a list of PMIDs from the Open Access dataset that all have this article type.
  * Ex: `[ 16704839, 18617994, 17067369 ]`
* `{PMID}:URL` -> holds the file path that belongs to this PMID.
  * Ex: `/mnt/ephemeral0/xml/Genome_Announc/Genome_Announc_2014_Sep_25_2(5)_e00942-14.nxml`
* `summary_abstract_1:{PMID}` -> holds a text string of a few sentences from the document, grabbed from the abstract.
  * Ex: `"Fruit quality is a very complex trait that is affected by both genetic and non-genetic factors. Generally, low temperature (LT) is used to delay fruit senescence and maintain fruit quality during post-harvest storage but the molecular mechanisms involved are poorly understood. Hirado Buntan Pummelo (HBP; "`

## Document link distance metadata

* `linked_summarized_article_1` -> This is a list of all the PMIDs of files that have a vectorized embedding of their summary. This is an important list since some of our articles actually are empty.
* `conn:{PMID}` -> Is a hashtable that holds keys of the form `{PMID} -> {cross_reference_count}`. This is used to form  the connection graph training data.
  * Ex: `$hgetall "conn:18371199" -> ("16704839", "1") ("18617994", "1") ("17067369", "1") ....`

## Training data metadata

* `'holdout_PMIDs'` -> This is a list of all the PMIDs of files that were used for the test set of the neural network.
* `'training_PMIDs'` -> This is a list of all the PMIDs of files that were used for the training set of the neural network.
