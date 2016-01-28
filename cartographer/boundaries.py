import math


def num2deg(xtile, ytile, zoom):
    """Convert x/y tile coordinates to latitude and longitude."""
    n = 2.0 ** zoom
    ytile = n - 1 - ytile
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lat_deg, lon_deg)


def deg2num(lat_deg, lon_deg, zoom):
    """Convert latitude and longitude to x/y tile coordinates."""
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return (xtile, int(n - 1 - ytile))


class Boundary:
    """Represents a generic rectangular boundary."""

    def __init__(self, left, bottom, right, top):
        self.left = left
        self.bottom = bottom
        self.right = right
        self.top = top

    def tile_bounds(self, zoom_level):
        """Get x/y tile coordinates for this boundary."""

        bottom_left = deg2num(self.bottom, self.left, zoom_level)
        top_right = deg2num(self.top, self.right, zoom_level)
        return bottom_left[0], bottom_left[1], top_right[0], top_right[1]

    def contains(self, x, y, zoom_level=None):
        """
        Check if the boundary contains the point x/y.

        If ``zoom_level`` is ``None`` it is assumed that x/y will be in
        tile coordinates, otherwise latitude and longitude.
        """

        if zoom_level is not None:
            y, x = num2deg(x, y, zoom_level)

        return self.left <= x <= self.right and self.bottom <= y <= self.top

    def as_metadata(self):
        """Return a string suitable for MBTiles metadata."""

        return '{},{},{},{}' \
            .format(self.left, self.bottom, self.right, self.top)


# left, bottom, right, top

world = Boundary(-180, -85, 180, 85)
united_kingdom = Boundary(-9, 49.8, 2, 62)
