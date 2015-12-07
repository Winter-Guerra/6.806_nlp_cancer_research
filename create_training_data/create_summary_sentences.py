# Let's find summary sentences for each article and see how they compare.
import redis
r = redis.StrictRedis(host='localhost', port=6379, db=0)

import string
import time
import itertools
from lxml import etree

from multiprocessing.pool import Pool
from multiprocessing import JoinableQueue as Queue

DEBUG = False

def parallel_worker():
    while True:
        path, PMID = uncatalogged.get()
        # print("EXploring", path)
        record_summary_sentences(path, PMID)

        # print(output)
        uncatalogged.task_done()

def record_summary_sentences(path, PMID):
    tree = etree.parse(path)

    # Get the last sentence/paragraph of the abstract
    abstract_list = tree.xpath('.//abstract')

    # An article without an abstract is useless
    if not len(abstract_list):
        return

    summary_paragraph_list = abstract_list[0].xpath('.//p') # Get the last paragraph

    if len(summary_paragraph_list):
        summary_paragraph = summary_paragraph_list[-1].text
    else:
        summary_paragraph = abstract_list[0].text

    # Check that we really do have a summary before continuing
    if not summary_paragraph:
        return

    # save the summary sentence in redis
    pipe = r.pipeline()
    pipe.set('summary_abstract_1:{0}'.format(PMID), summary_paragraph)
    # Save the PMID as linked_summarized_article
    pipe.sadd('linked_summarized_article_1', PMID)
    pipe.execute()
    # print(summary_paragraph)

if __name__ == '__main__':
    # Let's load the list of meta research articles 'review-article'
    print("Getting list of connected research articles")
    article_PMIDs = r.smembers('linked_articles')
    article_URLs = r.mget(['{0}:URL'.format(PMID) for PMID in article_PMIDs])

    uncatalogged = Queue()
    for args in zip(article_URLs, article_PMIDs):
        uncatalogged.put(args)

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
