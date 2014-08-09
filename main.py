#!/usr/bin/env python
# encoding: utf-8

from __future__ import absolute_import, division
import codecs
import json
from os.path import dirname, join, realpath
from time import sleep

from BeautifulSoup import BeautifulSoup
import requests


CURRENT_DIR = dirname(realpath(__file__))
REPO_ROOT_DIR = CURRENT_DIR
README_PATH = join(REPO_ROOT_DIR, 'README.md')
COMPUTER_FILE_PATH = join(REPO_ROOT_DIR, 'for_computers.json')
HUMAN_FILE_PATH = join(REPO_ROOT_DIR, 'for_humans.md')


def open(path, mode='r'):
    return codecs.open(path, encoding='utf-8', mode=mode)


def download_playlist_data(spotify_uri):
    """
    return {
        "name": "Foo Bar Baz",
        "uri": "spotify:user:1:playlist:1",
        "http_url": "http://open.spotify.com/user/1/playlist/1",
        "track_uris": [
            "spotify:track:1",
            "spotify:track:2"
        ]
    }
    """

    # get HTTP URL
    http_url = spotify_uri.replace(':', '/'). \
                           replace('spotify', 'http://open.spotify.com')

    # download HTML
    html = requests.get(http_url).text

    # extract title
    soup = BeautifulSoup(html)
    playlist_title = soup.find('title').text.split(' by ')[0]

    # extract track URIs
    track_uris = []
    for a in soup.findAll('a'):
        href = a['href']
        if href.startswith('/track/'):
            track_uri = 'spotify:track:' + href.split('/')[-1]
            if track_uri not in track_uris:
                track_uris.append(track_uri)

    return {
        'name': playlist_title,
        'uri': spotify_uri,
        'http_url': http_url,
        'track_uris': track_uris,
    }


def download_track_data(spotify_uri):
    url = 'http://ws.spotify.com/lookup/1/.json?uri=' + spotify_uri

    # download until status code is 200
    response = requests.get(url)
    while response.status_code != 200:
        print '-' * 80
        print 'URL:', url
        print 'status code:', response.status_code
        print
        print response.text

        sleep(1)
        response = requests.get(url)

    # read JSON
    try:
        return json.loads(response.text)['track']
    except ValueError as exception:
        print response.text
        print

        raise exception


def read_playlist_uris(file_path=COMPUTER_FILE_PATH):
    return [playlist['uri'] for playlist in read_file_for_computers(file_path)]


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
        for i, playlist in enumerate(playlists):
            # separate playlists
            if i > 0:
                f.write('\n\n')

            # write linkified playlist title
            f.write('[%s](%s)\n%s\n\n' \
                % (playlist['name'], playlist['http_url'],
                   '-' * (len(playlist['name']) + 2)))

            for track in playlist['tracks']:
                # write track number
                f.write('1. ')

                # write artists
                f.write(', '.join(x['name'] for x in track['artists']))

                # write separator
                f.write(' - ')

                # write title
                f.write(track['name'] + '\n')


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
        readme += '1. [%s](%s)\n' % (playlist['name'], playlist['http_url'])

    # save README
    with open(file_path, 'w') as f:
        f.write(readme)


def _main():
    # get playlist data
    playlists = map(download_playlist_data, read_playlist_uris())

    # get track data and remove "track_uris" key
    for pl in playlists:
        pl['tracks'] = map(download_track_data, pl.pop('track_uris'))

    save_file_for_computers(playlists)
    save_file_for_humans(playlists)
    save_readme(playlists)


if __name__ == '__main__':
    _main()
