# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='mosyco',
    version='0.1.0',
    description='Prototype for Model-System-Controller architecture',
    long_description=readme,
    author='Victor Brinkhege',
    author_email='vbrinkhege@uos.de',
    url='https://github.com/vab9/mosyco',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    python_requires='>=3.6'
)
