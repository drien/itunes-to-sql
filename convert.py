#!/usr/bin/env python3

import argparse
import os
import plistlib
import sqlite3
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--library',
                        help='Path to XML library file',
                        type=argparse.FileType('rb'),
                        default='./Library.xml')
    parser.add_argument('--db',
                        help='Path to SQLite DB file',
                        default='itunes.db')

    args = parser.parse_args()

    if os.path.exists(args.db):
        response = input(f'{args.db} already exists. Do you want to overwrite? (y/n): ')
        if response.lower() != 'y':
            sys.exit()
        else:
            os.remove(args.db)

    library = plistlib.load(args.library)

    create_tracks_tbl, insert_tracks = process_tracks(library)
    create_playlists_tbl, create_playlist_items_tbl, insert_playlists = process_playlists(library)

    conn = sqlite3.connect(args.db)
    conn.execute(create_tracks_tbl)
    conn.execute(create_playlists_tbl)
    conn.execute(create_playlist_items_tbl)

    for query in insert_tracks + insert_playlists:
        conn.execute(query[0], list(query[1]))

    conn.commit()
    conn.close()


def process_tracks(library):
    all_keys = set()
    inserts = []

    for track_id in library['Tracks'].keys():
        track = library['Tracks'][track_id]

        track_keys = list(map(slugify, track.keys()))
        track_values = track.values()

        all_keys = all_keys.union(set(track_keys))

        inserts.append(get_parameterized('tracks', track_keys, track_values))

    return "CREATE TABLE tracks ({0})".format(', '.join(all_keys)), inserts


def process_playlists(library):
    all_keys = set()
    inserts = []

    for playlist in library['Playlists']:
        try:
            track_ids = playlist['Playlist Items']
            del playlist['Playlist Items']
        except KeyError as e:
            track_ids = []

        playlist_keys = list(map(slugify, playlist.keys()))
        playlist_values = playlist.values()

        all_keys = all_keys.union(set(playlist_keys))

        inserts.append(get_parameterized(
            'playlists', playlist_keys, playlist_values)
        )

        for track in track_ids:
            inserts.append(get_parameterized(
                'playlist_items',
                ['playlist_id', 'track_id'],
                [playlist['Playlist ID'], track['Track ID']]
            ))

    playlists_table = "CREATE TABLE playlists ({0})".format(
        ', '.join(all_keys)
    )
    items_table = 'CREATE TABLE playlist_items (playlist_id, track_id)'

    return playlists_table, items_table, inserts


def get_parameterized(table, keys, values):
    return (
        "INSERT INTO {} ({}) VALUES ({})".format(
            table,
            ', '.join(map(str, keys)),
            ', '.join('?' * len(values))
        ),
        [value for value in values]
    )


def slugify(name):
    return name.lower().replace(' ', '_')


if __name__ == '__main__':
    main()
