# MukuroI

A discord bot. Yes, I made it thinking about the “16th student”.

It provides autoban and a cool minigame (coming soon).

Note: the bot’s messages are in Italian.

## Development Warning

This bot has multiple **unsolvable** (according to me) bugs, including:

* Constantly disconnecting from the database (peewee and asyncio is a known problematic combo)
* Has synchronous HTTP dependencies despite the bot being async
* Lack of support of discord.py for nested slash commands

For this reasons, I am no longer updating the project and you should not run it.  I decided to rewrite the bot with a different codebase.

## Deployment

The bot requires Python 3.10+ in order to run.

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

