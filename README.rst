|Logo|
======

A Python library for working with electronic tile maps.

Installation
------------

::

    $ pip install -e .

Commands
--------

``create-tileset``
~~~~~~~~~~~~~~~~~~

Create an MBTiles tileset.

::

    cartographer create-tileset [--type TYPE] [--version VERSION] [--description DESCRIPTION] [--format FORMAT] filename name

``import-tiles``
~~~~~~~~~~~~~~~~

Import tiles into a tileset from the Web.

::

    cartographer import-tiles filename url zoom_level

``url`` may be ``osm`` or ``satellite``.

``set-metadata``
~~~~~~~~~~~~~~~~

Set some metadata in the tileset.

::

    cartographer set-metadata filename name value

``extract-tile``
~~~~~~~~~~~~~~~~

Extract a tile from the tileset.

::

    cartographer extract-tile filename zoom_level row col

``web``
~~~~~~~

Serve tiles using a HTTP server.

::

    cartographer web [tiles]

.. |Logo| image:: https://github.com/thomasleese/cartographer/raw/master/logo.png

