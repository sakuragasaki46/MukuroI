"""Peewee migrations -- 001_init_db.py.

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
    class BaseModel(pw.Model):
        id = pw.AutoField()

        class Meta:
            table_name = "basemodel"

    @migrator.create_model
    class GuildConfig(pw.Model):
        id = pw.AutoField()
        guild_id = pw.BigIntegerField(unique=True)
        guild_name = pw.CharField(max_length=64)
        main_channel_id = pw.BigIntegerField(null=True)

        class Meta:
            table_name = "guildconfig"

    @migrator.create_model
    class Player(pw.Model):
        id = pw.AutoField()
        discord_id = pw.BigIntegerField(unique=True)
        discord_name = pw.CharField(constraints=[SQL("DEFAULT ''")], default='', max_length=64)
        balance = pw.IntegerField(constraints=[SQL("DEFAULT 0")], default=0)
        daily_streak = pw.IntegerField(constraints=[SQL("DEFAULT 0")], default=0)
        daily_streak_update = pw.DateTimeField(null=True)

        class Meta:
            table_name = "player"


def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    """Write your rollback migrations here."""
    
    migrator.remove_model('player')

    migrator.remove_model('guildconfig')

    migrator.remove_model('basemodel')
