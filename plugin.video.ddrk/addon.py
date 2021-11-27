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
            'path': plugin.url_for('show_category_all_first', main='airing'),
        },
        {
            'label': u'站长推荐',
            'path': plugin.url_for('show_tag', tag='recommend', page='1'),
        },
        {
            'label': u'剧集',
            'path': plugin.url_for('show_dramas'),
        },
        {
            'label': u'电影',
            'path': plugin.url_for('show_movies'),
        },
        {
            'label': u'新番',
            'path': plugin.url_for('show_category_first', main='anime', sub='new-bangumi'),
        },
        {
            'label': u'类别',
            'path': plugin.url_for('show_categories'),
        },
    ]

    return items


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


@plugin.route('/categories')
def show_categories():
    items = [
        {
            'label': u'动画',
            'path': plugin.url_for('show_category_all_first', main='anime')
        },
        {
            'label': u'动作',
            'path': plugin.url_for('show_tag', tag='action', page='1')
        },
        {
            'label': u'喜剧',
            'path': plugin.url_for('show_tag', tag='comedy', page='1')
        },
        {
            'label': u'爱情',
            'path': plugin.url_for('show_tag', tag='romance', page='1')
        },
        {
            'label': u'科幻',
            'path': plugin.url_for('show_tag', tag='sci-fi', page='1')
        },
        {
            'label': u'犯罪',
            'path': plugin.url_for('show_tag', tag='crime', page='1')
        },
        {
            'label': u'悬疑',
            'path': plugin.url_for('show_tag', tag='mystery', page='1')
        },
        {
            'label': u'恐怖',
            'path': plugin.url_for('show_tag', tag='horror', page='1')
        },
        {
            'label': u'纪录片',
            'path': plugin.url_for('show_category_all_first', main='documentary')
        },
        {
            'label': u'综艺',
            'path': plugin.url_for('show_category_all_first', main='variety')
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

    url, sub = ddrk.get_play_url(args)
    return plugin.set_resolved_url(url, sub)


if __name__ == '__main__':
    plugin.run()
