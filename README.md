# MukuroI

A discord bot for security and fun.

Yes, I made it thinking about the “16th student”, althought I am not a kinnie of that character.

It provides autoban and a cool minigame (coming soon).

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
* Run all the migrations: `pw_migrate python3 -m peewee_migrate migrate --database="$DATABASE_URL"`
* Done! You can now run this bot as a script.

## Caveats

* It has synchronous HTTP dependencies despite the bot being async.