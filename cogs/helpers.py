import discord
from discord import app_commands
from discord.ext import commands

import variables as v

class HelperCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="helper")
    async def helper(self, interaction: discord.Interaction):
        await interaction.response.send_message("test", view=HelperView())



         
    # @commands.command()
    # async def hello(self, ctx):
    #     await ctx.send("hiiiiiii")

async def setup(bot):
    await bot.add_cog(HelperCog(bot))

class HelperView(discord.ui.View):
    def __init__(self):
        super().__init__()


    @discord.ui.button(label="Test Button", style=discord.ButtonStyle.blurple)
    async def button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("button pressed")
