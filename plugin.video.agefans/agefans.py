#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import requests
from urllib2 import unquote


class Agefans(object):
    def __init__(self, plugin):
        self.__baseurl = 'https://api.agefans.app/v2'
        self.__plugin = plugin
        self.__cache = plugin.get_storage('cache')


    def get_rank(self, page, show_detail):
        j = self.__get('/rank?page={0}'.format(page + 1))
        pre = j['AniRankPre']
        items = [self.__pre_to_item(item, show_detail) for item in pre]
        lastNo = pre[len(pre) - 1]['NO']
        return items, j['AllCnt'] > lastNo


    def get_recommend(self, page, show_detail):
        page += 1
        j = self.__get('/recommend?page={0}&size=30'.format(page))
        pre = j['AniPre']
        items = [self.__pre_to_item(item, show_detail) for item in pre]
        return items, j['AllCnt'] > page * 30


    def search(self, keyword, page, show_detail):
        j = self.__get('/search?page={0}&query={1}'.format(page + 1, keyword))
        pre = j['AniPreL']
        items = []

        for ani in pre:
            item = {}
            item['label'] = ani[u'R动画名称']
            item['path'] = self.__plugin.url_for(show_detail, aid=ani['AID'])
            item['thumbnail'] = ani[u'R封面图小']
            items.append(item)

        return items, j['SeaCnt'] > (page + 1) * 24

    def get_detail(self, aid, show_playlist):
        j = self.__get('/detail/' + aid)
        info = j['AniInfo']
        playlists = info[u'R在线播放All']
        cache = { 'playlists': playlists }
        self.__cache[aid] = cache

        items = []

        for i in range(len(playlists)):
            playlist = playlists[i]
            n = len(playlist)
            if n == 0:
                continue

            item = {}
            item['label'] = u'播放列表 {0}'.format(i + 1)
            item['path'] = self.__plugin.url_for(show_playlist, aid=aid, index=i)
            items.append(item)

        return items


    def get_playlist(self, aid, index):
        playlist = self.__cache[aid]['playlists'][index]
        items = []

        for eps in playlist:
            item = {}
            item['label'] = eps['Title']
            item['path'] = unquote(eps['PlayVid']).decode('utf-8')
            item['is_playable'] = True
            items.append(item)

        return items


    def __get(self, url):
        r = requests.get(self.__baseurl + url)
        return json.loads(r.text)


    def __pre_to_item(self, pre, show_detail):
        thumb = pre['PicSmall']

        if thumb.startswith('//'):
            thumb = 'https:' + thumb

        item = {}
        item['label'] = pre['Title']
        item['path'] = self.__plugin.url_for(show_detail, aid=pre['AID'])
        item['thumbnail'] = thumb

        return item
