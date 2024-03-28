import discord
from discord import app_commands
from discord.ext import commands

from dotenv import load_dotenv
import os
import sys


sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from variables import GUILD_ID, TIMEOUT_CATEGORY_ID, MOD_LOG_CHANNEL_ID

class TimeoutCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def timeout(self, guild: discord.Guild, member: discord.Member):
        if not guild:
            return
        category = discord.utils.get(guild.categories, id=TIMEOUT_CATEGORY_ID)
        if not category:
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True),
        }

        name = member.nick
        if not name:
            name = member.name
        channel = await category.create_text_channel(name, overwrites=overwrites)
        initial_message = await channel.send(f"{member.mention}, you have been placed in timeout")

        lshiff = self.bot.get_user(426195398210879498)
        reshuffle_team = guild.get_role(1216392571161415870)
        print("Creating thread")
        try:
            thread = await channel.create_thread(name = "Mods")#, message=initial_message)
            await channel.send("thread created")
            await thread.send("this is a thread")
            await thread.send(f"{member.mention} {lshiff.mention} {reshuffle_team.mention}")
        except Exception as e:
            print("nope")
            print(e)

        return channel

    @app_commands.command(name="timeout", description="Create a private channel for user to talk to mods")
    @app_commands.describe(member = "User to time out")
    async def call_timeout(self, interaction: discord.Interaction, member: discord.Member):
        if not interaction.guild:
            return

        await interaction.response.defer(thinking=True, ephemeral=True)
        channel = await self.timeout(interaction.guild, member)
        await interaction.followup.send(f"Channel created: {channel.mention}", ephemeral=True)



async def setup(bot):
    await bot.add_cog(TimeoutCog(bot))



