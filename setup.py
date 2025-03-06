from distutils.core import setup
from setuptools import setup, find_packages

setup(
    name='MeteoFRtoEPW',
    version='0.1',
    author='Thibault Chevilliet', 
    author_email='thibault.chevilliet@enpc.fr',
    packages=find_packages(),
    long_description=open('README.md').read()
)
