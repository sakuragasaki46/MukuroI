# Changelog

## 0.5

+ Schema changes: 
  + Added `description` and `ban_count` to `Player` table.
+ Moved event handlers to cogs, too.

## 0.4.1

+ Fixed i18n bug that prevented some commands from being usable in DM.
+ `/say` and `/guildconfig` are now guild-only.
+ Added GuildConfig cleanup on guild remove.
+ Fixed bug in `GuildConfig.set_config_key()`.
+ No logs were sent to traffic channel due to coroutines not being awaited. Fixed.
+ Botmaster is now notified of unscanned members on member join. Previously notifications
  were sent only when handbook commands were used.

## 0.4

+ Added pronouns support. Pronouns can be stored on `Player` model or fetched from PronounDB.
+ Bots now can receive a role on their own.
+ Commands have been split into cogs.
+ `/lore` renamed to `/wiki`.
+ Added pronouns, danger level and user avatar thumbnail to `/handbook` command.
+ Added handbook CLI, for use by the bot admin.
+ `badusers.txt` changed file format: it now is a list in format `<id>!<danger_level>`.
+ Fixed bug that allowed Macoto’s (coins) to be given by spamming. Additionally, you can now level up
  with guild messages only.
+ Botmaster gets now notified via DM whenever a user whose danger level is unassessed is discovered.
  Note: it means a new `DISCORD_BOTMASTER_ID` environment variable needs to be set.
+ `/say` now takes a `channel` argument, default to `cctv_channel_id`.
+ `check_ip()` is now async.
+ Users joining and leaving are now logged by setting `traffic_channel_id`.
+ `/stats` now shows number of users and guilds mapped.

## 0.3

+ Switched to `py-cord` framework, a fork of discord.py that does support subcommands.
+ Added `/stats`, `/rich`, `/guildconfig` and `/say` commands.
+ Added multiple sources to `/lore` command.
+ `/handbook` available as a context-menu command on users.
+ Basic I18n is introduced. Language can now be set on a per-guild basis.
+ Command descriptions are now internationalized in Italian and English.

## 0.2.1

+ Changed `connect_reconnect()` in `dbutils.py` to address some issues in Peewee + asyncio.

## 0.2

+ Enhanced guild configs.
+ Changed calls to `print()` to logging calls.
+ Added timers.
+ Added `utils.py`, `dbutils.py`, `dsutils.py` and `timers.py` modules.
+ Added `/bibbia` and `/lore` commands.

## 0.1.1

+ Minor fixes and improvements.

## 0.1

Initial version.
+ Added `/rr`, `/bal` and `/handbook` commands.