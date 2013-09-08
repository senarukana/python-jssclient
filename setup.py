__version__ = '1.4'

import os
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()

install_requires = [
    "PrettyTable>=0.6,<0.8",
]

setup(
    name='python-jssclient',
    version=__version__,
    description='Higher Level Zookeeper Client',
    long_description=README + '\n\n',
    author="openinx",
    author_email="openinx@gmail.com",
    url="http://github.com/openinx/python-jssclient",
    license="Apache 2.0",
    packages=find_packages(),
    include_package_data=True,
    entry_points = { "console_scripts": [ "jss = jssclient.shell:main", ] },
    zip_safe=False,
    install_requires=install_requires,
)
