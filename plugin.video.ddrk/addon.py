#!/usr/bin/python
# -*- coding: utf-8 -*-
from xbmcswift2 import Plugin
from ddrk import DDRK


plugin = Plugin()
ddrk = DDRK(plugin)


@plugin.route('/')
def index():
    items = [{
        'label': u'热映中',
        'path': plugin.url_for('show_airing'),
    }]

    return items


@plugin.route('/airing')
def show_airing():
    items = ddrk.get_airing()
    return items


@plugin.route('/detail/<name>/')
def show_detail(name):
    print('Show ' + name)
    return []


if __name__ == '__main__':
    plugin.run()
