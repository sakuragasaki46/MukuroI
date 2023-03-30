import datetime
import re
from peewee import *
from playhouse.db_url import connect
import os
from .utils import letter_range, superscript_number
from .dbutils import connect_reconnect

database = connect_reconnect(connect(os.environ['DATABASE_URL']))

class BaseModel(Model):
    class Meta:
        database = database
        table_function = lambda cls:f'{os.environ.get("DATABASE_PREFIX","")}{cls.__name__.lower()}'

class Player(BaseModel):
    # identification
    discord_id = BigIntegerField(unique=True)
    discord_name = CharField(64, default='')

    # economy
    balance = IntegerField(default=0)
    daily_streak = IntegerField(default=0)
    daily_streak_update = DateTimeField(null=True)

    # helpers
    @classmethod
    def from_object(cls, user):
        try:
            p = cls.get(cls.discord_id == user.id)
            if p.discord_name != user.name:
                p.discord_name = user.name
                p.save()
        except cls.DoesNotExist:
            p = cls.create(
                discord_id = user.id,
                discord_name = user.name
            )
        return p
    
    def update_daily_streak(self) -> int:
        inc = 0

        with database.atomic():
            then = self.daily_streak_update
            now = datetime.datetime.now()

            if then == None:
                inc = 50
                self.daily_streak = 1
            else:
                gap = (
                    (now - then).days -
                    ((now.hour, now.minute, now.second) <
                     (then.hour, then.minute, then.second))
                )

                if gap == 0:
                    if now.timestamp() // 5 - then.timestamp() // 5 > 0:
                        inc = 1
                elif gap == 1:
                    self.daily_streak += 1
                    inc = 8 + 2 * self.daily_streak
                else:
                    self.daily_streak = 1
                    inc = 10

            self.daily_streak_update = now
            self.balance += inc
            self.save()

        return inc


class GuildConfig(BaseModel):
    guild_id = BigIntegerField(unique=True)
    guild_name = CharField(64)

    main_channel_id = BigIntegerField(null=True)

    # helpers
    @classmethod
    def from_object(cls, guild):
        try:
            g = cls.get(cls.guild_id == guild.id)
            if g.guild_name != guild.name:
                g.guild_name = guild.name
                g.save()
        except cls.DoesNotExist:
            g = cls.create(
                guild_id = guild.id,
                guild_name = guild.name
            )
        return g
    
# RELIGION

class Bibbia(BaseModel):
    libro = CharField(5, null=True)
    capitolo = IntegerField(null=True)
    versetto = IntegerField(null=True)
    lettera = CharField(2, null=True)
    testo = CharField(3000, null=True)

    class Meta:
        primary_key = False

    @classmethod
    def get_versetto(cls, libro, capitolo, versetto, lettera=None):
        if lettera:
            return cls.get(
                (cls.libro == libro) &
                (cls.capitolo == capitolo) &
                (cls.versetto == versetto) &
                (cls.lettera == lettera)
            )
        return cls.get(
            (cls.libro == libro) &
            (cls.capitolo == capitolo) &
            (cls.versetto == versetto)
        )

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.libro} {self.capitolo}:{self.versetto}{self.lettera or ""}>'

    @classmethod
    def get_versetti(cls, v):
        return cls.select().where(cls._get_versetti_query(v))
    @classmethod
    def _get_versetti_query(cls, v):
        mobj = re.match(r'([A-Za-z]+) (\d+):(\d+)([a-z])?(?:-(\d+)([a-z])?)?((?:,(?:\d+:)?(?:\d+[a-z]?(?:-\d+[a-z]?)))*)', v)
        if mobj is None:
            raise ValueError('invalid or unsupported verse format')
        libro, capitolo, versetto, lettera, versetto2, lettera2, rest = mobj.groups()
        versetto = int(versetto)
        if versetto2 is not None:
            versetto2 = int(versetto2)
        check_query = (
            (cls.libro == libro) &
            (cls.capitolo == capitolo)
        )
        if versetto2 and versetto != versetto2:
            if lettera and lettera2 and lettera != lettera2:
                check_query &= (
                    (cls.versetto << range(versetto + 1, versetto2)) |
                    ((cls.versetto == versetto) &
                     (cls.lettera >= lettera)) |
                    ((cls.versetto == versetto2) &
                     (cls.lettera <= lettera2))
                )
            elif lettera:
                check_query &= (
                    (cls.versetto << range(versetto + 1, versetto2 + 1)) |
                    ((cls.versetto == versetto) &
                     (cls.lettera >= lettera))
                )
            elif lettera2:
                check_query &= (
                    (cls.versetto << range(versetto, versetto2)) |
                    ((cls.versetto == versetto2) &
                     (cls.lettera <= lettera2))
                )
            else:
                check_query &= (cls.versetto << range(versetto, versetto2+1))
        else:
            check_query &= (cls.versetto == versetto)
            if lettera:
                if lettera2 and lettera != lettera2:
                    check_query &= (cls.lettera << letter_range(lettera, lettera2))
                else:
                    check_query &= (cls.lettera == lettera)
        if rest:
            check_query |= cls._get_versetti_query(
                f'{libro} {rest}' if ':' in rest.split(',')[0]
                else f'{libro} {capitolo}:{rest}'
            )
        return check_query