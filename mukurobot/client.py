import re
from discord import Bot, Embed, Member, Message
import os
import logging

_log : logging.Logger = logging.getLogger(__name__)

from .utils import money
from .models import Player, GuildConfig, database
from .security import is_bad_user
from .dbutils import ConnectToDatabase

_client = None

class Mukuro(Bot):
    def __init__(self, *a, **ka):
        super().__init__(*a, **ka)
        self.plz_check_ip = False
        self.is_dry_run = False
    async def setup_hook(self):
        pass
    async def on_ready(self):
        _log.info(f'Logged in as \x1b[1m{self.user.name}#{self.user.discriminator}\x1b[22m')

        if self.is_dry_run:
            exit()

        _log.info(f'Started receiving messages…')
    async def on_message(self, message: Message):
        # Message content is not needed at the moment, except in DM.
        _log.info(
            'Message received in ' + (
               f'{message.guild.name} #{message.channel.name}' if message.guild else 'DM'
            ) +
            f' by {message.author.name}' +
            ('\x1b[35m (BOT)\x1b[39m' if message.author.bot else '')
        )
        if message.author.bot:
            return
        
        if message.guild:
            async with ConnectToDatabase(database):
                pl = Player.from_object(message.author)
                pl.update_daily_streak()
        
        if message.content:
            _log.debug(f'\x1b[32m{message.content}\x1b[39m')

        if not message.guild and is_botmaster(message.author):
            # secret botmaster-only commands
            # XXX is it the best way?
            if mg := re.match(r'!dan +(\d+) +([1-5])', message.content):
                uid, level = int(mg.group(1)), int(mg.group(2))
                async with ConnectToDatabase(database):
                    try:
                        pl = Player.get(Player.discord_id == uid)
                    except Player.DoesNotExist:
                        pl = Player.create(
                            discord_id = uid,
                            discord_name = f'<@{uid}>'
                        )
                    pl.danger_level = level
                    pl.save()
                    _log.info(f'player {pl.discord_id} danger level updated to {pl.danger_level}')
    async def on_member_join(self, member: Member):
        ## WARNING This requires a Privileged Intent.
        ## When this bot reaches 100 servers, this event handler’s code
        ## may vanish.
        async with ConnectToDatabase(database):
            gc = GuildConfig.from_object(member.guild)

            _log.info(f'Member joined: {member.name}')

            first_time = False
            
            if member.bot:
                bot_role = member.guild.get_role(gc.bot_role_id)

                if bot_role:
                    await member.add_role(bot_role)
            elif gc.check_bad_user(pl := Player.from_object(member)):
                try:
                    await member.send(
                        f'Sei statə bannatə automaticamente da {member.guild.name} '
                        f'in quanto riconosciuto come malintenzionato/membro AOS.'
                    )
                except Exception:
                    _log.warn(f'Could not DM {member.guild.name}.')

                try:
                    await member.guild.ban(member, reason='Bad actor/AOS member detected')
                    _log.info(f'Banned {member.name} ({member.id})')
                except Exception:
                    _log.error(f'\x1b[31mCould not ban {member.name} ({member.id})\x1b[39m')
            else:
                if not pl.daily_streak_update:
                    first_time = True
                ds_inc = pl.update_daily_streak()
                
                if gc.main_channel_id:
                    main_channel = member.guild.get_channel(gc.main_channel_id)
                else:
                    _log.warn('Main channel not set. Checking if there is a system channel…')
                    # retrieve main channel
                    main_channel = member.guild.system_channel
                    if main_channel:
                        gc.main_channel_id = main_channel.id
                        gc.save()
                    else:
                        _log.warn('No system channel found.')
                
                if first_time and main_channel is not None:
                    await main_channel.send(embed=Embed(
                        title='Benvenutə!',
                        description=f'{pl.discord_name}, sembra che sia la prima volta qui.\n' +
                        f'Hai ricevuto {money(50)} come bonus 🥳'
                    ))
        
    async def on_member_ban(self, guild, u):
        async with ConnectToDatabase(database):
            _log.info(f'Member banned: {u.name}')

            gc = GuildConfig.from_object(guild)
            
            if gc.main_channel_id:
                main_channel = guild.get_channel(gc.main_channel_id)
            else:
                _log.warn('Main channel not set. Checking if there is a system channel…')
                # retrieve main channel
                main_channel = guild.system_channel
                if main_channel:
                    gc.main_channel_id = main_channel.id
                    gc.save()
                else:
                    _log.warn('No system channel found.')
            
            await main_channel.send(embed=Embed(
                title='Membro bannato',
                description=f'{u.name} ({u.id}) è statə bannatə.',
                color=0xcc0000
            ))
    async def on_interaction(self, interaction):
        async with ConnectToDatabase(database):
            await super().on_interaction(interaction)    
                   
def get_client() -> Mukuro | None:
    return _client

def set_global_client(client: Mukuro) -> Mukuro:
    global _client

    if not isinstance(client, Mukuro):
        raise TypeError(f'only instances of {Mukuro.__class__.__name__} allowed!')

    _client = client
    return client

# here because of circular imports
from .dsutils import is_botmaster
