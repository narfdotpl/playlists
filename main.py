#!/usr/bin/env python
# encoding: utf-8

from __future__ import absolute_import, division
from cgi import escape
import codecs
import json
from os.path import dirname, join, realpath

import requests

import spotify


CURRENT_DIR = dirname(realpath(__file__))
REPO_ROOT_DIR = CURRENT_DIR
README_PATH = join(REPO_ROOT_DIR, 'README.md')
COMPUTER_FILE_PATH = join(REPO_ROOT_DIR, 'for_computers.json')
HUMAN_FILE_PATH = join(REPO_ROOT_DIR, 'for_humans.md')


def open(path, mode='r'):
    return codecs.open(path, encoding='utf-8', mode=mode)


def authorize(user=spotify.client_id, password=spotify.client_secret):
    return requests.post(
        'https://accounts.spotify.com/api/token',
        auth=(user, password),
        data={'grant_type': 'client_credentials'}).json()['access_token']


def download_playlist(access_token, url):
    return requests.get(url,
        headers={'Authorization': 'Bearer ' + access_token}).json()


def read_playlist_urls(file_path=COMPUTER_FILE_PATH):
    return [pl['href'] for pl in read_file_for_computers(file_path)]


def read_file_for_computers(file_path=COMPUTER_FILE_PATH):
    with open(file_path) as f:
        return json.load(f)


def save_file_for_computers(playlists, file_path=COMPUTER_FILE_PATH):
    with open(file_path, 'w') as f:
        # create json string
        json_string = json.dumps(playlists, sort_keys=True, indent=4)

        # remove trailing whitespace and save
        f.write('\n'.join(x.rstrip() for x in json_string.split('\n')))


def save_file_for_humans(playlists, file_path=HUMAN_FILE_PATH):
    with open(file_path, 'w') as f:
        write = lambda s: f.write(escape(s))

        for i, playlist in enumerate(playlists):
            # separate playlists
            if i > 0:
                write('\n\n')

            # write linkified playlist title
            write('[%s](%s)\n%s\n\n' \
                % (playlist['name'], playlist['external_urls']['spotify'],
                   '-' * (len(escape(playlist['name'])) + 2)))

            for item in playlist['tracks']['items']:
                track = item['track']

                # write track number
                write('1. ')

                # write artists
                write(', '.join(x['name'] for x in track['artists']))

                # write separator
                write(' - ')

                # write title
                write(track['name'] + '\n')


def save_readme(playlists, file_path=README_PATH):
    # read README up to mixtapes list
    readme = ''
    with open(file_path) as f:
        for line in f:
            if line.startswith('1.'):
                break
            else:
                readme += line

    # add mixtapes list to README
    for playlist in playlists:
        readme += '1. [%s](%s)\n' % (playlist['name'],
                                     playlist['external_urls']['spotify'])

    # save README
    with open(file_path, 'w') as f:
        f.write(escape(readme))


def _main():
    token = authorize()
    playlists = map(lambda url: download_playlist(token, url),
                    read_playlist_urls())

    save_file_for_computers(playlists)
    save_file_for_humans(playlists)
    save_readme(playlists)


if __name__ == '__main__':
    _main()
