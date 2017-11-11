# MongoEngine Migrations

## About

The applicaiton allows you to create, execute and rollback migrations for MongoDB.
The migration files stored in a specified `migrations` directory.
Each file contains up and down python methods.
After execution a record about migration is added to `db_migrations` mongo collection.

This package is a fork of https://bitbucket.org/letsignitcloud/flask-mongoengine-migrations by Andrey Zhukov.


## Usage

### Create migration

    alley <PATH to migrations directory> create <name>

Creates migration file `<id>_<name>.py` with empty up and down methods.


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
Before the `<PATH>` parameter, you'll need to specify your mongo connection.
    
    alley -db <database name> -u <user> -w <password> -a <authentication database> -h <host> -p <port> <PATH> <command>
    
    
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

    
    

## Tests

    python setup.py test
    
    
## Todo:

- Other ways to set mongo connection parameters.
- Auto-detect migration directory. 