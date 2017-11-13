import imp
import os
import re
from datetime import datetime

from structlog import get_logger

logger = get_logger()


class MigrationFile(object):
    PATTERN = '^(?P<id>[0-9]+)_[a-z0-9_]+\.py$'

    def __init__(self, id, filename):
        self.id = int(id)
        self.filename = filename

    def __str__(self):
        return '{0.id}: {0.filename}'.format(self)

    def __eq__(self, other):
        return self.id == other.id and self.filename == other.filename

    @staticmethod
    def normalize_name(name):
        return re.sub('[^a-z0-9_]', '_', name)

    @staticmethod
    def validate_id(migration_id):
        try:
            return int(migration_id)
        except ValueError:
            logger.error(error='Invalid migration_id', id=migration_id)

    def as_dict(self):
        return {
            'id': self.id,
            'filename': self.filename
        }


class Migrations(object):
    """Manage MongoDB migrations."""

    MIGRATIONS_COLLECTION = 'db_migrations'
    MIGRATIONS_DIRECTORY = 'migrations'
    NO_MIGRATIONS_MSG = 'All migrations registered, nothing to execute'

    def __init__(self, path, db):
        self.path = path
        self.db = db

        self.directory = os.path.join(path, self.MIGRATIONS_DIRECTORY)
        self.collection = self.db[self.MIGRATIONS_COLLECTION]

    def get_migration_files(self):
        """Find migrations files."""
        migrations = (re.match(MigrationFile.PATTERN, filename)
                      for filename in os.listdir(self.directory))
        migrations = (MigrationFile(m.group('id'), m.group(0))
                      for m in migrations if m)
        return sorted(migrations, key=lambda m: m.id)

    def get_unregistered_migrations(self):
        """Find unregistered migrations."""
        return [m for m in self.get_migration_files()
                if not self.collection.find_one({'filename': m.filename})]

    def check_directory(self):
        """Check if migrations directory exists."""
        exists = os.path.exists(self.directory)
        if not exists:
            logger.error(error="No migrations directory found. Check your path or create a migration first.",
                         directory=self.directory)
        return exists

    def show_status(self):
        """Show status of unregistered migrations"""
        if not self.check_directory():
            return

        migrations = self.get_unregistered_migrations()
        if migrations:
            logger.info('Unregistered migrations:')
            for migration in migrations:
                logger.info(migration=migration.filename)
        else:
            logger.info(self.NO_MIGRATIONS_MSG)

    def get_new_filename(self, name):
        """Generate filename for new migration."""
        name = MigrationFile.normalize_name(name)
        migrations = self.get_migration_files()
        migration_id = migrations[-1].id if migrations else 0
        migration_id += 1
        return '{:04}_{}.py'.format(migration_id, name)

    def create(self, name):
        """Create a new empty migration."""
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        filename = self.get_new_filename(name)
        with open(os.path.join(self.directory, filename), 'w') as fp:
            fp.write("def up(db): pass\n\n\n")
            fp.write("def down(db): pass\n")
            logger.info(migration=filename)

    def load_migration_file(self, filename):
        """Load migration file as module."""
        path = os.path.join(self.directory, filename)
        # spec = spec_from_file_location("migration", path)
        # module = module_from_spec(spec)
        # spec.loader.exec_module(module)
        module = imp.load_source("migration", path)
        return module

    def get_migrations_to_up(self, migration_id=None):
        """Find migrations to execute."""
        if migration_id is not None:
            migration_id = MigrationFile.validate_id(migration_id)
            if not migration_id:
                return []

        migrations = self.get_unregistered_migrations()
        if not migrations:
            logger.info(self.NO_MIGRATIONS_MSG)
            return []

        if migration_id:
            try:
                last_migration = [m for m in migrations
                                  if m.id == migration_id][0]
            except IndexError:
                logger.error(error='Migration is not in unregistered list',
                             id=migration_id)
                self.show_status()
                return []
        else:
            last_migration = list(migrations)[-1]

        return [m for m in migrations if m.id <= last_migration.id]

    def up(self, migration_id=None, fake=False):
        """Executes migrations."""
        if not self.check_directory():
            return

        for migration in self.get_migrations_to_up(migration_id):
            log = logger.bind(migration=migration.filename)
            log.info('Executing migration...')

            migration_module = self.load_migration_file(migration.filename)
            if not fake:
                if hasattr(migration_module, 'up'):
                    migration_module.up(self.db)
                else:
                    log.error(error='No up method')

            record = migration.as_dict()
            record['date'] = datetime.utcnow()
            self.collection.insert(record)

    def get_last_migrated_id(self):
        """Find id of last applied migration."""
        return self.collection.find().sort('date', -1)[0]['id']

    def get_migrations_to_down(self, migration_id):
        """Find migrations to rollback."""
        migration_id = MigrationFile.validate_id(migration_id)
        if not migration_id:
            return []

        migrations = self.get_migration_files()
        last_migration_id = self.get_last_migrated_id()

        if migration_id in (m.id for m in self.get_unregistered_migrations()):
            logger.error(error='Migration is not applied', id=migration_id)
            return []

        try:
            migration = [m for m in migrations if m.id == migration_id][0]
        except IndexError:
            logger.error(error='Migration does not exists', id=migration_id)
            return []

        return list(reversed([m for m in migrations
                              if migration.id <= m.id <= last_migration_id]))

    def down(self, migration_id):
        """Rollback to migration."""
        if not self.check_directory():
            return

        for migration in self.get_migrations_to_down(migration_id):
            log = logger.bind(migration=migration.filename)
            log.info('Rollback migration...')

            migration_module = self.load_migration_file(migration.filename)
            if hasattr(migration_module, 'down'):
                migration_module.down(self.db)
            else:
                log.info('No down method')

            self.collection.remove({'filename': migration.filename})
