from setuptools import find_packages, setup

from cartographer import __version__


with open('README.rst') as file:
    long_description = file.read()

setup(
    name='cartographer',
    version=__version__,
    description='A Python library for working with electronic tile maps.',
    long_description=long_description,
    url='https://github.com/thomasleese/cartographer',
    author='Thomas Leese',
    author_email='inbox@thomasleese.me',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['cartographer = cartographer.cli:main']
    },
    setup_requires=[
        'Sphinx'
    ],
    install_requires=[
        'requests',
        'Flask'
    ],
    test_suite='tests'
)
