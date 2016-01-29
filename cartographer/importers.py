import requests


class Importer:
    """A tile importer."""

    def __init__(self, url):
        self.url = url

    def get_tile_url(self, zoom, col, row):
        """Get the URL for a particular tile."""

        l = (2 ** zoom) - 1
        nrow = l - row
        ncol = l - col
        return self.url.format(zoom=zoom, row=row, col=col, nrow=nrow,
                               ncol=ncol)

    def import_tile(self, tileset, zoom, col, row, compressor=None):
        """Import a tile into the tileset."""

        key = (zoom, col, row)

        url = self.get_tile_url(zoom, col, row)

        print('Importing {}x{}x{}: {}'.format(zoom, col, row, url))

        res = requests.get(url)

        if res.status_code == requests.codes.ok:
            if compressor is not None:
                content = compressor.compress(res.content)
            else:
                content = res.content

            tileset[key] = content

            return content
        else:
            print('Warning. This failed.')

    def __call__(self, tileset, zoom, boundary=None, compressor=None):
        """Run the importer on a zoom level and boundary."""

        count = 2 ** zoom

        if boundary is None:
            boundary = tileset.boundary

        min_col, min_row, max_col, max_row = boundary.tile_bounds(zoom)

        max_col = min(max_col, count)
        max_row = min(max_row, count)

        for row in range(min_row, max_row):
            imported_cols = tileset.tiles._get_row(row, zoom)

            for col in range(min_col, max_col):
                if col not in imported_cols and \
                        boundary.contains(col, row, zoom):
                    self.import_tile(tileset, zoom, col, row, compressor)


class OpenStreetMapImporter(Importer):
    def __init__(self):
        super().__init__(
            'http://tile.openstreetmap.org/{zoom}/{col}/{nrow}.png'
        )


class SatelliteImporter(Importer):
    def __init__(self):
        super().__init__(
            'http://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/Tile/{zoom}/{nrow}/{col}.jpg'
        )


class OrdnanceSurveyImporter(Importer):
    def __init__(self, key):
        super().__init__(
            'http://ak.dynamic.t1.tiles.virtualearth.net/comp/ch/{quad_key}?mkt=en-GB&it=G,OS,BX,RL&shading=hill&n=z&og=113&key={key}&c4w=1'
        )

        self.key = key

    @staticmethod
    def calculate_quad_key(zoom, x, y):
        key = ''
        pow_result = pow(2, zoom)

        x += 1
        y += 1

        for i in range(zoom):
            pow_result = pow_result / 2
            digit = 0
            if x > pow_result:
                digit += 1
                x -= pow_result
            if y > pow_result:
                digit += 2
                y -= pow_result
            key += str(digit)

        return key

    def get_tile_url(self, zoom, row, col):
        l = (2 ** zoom) - 1
        ncol = l - col

        quad_key = self.calculate_quad_key(zoom, row, ncol)

        return self.url.format(quad_key=quad_key, key=self.key)
