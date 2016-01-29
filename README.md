# ![cartographer][logo]

A Python library for working with electronic tile maps.

[![Docs](https://readthedocs.org/projects/cartographer/badge/?version=latest)](http://cartographer.readthedocs.org) [![Build Status](https://travis-ci.org/thomasleese/cartographer.svg?branch=master)](https://travis-ci.org/thomasleese/cartographer)

## Installation

    $ pip install -e .

## Features

- Command-line interface.
- Web-based tile importers, including OSM and Satellite imagery.
- Support for reading and writing MBTiles files.
- Web interface for viewing maps and tiles.

## Commands

### `create-tileset`

Create an MBTiles tileset.

    cartographer create-tileset [--type TYPE] [--version VERSION] [--description DESCRIPTION] [--format FORMAT] filename name

### `import-tiles`

Import tiles into a tileset from the Web.

    cartographer import-tiles filename url zoom_level

`url` may be `osm` or `satellite`.

### `set-metadata`

Set some metadata in the tileset.

    cartographer set-metadata filename name value

### `extract-tile`

Extract a tile from the tileset.

    cartographer extract-tile filename zoom_level row col

### `web`

Serve tiles using a HTTP server.

    cartographer web [tiles]

[![forthebadge](http://forthebadge.com/images/badges/built-with-love.svg)](http://forthebadge.com) [![forthebadge](http://forthebadge.com/images/badges/uses-badges.svg)](http://forthebadge.com) [![forthebadge](http://forthebadge.com/images/badges/uses-git.svg)](http://forthebadge.com)

[logo]: https://github.com/thomasleese/cartographer/raw/master/logo.png
