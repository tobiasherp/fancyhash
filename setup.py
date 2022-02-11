# -*- coding: utf-8 -*- vim: ts=8 sts=4 sw=4 si et tw=79
from setuptools import setup, find_packages
from os.path import dirname, abspath, join


def read(name):
    fn = join(dirname(abspath(__file__)), name)
    return open(fn, 'r').read()

__author__ = "Tobias Herp <tobias.herp@gmx.net>"
VERSION = (0,
           3,   # code cleanup; output interval
           4,   # initial public version
           )
__version__ = '.'.join(map(str, VERSION))

long_description = '\n\n'.join([
    read('README.rst'),
    read('TODO.rst'),
    read('HISTORY.rst'),
])


kwargs = {
    'name': 'fancyhash',
    'version': __version__,
    'packages': find_packages('src'),
    'entry_points': {
        'console_scripts': [
            'fancyhash = fancyhash:main',  # src/fancyhash.py
            ],
        },
    'author': 'Tobias Herp',
    'author_email': 'tobias.herp@gmx.net',
    'description': "user friendly hash calculation and checking",
    'license': 'MIT',
    'install_requires': [
        'setuptools',
        'thebops >= 0.1.11',
      ],
    'long_description': long_description,
    'long_description_content_type': 'text/x-rst',
    }
setup(**kwargs)
