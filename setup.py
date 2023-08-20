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
    classifiers = ['Development Status :: 3 - Alpha',], 
    install_requires=[
        'attrs>=23.1.0',
        'certifi>=2023.7.22',
        'charset-normalizer>=3.2.0',
        'exceptiongroup>=1.1.2',
        'h11>=0.14.0',
        'idna>=3.4',
        'outcome>=1.2.0',
        'packaging>=23.1',
        'PySocks>=1.7.1',
        'python-dotenv>=1.0.0',
        'requests>=2.31.0',
        'selenium>=4.11.2',
        'sniffio>=1.3.0',
        'sortedcontainers>=2.4.0',
        'trio>=0.22.2',
        'trio-websocket>=0.10.3',
        'urllib3>=2.0.4',
        'webdriver-manager>=4.0.0',
        'wsproto>=1.2.0'
    ],
)