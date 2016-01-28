from cartographer import __version__


extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon'
]

source_suffix = '.rst'
master_doc = 'index'

project = 'cartographer'
copyright = '2016, Thomas Leese'

release = __version__
version = __version__

html_theme = 'alabaster'

intersphinx_mapping = {'http://docs.python.org/': None}
