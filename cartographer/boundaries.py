from enum import Enum
import math


def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return (xtile, int(n - 1 - ytile))


class Boundary:
    def __init__(self, left, bottom, right, top):
        self.left = left
        self.bottom = bottom
        self.right = right
        self.top = top

    def tile_bounds(self, zoom_level):
        bottom_left = deg2num(self.bottom, self.left, zoom_level)
        top_right = deg2num(self.top, self.right, zoom_level)
        return bottom_left[0], bottom_left[1], top_right[0], top_right[1]

    def contains(self, x, y, zoom_level=None):
        if zoom_level is not None:
            x, y = deg2num(x, y, zoom_level)

        return self.left <= x <= self.right and self.bottom <= y <= self.top


# left, bottom, right, top

class Country(Boundary, Enum):
    united_kingdom = (-9, 49.8, 2, 62)


class Misc(Boundary, Enum):
    world = (-180, -85, 180, 85)
