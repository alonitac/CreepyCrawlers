#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: franzi, Alon
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
        page = page + 1
        seconds = 1
        print('wait for', seconds, 'seconds, then continue to page', page , datetime.datetime.now())
        rest(seconds=seconds)
    return url_list


def parseHTMLtoJSON(url, id):
    html = requests.get(url)
    soup = BeautifulSoup(html.text)
    record = {
        'id': id,
        'url': url,
    }

    # iterate over fields and parse them in the html
    for field, (tag, css_attr, convert_type_func) in product_fields.items():
        x = soup.find(tag, attrs=css_attr)
        record[field] = convert_type_func(x)

    record['rewards'] = []
    itr_rewards = iter(soup.findAll('div', attrs={'class': 'pledge__info'}))
    next(itr_rewards)  # exclude the first reward as it's a default one for all pages
    for reward in itr_rewards:
        reward_dict = {}
        for field, (tag, css_attr, convert_type_func) in rewards_fields.items():
            x = reward.find(tag, attrs=css_attr)
            reward_dict[field] = convert_type_func(x)
        record['rewards'].append(reward_dict)

    return record


def crawl(url_ser):
    records = {
        'records': {
            'record': []
        }
    }

    id = 1

    for i, url in enumerate(url_ser):
        print('{}\\ {}: start crawl {}'.format(i, len(url_ser), url))
        # parse record from url
        new_record = parseHTMLtoJSON(url, id)
        id += 1

        # save record
        records['records']['record'].append(new_record)
        time.sleep(1)

    return records


def rest(seconds):
    x = seconds/10
    for t in range(0,10):
        bar = '[' + '-'*(t+1) + ' '*(9-t) + ']'
        print(bar + '   ' + str((t+1)*10) + ' %')
        time.sleep(x)


def to_str(bs_element):
    return bs_element.string.strip()


def to_int(bs_element):
    return int(re.sub(r'[^\d.]', '', to_str(bs_element)))


def to_currency(bs_element):
    return re.sub(r'[\d,. ]', '', to_str(bs_element))


def to_bool(bs_element):
    return bs_element


def to_html_text(bs_element):
    return str(bs_element)


def get_total_possible(bs_element):
    if bs_element is None or to_str(bs_element) == 'Reward no longer available':
        return None
    return re.findall(r'(\d+)', to_str(bs_element))[1]  # take the second number


def is_all_or_nothing(bs_element):
    return bool(re.findall(r'This project will only be funded if it reaches its goal by', to_html_text(bs_element)))


if __name__ == '__main__':
    url_base = 'https://www.kickstarter.com/discover/advanced?state=live&category_id=16&sort=magic&seed=2568337&page='

    product_fields = {
        'Author': ('a', 'm0 p0 medium soft-black type-14 pointer keyboard-focusable', to_str),
        'Title': ('h2', 'type-24 type-28-sm type-38-md navy-700 medium mb3', to_str),
        'Currency': ('span', 'ksr-green-700', to_currency),
        'DolarsPelged': ('span', 'ksr-green-700', to_int),
        'DollarsGoal': ('span', 'money', to_int),
        'NumBackers': ('div', 'block type-16 type-24-md medium soft-black', to_int),
        'DaysToGo': ('span', 'block type-16 type-24-md medium soft-black', to_int),
        'AllOrNothing': ('p', 'mb3 mb0-lg type-12', is_all_or_nothing),
        'Text': ('div', 'col col-8 description-container', to_html_text),
    }

    rewards_fields = {
        'Text': ('h3', 'pledge__title', to_str),
        'Price': ('span', 'money', to_int),
        'NumBackers': ('span', 'pledge__backer-count', to_int),
        'TotalPossibleBackers': ('span', 'pledge__limit', get_total_possible),
    }
    # get 300 urls of open projects
    # or load pkl:
    url_list = pickle.load(open('data/urls.pkl', 'rb'))   # pandas Series
    # url_list = get_urls(url_base, 25)

    # crawl urls to the formatted dictionary
    records = crawl(url_list)

    # save results to json
    url_ser = pd.Series((e for e in url_list))
    url_ser.to_pickle(cwd + '/data/urls2.pkl')
    #
    with open('data/data_with_html.json', 'w') as f:
        json.dump(records, f, ensure_ascii=False, indent=4)
