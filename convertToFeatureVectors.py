# This is a converter file

directoryList = [ './sources/badFoods/adzuki-beans', './sources/badFoods/alcohol', './sources/badFoods/almonds', './sources/badFoods/avocados', './sources/badFoods/bacon', './sources/badFoods/basil', './sources/badFoods/beef', './sources/badFoods/brown-rice', './sources/badFoods/butter', './sources/badFoods/cheese', './sources/badFoods/coffee', './sources/badFoods/corn-oil', './sources/badFoods/escargot', './sources/badFoods/ginger', './sources/badFoods/herring-and-sardines', './sources/badFoods/lamb', './sources/badFoods/lavender', './sources/badFoods/mackerel', './sources/badFoods/milk', './sources/badFoods/mushrooms', './sources/badFoods/mustard', './sources/badFoods/papaya', './sources/badFoods/peanuts', './sources/badFoods/pork', './sources/badFoods/potatoes', './sources/badFoods/rhubarb', './sources/badFoods/safflower-oil', './sources/badFoods/saffron', './sources/badFoods/sage', './sources/badFoods/salt', './sources/badFoods/shellfish', './sources/badFoods/soy-protein-isolate', './sources/badFoods/soybean-oil', './sources/badFoods/soybean-paste', './sources/badFoods/sugar', './sources/badFoods/sunflower-oil', './sources/badFoods/yerba-mate', './sources/recommendedFoods/apples', './sources/recommendedFoods/artichokes', './sources/recommendedFoods/basil', './sources/recommendedFoods/bell-peppers', './sources/recommendedFoods/black-pepper', './sources/recommendedFoods/blackberries', './sources/recommendedFoods/blueberries', './sources/recommendedFoods/boysenberries', './sources/recommendedFoods/broccoli', './sources/recommendedFoods/brown-rice', './sources/recommendedFoods/brussels-sprouts', './sources/recommendedFoods/buckwheat', './sources/recommendedFoods/cabbage', './sources/recommendedFoods/canola-oil', './sources/recommendedFoods/carrots', './sources/recommendedFoods/cauliflower', './sources/recommendedFoods/celery', './sources/recommendedFoods/cherries', './sources/recommendedFoods/chicken', './sources/recommendedFoods/coffee', './sources/recommendedFoods/cranberries', './sources/recommendedFoods/cucumbers', './sources/recommendedFoods/currants', './sources/recommendedFoods/Dry Beans', './sources/recommendedFoods/dry-beans', './sources/recommendedFoods/flaxseed', './sources/recommendedFoods/ginger', './sources/recommendedFoods/grapes', './sources/recommendedFoods/green-tea', './sources/recommendedFoods/greens', './sources/recommendedFoods/herring-and-sardines', './sources/recommendedFoods/honey', './sources/recommendedFoods/horseradish', './sources/recommendedFoods/hot-peppers', './sources/recommendedFoods/kale', './sources/recommendedFoods/kefir', './sources/recommendedFoods/lake-trout', './sources/recommendedFoods/lettuce', './sources/recommendedFoods/low-fat-yogurt', './sources/recommendedFoods/mackerel', './sources/recommendedFoods/mushrooms', './sources/recommendedFoods/mustard', './sources/recommendedFoods/olives-and-olive-oil', './sources/recommendedFoods/onions-and-garlic', './sources/recommendedFoods/parsley', './sources/recommendedFoods/pomegranates', './sources/recommendedFoods/pumpkins', './sources/recommendedFoods/raspberries', './sources/recommendedFoods/saffron', './sources/recommendedFoods/salmon', './sources/recommendedFoods/seaweed', './sources/recommendedFoods/soybeans', './sources/recommendedFoods/spinach', './sources/recommendedFoods/tofu', './sources/recommendedFoods/tomatoes', './sources/recommendedFoods/turmeric', './sources/recommendedFoods/turnips-and-turnip-greens', './sources/recommendedFoods/walnuts', './sources/recommendedFoods/watercress', './sources/recommendedFoods/watermelon', './sources/recommendedFoods/zucchini']


def makeFeatureVector(articlePATH):

	# Let's get the file text



def test():

	# Make a feature vector of an article
	articlePATH = './sources/recommendedFoods/apples/A Novel Triterpenoid Isolated from Apple Functions as an Anti-mammary Tumor Agent via a Mitochondrial and Caspase-Indepe.md'

	featureVector = makeFeatureVector(articlePATH)

	print featureVector


def main():

	for directory in directoryList:

		for f in getFiles(directory):

			featureVector = makeFeatureVector(f)

			# Save the feature vector
			print featureVector

		outputLocation = './featureVectors'
		saveFeature



if __name__ == '__main__':
	main()