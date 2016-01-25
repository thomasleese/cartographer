from pathlib import Path
import subprocess
import tempfile

import requests


class Importer:
    def __init__(self, url):
        self.url = url

    def get_tile_url(self, zoom, row, col):
        l = (2 ** zoom) - 1
        nrow = l - row
        ncol = l - col
        return self.url.format(zoom=zoom, row=row, col=col, nrow=nrow,
                               ncol=ncol)

    def compress(self, path, tile_format):
        if tile_format == 'png':
            # TODO add '--skip-if-larger' flag
            command = ['pngquant',
                       '--quality', '40-60',
                       '--output', path,
                       '--speed', '1',
                       '--force',
                       path]

            try:
                subprocess.check_call(command)
            except subprocess.CalledProcessError as e:
                if e.returncode == 98:  # output bigger than input
                    pass
                else:
                    raise
        elif tile_format == 'jpg':
            command = ['jpegoptim',
                       '--max=70',
                       '-q',
                       '--strip-all',
                       path,
                       path]

            subprocess.check_call(command)
        else:
            raise ValueError('Unsupported map format: {}'.format(tile_format))

    def __call__(self, tileset, zoom, row, col):
        key = (zoom, row, col)

        try:
            tileset[key]
        except KeyError:
            pass
        else:
            return

        url = self.get_tile_url(zoom, row, col)
        res = requests.get(url)

        if res.status_code == requests.codes.ok:
            with tempfile.TemporaryDirectory() as tmpdirname:
                path = Path(tmpdirname) / 'tile'

                with path.open('wb') as file:
                    file.write(res.content)

                self.compress(str(path), tileset.format)

                with path.open('rb') as file:
                    tileset[key] = file.read()


class OpenStreetMapImporter(Importer):
    def __init__(self):
        super().__init__(
            'http://tile.openstreetmap.org/{zoom}/{row}/{ncol}.png'
        )


class SatelliteImporter(Importer):
    def __init__(self):
        super().__init__(
            'http://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/Tile/{zoom}/{ncol}/{row}.jpg'
        )
