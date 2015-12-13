# Let's make a gold mapping of which articles link to other articles.

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
        path = uncatalogged.get()
        # print("EXploring", path)
        process_meta_article(path)
        # print(output)
        uncatalogged.task_done()


def process_meta_article(path):
    tree = etree.parse(path)

    reference_lookup, refCodeList = get_reference_lookup(tree)

    # Find the groupings of citations
    citation_groupings = get_citation_groupings(tree, refCodeList)
    # print citation_groupings

    # Now, we need to transform these citations to a mapping of PMIDs (Also pruning out dead links)
    PMID_groupings = [ [ reference_lookup[citation] for citation in grouping if citation in reference_lookup] for grouping in citation_groupings ]

    # Now, let's upload these groupings to the DB store in the form of a hash.
    pipe = r.pipeline()
    for grouping in PMID_groupings:
        for i, HEAD in enumerate(grouping):
            # print(HEAD)
            subset = grouping[:i] + grouping[i+1:]
            for key in subset:
                pipe.hincrby('conn:{0}'.format(HEAD), key)

                # Keep track of which articles are actually linked to other articles
                pipe.sadd('linked_articles', HEAD)
    # Update the database
    pipe.execute()



def get_reference_number(reference_obj):
    return reference_obj.get('id')

def get_reference_lookup(tree):

    refList = tree.xpath('./back/ref-list/ref[//pub-id/@pub-id-type="pmid"]') # This creates a list of reference objects

    # # We should check if we have these PMIDs in our database
    # print(refList[0].xpath('.//pub-id[@pub-id-type="pmid"]')[0].text)
    PMIDs = []
    for reference in refList:
        # print(reference.xpath('.//pub-id[@pub-id-type="pmid"]'))
        results = reference.xpath('.//pub-id[@pub-id-type="pmid"]')
        if len(results):
            PMID = results[0].text
        else:
            PMID = ''
        PMIDs.append(PMID)

    pipe = r.pipeline()
    for PMID in PMIDs:
        # print(PMID)
        pipe.sismember('research-article', PMID)
    valid_files = pipe.execute()
    # print(valid_files)

    # Make a lookup table: Citation number -> PMID
    reference_lookup = dict( (get_reference_number(ref), PMID) for ref,PMID,is_valid_file in zip(refList, PMIDs, valid_files) if is_valid_file )

    refCodeList = [ get_reference_number(ref) for ref in refList]

    # print(reference_lookup, refCodeList)

    return (reference_lookup, refCodeList)

def get_citation_groupings(tree, refCodeList):
    # We want to match each item in the citation database to an entry in 'research-article' (if the match is good)
    citation_tags = tree.xpath('./body//xref[@ref-type="bibr"]')

    # Keep track of the last citation we saw
    citation_groupings = []
    lastCitationIndex = 0
    lastSuffix = ']'
    for citation in citation_tags:
        # Find the citation number
        try:
            citation_code = citation.get('rid')
            # Skip this citation
            if citation_code not in refCodeList:
                continue
        except Exception as e:
            print(etree.tostring(tree, pretty_print=True))
            raise e
        if citation.tail:
            citation_suffix = citation.tail[0]
        else:
            citation_suffix = ']'

        citation_index = refCodeList.index(citation_code)

        if lastSuffix == ']':
            # Make a new group
            citation_groupings.append(set())
        elif lastSuffix == ',':
            # Then this is another citation in the same group
            pass
        elif lastSuffix == '-':
            # Then we should be filling in the empty spots in this group
            citation_groupings[-1].update(refCodeList[lastCitationIndex+1:citation_index])

        # Regardless, we need to add ourselves to a group
        citation_groupings[-1].add(citation_code)

        lastSuffix = citation_suffix
        lastCitationIndex = citation_index

    return citation_groupings

if __name__ == '__main__':
    # Let's load the list of meta research articles 'review-article'
    print("Getting list of meta research articles")
    meta_article_PMIDs = r.smembers('review-article')
    meta_article_URLs = r.mget(['{0}:URL'.format(PMID) for PMID in meta_article_PMIDs])

    uncatalogged = Queue()
    for article in meta_article_URLs:
        uncatalogged.put(article)

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


# CITATIONS
# [<xref ref-type="bibr" rid="B3">3</xref>,<xref ref-type="bibr" rid="B15">15</xref>]


# REFERENCE
# <ref id="B2">
    # <mixed-citation publication-type="journal">
    #   <name>
    #     <surname>Fabbri</surname>
    #     <given-names>LM</given-names>
    #   </name>
    #   <name>
    #     <surname>Rabe</surname>
    #     <given-names>KF</given-names>
    #   </name>
    #   <article-title>From COPD to chronic systemic inflammatory syndrome?</article-title>
    #   <source>Lancet</source>
    #   <year>2007</year>
    #   <volume>370</volume>
    #   <fpage>797</fpage>
    #   <lpage>799</lpage>
    #   <pub-id pub-id-type="pmid">17765529</pub-id>
    # </mixed-citation>
    # </ref>
