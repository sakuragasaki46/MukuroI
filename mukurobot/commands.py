'''
Yes, Your Highness!

(c) 2023 Sakuragasaki46
See LICENSE for license information
'''


from .client import Mukuro

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

    if 'traffic' not in exclude:
        from .cogs.traffic import TrafficCog
        bot.add_cog(TrafficCog(bot))

    if 'levels' not in exclude:
        from .cogs.levels import LevelsCog
        bot.add_cog(LevelsCog(bot))

    # DO NOT INSERT NEW COGS below this line! 

    return bot


