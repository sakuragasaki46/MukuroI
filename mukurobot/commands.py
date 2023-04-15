
import logging

from .client import Mukuro

_log : logging.Logger = logging.getLogger(__name__)


def add_commands(bot: Mukuro, *, exclude=()):
    '''Add commands, one by one.'''

    if 'economy' not in exclude:
        from .cogs.economy import EconomyCog
        bot.add_cog(EconomyCog(bot))

    if 'handbook' not in exclude:
        from .cogs.handbook import HandbookCog
        bot.add_cog(HandbookCog(bot))

    if 'guildconfig' not in exclude:
        from .cogs.guildconfig import GuildConfigCog
        bot.add_cog(GuildConfigCog(bot))

    if 'fun' not in exclude:
        from .cogs.fun import FunCog
        bot.add_cog(FunCog(bot))

    if 'bible' not in exclude:
        from .cogs.bible import BibleCog
        bot.add_cog(BibleCog(bot))

    if 'wiki' not in exclude:
        from .cogs.wiki import WikiCog
        bot.add_cog(WikiCog(bot))

    if 'meta' not in exclude:
        from .cogs.meta import MetaCog
        bot.add_cog(MetaCog(bot))


    # DO NOT INSERT NEW COMMANDS below this line! 

    return bot


