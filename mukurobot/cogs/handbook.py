'''
The (in)famous e-handbook.
Information about users, and beyond.

Privacy note: no PII is collected aside from discord ID, usernames, and pronouns,
and danger levels and descriptions are subjective.

(c) 2023 Sakuragasaki46
See LICENSE for license information
'''

import re
import logging
from discord import ApplicationContext, ButtonStyle, Embed, Message, Option, User, slash_command, user_command
from discord.ui import View, button
from discord.ext.commands import Cog

from ..dbutils import ConnectToDatabase
from ..models import database, Player
from ..i18n import get_language_from_ctx
from ..dsutils import dm_botmaster, is_botmaster
from ..utils import money
from ..models import Player
from ..inclusion import fetch_pronouns, Pronouns

_log = logging.getLogger(__name__)

class HandbookView(View):
    def __init__(self, user: int):
        super().__init__(timeout=None)
        self.user = user

    @button(label='Fact File', row=0, style=ButtonStyle.blurple)
    async def button_callback(self, button, interaction):
        T = get_language_from_ctx(interaction)

        async with ConnectToDatabase(database):
            pl = Player.from_object(self.user)

            if pl.pronouns:
                pronouns = Pronouns(pl.pronouns)
            else:
                pronouns = None

            embed = Embed(
                title=(
                    T('ehandbook-of-pronouns').format(name=pl.discord_name, pronouns=pronouns)
                    if pronouns else
                    T('ehandbook-of').format(name=pl.discord_name)
                ),
                color=(
                    0x990000 if pl.danger_level == 5 else
                    0xee5500 if pl.danger_level == 4 else
                    0x990099 if pl.danger_level == 3 else
                    0x0033ff
                )
            )
            embed.add_field(name=T("ban-count"), value=f'{pl.ban_count}')
            if pl.description:
                embed.add_field(name=T("description"), value=pl.description)
            
            if self.user.avatar:
                embed.set_thumbnail(url=self.user.avatar.url)

            await interaction.response.send_message(
                embed=embed
            )

class HandbookCog(Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # List of users with no danger level set.
        # It resets on every startup, and I’m fine with it
        self.dmd_ids = []
    
    @slash_command(
        name='handbook', description='Apri il tuo e-handbook.',
        description_localizations={
            'en-US': 'Open your e-handbook.',
            'en-GB': 'Open your e-handbook.',
            'fr': 'Ouvre ton manuel électronique.',
            'it': 'Apri il tuo e-handbook.'
        },
        options=[
            Option(User, name='u', value='L’utente.', required=False)
        ]
    )
    async def cmd_handbook(self, inter: ApplicationContext, u: User = None):
        T = get_language_from_ctx(inter)
        u = u or inter.user
        pl: Player = Player.from_object(u)

        await inter.response.defer()

        if pl.pronouns:
            pronouns = Pronouns(pl.pronouns)
        else:
            pronouns = await fetch_pronouns(pl.discord_id)
            pl.pronouns = pronouns.short
            pl.save()

        embed = Embed(
            title=(
                T('ehandbook-of-pronouns').format(name=pl.discord_name, pronouns=pronouns)
                if pronouns else
                T('ehandbook-of').format(name=pl.discord_name)
            ),
            color=(
                0x990000 if pl.danger_level == 5 else
                0xee5500 if pl.danger_level == 4 else
                0x990099 if pl.danger_level == 3 else
                0x0033ff
            )
        )
        embed.add_field(name='ID', value=pl.discord_id)
        embed.add_field(name=T('balance'), value=f'{money(pl.balance)}')
        if not u.bot:
            embed.add_field(name=T('danger-level'), value=f'`{pl.danger_level_str}`')

        if u.avatar:
            embed.set_thumbnail(url=u.avatar.url)

        await inter.followup.send(embed=embed, view=HandbookView(u))

        if not u.bot and pl.danger_level == 0 and pl.discord_id not in self.dmd_ids:
            await dm_botmaster(
                f'Someone requested information for a user whose danger level is not assessed yet.\n'
                f'Please investigate on this user: {pl.discord_name} <@{pl.discord_id}> ID `{pl.discord_id}`\n'
                f'Once you’re done, please reply with:\n'
                f'`!dan {pl.discord_id}`\n'
                f'followed by the danger level (1-5).'
            )

            self.dmd_ids.append(pl.discord_id)

            if len(self.dmd_ids) > 50:
                self.dmd_ids.pop(0)

    
    cmd_handbook_menu = user_command(
        name='Apri E-Handbook',
        name_localizations={
            'en-US': 'Open E-Handbook',
            'en-GB': 'Open E-Handbook',
            'it': 'Apri E-Handbook',
            'fr': 'Ouvre le manuel électronique'
        }
    )(cmd_handbook)

    # Secret command handler.
    @Cog.listener()
    async def on_message(self, message: Message):
        if not message.guild and is_botmaster(message.author):
            # secret botmaster-only commands
            # XXX is it the best way?
            if mg := re.match(r'!dan +(\d+) +([1-5])(?: *: *(.+))', message.content):
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
                    if mg.group(3):
                        pl.description = mg.group(3)
                    pl.save()
                    _log.info(f'player {pl.discord_id} danger level updated to {pl.danger_level}')
                    
                    try:
                        await message.add_reaction('✅')
                    except Exception:
                        pass

