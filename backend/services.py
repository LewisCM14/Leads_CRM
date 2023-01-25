"""Database Connection"""

import database as _database


def create_database():
    """Create Database"""

    return _database.Base.metadata.create_all(bind=_database.engine)
