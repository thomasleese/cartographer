import math

import sqlite3


def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return (xtile, int(n - 1 - ytile))


class TilesetMetadata:
    KNOWN_KEYS = ['name', 'type', 'version', 'description', 'format',
                  'bounds', 'attribution']

    def __init__(self, db):
        self.db = db

    def __setitem__(self, name, value):
        cursor = self.db.cursor()
        cursor.execute('UPDATE metadata SET value = ? WHERE name = ?',
                       (value, name))
        if cursor.rowcount == 0:
            cursor.execute('INSERT INTO metadata (name, value) VALUES (?, ?)',
                           (name, value))
        self.db.commit()

    def __getitem__(self, name):
        cursor = self.db.cursor()
        cursor.execute('SELECT value FROM metadata WHERE name = ?', (name,))
        row = cursor.fetchone()
        if row is None:
            raise KeyError(name)
        else:
            return row[0]

    def __delitem__(self, name):
        cursor = self.db.cursor()
        cursor.execute('DELETE FROM metadata WHERE name = ?', (name,))
        if cursor.rowcount == 0:
            raise KeyError(name)
        self.db.commit()


class TilesetTiles:
    def __init__(self, db):
        self.db = db

    def __setitem__(self, key, value):
        zoom, x, y = key

        cursor = self.db.cursor()
        cursor.execute("""
            UPDATE tiles
            SET tile_data = ?
            WHERE zoom_level = ? AND tile_column = ? AND tile_row = ?
        """, (value, zoom, x, y))

        if cursor.rowcount == 0:
            cursor.execute("""
                INSERT INTO
                    tiles (zoom_level, tile_column, tile_row, tile_data)
                VALUES (?, ?, ?, ?)
            """, (zoom, x, y, value))

        self.db.commit()

    def __getitem__(self, key):
        zoom, x, y = key

        cursor = self.db.cursor()
        cursor.execute("""
            SELECT tile_data
            FROM tiles
            WHERE zoom_level = ? AND tile_column = ? AND tile_row = ?
        """, (zoom, x, y))

        row = cursor.fetchone()
        if row is None:
            raise KeyError(key)
        else:
            return row[0]

    def __contains__(self, key):
        zoom, x, y = key

        cursor = self.db.cursor()
        cursor.execute("""
            SELECT COUNT(*)
            FROM tiles
            WHERE zoom_level = ? AND tile_column = ? AND tile_row = ?
        """, (zoom, x, y))

        row = cursor.fetchone()
        return row[0] > 0

    def __delitem__(self, key):
        zoom, x, y = key

        cursor = self.db.cursor()
        cursor.execute("""
            DELETE FROM tiles
            WHERE zoom_level = ? AND tile_column = ? AND tile_row = ?
        """, (zoom, x, y))

        if cursor.rowcount == 0:
            raise KeyError(key)

        self.db.commit()

    def count(self, zoom=None, col=None, row=None):
        sql = 'SELECT COUNT(*) FROM tiles WHERE '

        where = []
        args = []

        if zoom is not None:
            where.append('zoom_level = ?')
            args.append(zoom)

        if col is not None:
            where.append('tile_column = ?')
            args.append(col)

        if row is not None:
            where.append('tile_row = ?')
            args.append(row)

        sql += ' AND '.join(where)

        cursor = self.db.cursor()
        cursor.execute(sql, args)
        row = cursor.fetchone()
        return row[0]

    @property
    def zoom_levels(self):
        cursor = self.db.cursor()
        cursor.execute('SELECT DISTINCT zoom_level FROM tiles')
        return [row[0] for row in cursor.fetchall()]


class Tileset:
    def __init__(self, filename):
        self.db = sqlite3.connect(filename)
        self.metadata = TilesetMetadata(self.db)
        self.tiles = TilesetTiles(self.db)

        self.create_schema()

    def create_schema(self):
        cursor = self.db.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metadata (
                name TEXT,
                value TEXT
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tiles (
                zoom_level INTEGER,
                tile_column INTEGER,
                tile_row INTEGER,
                tile_data BLOB
            );
        """)

    @property
    def coordinate_bounds(self):
        tokens = [float(x) for x in self.bounds.split(',')]
        return tuple(tokens)

    def calculate_tile_bounds(self, zoom):
        left, bottom, right, top = self.coordinate_bounds

        bottom_left = deg2num(bottom, left, zoom)
        top_right = deg2num(top, right, zoom)
        return bottom_left[0], bottom_left[1], top_right[0], top_right[1]

    @property
    def mime_type(self):
        if self.format == 'png':
            return 'image/png'
        elif self.format == 'jpg':
            return 'image/jpeg'
        else:
            raise ValueError('Unsupported format.')

    @property
    def zoom_levels(self):
        return self.tiles.zoom_levels

    def __getattr__(self, key):
        if key in TilesetMetadata.KNOWN_KEYS:
            return self.metadata[key]
        else:
            super().__getattr__(key)

    def __setattr__(self, key, value):
        if key in TilesetMetadata.KNOWN_KEYS:
            self.metadata[key] = value
        else:
            super().__setattr__(key, value)

    def __delattr__(self, key):
        if key in TilesetMetadata.KNOWN_KEYS:
            del self.metadata[key]
        else:
            super().__delattr__(key)

    def __setitem__(self, key, value):
        self.tiles[key] = value

    def __getitem__(self, key):
        return self.tiles[key]

    def __delitem__(self, key):
        del self.tiles[key]

    def __contains__(self, key):
        return key in self.tiles
