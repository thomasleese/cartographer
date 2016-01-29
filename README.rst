|cartographer|
==============

A Python library for working with electronic tile maps.

|Docs| |Build Status|

Installation
------------

::

    $ pip install -e .

Features
--------

-  Command-line interface.
-  Web-based tile importers, including OSM and Satellite imagery.
-  Support for reading and writing MBTiles files.
-  Web interface for viewing maps and tiles.

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

.. |cartographer| image:: https://github.com/thomasleese/cartographer/raw/master/logo.png
.. |Docs| image:: https://readthedocs.org/projects/cartographer/badge/?version=latest
   :target: http://cartographer.readthedocs.org
.. |Build Status| image:: https://travis-ci.org/thomasleese/cartographer.svg?branch=master
   :target: https://travis-ci.org/thomasleese/cartographer
