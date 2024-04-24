# ReShuffle Discord Bot

### Notes
Uses discord.py\
To run:\
`pip install -r requirements.txt`\
`python3 bot.py`

Set environment variables:\
`TOKEN=''`\
`DATABASE_URI=''`

bot.py is the main file, cogs is where all of the commands are in
database_commands.py is where the database connection is.


# To set up on the Discord server

- Set all variables in `variables.py`

---
This program is a discord bot built with discord.py [link].
## Overfiew of each file
**`bot.py`**

Runs the bot and loads all cogs
- `.r` – reloads all cogs
- `.sync` – syncs the bot's command tree [link to when to sync]

\
**`database_commands.py`**

This is the file that interacts with the database. It creates a database connection with sqlalchemy and defines the models. A number of useful getter and setter commands are in the `DatabseCommands` class, which is imported into all files that reuqire database interaction

\
`utils.py`

Useful functions used by other files.
- `discord_timestamp(datetime, style="relative time")` 
Returns a Discord Timestamp [link to ]. Shows a datetime in relative time (2 days ago) or as a timezone adjusted timestamp


**`variables.py`** 
Constant variables that are used in other functions. Includes
```python
Guild ID
Mod Log Channel ID
Timeout Category ID
Report Channel ID
```
It also includes role_users, a dictionary of custom users that can be used with webhooks, though it's not currently in use

\
`cogs/`

A folder with discord.py cogs. Each cog contains a class with discord commands. [link to cogs]

**`remod.py`** and **`rehelp.py`**

These files contain the moderation and help commands.\
Can be used with slash commands:\
`/support`\
`/moderation`\
Or, with context menus\
Right click on a message -> apps -> `Support` or `Moderation`

Each use a series of dropdown menus to navigate the tree of pre written messages. The user will be able to choose a message to send, or send a custom one
The prewritten messages are saved in `customer_support_messages`, in `moderation.json` and `support.json`. These messages are used to fill the dropdown tree.


**`update.py`**\
*Updates the support and moderation messages*

Command:\
`/update_from_spreadsheet`\
This command queries the master spreadsheet using sheety and updates the json files located in `customer_support_messages/` 






