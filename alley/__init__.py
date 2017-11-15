from mongoengine.connection import get_db, connect

from .migrations import Migrations


class MongoMigrations(object):
    """Helper for migration cli commands."""

    path = None

    def __init__(self, path, database, username, password, host=None, port=None, auth=None):
        if host is None:
            host = 'localhost'
        if port is None:
            port = 27017
        self.path = path
        connect(database, host=host, port=port, username=username, password=password, authentication_source=auth)

        self.db = get_db()

    @property
    def migrations(self):
        return Migrations(self.path, self.db)
