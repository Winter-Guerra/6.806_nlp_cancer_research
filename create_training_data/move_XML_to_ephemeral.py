# Copies meta research articles and connected articles to ephemeral0 for faster access
import redis
r = redis.StrictRedis(host='localhost', port=6379, db=0)

import string
import time
import itertools
from lxml import etree
import os
import shutil

from multiprocessing.pool import Pool
from multiprocessing import JoinableQueue as Queue

DEBUG = False

def parallel_worker():
    while True:
        URL = uncatalogged.get()
        # print("EXploring", path)
        moveFile(URL)

        # print(output)
        uncatalogged.task_done()

def moveFile(URL):
    # URL will look like "/mnt/ephemeral0/xml/Genome_Announc/Genome_Announc_2014_Sep_25_2(5)_e00942-14.nxml"
    # want "/mnt/nlp/xml/Genome_Announc/Genome_Announc_2014_Sep_25_2(5)_e00942-14.nxml"

    origin_URL = URL.replace("ephemeral0", 'nlp')
    # Check that the destination path exists
    if not os.path.exists(os.path.dirname(URL)):
        os.makedirs(os.path.dirname(URL))
    # Copy the file
    shutil.copy(origin_URL, URL)

if __name__ == '__main__':

    print("Getting list of meta research articles")
    meta_article_PMIDs = r.smembers('review-article')

    print("Getting list of connected research articles")
    connected_article_PMIDs = r.smembers('linked_articles')

    print("Getting URLs of all relevant articles")
    article_URLs = r.mget(['{0}:URL'.format(PMID) for PMID in meta_article_PMIDs.union(connected_article_PMIDs) ])

    uncatalogged = Queue()
    for args in article_URLs:
        uncatalogged.put(args)

    print("Copying data")

    if DEBUG:
        # Run one process
        print("DEBUG: Running single threaded.")
        parallel_worker()

    else:

        print("Starting pool")
        NUM_WORKERS = 7
        pool = Pool(NUM_WORKERS)

        results = [pool.apply_async(parallel_worker) for i in range(NUM_WORKERS)]

        print("Running progress capture.")
        while (True):
          remaining = uncatalogged.qsize()
          print "Waiting for", remaining, "tasks to complete..."
          time.sleep(0.5)
        #   print [result.get() for result in results]

        uncatalogged.join()
        print 'Done'
