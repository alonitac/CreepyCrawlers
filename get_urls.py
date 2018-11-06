#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: franzi
"""

import requests
from bs4 import BeautifulSoup
import os
import re
import datetime
import time
import pickle
import pandas as pd
import json

cwd = os.getcwd()
url_base = 'https://www.kickstarter.com/discover/advanced?state=live&category_id=16&sort=magic&seed=2568337&page='


classes_identifiers = {
    'Author': ['a', 'm0 p0 medium soft-black type-14 pointer keyboard-focusable'],
    'Title': ['h2', 'type-24 type-28-sm type-38-md navy-700 medium mb3'],
    'DolarsPelged': ['span', 'ksr-green-700'],
    'DollarsGoal': ['span', 'money'],
    'NumBackers': ['div', 'block type-16 type-24-md medium soft-black'],
    'DaysToGo': ['span', 'block type-16 type-24-md medium soft-black'],
    'AllOrNothing': ['p', 'mb3 mb0-lg type-12'],
}

reward_class_identifiers = {
    'Text': ['h3', 'pledge__title'],
    'Price': ['span', 'money'],
    'NumBackers': ['span', 'pledge__backer-count'],
    'TotalPossibleBackers': ['span', 'pledge__limit'],
}


def get_urls(url_base, max_pages):
    page = 1
    url_list = list()
    
    while page <= max_pages:
        url = url_base + str(page)
        print('-------------- load', url, ' --------------')
        html = requests.get(url)              # load page
        soup = BeautifulSoup(html.text)       # create BeautifulSoup object
        for box in soup.findAll(attrs={'class': 'js-react-proj-card col-full col-sm-12-24 col-lg-8-24'}):   #every box (12 per page)
            box  = re.sub('&quot;', '\"', str(box))    #sometimes translated incorrectly, findall didn't work
            link = re.findall(r'web":{"project":"(.*)",', str(box))[0]
            url_list.append(link)
        print('len(url_list) = ', len(url_list))
        
        #save progress as txt-file
        file = open(cwd + '/data/url_list'+str(page)+'.txt', 'w')
        file.write(str(url_list))
        file.close()
        
        #wait 1 minute
        page    = page + 1
        seconds = 5
        print('wait for', seconds, 'seconds, then continue to page', page , datetime.datetime.now())
        rest(seconds=seconds)
    return(url_list)


def rest(seconds):
    x = seconds/10
    for t in range(0,10):
        bar = '[' + '-'*(t+1) + ' '*(9-t) + ']'
        print(bar + '   ' + str((t+1)*10) + ' %') 
        time.sleep(x)


def parseHTMLtoJSON():
    records = {
        'records': {
            'record': []
        }
    }

    id = 1

    # iterate over urls
    for url in url_ser:
        html = requests.get(url)
        soup = BeautifulSoup(html.text)
        rec = {
            'id': id,
            'url': url,
            # 'text': html.text
        }

        # iterate over fields and parse them in the html
        for field, params in classes_identifiers.items():
            x = soup.find(params[0], attrs=params[1])
            rec[field] = x.string

        rec['rewards'] = []
        itr_rewards = iter(soup.findAll('div', attrs={'class': 'pledge__info'}))
        next(itr_rewards)
        for reward in itr_rewards:
            reward_dict = {}
            for field, params in reward_class_identifiers.items():
                x = reward.find(params[0], attrs=params[1])
                if field == 'TotalPossibleBackers' and x is None:
                    continue
                reward_dict[field] = x.string.strip()
            rec['rewards'].append(reward_dict)

        # save record
        records['records']['record'].append(rec)
        id += 1
        with open('data/data.json', 'w') as f:
            json.dump(records, f, ensure_ascii=False, indent=4)
        time.sleep(1)


if __name__ == '__main__':
    # url_list = get_urls(url_base, 25)
    # url_ser  = pd.Series( (e for e in url_list))
    # url_ser.to_pickle(cwd + '/data/urls_6-11.pkl')
    # to load
    url_ser = pickle.load(open('data/urls_6-11.pkl', 'rb'))   # pandas Series
    parseHTMLtoJSON()
