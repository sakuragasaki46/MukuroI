from discord import Client, Embed, Member
import os

from . import CURRENCY_SYMBOL
from .models import Player, GuildConfig
from .security import is_bad_user

class Mukuro(Client):
    def __init__(self, *a, **ka):
        super().__init__(*a, **ka)
        self.plz_do_sync = False
        self.plz_check_ip = False
        self.is_dry_run = False
    async def setup_hook(self):
        if self.plz_do_sync:
            from .commands import ct
            await ct.sync()

        if self.is_dry_run:
            raise SystemExit('exit requested')
    async def on_ready(self):
        print(f'Logged in as \x1b[1m{self.user.name}#{self.user.discriminator}\x1b[22m')
        print(f'Started receiving messages…')
    async def on_message(self, message):
        print(
            'Message received in ' + (
               f'{message.guild.name} #{message.channel.name}' if message.guild else 'DM'
            ) +
            f' by {message.author.name}' +
            ('\x1b[35m(BOT)\x1b[39m' if message.author.bot else '')
        )
        if message.author.bot:
            return

        pl = Player.from_object(message.author)
        pl.update_daily_streak()
        
        if message.content:
            print(f'\x1b[32m{message.content}\x1b[39m')
    async def on_member_join(self, member: Member):
        print(f'Member joined: {member.name}')

        first_time = False

        if is_bad_user(member):
            try:
                await member.send(
                    f'Sei statə bannatə automaticamente da {member.guild.name} '
                    f'in quanto riconosciuto come malintenzionato/membro AOS.'
                )
            except Exception:
                print(f'Could not DM {member.guild.name}.')

            try:
                await member.guild.ban(member, reason='Bad actor/AOS member detected')
                print(f'Banned {member.name} ({member.id})')
            except Exception:
                print(f'\x1b[31mCould not ban {member.name} ({member.id})\x1b[39m')
        else:
            pl = Player.from_object(member)
            if not pl.daily_streak_update:
                first_time = True
            ds_inc = pl.update_daily_streak()
                
            gc = GuildConfig.from_object(member.guild)
            if gc.main_channel_id:
                main_channel = member.guild.get_channel(gc.main_channel_id)
            else:
                print('Main channel not set.')
                # retrieve main channel
                main_channel = member.guild.system_channel
                if main_channel:
                    gc.main_channel_id = main_channel.id
                    gc.save()
            
            if first_time and main_channel is not None:
                await main_channel.send(embed=Embed(
                    title='Benvenutə!',
                    description=f'{pl.discord_name}, sembra che sia la prima volta qui.\n' +
                    'Hai ricevuto {CURRENCY_SYMBOL} 50 come bonus 🥳'
                ))
    async def on_member_ban(self, guild, u):
        print(f'Member banned: {u.name}')

        gc = GuildConfig.from_object(guild)
        
        if gc.main_channel_id:
            main_channel = guild.get_channel(gc.main_channel_id)
        else:
            print('Main channel not set.')
            # retrieve main channel
            main_channel = guild.system_channel
            if main_channel:
                gc.main_channel_id = main_channel.id
                gc.save()
        
        await main_channel.send(embed=Embed(
            title='Membro bannato',
            description=f'{u.name} ({u.id}) è statə bannatə.',
            color=0xcc0000
        ))
                


