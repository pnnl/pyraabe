from setuptools import setup, find_packages
from pyraabe import __version__


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

# with open('requirements.txt') as f:
#     required = f.read().splitlines()
required = None

pkgs = find_packages(exclude=('examples', 'docs', 'resources'))

setup(
    name='pyraabe',
    version=__version__,
    description='Automated Raabe table generation',
    long_description=readme,
    author='Sean M. Colby',
    author_email='sean.colby@pnnl.gov',
    url='https://github.com/pnnl/pyraabe',
    license=license,
    packages=pkgs,
    install_requires=required,
    entry_points={
        'console_scripts': ['pyraabe = pyraabe.cli:main']
    }
)
