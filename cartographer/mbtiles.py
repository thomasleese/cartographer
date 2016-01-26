import os

import sqlite3

from .boundaries import Boundary


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


class TilesetSchema:
    def __init__(self, db):
        self.db = db

    def _create_metadata_table(cursor):
        cursor.execute("""
            CREATE TABLE metadata (
                name TEXT,
                value TEXT
            )
        """)

        cursor.execute("""
            CREATE UNIQUE INDEX metadata_name ON metadata (name);
        """)

    def _create_map_table(cursor):
        cursor.execute("""
            CREATE TABLE map (
                tile_id INTEGER,
                zoom_level INTEGER,
                tile_column INTEGER,
                tile_data BLOB
            );
        """)

    def create(self):
        cursor = self.db.cursor()

        self._create_metadata_table(cursor)
        self._create_tiles_table(cursor)

        self.db.commit()


class Tileset:
    def __init__(self, filename, create=False, upgrade=False):
        if not create and not os.path.exists(filename):
            raise ValueError('Tileset does not exist: {}'.format(filename))

        self.db = sqlite3.connect(filename)

        self.schema = TilesetSchema(self.db)

        if create:
            self.schema.create()

        self.metadata = TilesetMetadata(self.db)
        self.tiles = TilesetTiles(self.db)

    @property
    def boundary(self):
        tokens = [float(x) for x in self.bounds.split(',')]
        return Boundary(*tokens)

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
