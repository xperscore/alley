import logging.config

import structlog
from mongoengine.connection import get_db, connect

from .migrations import Migrations

pre_chain = [
    structlog.stdlib.add_log_level,
]

logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "plain": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(colors=False),
            "foreign_pre_chain": pre_chain,
        },
        "colored": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(colors=True),
            "foreign_pre_chain": pre_chain,
        },
    },
    "handlers": {
        "default": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "colored",
        }
    },
        "loggers": {
            "": {
                "handlers": ["default"],
                "level": "DEBUG",
                "propagate": True,
            },
        }
})
structlog.configure(
    processors=[
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.KeyValueRenderer(),
    ],
    context_class=structlog.threadlocal.wrap_dict(dict),
    logger_factory=structlog.stdlib.LoggerFactory(),
)


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
