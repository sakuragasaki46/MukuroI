'''
A sort of calendar.

(c) 2023 Sakuragasaki46
See LICENSE for license info
'''


from typing import Optional
from discord import ApplicationContext, Cog, Option, slash_command
from discord.abc import GuildChannel
import logging
import re

from ..utils import parseInt, parse_date_and_hour
from ..models import Meeting, Player, database
from ..i18n import get_language_from_ctx, lang_join
from ..dsutils import is_botmaster, you_do_not_have_permission

_log = logging.getLogger(__name__)


class PlannerCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(
        name='plan', description='Pianifica un incontro.',
        description_localizations={
            'en-US': 'Plan a meeting',
            'en-GB': 'Plan a meeting',
            'it': 'Pianifica un incontro'
        },
        options=[
            Option(str, name='dt', description='Data e ora dell’incontro.'),
            Option(str, name='reason', description="La ragione dell’incontro."),
            Option(str, name="with", description="Utenti o nomi coi quali vedersi.", required=False),
            Option(GuildChannel, name="channel", description="Canale dove mandare il promemoria.", required=False)
        ]
    )
    async def cmd_plan(self, ctx: ApplicationContext, dt: str, reason: str, with_: Optional[str] = None, channel: Optional[GuildChannel] = None):
        T = get_language_from_ctx()

        _log.debug(f"{dt=}, {reason=}, {with_=}, {channel=}")

        try:
            dt = parse_date_and_hour(dt)
        except Exception:
            await ctx.response.send_message(
                T("invalid-date-time"),
                ephemeral=True
            )
            return

        with_ = with_ or ""
        mention_list = re.findall(r"<@!?\d+>", with_)
        name_list = re.sub(r"<@!?\d+>", '', with_).strip().split(",")
        
        if not is_botmaster(ctx.author):
            await you_do_not_have_permission()


        with database.atomic():
            try:
                meeting = Meeting.create(
                    planned_at = dt,
                    host = Player.from_object(ctx.author),
                    reason = reason,
                    notify_channel = channel.id if channel else None
                )
                for i in mention_list:
                    meeting.add_guest(id=parseInt(i))
                for n in name_list:
                    meeting.add_guest(name=n)
            except Exception as e:
                database.rollback()

                _log.warn(f"Exception caught: {e.__class__.__name__}: {e}")

                await ctx.response.send_message(
                    "Impossibile creare l’evento (probabilmente a causa di un conflitto)",
                    ephemeral=True
                )

                return
        
        dm = True

        await ctx.response.send_message(
            "Evento creato!\n"
            f"Dettagli: **{meeting.reason}** (<t:{int(meeting.planned_at.timestamp())}>)\n"
            "Sarai ricordato di esso " +
            lang_join(T, [
                "in DM" if dm else None,
                f"nel canale {channel.mention}" if channel else None
            ]) + ".",
            ephemeral=True
        )

