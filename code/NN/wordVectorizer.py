# wordVectorizer

# Takes in a list of tuples and outputs 2 np matrices where each row is a document vector.

# This file grabs the dataset from redis, tokenizes it, scrables it, and vectorizes it.

import redis
r = redis.StrictRedis(host='localhost', port=6379, db=0)
r.set_response_callback('SMEMBERS', lambda l: [int(i) for i in l]) # Converts member responses to a list of ints.
r.set_response_callback('SRANDMEMBER', lambda l: [int(i) for i in l]) # Converts member responses to a list of ints.
r.set_response_callback('HGETALL', lambda l: {int(key):int(value) for key,value in pairwise(l)}) # Converts member responses to a list of ints.


import string
import cPickle as pickle
import time
import random
import itertools
import numpy as np
from gensim.models.word2vec import Word2Vec
from keras.preprocessing.text import Tokenizer, text_to_word_sequence
from sklearn.preprocessing import normalize
from sklearn.utils import resample
import h5py

import redis_dataset


DEBUG = True

def getMatrices(data, path):
    x,y = data

    # Necesary to avoid errors
    y = y.reshape((y.shape[0],1))

    X1_PMIDS = []
    X2_PMIDS = []
    for PMID1, PMID2 in x:
        X1_PMIDS.append(PMID1)
        X2_PMIDS.append(PMID2)

    # Now, fetch the matrices
    print "Reducing PMIDs"
    PMIDS_needed = list(set(X1_PMIDS + X2_PMIDS))

    print "Fetching vectors"
    vectors = r.mget(['summary_vector:{}'.format(PMID) for PMID in PMIDS_needed])

    print "Db Response length: {}".format(len(vectors))
    print "Number of empy responses: {}".format(len([1 for vector in vectors if vector==None]))

    # Turn vectors into dictionary (and unpickle the vectors)
    vector_dict = {PMID: pickle.loads(vector).reshape((1,200)) if vector else np.random.rand(1,200) for PMID,vector in itertools.izip(PMIDS_needed, vectors)}

    # for PMID in X1_PMIDS:
    #     print vector_dict[PMID].dtype

    X1_matrix = np.vstack([vector_dict[PMID] for PMID in X1_PMIDS])
    X2_matrix = np.vstack([vector_dict[PMID] for PMID in X2_PMIDS])

    return ((X1_matrix, X2_matrix, y), path)

def convertData(data, path):
    (X1_matrix, X2_matrix, y) = data

    # Shuffle the data
    X1_matrix, X2_matrix, y = resample(X1_matrix, X2_matrix, y, random_state=0)

    # Let's save this data to a file on disk for retrival
    with h5py.File(path, "w") as f:
        dset_1 = f.create_dataset("X1", data=X1_matrix, dtype='float32')
        dset_2 = f.create_dataset("X2", data=X2_matrix, dtype='float32')
        dset_3 = f.create_dataset("y", data=y, dtype='float32')

    print "Saved data shapes"
    print (X1_matrix.shape, X2_matrix.shape, y.shape)

    return (path, X1_matrix.shape)

def get_large_datasets():
    # Get a list of combinations from redis
    ((training), (testing)) = redis_dataset.get_dataset(test_split=0.2)
    # Convert these lists to vector matrices using word2vec

    print("Getting embeddings")

    (train, path) = getMatrices(training, '/mnt/ephemeral0/training.hdf5')
    (test, path) = getMatrices(testing, '/mnt/ephemeral0/testing.hdf5')
    return (train, test)

def save_large_datasets():
    # Get a list of combinations from redis
    ((training), (testing)) = redis_dataset.get_dataset(test_split=0.2)
    # Convert these lists to vector matrices using word2vec

    print("Getting embeddings")

    (train, path) = getMatrices(training, '/mnt/ephemeral0/training.hdf5')
    datapath, shape = convertData(train, path)
    print "Training data saved to {} with shape {}".format(datapath, shape)

    (test, path) = getMatrices(testing, '/mnt/ephemeral0/testing.hdf5')
    datapath, shape = convertData(test, path)
    print "Testing data saved to {} with shape {}".format(datapath, shape)

    return (train, test)

def get_embeddings_to_redis():

    print "Loading wordvector model"
    model = Word2Vec.load_word2vec_format('/mnt/ephemeral0/word2vec_models/PubMed-and-PMC-w2v.bin', binary=True)

    d = model['the'].size
    print "Dimensionality of wordvector model is {}".format(d)

    print "Loading summaries from redis"
    # Let's get our listing of interesting articles.
    global_PMID_listing = r.smembers('linked_summarized_article_1') # a list

    # Let's get the text document summaries for all PMIDs.
    article_summaries = r.mget(['summary_abstract_1:{}'.format(PMID) for PMID in global_PMID_listing])

    # Let's convert these summaries to their wordvector equivalent.
    print "Converting summaries to wordvectors"

    for summary, PMID in itertools.izip(article_summaries, global_PMID_listing):
        # Split the summary
        word_sequence = text_to_word_sequence(summary)
        # Vectorize
        vector_sequence = []
        for word in word_sequence:
            if word in model:
                try:
                    vector = model[word].reshape((d,1))
                    vector_sequence.append(vector)
                except Exception as e:
                    print "ERROR: {}".format(e)

        if len(vector_sequence):
            vector_sequence = np.hstack(vector_sequence)
        else:
            vector_sequence = np.random.rand(d,1)
        summary_vector = np.sum(vector_sequence, axis=1).reshape((d,1))
        # print summary_vector

        # Edge case: No vector was found. Populate it with zeros
        if summary_vector.size < d:
            print "ERROR: VECTOR NOT FOUND! :("
            summary_vector = np.random.rand(d,1)
            r.sadd('empty_vector_articles', PMID)

        # print "Vector shape: {}".format(summary_vector.shape)
        # summary_vector.T()
        # Normalize
        normalized_summary_vector = normalize(summary_vector.T) # l2 euclidian norm of (1,d)
        # Store result
        pickled_summary_vector = pickle.dumps(normalized_summary_vector)
        r.set('summary_vector:{}'.format(PMID), pickled_summary_vector)

    print "Done!"

if __name__ == '__main__':
    # get_embeddings_to_redis()
    # save_large_datasets()
