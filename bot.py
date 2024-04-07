import discord
from discord.ext import commands

from cogwatch import Watcher, watch
from dotenv import load_dotenv
import os
import sys, traceback

load_dotenv()
TOKEN = os.getenv('TOKEN')

if not TOKEN:
    print("NO TOKEN")
    exit()

bot = commands.Bot(command_prefix=".", intents = discord.Intents.all())

@bot.event
async def setup_hook():
    await load()

#Lods all cogs
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

    #Starts cogwatch – reloads cog whenever a file in cogs/ is saved. Useful for development
    watcher = Watcher(bot, path='cogs', preload=True)
    await watcher.start()

@bot.command()
async def sync(ctx):
    try:
        #Syncs all comamnds to the command tree – means that discord will recognize them. Should be called when a slash comamnd or context menu is created or name changed
        synced = await bot.tree.sync()
    except Exception as e:
        print("Sync failed")
        print(e)
        await ctx.send("Sync failed")
    else:
        print(f"Synced {len(synced)} command(s)")


#Reloads all cogs when '.r' typed into discord. Useful for development along with cogwatch
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
