import argparse

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


def import_mapbox(subparsers):
    pass


def main():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(help='sub-command help')
    create_tileset(subparsers)

    args = parser.parse_args()

    try:
        func = args.func
    except AttributeError:
        args.print_help()
    else:
        func(args)
