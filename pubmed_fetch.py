# This is a pubmed fetcher

# you need to install Biopython:
# pip install biopython
 
# Full discussion:
# https://marcobonzanini.wordpress.com/2015/01/12/searching-pubmed-with-python/
 
from Bio import Entrez
import json
 
def search(query):
	Entrez.email = 'winterg@mit.edu'
	handle = Entrez.esearch(db='pubmed', 
							sort='relevance', 
							retmax='100',
							retmode='xml', 
							term=query)
	results = Entrez.read(handle)
	return results
 
def fetch_details(id_list):
	ids = ','.join(id_list)
	Entrez.email = 'winterg@mit.edu'
	handle = Entrez.efetch(db='pubmed',
						   retmode='xml',
						   id=ids)
	results = Entrez.read(handle)
	return results

def find_result(abstractText):
	# pass

	for i in range(len(abstractText)):
		if "attributes={u'NlmCategory': u'RESULTS'" in repr(abstractText[i]) :
			# Then, we have a result!
			return abstractText[i+1]

	# No Result
	return None


def findAbstract(abstractText):
	abstractList = json.dumps(abstractText)
	abstract = str().join(abstractList)
	return abstract


 
if __name__ == '__main__':
	results = search('green tea cancer')
	id_list = results['IdList']
	papers = fetch_details(id_list)

	numberPapersHaveHits = 0
	for i, paper in enumerate(papers):
	   print("%d) %s" % (i+1, paper['MedlineCitation']['Article']['ArticleTitle'].encode('ascii', 'ignore')))
	   # abstract = paper['MedlineCitation']['Article']['Abstract']
	   # print abstract
	   # print(json.dumps(paper['MedlineCitation']['Article']['Abstract']['AbstractText'], indent=2, separators=(',', ':')))

	   # Print the abstract if there is one.

	   abstract = paper['MedlineCitation']['Article'].get('Abstract', None)

	   if abstract is not None:
	   		# Print the text
	   		print "ABSTRACT", findAbstract(abstract['AbstractText']).encode('ascii', 'ignore')
	   		result = find_result(abstract['AbstractText'])
	   		if result is not None:
	   			result = result.encode('ascii', 'ignore')
	   			numberPapersHaveHits += 1
	   		print "RESULT", result


	   # Now, find the results
	   print '--------'

	print "Ratio of papers that have annotated results:", numberPapersHaveHits, '/100'
	# Pretty print the first paper in full
	# import json
	# print(json.dumps(papers[0], indent=2, separators=(',', ':')))