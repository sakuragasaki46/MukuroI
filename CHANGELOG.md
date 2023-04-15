# Changelog

## 0.4

+ Added pronouns support. Pronouns can be stored on `Player` model or fetched from PronounDB.
+ Bots now can receive a role on their own.
+ `check_ip()` is now async.
+ Commands have been split into cogs.

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