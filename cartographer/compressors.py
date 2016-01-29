"""A tool for compressing tile images."""

import io
import logging
import subprocess


logger = logging.getLogger(__name__)


class Compressor:
    """The abstract compressor class."""

    def compress(self, data):
        """
        Compress the input data and return the result, or raise an exception if
        something has gone wrong.
        """

        raise NotImplementedError('This method should be overridden.')


class CommandLineCompressor(Compressor):
    """
    A compressor which executed a command and uses stdin/stdout to provide and
    retrieve the data.
    """

    def __init__(self, args):
        logger.info('Initialising command-line compressor: %s', args)
        self.args = args

    def compress(self, data):
        logger.debug('Executing: %s', self.args)
        return subprocess.check_output(self.args, input=data)


class Pngquant(CommandLineCompressor):
    """A compressor for PNGs."""

    def __init__(self, quality='50-75'):
        super().__init__(['pngquant',
                          '--quality', quality,
                          '--speed', '1',
                          '-'])


class Jpegoptim(CommandLineCompressor):
    """A compressor for JPEGs."""

    def __init__(self, max_quality='75'):
        super().__init__(['jpegoptim', '--max', max_quality, '-'])
