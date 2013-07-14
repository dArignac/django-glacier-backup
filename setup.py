#!/usr/bin/env python
from setuptools import setup


setup(
    name='django-glacier-backup',
    description='Manage AWS Glacier vaults in Django and backup local files to Glacier.',
    version='0.0.1a',
    author='Alexander Herrmann',
    author_email='darignac@gmail.com',
    license='MIT',
    url='https://github.com/dArignac/django-glacier-backup',
    packages=['glacier_backup'],
    long_description=open('README.md').read(),
    install_requires=[

    ],
    dependency_links=[
    ]
)
