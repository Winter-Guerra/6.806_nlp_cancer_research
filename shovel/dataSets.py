# File for dealing with training and test sets

from . import query
import multiprocessing

# For templating
from pybars import Compiler
compiler = Compiler()
# Get templates
templates = {}
with open('./templates/trainingData.handlebars') as f:
	templates['trainingData'] = f.read()
# Compile the templates
templater = {key: compiler.compile(template) for key,template in templates.items()}

class TrainingSet():

	def __init__(self):
		self.trainingSetDir = './training_data'

	def createTrainingSet(self):
		threads = 4

		# Let's create the positive training set (I.E. set of important sentences).

		# Get list of foods
		foodList = []
		with open('./foodList.txt') as f:
			foodList = f.read().split('\n')

		# Grab our query results
		# queryObjects = [query.Query(foodList[0]), query.Query(foodList[1])]
		# queryObjects = [query.Query(subject) for subject in foodList]

		pool = multiprocessing.Pool(threads)
		queryObjects = pool.map(query.Query, foodList)

		context = {
			'query': queryObjects
		}

		# Print out our unannotated dataset to a file for human annotation
		html = templater['trainingData'](context)
		# Output the rendered html
		with open(self.trainingSetDir+"/positiveDataset.txt", 'w') as f:
			f.write(html)


if __name__ == '__main__':
	trainingSet = TrainingSet()
	trainingSet.createTrainingSet()
