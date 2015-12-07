# Let's find all of the files that are meta research articles

# Creates a database of tags
import redis
r = redis.StrictRedis(host='localhost', port=6379, db=0)

from multiprocessing.pool import Pool
from multiprocessing import JoinableQueue as Queue
import os
import re
import sys
import time

# XML import
from lxml import etree
print("running with lxml.etree")

DEBUG = False

# Here is a regex for finding the type of the report
# regex = re.compile("article-type=\W(\S*?)\W>")
# regex = re.compile("article-type=\W(?P<article_type>\S*?)\W>")

def explore_file(path):
    # Record the type of this file
    tree = etree.parse(path)
    typeofDocument = str(tree.xpath('./@article-type')[0])
    PMID_results = tree.xpath('./front/article-meta/article-id[@pub-id-type="pmid"]')

    # Check that this article can be referenced using a PMID
    if not len(PMID_results):
        # Ignore this file
        if DEBUG:
            print("No PMID. Ignoring ",typeofDocument,path)
        return
    else:
        PMID = PMID_results[0].text

    if DEBUG:
        print(typeofDocument,PMID)

    # Update the database using a pipeline
    pipe = r.pipeline()
    # Add this type to the list of known types.
    pipe.sadd('article_types', typeofDocument)
    pipe.sadd(typeofDocument, PMID)
    pipe.set('{0}:URL'.format(PMID), path)
    DB_results = pipe.execute()


def parallel_worker():
    while True:
        path = unsearched.get()
        # print("EXploring", path)
        explore_file(path)
        # print(output)
        unsearched.task_done()

# acquire the list of paths
def findFilesInDir(source):
    fileExtensions = ('.nxml','.NXML')
    matches = []

    for root, dirnames, filenames in os.walk(source):
        filenames = [ f for f in filenames if os.path.splitext(f)[1] in fileExtensions ]
        for filename in filenames:
            matches.append(os.path.join(root, filename))
    return matches

if __name__ == '__main__':

    print("Finding paths")
    paths = findFilesInDir('/mnt/ephemeral0/xml/')

    unsearched = Queue()
    for path in paths:
        unsearched.put(path)

    print("Number of files", len(paths))

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
          remaining = unsearched.qsize()
          print "Waiting for", remaining, "tasks to complete..."
          time.sleep(0.5)
        #   print [result.get() for result in results]

        unsearched.join()
        print 'Done'
