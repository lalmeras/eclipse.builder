#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

setup(
    name='eclipse_builder',
    version='0.1.1',
    description="Helpers to build custom Eclipse packages",
    long_description=readme + '\n\n' + history,
    author="Laurent Almeras",
    author_email='lalmeras@gmail.com',
    url='https://github.com/lalmeras/eclipse_builder',
    packages=find_packages(include=['eclipse_builder']),
    entry_points={
        'console_scripts': [
            'eclipse_builder=eclipse_builder.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=[
        "Click==7.0",
        "requests==2.20.0",
        "CacheControl==0.12.3",
        "CacheControl[filecache]==0.12.3",
        "lockfile==0.12.2",
        "coloredlogs==15.0",
        "pyyaml==5.4.1",
        "requests-testadapter"
        ],
    license="MIT license",
    zip_safe=False,
    keywords='eclipse_builder',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=[
        "requests-testadapter"
        ],
    setup_requires=[]
)
