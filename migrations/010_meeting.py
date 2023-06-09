"""Peewee migrations -- 010_meeting.py.

Some examples (model - class or model name)::

    > Model = migrator.orm['table_name']            # Return model in current state by name
    > Model = migrator.ModelClass                   # Return model in current state by name

    > migrator.sql(sql)                             # Run custom SQL
    > migrator.python(func, *args, **kwargs)        # Run python code
    > migrator.create_model(Model)                  # Create a model (could be used as decorator)
    > migrator.remove_model(model, cascade=True)    # Remove a model
    > migrator.add_fields(model, **fields)          # Add fields to a model
    > migrator.change_fields(model, **fields)       # Change fields
    > migrator.remove_fields(model, *field_names, cascade=True)
    > migrator.rename_field(model, old_field_name, new_field_name)
    > migrator.rename_table(model, new_table_name)
    > migrator.add_index(model, *col_names, unique=False)
    > migrator.drop_index(model, *col_names)
    > migrator.add_not_null(model, *field_names)
    > migrator.drop_not_null(model, *field_names)
    > migrator.add_default(model, field_name, default)

"""

import peewee as pw
from peewee_migrate import Migrator
from decimal import ROUND_HALF_EVEN

try:
    import playhouse.postgres_ext as pw_pext
except ImportError:
    pass

SQL = pw.SQL


def migrate(migrator: Migrator, database: pw.Database, *, fake=False):
    """Write your migrations here."""

    @migrator.create_model
    class Meeting(pw.Model):
        id = pw.AutoField()
        planned_at = pw.DateTimeField()
        host = pw.ForeignKeyField(column_name='host_id', field='id', model=migrator.orm['player'])
        reason = pw.CharField(max_length=64)
        notify_channel = pw.BigIntegerField(null=True)

        class Meta:
            table_name = "meeting"
            indexes = [(('planned_at', 'host'), True)]

    @migrator.create_model
    class MeetingGuest(pw.Model):
        id = pw.AutoField()
        meeting = pw.ForeignKeyField(column_name='meeting_id', field='id', model=migrator.orm['meeting'])
        guest_id = pw.BigIntegerField(null=True)
        guest_name = pw.CharField(max_length=32, null=True)

        class Meta:
            table_name = "meetingguest"
            indexes = [(('meeting', 'guest_id', 'guest_name'), True)]


def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    """Write your rollback migrations here."""

    migrator.remove_model('meetingguest')

    migrator.remove_model('meeting')
