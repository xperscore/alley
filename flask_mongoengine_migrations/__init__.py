import click
from mongoengine.connection import get_db
from .migrations import Migrations

import structlog

logger = structlog.get_logger(__name__)


class FlaskMigrations(object):
    """Flask extension, register migration cli commands."""

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        path = app.root_path
        if 'mongoengine' not in app.extensions:
            logger.error('No mongoengine extension.')
            return

        @app.cli.command()
        def migration_status():
            migrations = Migrations(path, get_db())
            migrations.show_status()

        @app.cli.command()
        @click.argument('name')
        def migration_create(name):
            migrations = Migrations(path, get_db())
            migrations.create(name)

        @app.cli.command()
        @click.argument('migration_id', required=False)
        @click.option('--fake', is_flag=True)
        def migration_up(migration_id=None, fake=False):
            migrations = Migrations(path, get_db())
            migrations.up(migration_id, fake)

        @app.cli.command()
        @click.argument('migration_id')
        def migration_down(migration_id):
            migrations = Migrations(path, get_db())
            migrations.down(migration_id)
