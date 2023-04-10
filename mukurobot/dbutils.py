from playhouse.shortcuts import ReconnectMixin
from peewee import MySQLDatabase, _ConnectionState
from contextvars import ContextVar

class ReconnectMysqlDatabase(ReconnectMixin, MySQLDatabase):
    _reconnect_errors = ReconnectMixin.reconnect_errors
    _reconnect_errors += ((0, ''),)


# async peewee helpers (from https://fastapi.tiangolo.com/advanced/sql-databases-peewee/ )

class PeeweeConnectionState(_ConnectionState):
    def __init__(self, **kwargs):
        super().__setattr__("_state", db_state)
        super().__init__(**kwargs)

    def __setattr__(self, name, value):
        self._state.get()[name] = value

    def __getattr__(self, name):
        return self._state.get()[name]

db_state_default = {"closed": None, "conn": None, "ctx": None, "transactions": None}
db_state = ContextVar("db_state", default=db_state_default.copy())

def connect_reconnect(db):
    if db.__class__ == MySQLDatabase:
        db.__class__ = ReconnectMysqlDatabase

    db._state = PeeweeConnectionState()
    
    return db

class ConnectToDatabase(object):
    def __init__(self, db):
        self.db = db
    async def __aenter__(self):
        self.db.connect(reuse_if_open=True)
        return self
    async def __aexit__(self, *a):
        self.db.close()