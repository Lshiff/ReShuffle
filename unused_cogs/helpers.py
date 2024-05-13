import discord
from discord import app_commands
from discord.ext import commands

import variables as v

class HelperCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="helper", description="Sends the helper application message")
    async def helper(self, interaction: discord.Interaction):
        await interaction.response.send_message("test", view=HelperView())


        embed = discord.Embed(title="Helper applications :)", description = f"Apply to become a <@{v.HELPER_ROLE_ID}>", color=discord.Color.green()
## Apply here to become a <@&1047849095756255293> !

        embed.add_field(name= "**What is a helper?**", value = "A helper is a student who helps others to complete tasks or solve quest related dilemmas on the ReShuffle discord server. It could be content oriented, technical help, or anything else - helpers are the first people to answer.", inline=True)

        embed.add_field(name = " **Am I qualified to become a helper?**", value = "If you feel confident in technology (Instagram, Discord, the ReShuffle portfolio), or if you feel great about the quality of your tasks, then yes!", inline=True)

        embed.add_field(name = " **Why should I become a helper?**", value = "To help quest-mates in the server! Being a helper can be rewarding, as you get to help students from other schools use the platform and make awesome quests. Best of all, you get a cool green name. (There may be extra credit points involved too!)", inline=True)

        embed.add_field(name = " **How do I apply to become a helper?**", value = "Push the “Apply Now” button below!", inline=True)

        await interaction.channel.send(embed=embed, view=HelperView())
        await interaction.response.send_message("Helper message sent :)", ephemeral=True, delete_after=5)

async def setup(bot):
    await bot.add_cog(HelperCog(bot))

class HelperView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(ApplyButton())


class ApplyButton(discord.ui.Button):
    def __init__(self):
        super().__init__(emoji = "🚀", label="Apply Now", style=discord.ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_messsage("you pushedthe button lol", ephemeral=True)



