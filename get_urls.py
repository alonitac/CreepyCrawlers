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

cwd = os.getcwd()
url_base = 'https://www.kickstarter.com/discover/advanced?state=live&category_id=16&sort=magic&seed=2568337&page='

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
        seconds = 120
        print('wait for', seconds, 'seconds, then continue to page', page , datetime.datetime.now())
        rest(seconds=seconds)
    return(url_list)

def rest(seconds):
    x = seconds/10
    for t in range(0,10):
        bar = '[' + '-'*(t+1) + ' '*(9-t) + ']'
        print(bar + '   ' + str((t+1)*10) + ' %') 
        time.sleep(x)

# url_list = get_urls(url_base, 25)

# url_ser  = pd.Series( (e for e in url_list))

# url_ser.to_pickle(cwd + '/data/urls.pkl')
# to load 
url_ser = pickle.load(open('urls.pkl', 'rb'))   # pandas Series
print(url_ser)
