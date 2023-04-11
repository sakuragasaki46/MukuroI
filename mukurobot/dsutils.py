from discord import Interaction, Permissions
from .models import GuildConfig
import logging

_log = logging.getLogger(__name__)

from . import get_client

async def lockdown_guild(gc: GuildConfig):
    client = get_client()

    if not client:
        return

    guild = client.get_guild(gc.guild_id)

    try:
        default_role = guild.default_role
        default_role.permissions.update(
            send_messages=False,
            send_messages_in_threads=False,
            add_reactions=False
        )
        await default_role.edit(permissions=default_role.permissions, reason='lockdown guild')

        if gc.main_role_id:
            main_role = guild.get_role(gc.main_role_id)
            main_role.permissions.update(
                send_messages=False,
                send_messages_in_threads=False,
                add_reactions=False
            )
            await main_role.edit(permissions=main_role.permissions, reason='lockdown guild')
    except Exception:
        _log.error(f'Could not lockdown guild {guild.id}')

async def unlockdown_guild(gc: GuildConfig):
    client = get_client()

    if not client:
        return

    guild = client.get_guild(gc.guild_id)

    try:
        if gc.main_role_id:
            main_role = guild.get_role(gc.main_role_id)
            main_role.permissions.update(
                send_messages=True,
                send_messages_in_threads=True,
                add_reactions=True
            )
            await main_role.edit(permissions=main_role.permissions, reason='unlockdown guild')

        default_role = guild.default_role
        default_role.permissions.update(
            send_messages=True,
            send_messages_in_threads=True,
            add_reactions=True
        )
        await default_role.edit(permissions=default_role.permissions, reason='unlockdown guild')
    except Exception:
        _log.error(f'Could not unlockdown guild {guild.id}')
    
async def you_do_not_have_permission(inter: Interaction):
    return await inter.response.send_message(
        'Non hai i permessi per eseguire questo comando!',
        ephemeral=True
    )