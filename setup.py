"""
Flask-MongoEnginge-Migrations
-------------

Flask-MongoEngine-Migrations is a Flask extension
that provides posibility to create migrations for MongoDB.
"""
from setuptools import setup


setup(
    name='flask-mongoengine-migrations',
    version='0.2.1',
    url='https://bitbucket.org/letsignitcloud/flask-mongoengine-migrations',
    license='BSD',
    author='Andrey Zhukov',
    author_email='azhukov@mailinblack.com',
    description='Flask extension for MongoDB migrations',
    long_description=__doc__,
    packages=['flask_mongoengine_migrations'],
    include_package_data=True,
    platforms='any',
    python_requires='>=3.5',
    install_requires=[
        'Flask>=0.11',
        'flask-mongoengine>=0.8.2',
        'structlog>=16.0.0'
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest-cov', 'pytest'],
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
