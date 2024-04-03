import discord
from discord import app_commands
from discord.ext import commands

import variables as v

class ExtraCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="change_status", description="Change the bot's sidebar status")
    # @commands.check_any(commands.has_guild_permissions(administrator=True), commands.has_role("Key Gen"))
    @app_commands.describe(activity="Activity to display")
    @app_commands.choices(activity=[
        app_commands.Choice(name="Playing", value="playing"),
        app_commands.Choice(name="Listening", value="listening"),
        app_commands.Choice(name="Watching", value="watching"),
        ])
    @app_commands.describe(status="The status text")
    async def change_status(self, interaction: discord.Interaction, activity: app_commands.Choice[str], status: str):
        match activity.value:

            case "playing":
                await self.bot.change_presence(activity=discord.Game(name=status))
            case "listening":
                await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=status))
            case "watching":
                await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=status))

        await interaction.response.send_message(f"Bot status has been changed", ephemeral=True)

    # @app_commands.command(name="test")
    # async def test(self, interaction: discord.Interaction):
    #     await interaction.response.send_message("test")
         
    @commands.command()
    async def hello(self, ctx):
        await ctx.send("hiiiiiii")

async def setup(bot):
    await bot.add_cog(ExtraCog(bot))



