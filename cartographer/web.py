import io

import flask

from .mbtiles import Tileset

app = flask.Flask(__name__)


HTML = """
<!DOCTYPE html>
<html lang="en">

    <head>
        <meta charset="UTF-8" />

        <title>Map</title>

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


@app.route('/<tileset_name>')
def serve_map(tileset_name):
    return HTML.format(tileset=tileset_name)


@app.route('/<tileset_name>/<int:zoom>/<int:row>/<int:col>')
def serve_tile(tileset_name, zoom, row, col):
    tileset = Tileset(tileset_name)

    try:
        ncol = (2 ** zoom) - 1 - col
        tile = tileset[(zoom, row, ncol)]

        stream = io.BytesIO(tile)
        return flask.send_file(stream, mimetype=tileset.mime_type)
    except KeyError:
        flask.abort(404)


if __name__ == "__main__":
    app.run()
