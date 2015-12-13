
# Dataset Information

The dataset for my [fall 2015 6.806 MIT research project](https://github.com/Winter-Guerra/6.806_nlp_cancer_research) can be found at [this Amazon S3 bucket.](http://nlp-dataset-6806-2015.s3-website-us-east-1.amazonaws.com/)

Below is a listing of all of the directories in this dataset and their file sizes.

```
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

## Folder Usages

On a high level, the dataset has the following structure:

```
.
├── [8.0G]  neural_net_training_data
```

This folder contains training and testing data `(*.hdf5)` that were created using citation cross linking across the Pubmed Open Access dataset. Each file holds a giant tuple list of the form (X1, X2, Y) where X1 is a vector embedding of a document, X2 is another vector embedding of a document, and Y is a continuous label between [0,1] that states how 'good' the document similarity is based on citation cross linking.

```  
│   ├── [1.0G]  testing.hdf5
│   ├── [3.8G]  training.hdf5
│   └── [3.1G]  word2vec_models
```
The `word2vec_models` folder contains a word2vec model from [bio.nlplab.org](http://bio.nlplab.org/) that has been trained on the NIH's PubMed and PMC datasets. This model is used to create the embedded representations of the documents in the dataset for use in the `neural_net_training_data` files used to train the neural network.

```
├── [94G]  pubmed_files
│   ├── [17G]  cited_xml_files
│   └── [77G]  full_xml_dataset
```
Here we have both the [full NIH Open Access dataset](http://www.ncbi.nlm.nih.gov/pmc/tools/openftlist/) and a smaller subset of the Open Access dataset that only includes `research-article` documents that were cited in at least 1 `meta-review` document. The `cited_xml_files` folder contains the subset of the data that is actually interesting to my research, and is thus compiled into the `neural_net_training_data` folder.

```
└── [448M]  redis_memory_cache
    ├── [321M]  dump.rdb
    └── [127M]  temp-9201.rdb
```
Here we have the data from my research's [in-memory Redis cache](http://redis.io/). This database is very lightweight and contains meta-information on all of the relevant articles in the NIH Open Access dataset. For more information on what information is stored in this database, please look at the section in this [readme concerning the database structure.](#)
