#!/usr/bin/python
# -*- coding: utf-8 -*-
from xbmcswift2 import Plugin
from ddrk import DDRK


plugin = Plugin()
ddrk = DDRK(plugin)


@plugin.route('/')
def index():
    items = [
        {
            'label': u'热映中',
            'path': plugin.url_for('show_airing'),
        },
        {
            'label': u'站长推荐',
            'path': plugin.url_for('show_recommend'),
        },
        {
            'label': u'剧集',
            'path': plugin.url_for('show_dramas'),
        },
        {
            'label': u'电影',
            'path': plugin.url_for('show_movies'),
        },
    ]

    return items


@plugin.cached_route('/airing')
def show_airing():
    return ddrk.get_airing()

@plugin.cached_route('/recommend')
def show_recommend():
    return ddrk.get_recommend()

@plugin.route('/dramas')
def show_dramas():
    items = [
        {
            'label': u'欧美剧',
            'path': plugin.url_for('show_category_first', main='drama', sub='western-drama')
        },
        {
            'label': u'日剧',
            'path': plugin.url_for('show_category_first', main='drama', sub='jp-drama')
        },
        {
            'label': u'韩剧',
            'path': plugin.url_for('show_category_first', main='drama', sub='kr-drama')
        },
        {
            'label': u'华语剧',
            'path': plugin.url_for('show_category_first', main='drama', sub='cn-drama')
        },
        {
            'label': u'其他地区',
            'path': plugin.url_for('show_category_first', main='drama', sub='other')
        },
    ]

    return items

@plugin.route('/movies')
def show_movies():
    items = [
        {
            'label': u'全部',
            'path': plugin.url_for('show_category_all_first', main='movie')
        },
        {
            'label': u'欧美电影',
            'path': plugin.url_for('show_category_first', main='movie', sub='western-movie')
        },
        {
            'label': u'日韩电影',
            'path': plugin.url_for('show_category_first', main='movie', sub='asian-movie')
        },
        {
            'label': u'华语电影',
            'path': plugin.url_for('show_category_first', main='movie', sub='chinese-movie')
        },
        {
            'label': u'豆瓣电影 Top250',
            'path': plugin.url_for('show_tag', tag='douban-top250', page='1')
        },
    ]

    return items

@plugin.cached_route('/category/<main>', name='show_category_all_first')
@plugin.cached_route('/category/<main>/<page>', name='show_category_all')
@plugin.cached_route('/category/<main>/<sub>', name='show_category_first')
@plugin.cached_route('/category/<main>/<sub>/<page>')
def show_category(main, sub='', page='1'):
    page = int(page)
    items, next_page = ddrk.get_category(main, sub, page)

    if page > 1:
        items.insert(0, {
            'label': u'<< 上一页',
            'path': plugin.url_for('show_category', main=main, sub=sub, page=str(page - 1))
        })

    if next_page:
        items.append({
            'label': u'下一页 >>',
            'path': plugin.url_for('show_category', main=main, sub=sub, page=str(page + 1))
        })

    return items

@plugin.cached_route('/tag/<tag>/<page>')
def show_tag(tag, page='1'):
    page = int(page)
    items, next_page = ddrk.get_tag(tag, page)

    if page > 1:
        items.insert(0, {
            'label': u'<< 上一页',
            'path': plugin.url_for('show_tag', tag=tag, page=str(page - 1))
        })

    if next_page:
        items.append({
            'label': u'下一页 >>',
            'path': plugin.url_for('show_tag', tag=tag, page=str(page + 1))
        })

    return items

@plugin.route('/detail/<name>')
def show_detail(name):
    items = ddrk.get_detail(name)
    return items


@plugin.route('/play')
def play():
    args = {}

    for attr, value in plugin.request.args.iteritems():
        args[attr] = value[0]

    url = ddrk.get_play_url(args)
    return plugin.set_resolved_url(url)


if __name__ == '__main__':
    plugin.run()
