"""
Alley
-------------

Alley is a framework-agnostic migration helper for MongoDB.
"""

from setuptools import setup


setup(
    name='alley',
    version='0.0.1',
    url='https://github.com/xperscore/alley',
    license='BSD',
    author='Zach Layng',
    author_email='zach@whoknows.com',
    description='Framework agnostic MongoEngine migrations.',
    long_description=__doc__,
    packages=['alley'],
    include_package_data=True,
    platforms='any',
    python_requires='>=2.7',
    install_requires=[
        'mongoengine>=0.9.0'
        'structlog[dev]',
        'click'
    ],
    setup_requires=['pytest-runner'],
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
