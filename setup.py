#!/usr/bin/env python

#import sys
## Without this, Flask complains that the .egg file
## is not a directory.
#sys.argv.append('--old-and-unmanageable')

import os

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
    'six>=1.7.0',
    'Flask',
    "python-dateutil",
    'dnslib',
    'oslo.config',
    'IPy',
]

data_files=[
    ('/etc', ['config/dnspc.example.conf']),
    ('/var/lib/dnspc', ['config/rules.example.json','config/hosts.example.json','config/README.md']),
]

whichinit = os.popen('install/whichinit.sh').read().strip()

if whichinit:
    if whichinit == 'upstart':
        initfiles = ('/etc/init', ['install/dnspc.conf'])
    elif whichinit == 'lsb':
        initfiles = ('/etc/init.d', ['install/dnspc'])
    elif whichinit == 'systemd':
        initfiles = ('/usr/lib/systemd/system', ['install/dnspc.system'])
    data_files.append(initfiles)

setup(name=__packagename__,
    version=__version__,
    description=desc,
    long_description=long_desc,
    author=__author__,
    author_email=__email__,
    url=__url__,
    packages=find_packages(),
    install_requires=requires,
    include_package_data=True,
    data_files=data_files,
    scripts=[
        'bin/dnspc-setloglevel',
    ],
    entry_points={
        'console_scripts': {
            'start_dnspc = dnspc.start_server:main'
        }
    },
)
