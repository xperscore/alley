## About

Alley allows you to create, execute and rollback migrations for MongoDB in python using MongoEngine.

Migration files are stored in a specified `migrations` directory.
Each file contains up and down methods: python functions that receive the MongoEngine database connection.
After execution a record about the migration run is added to `db_migrations` mongo collection. 
Migrations can be run from the command line, such as in a deployment script, or imported. 

Forked from https://bitbucket.org/letsignitcloud/flask-mongoengine-migrations by Andrey Zhukov.

## Install

    pip install alley
    

## Usage

### Create migration

    alley <PATH to migrations parent directory> create <name>

Creates migration file `<id>_<name>.py` with no-op up and down methods. 
Also creates a `migrations` directory at this path if none exists.


### Show status

    alley <PATH> status

Show migrations available for execution.


### Run migration

    alley <PATH> up [migration_id]
    

Save migration as having been run, but skip execution:

    alley <PATH> up [migration_id] --fake


### Rollback migration

    alley <PATH> down <migration_id>

 
### Connecting to MongoDB
Before the `<PATH>` parameter, specify your mongo connection.
    
    alley -db <database name> -u <user> -w <password> -a <authentication database> -h <host> -p <port> <PATH> <command> [options]
    
    
----

To see all available command line options run:

    alley --help

## Examples

### Remove field

```
def up(db):
    db['your_collection'].update_many(
        {'some_field': {'$exists': True}},
        {'$unset': {'some_field': 1}}
    )
```

### Run migration from code
```
from mongoengine.connection import get_db, connect

connect(**connection_args)
db = get_db()
path = os.path.dirname(__file__) # where __file__ is a sibling of migrations/

Migrations(path, db).up()
```    
    

## Test

    python setup.py test
    
    
## Todo

- Other ways to set mongo connection parameters, such as environment variables.
- Auto-detect migration directory. 