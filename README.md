# Flask MongoEngine Migrations

## About

The applicaiton allows to create, execute and rollback migrations for MongoDB.
The migration files stored in `<application>/migrations` directory.
Each file contains up and down python methods.
After execution the record about migration is added to `migrations` mongo collection.


## Usage

### Create migration

    FLASK_APP=app.py flask migration_create <name>

Creates migration file `<id>_<name>.py` with empty up and down methods.


### Show status

    FLASK_APP=app.py flask migration_status

Show migrations available for execution.


### Run migration

    FLASK_APP=app.py flask migration_up

#### To specific migration

    FLASK_APP=app.py flask migration_up <migration_id>


#### Register migration, but skip execution

    FLASK_APP=app.py flask migration_up --fake


### Rollback migration

    FLASK_APP=app.py flask migration_down <migration_id>


## Test

    python setup.py test


## Examples

### Remove field

```
def up(db):
    db['some_collection'].update_many(
        {'some_field': {'$exists': True}},
        {'$unset': {'some_field': 1}}
    )
```
