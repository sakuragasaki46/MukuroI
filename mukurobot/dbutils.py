from playhouse.shortcuts import ReconnectMixin
from peewee import MySQLDatabase

class ReconnectMysqlDatabase(ReconnectMixin, MySQLDatabase):
    pass

def connect_reconnect(db):
    if db.__class__ == MySQLDatabase:
        db.__class__ = ReconnectMysqlDatabase
    return db