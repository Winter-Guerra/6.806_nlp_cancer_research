# This file helps increase scrape rate using randomized user agents

# from shovel import task
import requests
import random

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
def get(url):
    # user_agents = ['a', 'b']

    ua = random.choice(user_agents)
    headers = {
    "Connection" : "close",  # another way to cover tracks
    "User-Agent" : ua}

    # print(ua)

    try:
        r = requests.get(url, headers=headers)
    except:
        returnObj = lambda: None
        returnObj.text = ''
        returnObj.json = lambda: None
        return returnObj
    else:
        return r
