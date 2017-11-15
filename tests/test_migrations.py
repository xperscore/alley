from unittest import TestCase
from mock import call, patch, MagicMock
from alley.migrations import MigrationFile, Migrations


def get_migrations(from_id, to_id=None):
    if not to_id:
        to_id = from_id + 1
    return [
        MigrationFile(id=m, filename='{:04}_test.py'.format(m))
        for m in range(from_id, to_id + 1)
    ]


class MockMigrations(Migrations):

    def __init__(self):
        self.db = 'db'
        self.directory = 'migrations'
        self.collection = MagicMock()


class MigrationFileTests(TestCase):

    def test_name_normalize(self):
        self.assertEqual('test_it_', MigrationFile.normalize_name('test it!'))

    def test_id_validate(self):
        self.assertEqual(1, MigrationFile.validate_id('0001'))
        self.assertEqual(None, MigrationFile.validate_id('a'))

    def test_as_dict(self):
        self.assertEqual(
            {
                'id': 1,
                'filename': '0001_test.py'
            }, MigrationFile(1, '0001_test.py').as_dict())

    def test_str(self):
        self.assertTrue(str(MigrationFile(1, '0001_test.py')).startswith('1'))


class MigrationTests(TestCase):

    def test_init(self):
        migrations = Migrations('/path', {'db_migrations': 'test'})

        self.assertEqual(migrations.directory, '/path/migrations')
        self.assertEqual(migrations.collection, 'test')

    @patch('os.listdir')
    def test_get_migration_files(self, mock_listdir):
        mock_listdir.return_value = [
            '0002_test.py', 'xxx', 'some.py', '0003_wrong name.py',
            '0003_test.pyc', '0001_first.py']

        result = MockMigrations().get_migration_files()
        self.assertEqual(
            [
                MigrationFile(1, '0001_first.py'),
                MigrationFile(2, '0002_test.py')
            ],
            result)

    def test_get_unregistered_migrations(self):
        migrations = MockMigrations()
        migrations.get_migration_files = MagicMock(
            return_value=get_migrations(1, 2)
        )
        mock_find_one = lambda m: m['filename'].startswith('0001')
        migrations.collection.find_one.side_effect = mock_find_one

        result = migrations.get_unregistered_migrations()
        self.assertEqual(
            [
                MigrationFile(2, '0002_test.py')
            ],
            result)

    def test_get_last_migrated_id(self):
        migrations = MockMigrations()
        migrations.collection.find.return_value = MagicMock()

        migrations.get_last_migrated_id()
        self.assertTrue(migrations.collection.find.return_value.sort.called)

    @patch('os.path.exists')
    def test_check_directory(self, mock_exists):
        mock_exists.return_value = True
        self.assertTrue(MockMigrations().check_directory())
        mock_exists.return_value = False
        self.assertFalse(MockMigrations().check_directory())

    def test_get_new_filename(self):
        migrations = MockMigrations()
        migrations.get_migration_files = MagicMock(
            return_value=get_migrations(1, 2)
        )

        self.assertEqual(
            '0003_new_migration.py',
            migrations.get_new_filename('new migration'))

    @patch('imp.load_source')
    def test_load_migration_file(self, mock_module):
        migrations = MockMigrations()
        migrations.load_migration_file('test')
        mock_module.assert_called_once_with('migration', 'migrations/test')


class ShowStatusTests(TestCase):

    def setUp(self):
        self.migrations = MockMigrations()
        self.migrations.check_directory = MagicMock(return_value=True)

    @patch('alley.migrations.logger')
    def test_no_migrations(self, mock_logger):
        self.migrations.get_unregistered_migrations = MagicMock(
            return_value=[])

        self.migrations.show_status()
        mock_logger.info.assert_called_once_with(
            MockMigrations.NO_MIGRATIONS_MSG)

    @patch('alley.migrations.logger')
    def test_show_migrations(self, mock_logger):
        unregistered_migrations = get_migrations(2, 3)
        self.migrations.get_unregistered_migrations = MagicMock(
            return_value=unregistered_migrations)

        self.migrations.show_status()
        mock_logger.info.assert_has_calls(
            [call("Unregistered migrations:")] + [call(m.filename) for m in unregistered_migrations])


class CreateTests(TestCase):
    def setUp(self):
        self.migrations = MockMigrations()
        self.migrations.get_new_filename = MagicMock(return_value='test')

    @patch('os.makedirs')
    @patch('os.path.exists', return_value=False)
    @patch('__builtin__.open')
    def test_create_direcrory(self, mock_open, mock_exists, mock_makedirs):
        self.migrations.create('test')

        mock_makedirs.assert_called_once_with(self.migrations.directory)

    @patch('os.makedirs')
    @patch('os.path.exists', return_value=True)
    @patch('__builtin__.open')
    def test_write_file(self, mock_open, mock_exists, mock_makedirs):
        mock_open.return_value = MagicMock()
        self.migrations.create('test')

        self.assertFalse(mock_makedirs.called)
        self.assertTrue(mock_open.called)
        file_handle = mock_open.return_value.__enter__.return_value
        self.assertTrue(file_handle.write.called)


class GetMigrationsToUpTests(TestCase):
    def setUp(self):
        self.migrations = MockMigrations()
        self.migrations.get_unregistered_migrations = MagicMock(
            return_value=get_migrations(2, 3)
        )

    def test_invalid_id(self):
        self.assertEqual([], self.migrations.get_migrations_to_up('xx'))

    def test_no_available_migrations(self):
        self.migrations.get_unregistered_migrations = MagicMock(
            return_value=[])

        self.assertEqual([], self.migrations.get_migrations_to_up())

    def test_migrated(self):
        self.assertEqual([], self.migrations.get_migrations_to_up(1))

    def test_up_to_last(self):
        self.assertEqual(
            [
                MigrationFile(2, '0002_test.py'),
                MigrationFile(3, '0003_test.py')
            ],
            self.migrations.get_migrations_to_up())

    def test_up_to_2(self):
        self.assertEqual(
            [
                MigrationFile(2, '0002_test.py')
            ],
            self.migrations.get_migrations_to_up(2))


class GetMigrationsToDownTests(TestCase):

    def setUp(self):
        self.migrations = MockMigrations()
        self.migrations.get_migration_files = MagicMock(
            return_value=get_migrations(1, 4)
        )
        self.migrations.get_unregistered_migrations = MagicMock(
            return_value=get_migrations(4)
        )
        self.migrations.get_last_migrated_id = MagicMock(return_value=3)

    def test_invalid_id(self):
        result = self.migrations.get_migrations_to_down('xx')
        self.assertEqual([], result)

    def test_not_applied(self):
        result = self.migrations.get_migrations_to_down(4)
        self.assertEqual([], result)

    def test_not_exists(self):
        result = self.migrations.get_migrations_to_down(52)
        self.assertEqual([], result)

    def test_down_to_1(self):
        result = self.migrations.get_migrations_to_down(3)
        self.assertEqual(
            [
                MigrationFile(3, '0003_test.py')
            ],
            result)

    def test_down_to_2(self):
        result = self.migrations.get_migrations_to_down(2)
        self.assertEqual(
            [
                MigrationFile(3, '0003_test.py'),
                MigrationFile(2, '0002_test.py')
            ],
            result)

    def test_down_to_first(self):
        result = self.migrations.get_migrations_to_down(1)
        self.assertEqual(
            [
                MigrationFile(3, '0003_test.py'),
                MigrationFile(2, '0002_test.py'),
                MigrationFile(1, '0001_test.py')
            ],
            result)


class UpTests(TestCase):

    def setUp(self):
        self.migration_module = MagicMock()
        self.migrations = MockMigrations()
        self.migrations.check_directory = MagicMock(return_value=True)
        self.migrations.get_migrations_to_up = MagicMock(
            return_value=get_migrations(1, 3)
        )
        self.migrations.load_migration_file = MagicMock(
            return_value=self.migration_module)
        self.migrations.collection.insert = MagicMock()

    def test_no_directory(self):
        self.migrations.check_directory = MagicMock(return_value=False)
        self.migrations.up(3)

        self.assertFalse(self.migration_module.up.called)
        self.assertFalse(self.migrations.collection.insert.called)

    def test_up(self):
        self.migrations.up(3)

        self.assertEqual(3, self.migration_module.up.call_count)
        self.assertEqual(3, self.migrations.collection.insert.call_count)

    def test_up_fake(self):
        self.migrations.up(3, fake=True)

        self.assertFalse(self.migration_module.up.called)
        self.assertEqual(3, self.migrations.collection.insert.call_count)

    def test_no_up_method(self):
        def only_one_has_up(filename):
            if filename.startswith('0001'):
                return self.migration_module
        self.migrations.load_migration_file.side_effect = only_one_has_up
        self.migrations.up(3)

        self.assertEqual(1, self.migration_module.up.call_count)
        self.assertEqual(3, self.migrations.collection.insert.call_count)


class DownTests(TestCase):

    def setUp(self):
        self.migration_module = MagicMock()
        self.migrations = MockMigrations()
        self.migrations.check_directory = MagicMock(return_value=True)
        self.migrations.get_migrations_to_down = MagicMock(
            return_value=get_migrations(2, 3)
        )
        self.migrations.load_migration_file = MagicMock(
            return_value=self.migration_module)
        self.migrations.collection.remove = MagicMock()

    def test_no_directory(self):
        self.migrations.check_directory = MagicMock(return_value=False)
        self.migrations.down(2)

        self.assertFalse(self.migration_module.down.called)
        self.assertFalse(self.migrations.collection.insert.called)

    def test_down(self):
        self.migrations.down(2)

        self.assertEqual(2, self.migration_module.down.call_count)
        self.assertEqual(2, self.migrations.collection.remove.call_count)

    def test_no_down_method(self):
        def only_one_has_down(filename):
            if filename.startswith('0002'):
                return self.migration_module
        self.migrations.load_migration_file.side_effect = only_one_has_down
        self.migrations.down(2)

        self.assertEqual(1, self.migration_module.down.call_count)
        self.assertEqual(2, self.migrations.collection.remove.call_count)
