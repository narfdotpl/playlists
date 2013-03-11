#!/usr/bin/env python
# encoding: utf-8

from __future__ import absolute_import, division
import json
from os.path import dirname, join, realpath

from BeautifulSoup import BeautifulSoup
import requests


CURRENT_DIR = dirname(realpath(__file__))
REPO_ROOT_DIR = CURRENT_DIR
README_PATH = join(REPO_ROOT_DIR, 'README.md')
COMPUTER_DUMP_PATH = join(REPO_ROOT_DIR, 'for_computers.json')
HUMAN_DUMP_PATH = join(REPO_ROOT_DIR, 'for_humans.md')


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
    http_url = 'http://ws.spotify.com/lookup/1/.json?uri=' + spotify_uri
    return json.loads(requests.get(http_url).text)['track']


def _main():
    # get playlist URIs
    playlist_uris = []
    with open(COMPUTER_DUMP_PATH) as f:
        for dct in json.load(f):
            playlist_uris.append(dct['uri'])

    # get playlist data
    computer_dump = []
    for uri in playlist_uris:
        data = download_playlist_data(uri)
        computer_dump.append(data)

    # get track data and remove "track_uris" key
    for dct in computer_dump:
        tracks = dct['tracks'] = []
        for uri in dct.pop('track_uris'):
            data = download_track_data(uri)
            tracks.append(data)

    # save file for computers
    with open(COMPUTER_DUMP_PATH, 'w') as f:
        json.dump(computer_dump, f, sort_keys=True, indent=4)

    # save file for humans
    with open(HUMAN_DUMP_PATH, 'w') as f:
        for i, playlist in enumerate(computer_dump):
            # separate playlists
            if i > 0:
                f.write('\n\n')

            # write linkified playlist title
            f.write('[%s](%s)\n%s\n\n' \
                % (playlist['name'], playlist['http_url'],
                   '-' * (len(playlist['name']) + 2)))

            for j, track in enumerate(playlist['tracks'], start=1):
                # write track number
                f.write('%d. ' % j)

                # write artists
                f.write(', '.join(x['name'] for x in track['artists']))

                # write separator
                f.write(' - ')

                # write title
                f.write(track['name'] + '\n')

    # read README up to mixtapes list
    readme = ''
    with open(README_PATH) as f:
        for line in f:
            if line.startswith('1.'):
                break
            else:
                readme += line

    # add mixtapes list to README
    for i, dct in enumerate(computer_dump, start=1):
        readme += '%d. [%s](%s)\n' % (i, dct['name'], dct['http_url'])

    # save README
    with open(README_PATH, 'w') as f:
        f.write(readme)


if __name__ == '__main__':
    _main()
