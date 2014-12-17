#!/usr/bin/env python

from setuptools import setup, find_packages

# Get version from pkg index
from dnspc import __version__
from dnspc import __author__
from dnspc import __maintainer__
from dnspc import __url__
from dnspc import __email__
from dnspc import __doc__
from dnspc import __shortdesc__
from dnspc import __name__ as __packagename__

desc = __shortdesc__
long_desc = __doc__

requires = [
    'Flask',
    'dateutil',
    'dnslib',
    'oslo.config',
    'IPy',
]

setup(name=__packagename__,
    version=__version__,
    description=desc,
    long_description=long_desc,
    author=__author__,
    author_email=__email__,
    url=__url__,
    packages=['dnspc'],
    requires=requires,
    data_files=[
        #('/etc', ['config/dnspc.conf']),
        #('/etc/init', ['install/dnspc.conf']),
        #('/var/lib/dnspc', ['config/rules.json','config/hosts.json'])
    ],
    entry_points={
        'console_scripts': {
            'startdnspc = runserver:main'
        }
    },
)
