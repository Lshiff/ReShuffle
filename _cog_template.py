import discord
from discord import app_commands
from discord.ext import commands

import variables as v

class TestCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # @app_commands.command(name="test")
    # async def test(self, interaction: discord.Interaction):
    #     await interaction.response.send_message("test")
         
    @commands.command()
    async def hello(self, ctx):
        await ctx.send("hiiiiiii")

async def setup(bot):
    await bot.add_cog(TestCog(bot))
