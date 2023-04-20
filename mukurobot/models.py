'''
Someone said… models? Look at my cosplay of Junko Enoshima :)
'''

import datetime
import re
from discord import Guild, User
from peewee import *
from playhouse.db_url import connect
import os
import logging

from .i18n import get_language
from .utils import letter_range
from .dbutils import connect_reconnect
from itertools import islice

_log = logging.getLogger(__name__)

database = connect_reconnect(connect(os.environ['DATABASE_URL']))

class BaseModel(Model):
    class Meta:
        database = database
        table_function = lambda cls:f'{os.environ.get("DATABASE_PREFIX","")}{cls.__name__.lower()}'

DANGER_LEVELS = {
    0: 'Unscanned',
    1: 'Innocent',
    2: 'Safe',
    3: 'Suspicious',
    4: 'Dangerous',
    5: 'Deathly'
}

class Player(BaseModel):
    # identification
    discord_id = BigIntegerField(unique=True)
    discord_name = CharField(64, default='')
    pronouns = CharField(16, null=True)

    # economy
    balance = IntegerField(default=0)
    daily_streak = IntegerField(default=0)
    daily_streak_update = DateTimeField(null=True)

    # security (to be compiled by admins)
    danger_level = SmallIntegerField(default=0)

    # helpers
    @classmethod
    def from_object(cls, user: User):
        try:
            p = cls.get(cls.discord_id == user.id)
            if user.name is not None and p.discord_name != user.name:
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

                _log.debug(f'then: {then}, now: {now}, gap: {gap}')

                if gap == 0:
                    if now.timestamp() // 300 - then.timestamp() // 300 > 0:
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

    @property
    def danger_level_str(self):
        return DANGER_LEVELS[self.danger_level]


GC_NONE = 0
GC_TRANSITIONAL = 1
GC_STRICT = 2

class GuildConfig(BaseModel):
    CONFIGKEYS = (
        'main_channel_id',
        'main_role_id',
        'cctv_channel_id',
        'daytime_start',
        'daytime_end',
        'language',
        'bot_role_id',
        'risk_checking',
        'traffic_channel_id'
    )

    guild_id = BigIntegerField(unique=True)
    guild_name = CharField(64)

    main_channel_id = BigIntegerField(null=True)
    main_role_id = BigIntegerField(null=True)
    cctv_channel_id = BigIntegerField(null=True)
    daytime_start = IntegerField(default=7 * 60, null=True)
    daytime_end = IntegerField(default=23 * 60, null=True)
    language = CharField(16, default='en')
    bot_role_id = BigIntegerField(null=True)
    risk_checking = SmallIntegerField(default=GC_TRANSITIONAL)
    traffic_channel_id = BigIntegerField(null=True)


    # helpers
    @classmethod
    def from_object(cls, guild: Guild):
        try:
            g = cls.get(cls.guild_id == guild.id)
            if g.guild_name != guild.name:
                g.guild_name = guild.name
                g.save()
        except cls.DoesNotExist:
            g = cls.create(
                guild_id = guild.id,
                guild_name = guild.name,
                language = guild.preferred_locale or 'en'
            )
        return g
    
    @classmethod
    def get_config_keys(cls, autocomplete=''):
        return islice(filter(lambda x:autocomplete in x, cls.CONFIGKEYS), 0, 25)

    def set_config_key(self, k: str, v: str):
        if not k in self.CONFIGKEYS:
            return None

        if isinstance(getattr(self, k), (SmallIntegerField, IntegerField, BigIntegerField)) and not v.isdigit():
            if mg := re.match(r'(\d+):(\d+)', v):
                v = int(mg.group(1)) * 60 + int(mg.group(2))
            else:
                try:
                    v = int(re.search(r'(\d+)', v).group(1))
                except Exception:
                    return None

        setattr(self, k, v)
        self.save()
        return v

    def get_translate(self):
        return get_language(self.language)

    def check_bad_user(self, pl: Player) -> bool:
        return pl.danger_level >= 5 or (
            self.risk_checking >= GC_STRICT and pl.danger_level == 4
        )


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