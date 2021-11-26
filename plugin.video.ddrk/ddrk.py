#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import json
import requests
from bs4 import BeautifulSoup
from base64 import b64encode
from urllib2 import quote
from xbmcswift2 import xbmc
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

epoch = datetime.datetime.utcfromtimestamp(0)
ukey = u'zevS%th@*8YWUm%K'.encode()
iv = u'5080305495198718'.encode()

def aes(obj):
    s = json.dumps(obj)
    cipher = AES.new(ukey, AES.MODE_CBC, iv=iv)
    enc = cipher.encrypt(pad(s.encode('UTF-8'), AES.block_size))
    return b64encode(enc).decode('UTF-8')


class DDRK(object):
    def __init__(self, plugin):
        self.__baseurl = 'https://ddrk.me'
        self.__plugin = plugin
        self.__videoserver = 'https://v3.ddrk.me:19443'


    # 获取“热播中”
    def get_airing(self):
        soup = self.__get('/category/airing')
        return self.__parse_articles(soup)

    # 获取剧集播放列表
    def get_detail(self, name):
        soup = self.__get('/' + name + '/')
        return self.__parse_playlist(soup)

    # 获取视频播放地址
    def get_play_url(self, args):
        methods = {
            '0': self.__get_video_url_0,
            '1': self.__get_video_url_1,
            '3': self.__get_video_url_0,
            '4': self.__get_video_url_4,
        }

        method = methods.get(args['srctype'])
        url = method(args)
        return url


    def __get_video_url_0(self, args):
        obj = {}
        obj['path'] = args['src0']
        obj['expire'] = '{:.0f}'.format(((datetime.datetime.now() - epoch).total_seconds() + 600) * 1000)
        vid = quote(aes(obj))
        url = self.__videoserver + '/video?id=' + vid + '&type=mix'
        r = requests.get(url);
        j = json.loads(r.text)
        return j['url']

    def __get_video_url_1(self, args):
        return 'https://w.ddrk.me' + args['src0'] + '?ddrkey=' + args['src2']

    def __get_video_url_4(self, args):
        return args['src0']

    # 从 style 的 backgroud-image 中分析图片地址
    @staticmethod
    def __parse_image(style):
        start = style.find('(')
        end = style.find(')', start)
        return style[start + 1:end]


    # 分析页面上的剧集列表
    def __parse_articles(self, soup):
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


    def __parse_playlist(self, soup):
        script = soup.find('script', class_='wp-playlist-script')
        j = json.loads(script.string)
        tracks = j['tracks']
        items = [self.__track_to_item(track) for track in tracks]
        return items


    def __track_to_item(self, track):
        item = {}
        item['label'] = track['caption']
        item['is_playable'] = True
        item['path'] = self.__plugin.url_for('play',
                srctype=track['srctype'],
                src0=track['src0'],
                src1=track['src1'],
                src2=track['src2'],
                src3=track['src3'])
        return item


    # 获取网页 soup
    def __get(self, url):
        r = requests.get(self.__baseurl + url);
        return BeautifulSoup(r.text, 'html.parser')
