from collections import defaultdict
import io
import os
from pathlib import Path

import flask

from .mbtiles import Tileset

app = flask.Flask(__name__)


if 'CARTOGRAPHER_TILES_PATH' in os.environ:
    app.config['TILES_PATH'] = os.environ['CARTOGRAPHER_TILES_PATH']


HTML = """
<!DOCTYPE html>
<html lang="en">

    <head>
        <meta charset="UTF-8" />

        <title>{tileset} - Tileset</title>

        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
        <meta http-equiv="X-UA-Compatible" content="IE=Edge" />

        <link rel="stylesheet" href="//cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/leaflet.css" />

        <script src="//cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/leaflet.js"></script>

        <style>
            html, body, #map {{
                width: 100%;
                height: 100%;
                margin: 0;
                padding: 0;
            }}
        </style>
    </head>

    <body>
        <div id="map"></div>

        <script>
            var map = L.map("map", {{
                center: [49.2, -9],
                zoom: 13,
            }});

            L.tileLayer("/{tileset}/{{z}}/{{x}}/{{y}}", {{
                maxZoom: 19,
            }}).addTo(map);
        </script>
    </body>

</html>
"""

MAPS = defaultdict(list)


@app.before_first_request
def load_tiles():
    path = Path(app.config['TILES_PATH'])
    for p in path.glob('*.mbtiles'):
        tileset = Tileset(str(p))
        name = tileset.name

        app.logger.info('Registering tileset: {} ({})'.format(name, p))
        for zoom_level in tileset.zoom_levels:
            app.logger.info(' - Zoom level: {}'.format(zoom_level))
            MAPS[(name, zoom_level)].append(tileset)


def find_tile(name, zoom, row, col):
    tilesets = MAPS[(name, zoom)]
    ncol = (2 ** zoom) - 1 - col

    for tileset in tilesets:
        try:
            return tileset[(zoom, row, ncol)], tileset
        except KeyError:
            pass

    raise KeyError('No such tile.')


@app.route('/<name>')
def serve_map(name):
    return HTML.format(tileset=name)


@app.route('/<name>/<int:zoom>/<int:row>/<int:col>')
def serve_tile(name, zoom, row, col):
    try:
        tile, tileset = find_tile(name, zoom, row, col)
    except KeyError:
        flask.abort(404)
    else:
        stream = io.BytesIO(tile)
        return flask.send_file(stream, mimetype=tileset.mime_type)


if __name__ == "__main__":
    app.run()
