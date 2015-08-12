# This file helps increase scrape rate using randomized user agents

# from shovel import task
import requests
import random
from urllib.parse import urlparse

import redis
import pickle

# Connect to the cache
r = redis.StrictRedis(host='localhost', port=6379, db=0)

def LoadUserAgents(uafile):
    """
    uafile : string
        path to text file of user agents, one per line
    """
    uas = []
    with open(uafile, 'rb') as uaf:
        for ua in uaf.readlines():
            if ua:
                uas.append(ua.strip()[1:-1-1])
    random.shuffle(uas)
    return uas

# load the user agents, in random order
user_agents = LoadUserAgents("./user_agents.txt")
# user_agents = ['a', 'b']

# @task
def get(url, ignoreFailure=False):

    # Sanitize the url
    url = urlparse(url, 'http').geturl()

    # Check if the cache has our data
    cacheResponse = r.get(url)
    if cacheResponse is not None:
        response = pickle.loads(cacheResponse)
        if (response.status_code < 400) or (response.status_code == 404) or ignoreFailure:
            print("URL cache hit")
            return response
        else:
            print("BAD CACHE HIT")
    else:

        # CACHE MISS.
        print("URL cache miss")

    # Prepare the download the data
    ua = random.choice(user_agents)
    headers = {
    "Connection" : "close",  # another way to cover tracks
    "User-Agent" : ua}

    response = requests.get(url, headers=headers)

    # save the request in the cache if the response is sane
    if (response.status_code < 400) or (response.status_code == 404) or ignoreFailure:
        dataToCache = pickle.dumps(response)
        r.set(url, dataToCache)

    return response
