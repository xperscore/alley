from unittest import TestCase

from click.testing import CliRunner
from mock import patch, MagicMock

from alley import alley_cli


class MockMongoMigrations(object):
    def __init__(self, migrations):
        self.migrations = migrations


class CommandsTests(TestCase):
    def setUp(self):
        self.mock_migrations_patcher = patch(
            "alley.Migrations")
        self.addCleanup(self.mock_migrations_patcher.stop)
        self.mock_migrations = self.mock_migrations_patcher.start()
        self.mock_migrations.return_value = MagicMock()
        self.commands = alley_cli.cli.commands
        self.runner = CliRunner()
        self.context = MockMongoMigrations(self.mock_migrations.return_value)

    def test_status(self):
        result = self.runner.invoke(self.commands['status'], obj=self.context)
        self.assertEqual(0, result.exit_code)
        self.assertTrue(self.mock_migrations.return_value.show_status.called)

    def test_create(self):
        result = self.runner.invoke(self.commands['create'], obj=self.context)
        self.assertEqual(2, result.exit_code)

        result = self.runner.invoke(self.commands['create'],
                                    ['name'], obj=self.context)
        self.assertEqual(0, result.exit_code)
        self.assertTrue(self.mock_migrations.return_value.create.called)

    def test_up(self):
        result = self.runner.invoke(self.commands['up'], obj=self.context)
        self.assertEqual(0, result.exit_code)
        self.assertTrue(self.mock_migrations.return_value.up.called)

        result = self.runner.invoke(self.commands['up'], ['1'], obj=self.context)
        self.assertEqual(0, result.exit_code)
        self.assertTrue(self.mock_migrations.return_value.up.called)

        result = self.runner.invoke(self.commands['up'],
                                    ['1', '--fake'], obj=self.context)
        self.assertEqual(0, result.exit_code)
        self.assertTrue(self.mock_migrations.return_value.up.called)

    def test_down(self):
        result = self.runner.invoke(self.commands['down'], obj=self.context)
        self.assertEqual(2, result.exit_code)

        result = self.runner.invoke(self.commands['down'], ['1'], obj=self.context)
        self.assertEqual(0, result.exit_code)
        self.assertTrue(self.mock_migrations.return_value.down.called)
