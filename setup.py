from setuptools import setup
from codecs import open
from os import path
import re

# Get the version from tmarket/__init__.py
version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('tmarket/__init__.py').read(),
    re.M
    ).group(1)

# Get the long description from the README file
with open(path.join(path.abspath(path.dirname(__file__)), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Setup
setup( 
    name = 'tmarket', 
    packages = ['tmarket'],
    version = version, 
    description = 'FETCH SOCCER PLAYERS DATA FROM https://www.transfermarkt.com', 
    long_description = long_description,
    long_description_content_type='text/markdown',
    author = 'Haotian Yang', 
    author_email = 'hyang57@u.rochester.edu', 
    url = 'https://github.com/htyyang/tmarket', 
    download_url = 'https://github.com/htyyang/tmarket/dist/' + version + '.tar.gz', 
    keywords = ['soccer', 'data', 'scraper'],
    classifiers = [], 
    install_requires=[package.split("\n")[0] for package in open("requirements.txt", "r").readlines()]
)