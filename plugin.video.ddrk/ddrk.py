#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from xbmcswift2 import xbmc

class DDRK(object):
    def __init__(self, plugin):
        self.__baseurl = 'https://ddrk.me'
        self.__plugin = plugin
        self.__cache = plugin.get_storage('cache')

    def get_airing(self):
        return self.__get('/category/airing')

    @staticmethod
    def __parse_image(style):
        start = style.find('(')
        end = style.find(')', start)
        return style[start + 1:end]


    def __get(self, url):
        r = requests.get(self.__baseurl + url);
        soup = BeautifulSoup(r.text, 'html.parser')
        articles = soup.find_all('article')
        items = []

        for article in articles:
            item = {}
            a = article.find('a', rel='bookmark')
            item['label'] = a.string

            div = article.find('div', class_='post-box-image')
            img = DDRK.__parse_image(div['style'])
            item['icon'] = img
            item['thumbnail'] = img

            href = article['data-href']
            href = href[len(self.__baseurl) + 1:-1]
            item['path'] = self.__plugin.url_for('show_detail', name=href)

            items.append(item)

        return items
