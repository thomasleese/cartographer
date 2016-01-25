import sqlite3


class TilesetMetadata:
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
                    metadata (zoom_level, tile_column, tile_row, tile_data)
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


class Tileset:
    def __init__(self, filename):
        self.db = sqlite3.connect(filename)
        self.metadata = TilesetMetadata(self.db)
        self.tiles = TilesetTiles(self.db)

        for name in ['name', 'type', 'version', 'description', 'format',
                     'bounds', 'attribution']:
            fget = lambda: self.metadata[name]

            def fset(value):
                self.metadata[name] = value

            def fdel():
                del self.metadata[name]

            setattr(self, name, property(fget, fset, fdel))

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

    def __setitem__(self, key, value):
        self.tiles[key] = value

    def __getitem__(self, key):
        return self.tiles[key]

    def __delitem__(self, key):
        del self.tiles[key]
