"""
Alley
-------------

Alley is a framework-agnostic migration helper for MongoDB.
"""
import sys
from setuptools import setup

needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
pytest_runner = ['pytest-runner'] if needs_pytest else []

setup(
    name='alley',
    version='0.0.3',
    url='https://github.com/xperscore/alley',
    license='BSD',
    author='WhoKnows, Inc.',
    author_email='dev@whoknows.com',
    description='Framework agnostic MongoEngine migrations.',
    long_description=__doc__,
    packages=['alley'],
    include_package_data=True,
    platforms='any',
    python_requires='>=2.7',
    install_requires=[
        'mongoengine>=0.9.0',
        'click'
    ],
    setup_requires=pytest_runner,
    tests_require=['pytest-cov', 'pytest', 'mock'],
    entry_points='''
        [console_scripts]
        alley=alley.alley_cli:cli
    ''',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
