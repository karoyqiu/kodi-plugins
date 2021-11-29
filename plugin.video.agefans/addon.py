#!/usr/bin/python
# -*- coding: utf-8 -*-
from xbmcswift2 import Plugin
from agefans import Agefans


plugin = Plugin()


def add_page_ctrl(items, page, more, func):
    if page > 0:
        items.insert(0, {
            'label': u'<< 上一页',
            'path': plugin.url_for(func, page=str(page - 1))
        })

    if more:
        items.append({
            'label': u'下一页 >>',
            'path': plugin.url_for(func, page=str(page + 1))
        })

    return items


@plugin.route('/')
def index():
    items = [
        {
            'label': u'排行榜',
            'path': plugin.url_for('show_rank', page='0'),
        },
        {
            'label': u'推荐',
            'path': plugin.url_for('show_recommend', page='0'),
        },
        {
            'label': u'搜索',
            'path': plugin.url_for('search', keyword='null', page='0'),
        },
    ]

    return items


@plugin.route('/rank/<page>/')
def show_rank(page='0'):
    page = int(page)
    agefans = Agefans(plugin)
    items, more = agefans.get_rank(page, 'show_detail')
    items = add_page_ctrl(items, page, more, 'show_rank')
    return plugin.finish(items, update_listing=True)


@plugin.route('/recommend/<page>/')
def show_recommend(page='0'):
    page = int(page)
    agefans = Agefans(plugin)
    items, more = agefans.get_recommend(page, 'show_detail')
    items = add_page_ctrl(items, page, more, 'show_recommend')
    return plugin.finish(items, update_listing=True)


@plugin.route('/search/<keyword>/<page>/')
def search(keyword, page='0'):
    if keyword == 'null':
        keyboard = xbmc.Keyboard('', '请输入搜索内容')
        xbmc.sleep(1500)
        keyboard.doModal()

        if (keyboard.isConfirmed()):
            keyword = keyboard.getText()

    if keyword == 'null':
        return []

    page = int(page)
    agefans = Agefans(plugin)
    items, more = agefans.search(keyword, page, 'show_detail')

    if page > 0:
        items.insert(0, {
            'label': u'<< 上一页',
            'path': plugin.url_for('search', keyword=keyword, page=str(page - 1))
        })

    if more:
        items.append({
            'label': u'下一页 >>',
            'path': plugin.url_for('search', keyword=keyword, page=str(page + 1))
        })

    return plugin.finish(items, update_listing=True)


@plugin.cached_route('/detail/<aid>/')
def show_detail(aid):
    agefans = Agefans(plugin)
    return agefans.get_detail(aid, 'show_playlist')


@plugin.cached_route('/playlist/<aid>/<index>/')
def show_playlist(aid, index):
    index = int(index)
    agefans = Agefans(plugin)
    return agefans.get_playlist(aid, index)


if __name__ == '__main__':
    print str(sys.argv)
    plugin.run()
