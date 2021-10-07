from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    required = f.read().splitlines()

version = 'v0.0.3.dev'

setup(
    name='rocrate_lang',
    packages=find_packages(exclude=['test']),
    version=version,
    description='RO-Crate Data Getter',
    author=", ".join((
        'Peter Sefton',
        'Mel Mistica',
        'Moises Sacal'
    )),
    python_requires='>=3.6',
    license="gplv2",
    url='https://github.com/Language-Research-Technology/rocrate-lang-py',
    download_url=('https://github.com/Language-Research-Technology/rocrate-lang-py/archive/'
                  f'{version}.tar.gz'),
    keywords="atap ldaca rocrates",
    install_requires=[required]
)
