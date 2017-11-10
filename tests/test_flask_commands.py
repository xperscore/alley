import os
from unittest import TestCase
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from flask import Flask
from flask_mongoengine import MongoEngine
from flask_mongoengine_migrations import FlaskMigrations

app = Flask(__name__)
MongoEngine(app)


class InitTests(TestCase):

    @patch('flask_mongoengine_migrations.logger')
    def test_no_mongoengine(self, mock_logger):
        app = Flask(__name__)
        FlaskMigrations(app)
        self.assertTrue(mock_logger.error.called)

    def test_commands_registered(self):
        FlaskMigrations(app)
        self.commands = app.cli.commands.keys()
        self.assertTrue('migration_status' in self.commands)
        self.assertTrue('migration_create' in self.commands)
        self.assertTrue('migration_up' in self.commands)
        self.assertTrue('migration_down' in self.commands)


class CommandsTests(TestCase):

    def setUp(self):
        os.environ['FLASK_APP'] = 'tests.test_flask_commands'

        self.mock_migrations_patcher = patch(
            "flask_mongoengine_migrations.Migrations")
        self.addCleanup(self.mock_migrations_patcher.stop)
        self.mock_migrations = self.mock_migrations_patcher.start()
        self.mock_migrations.return_value = MagicMock()

        FlaskMigrations(app)
        self.commands = app.cli.commands

        self.runner = CliRunner()

    def test_status(self):
        result = self.runner.invoke(self.commands['migration_status'])
        self.assertEqual(0, result.exit_code)
        self.assertTrue(self.mock_migrations.return_value.show_status.called)

    def test_create(self):
        result = self.runner.invoke(self.commands['migration_create'])
        self.assertEqual(2, result.exit_code)

        result = self.runner.invoke(self.commands['migration_create'],
                                    ['name'])
        self.assertEqual(0, result.exit_code)
        self.assertTrue(self.mock_migrations.return_value.create.called)

    def test_up(self):
        result = self.runner.invoke(self.commands['migration_up'])
        self.assertEqual(0, result.exit_code)
        self.assertTrue(self.mock_migrations.return_value.up.called)

        result = self.runner.invoke(self.commands['migration_up'], ['1'])
        self.assertEqual(0, result.exit_code)
        self.assertTrue(self.mock_migrations.return_value.up.called)

        result = self.runner.invoke(self.commands['migration_up'],
                                    ['1', '--fake'])
        self.assertEqual(0, result.exit_code)
        self.assertTrue(self.mock_migrations.return_value.up.called)

    def test_down(self):
        result = self.runner.invoke(self.commands['migration_down'])
        self.assertEqual(2, result.exit_code)

        result = self.runner.invoke(self.commands['migration_down'], ['1'])
        self.assertEqual(0, result.exit_code)
        self.assertTrue(self.mock_migrations.return_value.down.called)
