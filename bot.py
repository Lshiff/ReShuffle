import discord
from discord.ext import commands

from cogwatch import Watcher, watch
from dotenv import load_dotenv
import os
import sys, traceback

load_dotenv()
TOKEN = os.getenv('TOKEN')

from variables import GUILD_ID

# if not isinstance(GUILD_ID, int):

#     exit()

if not TOKEN:
    print("NO TOKEN")
    exit()

bot = commands.Bot(command_prefix=".", intents = discord.Intents.all())

@bot.event
async def setup_hook():
    await load()

async def load():
    print("Loading cogs...")
    for file in os.listdir('./cogs'):
        if file.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{file[:-3]}")
            except Exception as e:
                print(f'Failed to load extension {file}.', file=sys.stderr)
                traceback.print_exc()
            else:
                print(f"{file} loaded successfully!")

@bot.event
async def on_ready():
    print("Bot is ready")
    watcher = Watcher(bot, path='cogs', preload=True)
    await watcher.start()

@bot.command()
async def sync(ctx):
    try:
        # synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        # print(f"Synced {len(synced)} command(s) to guild")
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s) globally")
        # bot.tree.clear_commands(guild=discord.Object(id=GUILD_ID))
        # await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        # bot.tree.clear_commands(guild=None)
        # await bot.tree.sync()
    except Exception as e:
        print("sync not wor")
        print(e)
        await ctx.send("no sync...")
    else:
        print(f"Synced {len(synced)} command(s)")



@bot.command()
async def r(ctx):
    for file in os.listdir('./cogs'):
        if file.endswith(".py"):
            try:
                await bot.unload_extension(f"cogs.{file[:-3]}")
            except Exception as e:
                print(f'Failed to unload extension {file}.', file=sys.stderr)
                # traceback.print_exc()
            else:
                print(f"{file} unloaded successfully!")

            try:
                await bot.load_extension(f"cogs.{file[:-3]}")
            except Exception as e:
                print(f'Failed to load extension {file}.', file=sys.stderr)
                traceback.print_exc()
            else:
                print(f"{file} reloaded successfully!")

@bot.command(name="load")
async def load_cogs(ctx):
    await load()

@bot.command(name="load_cog")
async def load_cog(ctx, cog):
    print(f"Loading cog {cog}...")
    for file in os.listdir('./cogs'):
        if cog in file:
            await bot.unload_extension(f"cogs.{file[:-3]}")
            try:
                await bot.load_extension(f"cogs.{file[:-3]}")
            except Exception as e:
                print(f'Failed to load extension {file}.', file=sys.stderr)
                traceback.print_exc()
                await ctx.send(f'Failed to load extension {file}.', file=sys.stderr)
            else:
                print(f"{file} loaded successfully!")
                await ctx.send(f"{file} loaded successfully!")




bot.run(TOKEN)
