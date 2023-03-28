import datetime
from peewee import *
from playhouse.db_url import connect
import os

database = connect(os.environ['DATABASE_URL'])

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
    
