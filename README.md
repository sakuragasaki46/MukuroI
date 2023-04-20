# MukuroI

A discord bot for security and fun.

Yes, I made it thinking about the “16th student”, althought I am ~~not~~ a kinnie of that character.

This is the codebase for Yusurland Security bot.

It provides autoban based on user lists and a cool minigame (coming soon).

Note: the bot’s messages are mostly in Italian.

## Guild config

Once you added the bot to your guild, you have to configure it (run `/guildconfig view` to see possible options).

The configurable variables are:

* **Main Channel**: The main channel, usually `#general` or the system logs channel.
* **CCTV Channel**: The announcement channel.
* **Main Role**: The User role. This and the `@everyone` role are locked down at daytime end,
  and unlocked at daytime start.
* **Daytime Start**: The unlockdown hour, in UTC format. It means you have to add or subtract hours
  according to your time zone. Moreover, only precise quarter hours work (i.e. `:00`, `:15`, `:30` and `:45`)
* **Daytime End**: The lockdown hour, in UTC format. Same considerations as above.
* **Language**: The guild locale. Currently supported are Italian and English locale.
* **Bot role**: The role assigned to all bots.
* **Risk checking**: transitional (1), strict (2) or disabled (0). Defaults to transitional.
* **Traffic channel**: The channel used to log joins/leaves.

## Deployment

The bot requires Python 3.10+ and a Unix-derived system in order to run.

Recommended steps:

* Create a virtualenv: `python3 -m venv venv`
* Activate the virtualenv: `source venv/bin/activate`
* Run `pip install -r requirements.txt`
* If you are going to use MySQL, install `pymysql` via pip as well.
* Create `.env` with all of your environment variables:
    1. `DISCORD_TOKEN` for the token
    2. `DISCORD_APPLICATION_ID` for the application ID
    3. `DATABASE_URL` for the database URL (supported: MySQL and SQLite)
    4. `DISCORD_BOTMASTER_ID` for the botmaster’s user ID
* Run all the migrations: `pw_migrate python3 -m peewee_migrate migrate --database="$DATABASE_URL"`
* Done! You can now run this bot as a script.

## Management

To simplify management, I created a script named Handbook. You can run it by running 
`python3 -m mukurobot.handbook`.
Here you can easily view user info (please note no PII is collected aside from Discord IDs, names and 
pronoun preference), set risk level on users, and export `badusers.txt`.

`badusers.txt` is a list of potentially dangerous user IDs, loaded on startup.
To prevent sharing PII, I did not ship it with the bot, but you have to ask me personally for it.

Also, the definition of “dangerous” is subjective, so every instance of this bot has a list on its own.

## Caveats

* It has synchronous HTTP dependencies despite the bot being async.
* The whole code has no tests.
* The current implementation of security requires constant presence of the botmaster in order to work.
  Moreover, it is implemented using owner-only prefix command, and that’s bad.
* One day S.E.S.S.O. will discover this repository and make some despairful product out of it,
  without giving me credit. I’m not fine with that, but whatever is meant to happen, happens.

## Final Word

Together we have to strive to mantain the world a livable place, and protect it from the seductions of despair.

This security and fun MIT-licensed bot is an attempt to keep world peace thriving, and to preserve
everyone’s hope.
