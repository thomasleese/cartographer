import argparse
from pathlib import Path

from . import boundaries, importers
from .mbtiles import Tileset


def create_tileset(subparsers):
    def func(args):
        if args.description is None:
            args.description = args.name

        tileset = Tileset(args.filename, create=True)
        tileset.name = args.name
        tileset.type = args.type
        tileset.version = args.version
        tileset.description = args.description
        tileset.format = args.format

    parser = subparsers.add_parser('create-tileset')
    parser.add_argument('filename')
    parser.add_argument('name')
    parser.add_argument('--type', '-t', default='baselayer')
    parser.add_argument('--version', '-v', type=int, default=0)
    parser.add_argument('--description', '-d', default=None)
    parser.add_argument('--format', '-f', default='png')
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


def set_boundary(subparsers):
    def func(args):
        tileset = Tileset(args.filename)
        boundary = getattr(boundaries, args.boundary)
        tileset.boundary = boundary

    parser = subparsers.add_parser('set-boundary')
    parser.add_argument('filename')
    parser.add_argument('boundary')
    parser.set_defaults(func=func)


def import_tiles(subparsers):
    def func(args):
        tileset = Tileset(args.filename)

        if args.url == 'osm':
            importer = importers.OpenStreetMap()
        elif args.url == 'satellite':
            importer = importers.Satellite()
        elif args.url == 'mapquest':
            importer = importers.MapQuest()
        elif args.url.startswith('os:'):
            key = args.url[3:]
            print(key)
            importer = importers.OrdnanceSurvey(key)
        else:
            importer = importers.Importer(args.url)

        boundary = None
        if args.boundary:
            boundary = getattr(boundaries, args.boundary)

        for zoom in args.zoom_level:
            importer(tileset, zoom, boundary)

    parser = subparsers.add_parser('import-tiles')
    parser.add_argument('filename')
    parser.add_argument('url')
    parser.add_argument('zoom_level', type=int, nargs='+')
    parser.add_argument('--boundary')
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


def extract_all(subparsers):
    def func(args):
        tileset = Tileset(args.filename)

        for zoom_level, col, row, data in tileset:
            path = Path(args.target) / str(zoom_level) / str(col)
            path.mkdir(parents=True, exist_ok=True)

            path = path / '{row}.{format}'.format(row=row, format=tileset.format)

            if path.exists():
                continue

            print(path)

            with path.open('wb') as file:
                file.write(data)

    parser = subparsers.add_parser('extract-all')
    parser.add_argument('filename')
    parser.add_argument('target')
    parser.set_defaults(func=func)


def web(subparsers):
    def func(args):
        from .web import app
        app.config['TILES_PATH'] = args.tiles
        app.run(debug=True)

    parser = subparsers.add_parser('web')
    parser.add_argument('tiles', default='tiles')
    parser.set_defaults(func=func)


def main():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(help='sub-command help')
    create_tileset(subparsers)
    import_tiles(subparsers)
    set_metadata(subparsers)
    set_boundary(subparsers)
    extract_tile(subparsers)
    extract_all(subparsers)
    web(subparsers)

    args = parser.parse_args()

    try:
        func = args.func
    except AttributeError:
        args.print_help()
    else:
        func(args)
