from playhouse.shortcuts import ReconnectMixin
from peewee import MySQLDatabase

class ReconnectMysqlDatabase(ReconnectMixin, MySQLDatabase):
    _reconnect_errors = ReconnectMixin.reconnect_errors

def connect_reconnect(db):
    if db.__class__ == MySQLDatabase:
        db.__class__ = ReconnectMysqlDatabase
    return db