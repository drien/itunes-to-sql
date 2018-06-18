#!/usr/bin/env python3

import argparse
import plistlib
import sqlite3


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
    library = plistlib.load(args.library)

    tracks_table, tracks = process_tracks(library)
    playlists_table, playlist_itms_table, playlists = process_playlists(library)

    conn = sqlite3.connect(args.db)
    conn.execute(tracks_table)
    conn.execute(playlists_table)
    conn.execute(playlist_itms_table)

    for query in tracks + playlists:
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

    all_keys = list(map(slugify, all_keys))

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
            ', '.join(['?'] * len(values))
        ),
        [value for value in values]
    )


def slugify(name):
    return name.lower().replace(' ', '_')


if __name__ == '__main__':
    main()
