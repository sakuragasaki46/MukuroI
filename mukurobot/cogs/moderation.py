'''
Time for banhammer.

(c) 2023 Sakuragasaki46
See LICENSE for license info
'''


from typing import Optional
from discord import ApplicationContext, ButtonStyle, Cog, Guild, Interaction, Member, Option, Permissions, User, slash_command
from discord.ui import View, button
import logging

from ..dsutils import you_do_not_have_permission
from ..models import Player

_log = logging.getLogger(__name__)


async def ban_user(inter: Interaction, guild: Guild, u: User, reason: Optional[str] = None, dm: bool = False):
    if dm and isinstance(u, Member):
        try:
            await u.send(
                f"Sei statə bannatə da **{inter.guild.name}**.\n" + 
                (f"Il moderatore che ha eseguito il ban ha specificato la seguente ragione:\n"
                f"{reason}" if reason else "")
            )
        except Exception:
            dm = False

    try:
        await guild.ban(
            u,
            delete_message_days=0,
            reason=f"Banned by {inter.author.name}#{inter.author.discriminator}: {reason}"
        )
        await inter.response.send_message(
            "Membro bannato." +
            ("L’utente è stato notificato." if dm else ""),
        )
    except Exception:
        await inter.response.send_message(
            "Impossibile bannare il membro.",
            ephemeral=True
        )

class BanView(View):
    def __init__(self, guild: Guild, user: User, reason: Optional[str] = None, dm: bool = False):
        super().__init__(timeout=30.0, disable_on_timeout=True)
        self.user = user
        self.reason = reason
        self.dm = dm
        self.guild = guild
    
    @button(label="Ban", row=0, style=ButtonStyle.danger)
    async def button_callback(self, button, interaction):
        if interaction.author == self.user:
            await interaction.response.send_message(
                'Stai cercando di bannarti da solə, sei davvero così stupidə?',
                ephemeral=True
            )
            return

        if not interaction.author.guild_permissions.ban_members:
            return await you_do_not_have_permission(interaction)

        await self.user.ban(interaction, self.guild, self.user, reason=self.reason, dm=self.dm)

class ModerationCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    
    @slash_command(
        name='ban', description='Banna un utente',
        description_localizations={
            'en-US': 'Ban a user',
            'en-GB': 'Ban a user',
            'it': 'Banna un utente'
        },
        options = [
            Option(User, name="u", description="L’utente"),
            Option(str, name="reason", description="La ragione del ban.", required=False),
            Option(bool, name="dm", description="Notifica il membro bannato.", required=False)
        ],
        dm_permission=False
    )
    async def cmd_ban(self, inter: ApplicationContext, u: User, reason: Optional[str] = None, dm: bool = False):
        if inter.author == u:
            await inter.response.send_message(
                'Stai cercando di bannarti da solə, sei davvero così stupidə?',
                ephemeral=True
            )
            return

        if not inter.author.guild_permissions.ban_members:
            return await you_do_not_have_permission(inter)

        pl = Player.from_object(u)

        if pl.danger_level < 4:
            await inter.response.send_message(
                f"Bannare {u.name}#{u.discriminator}?",
                view=BanView(inter.guild, u, reason=reason, dm=dm),
                ephemeral=True
            )
        else:
            await ban_user(inter, inter.guild, u, reason=reason, dm=dm)

    cmd_ban.default_member_permissions = Permissions(
        ban_members=True
    )

