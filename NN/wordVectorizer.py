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
# from sklearn.preprocessing import Normalizer
# from lxml import etree
# from multiprocessing.pool import Pool
# from multiprocessing import JoinableQueue as Queue

DEBUG = True

def convertData(inp):
    ''' Returns (X1_train, X2_train) '''
    X1_PMIDS = []
    X2_PMIDS = []
    for PMID1, PMID2 in inp:
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
    #     print vector_dict[PMID].shape

    X1_matrix = np.vstack([vector_dict[PMID] for PMID in X1_PMIDS])
    X2_matrix = np.vstack([vector_dict[PMID] for PMID in X2_PMIDS])

    return (X1_matrix, X2_matrix)

if __name__ == '__main__':

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
        vector_sequence = np.array([ model[word].reshape((d,1)) for word in word_sequence if word in model])
        summary_vector = np.sum(vector_sequence, axis=0)
        # print summary_vector

        # Edge case: No vector was found. Populate it with zeros
        if summary_vector.size < d:
            print "ERROR: VECTOR NOT FOUND! :("
            summary_vector = np.random.rand(1,d)
            r.sadd('empty_vector_articles', PMID)

        # print "Vector shape: {}".format(summary_vector.shape)
        summary_vector.reshape((1,d))
        # Normalize
        normalized_summary_vector = normalize(summary_vector) # l2 euclidian norm
        # Store result
        pickled_summary_vector = pickle.dumps(normalized_summary_vector)
        r.set('summary_vector:{}'.format(PMID), pickled_summary_vector)

    print "Done!"
