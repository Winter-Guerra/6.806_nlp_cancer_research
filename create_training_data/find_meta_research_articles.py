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

# Here is a regex for finding the type of the report
# regex = re.compile("article-type=\W(\S*?)\W>")
# regex = re.compile("article-type=\W(?P<article_type>\S*?)\W>")

def explore_file(path):
    # Record the type of this file
    tree = etree.parse(path)
    typeofDocument = tree.xpath('./@article-type')[0]

    # Add this type to the list of known types.
    r.sadd('article_types', typeofDocument)
    r.sadd(typeofDocument, path)


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

print("Finding paths")
paths = findFilesInDir('/mnt/ephemeral0/xml/')

unsearched = Queue()
for path in paths:
    unsearched.put(path)

print("Number of files", len(paths))


print("Starting pool")
NUM_WORKERS = 6
pool = Pool(NUM_WORKERS)

results = [pool.apply_async(parallel_worker) for i in range(NUM_WORKERS)]

print("Running progress capture.")
while (True):
  remaining = unsearched.qsize()
  print "Waiting for", remaining, "tasks to complete..."
  time.sleep(0.5)
  # [result.get() for result in results]


pool.close() # No more work

unsearched.join()
print 'Done'
