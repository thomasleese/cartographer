import argparse

from . import importers
from .mbtiles import Tileset


def create_tileset(subparsers):
    def func(args):
        tileset = Tileset(args.filename)
        tileset.name = args.name
        tileset.type = args.type
        tileset.version = args.version
        tileset.description = args.description
        tileset.format = args.format

    parser = subparsers.add_parser('create-tileset')
    parser.add_argument('name')
    parser.add_argument('type')
    parser.add_argument('version')
    parser.add_argument('description')
    parser.add_argument('format')
    parser.add_argument('filename')
    parser.set_defaults(func=func)


def set_metadata(subparsers):
    def func(args):
        tileset = Tileset(args.filename)
        tileset.metadata[args.name] = args.value

    parser = subparsers.add_parser('set-metadata')
    parser.add_argument('filename')
    parser.add_argument('name')
    parser.add_argument('value')
    parser.set_defaults(func=func)


def import_tiles(subparsers):
    def func(args):
        tileset = Tileset(args.filename)

        if args.url == 'osm':
            importer = importers.OpenStreetMapImporter()
        elif args.url == 'satellite':
            importer = importers.SatelliteImporter()
        else:
            importer = importers.Importer(args.url)

        for x in range(2 ** args.zoom_level):
            for y in range(2 ** args.zoom_level):
                print('Importing:', args.zoom_level, x, y)
                importer(tileset, args.zoom_level, x, y)

    parser = subparsers.add_parser('import-tiles')
    parser.add_argument('filename')
    parser.add_argument('url')
    parser.add_argument('zoom_level', type=int)
    parser.set_defaults(func=func)


def extract_tile(subparsers):
    def func(args):
        tileset = Tileset(args.filename)

        tile = tileset.tiles[(args.zoom_level, args.row, args.col)]

        with open('tile.{}'.format(tileset.format), 'wb') as file:
            file.write(tile)

    parser = subparsers.add_parser('extract-tile')
    parser.add_argument('filename')
    parser.add_argument('zoom_level', type=int)
    parser.add_argument('row', type=int)
    parser.add_argument('col', type=int)
    parser.set_defaults(func=func)


def main():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(help='sub-command help')
    create_tileset(subparsers)
    import_tiles(subparsers)
    set_metadata(subparsers)
    extract_tile(subparsers)

    args = parser.parse_args()

    try:
        func = args.func
    except AttributeError:
        args.print_help()
    else:
        func(args)
