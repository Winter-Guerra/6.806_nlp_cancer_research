
from shovel import task

import glob
import random
import os
from bs4 import BeautifulSoup
import datetime
import re
import requests
# Import C yaml bindings
import yaml
try:
	from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
	from yaml import Loader, Dumper

@task
def reduceTo100Files(directory, probability):
	for file in glob.iglob(directory+'*.md'):

		shouldDelete = (random.random() <= float(probability))

		if shouldDelete:
			os.remove(file)
