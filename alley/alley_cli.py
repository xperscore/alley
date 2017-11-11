import click

from alley import MongoMigrations


@click.group()
@click.argument('path', type=click.Path(exists=True, file_okay=False, writable=True, resolve_path=True))
@click.option('--database', '-db')
@click.option('--username', '-u')
@click.option('--password', '-w')
@click.option('--host', '-h')
@click.option('--port', '-p', type=int)
@click.option('--auth', '-a')
@click.pass_context
def cli(ctx, path, database, username, password, host=None, port=None, auth=None):
    ctx.obj = MongoMigrations(path, database, username, password, host=host, port=port, auth=auth)


@cli.command()
@click.pass_obj
def status(ctx):
    migrations = ctx.migrations
    migrations.show_status()


@cli.command()
@click.argument('name')
@click.pass_obj
def create(ctx, name):
    migrations = ctx.migrations
    migrations.create(name)


@cli.command()
@click.argument('migration_id', required=False)
@click.option('--fake', is_flag=True, help="Migration to run up to")
@click.pass_obj
def up(ctx, migration_id=None, fake=False):
    migrations = ctx.migrations
    migrations.up(migration_id, fake)


@cli.command()
@click.argument('migration_id')
@click.pass_obj
def down(ctx, migration_id):
    migrations = ctx.migrations
    migrations.down(migration_id)

