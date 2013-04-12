#!/usr/bin/env python
# encoding: utf-8

from __future__ import absolute_import, division
import json

from dump import COMPUTER_DUMP_PATH


def get_playlists(json_path=COMPUTER_DUMP_PATH):
    with open(json_path) as f:
        return json.load(f)


def create_tweet(playlist):
    return 'New mixtape: %s\n%s\nhttps://github.com/narfdotpl/mixtapes' % \
           (playlist['name'], playlist['http_url'])


def _main():
    print create_tweet(get_playlists()[-1])

if __name__ == '__main__':
    _main()
