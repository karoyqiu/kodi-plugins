#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import json
import requests
import tempfile
import zlib
from bs4 import BeautifulSoup
from base64 import b64encode
from urllib2 import quote
from xbmcswift2 import xbmc
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

epoch = datetime.datetime.utcfromtimestamp(0)
ukey = b'zevS%th@*8YWUm%K'
iv = b'5080305495198718'


def aes(obj):
    s = json.dumps(obj)
    cipher = AES.new(ukey, AES.MODE_CBC, iv=iv)
    enc = cipher.encrypt(pad(s.encode('UTF-8'), AES.block_size))
    return b64encode(enc).decode('UTF-8')


def ddr(dd):
    key = dd[:16]
    enc = dd[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv=key)
    dec = cipher.decrypt(pad(enc, AES.block_size))
    uz = zlib.decompress(dec, 47)
    return uz


class DDRK(object):
    def __init__(self, plugin):
        self.__baseurl = 'https://ddrk.me'
        self.__plugin = plugin
        self.__zimuoss = 'https://ddrk.oss-accelerate.aliyuncs.com'
        self.__s = requests.Session()
        self.__cf = ''

    # 类别
    def get_category(self, main, sub, page):
        path = '/category/' + main + '/'

        if (sub != ''):
            path = path + sub + '/'

        if (page > 1):
            path = path + 'page/' + str(page) + '/'

        soup = self.__get(path)
        items = self.__parse_articles(soup)
        next_page = DDRK.__parse_next_page(soup)
        return items, next_page

    # 标签
    def get_tag(self, tag, page):
        path = '/tag/' + tag + '/'

        if (page > 1):
            path = path + 'page/' + str(page) + '/'

        soup = self.__get(path)
        items = self.__parse_articles(soup)
        next_page = DDRK.__parse_next_page(soup)
        return items, next_page

    # 获取剧集播放列表
    def get_detail(self, name, page):
        path = '/' + name + '/'

        if (page != 1):
            path = path + str(page) + '/'

        soup = self.__get(path)
        self.__get('/cdn-cgi/challenge-platform/h/g/cv/result/' + self.__cf)
        return self.__parse_playlist(name, soup)

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
        suburl = None

        if 'subsrc' in args:
            subsrc = args['subsrc']

            if subsrc:
                r = self.__s.get(self.__zimuoss + subsrc)

                if r.status_code == 200:
                    sub = ddr(r.content)
                    t = tempfile.NamedTemporaryFile(delete=False)
                    t.write(sub)
                    suburl = t.name

        return url, suburl

    def __get_video_url_0(self, args):
        # obj = {}
        # obj['path'] = args['src0']
        # obj['expire'] = '{:.0f}'.format(
        #     ((datetime.datetime.now() - epoch).total_seconds() + 600) * 1000)
        # vid = quote(aes(obj))
        vid = args['src1']
        url = 'https://ddrk.me/getvddr/video?id=' + vid + '&type=mix'
        r = self.__s.get(url)
        print(r.text)
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
            item['path'] = self.__plugin.url_for(
                'show_detail', name=href, page='1')

            items.append(item)

        return items

    @staticmethod
    def __parse_next_page(soup):
        # type (BeautifulSoup) -> bool
        node = soup.find('a', class_='next')
        return node != None

    def __parse_playlist(self, name, soup):
        script = soup.find('script', class_='wp-playlist-script')
        j = json.loads(script.string)
        tracks = j['tracks']
        items = [self.__track_to_item(track) for track in tracks]

        links = soup.find('div', class_='page-links')

        if links:
            prefix = links.contents[0].string
            n = prefix.find(':')
            prefix = prefix[:n]

            link_items = [self.__page_link_to_item(name, prefix, a)
                          for a in links.find_all('a')]
            items = items + link_items

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
                                             src3=track['src3'],
                                             subsrc=track['subsrc'])
        return item

    def __page_link_to_item(self, name, prefix, link):
        item = {}
        page = link['href'].split('/')[-2]

        if (not page.isdigit()):
            page = '1'

        item['label'] = prefix + ': ' + link.string
        item['path'] = self.__plugin.url_for(
            'show_detail', name=name, page=page)
        return item

    # 获取网页 soup
    def __get(self, url):
        headers = {}

        if (self.__cf):
            headers['cf-ray'] = self.__cf

        r = self.__s.get(self.__baseurl + url, headers=headers)
        cf = r.headers.get('cf-ray')

        if (cf):
            self.__cf = cf[:-4]

        return BeautifulSoup(r.text, 'html.parser')
