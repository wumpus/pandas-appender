#!/usr/bin/env python

from os import path

from setuptools import setup

packages = [
    'pandas_appender',
]

test_requirements = ['pytest', 'pytest-cov', 'pytest-sugar']

requires = ['pandas']

extras_require = {
    'test': test_requirements,
}

setup_requires = ['setuptools_scm']

scripts = []

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    description = f.read()

setup(
    name='pandas_appender',
    use_scm_version=True,
    description='A helper class that makes appending to a Pandas DataFrame efficient',
    long_description=description,
    long_description_content_type='text/markdown',
    author='Greg Lindahl and others',
    author_email='lindahl@pbm.com',
    url='https://github.com/wumpus/pandas-appender',
    packages=packages,
    python_requires='>=3.7',
    extras_require=extras_require,
    setup_requires=setup_requires,
    install_requires=requires,
    scripts=scripts,
    license='Apache 2.0',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Operating System :: POSIX :: Linux',
        'Environment :: MacOS X',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        #'Programming Language :: Python :: 3.5',  # setuptools_scm 6 dropped Py 3.5 and somehow I can't ask for an old version?
        #'Programming Language :: Python :: 3.6',  # no longer in github actions
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3 :: Only',
    ],
)
