

# This file grabs the dataset from redis, tokenizes it, scrables it, and vectorizes it.

import redis
r = redis.StrictRedis(host='localhost', port=6379, db=0)
r.set_response_callback('SMEMBERS', lambda l: [int(i) for i in l]) # Converts member responses to a list of ints.
r.set_response_callback('SRANDMEMBER', lambda l: [int(i) for i in l]) # Converts member responses to a list of ints.
r.set_response_callback('HGETALL', lambda l: {int(key):int(value) for key,value in pairwise(l)}) # Converts member responses to a list of ints.


import string
import time
import random
import itertools
import numpy as np
# from lxml import etree
from multiprocessing.pool import Pool
from multiprocessing import JoinableQueue as Queue

DEBUG = True

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)

def get_dataset(test_split=0.2):
    ''' Returns: (X_train, y_train), (X_test, y_test) '''

    print("Loading global PMID listings")
    global_PMID_listing = r.smembers('linked_summarized_article_1')
    holdout_PMIDs = r.srandmember('linked_summarized_article_1', int(len(global_PMID_listing)*test_split))
    holdout_PMIDs_SET = frozenset(holdout_PMIDs)

    # Record our dataset in the DB for ease of checks.
    r.sadd('holdout_PMIDs', holdout_PMIDs)
    r.sdiffstore('training_PMIDs', 'linked_summarized_article_1', 'holdout_PMIDs')
    training_PMIDs = r.smembers('training_PMIDs')
    training_PMIDs_SET = frozenset(training_PMIDs)

    print "Loaded {} training PMIDs and {} holdout PMIDs.".format(len(training_PMIDs), len(holdout_PMIDs))

    # Get the training set
    (X_training, y_training) = getTupleList(holdout_PMIDs, holdout_PMIDs_SET, training_PMIDs, training_PMIDs_SET, mode='training')

    # Get the test set
    (X_test, y_test) = getTupleList(holdout_PMIDs, holdout_PMIDs_SET, training_PMIDs, training_PMIDs_SET, mode='testing')

    # Test that nothing has been mutated
    print "FINISHED! {} training PMIDs and {} holdout PMIDs.".format(len(training_PMIDs), len(holdout_PMIDs))

    # Convert the y_vectors to numpy vectors and normalize
    y_training = np.array(y_training)
    y_test = np.array(y_test)

    # Normalize
    total_sum = y_training.sum() + y_test.sum()
    total_length = y_training.size + y_test.size
    y_test *= float(total_length)/total_sum
    y_training *= float(total_length)/total_sum

    # Let's return this and process it using word2vec
    return ((X_training, y_training), (X_test, y_test))

def getTupleList(holdout_PMIDs, holdout_PMIDs_SET, training_PMIDs, training_PMIDs_SET, mode='training'):

    print "Creating CORRECT combinations of PMIDs from {} dataset.".format(mode)

    # Fetch connection dictionaries for all of the a1 nodes.
    if mode == 'testing':
        training_PMIDs = holdout_PMIDs
        training_PMIDs_SET = holdout_PMIDs_SET.copy()
        holdout_PMIDs = []
        holdout_PMIDs_SET = frozenset()

    # print (len(holdout_PMIDs), len(holdout_PMIDs_SET), len(training_PMIDs), len(training_PMIDs_SET))

    pipe = r.pipeline()
    for a1 in training_PMIDs:
        # Find a2 that it likes
        pipe.hgetall("conn:{}".format(a1))
    connection_dictionaries = pipe.execute()
    # This list of connection dictionaries will be unravled into tuples and cleaned to remove all holdout_PMIDs

    correct_training_tuples = []
    correct_training_y = []
    connection_counts = {}
    for a1,connections in itertools.izip(training_PMIDs, connection_dictionaries):
        for a2 in (connections.keys()+[a1]): # Include yourself!
            if a2 not in holdout_PMIDs_SET:
                correct_training_tuples.append( (a1, a2 ) )

                # A metric for how good the correlation is
                correct_training_y.append( \
                    connections.get( a2, sum([val for key,val in connections.items()]) ) \
                    )

                # Keep track of how many connections each node has
                connection_counts[a1] = connection_counts.get(a1, 0) + 0.5
                # if not a1 == a2:
                # Each one of these tupes counts as a half connection.
                connection_counts[a2] = connection_counts.get(a2, 0) + 0.5

    if DEBUG:
        print correct_training_tuples[:25]
        print "------------------------------"

    print "Creating BAD combinations of PMIDs from {} dataset.".format(mode)
    bad_training_tuples = []
    bad_training_y = []
    c = 2 if mode == 'testing' else 1 # normalize the dev/test set
    for a1,connections in itertools.izip(training_PMIDs, connection_dictionaries):
        number_of_bad_connections_to_generate = int(c*connection_counts.get(a1,0))
        docs_to_avoid = frozenset(connections.keys() + [a1]) # Cannot include yourself!

        for i in xrange(number_of_bad_connections_to_generate+1):
            a2 = random.choice(training_PMIDs)
            # Force a2 to not be in the forbidden elements
            while (a2 in docs_to_avoid):
                a2 = random.choice(training_PMIDs)
            bad_training_tuples.append( (a1,a2) )
            bad_training_y.append(0)

    if DEBUG:
        print bad_training_tuples[:25]

        print '-------------------------------'
        print "Length of good conns: {} Length of bad conns: {}. Ratio: {}".format(len(correct_training_tuples), len(bad_training_tuples), float(len(correct_training_tuples))/len(bad_training_tuples))

    return (correct_training_tuples+bad_training_tuples, correct_training_y+bad_training_y )

if __name__ == '__main__':
    # Test
    get_dataset(test_split=0.2)
