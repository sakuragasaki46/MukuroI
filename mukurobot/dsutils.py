import os
from discord import Interaction, Permissions, User
from .models import GuildConfig, Player
import logging

_log = logging.getLogger(__name__)
_botmaster = None

from .client import get_client

async def lockdown_guild(gc: GuildConfig):
    client = get_client()

    if not client:
        return

    guild = client.get_guild(gc.guild_id)

    if guild is None:
        _log.error(f'Guild {gc.guild_id} not in cache')
        return

    try:
        default_role = guild.default_role
        perms = default_role.permissions
        perms.update(
            send_messages=False,
            send_messages_in_threads=False,
            add_reactions=False
        )
        await default_role.edit(permissions=perms, reason='lockdown guild')

        if gc.main_role_id:
            main_role = guild.get_role(gc.main_role_id)
            perms = main_role.permissions
            perms.update(
                send_messages=False,
                send_messages_in_threads=False,
                add_reactions=False
            )
            await main_role.edit(permissions=perms, reason='lockdown guild')
    except Exception:
        _log.error(f'Could not lockdown guild {gc.guild_id}')

async def unlockdown_guild(gc: GuildConfig):
    client = get_client()

    if not client:
        return

    guild = client.get_guild(gc.guild_id)

    if guild is None:
        _log.error(f'Guild {gc.guild_id} not in cache')
        return

    try:
        if gc.main_role_id:
            main_role = guild.get_role(gc.main_role_id)
            perms = main_role.permissions
            perms.update(
                send_messages=True,
                send_messages_in_threads=True,
                add_reactions=True
            )
            await main_role.edit(permissions=perms, reason='unlockdown guild')

        default_role = guild.default_role
        perms = default_role.permissions
        perms.update(
            send_messages=True,
            send_messages_in_threads=True,
            add_reactions=True
        )
        await default_role.edit(permissions=perms, reason='unlockdown guild')
    except Exception:
        _log.error(f'Could not unlockdown guild {gc.guild_id}')
    
async def you_do_not_have_permission(inter: Interaction):
    return await inter.response.send_message(
        'Non hai i permessi per eseguire questo comando!',
        ephemeral=True
    )


async def get_botmaster():
    global _botmaster

    if not _botmaster:
        client = get_client()

        if not client:
            return

        _botmaster = await client.get_or_fetch_user(os.getenv('DISCORD_BOTMASTER_ID'))
        
    return _botmaster

def is_botmaster(u: User):
    if 'DISCORD_BOTMASTER_ID' not in os.environ:
        return False
    return int(os.environ['DISCORD_BOTMASTER_ID']) == u.id


async def dm_botmaster(msg: str):
    '''Notifies the botmaster.
    Useful for missing information.
    '''
    botmaster = await get_botmaster()
    if not botmaster:
        _log.error('botmaster user not found')
        return

    try:
        await botmaster.send(msg)
    except Exception:
        _log.warn('Could not send message to botmaster')
