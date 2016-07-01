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

    conn = sqlite3.connect('itunes.db')
    conn.execute(tracks_table)

    for query in tracks:
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

        inserts.append(("INSERT INTO tracks ({0}) VALUES ({1})".format(
            ', '.join(track_keys), ', '.join(['?'] * len(track_values))),
            [value for value in track_values]
        ))

    all_keys = list(map(slugify, all_keys))

    return "CREATE TABLE tracks ({0});".format(', '.join(all_keys)), inserts


def slugify(name):
    return name.lower().replace(' ', '_')


if __name__ == '__main__':
    main()
