import discord
from discord import app_commands
from discord.ext import commands

import variables as v

class MessagesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.report_context_menu = app_commands.ContextMenu(
            name="Report Message",
            callback = self.report_context_menu_callback
        )
        self.bot.tree.add_command(self.report_context_menu)

    async def report_context_menu_callback(self, interaction: discord.Interaction, message: discord.Message):
        report_channel = await interaction.guild.fetch_channel(v.REPORT_CHANNEL_ID)
        if not report_channel:
            print("NO REPORT CHANNEL FOUND")
            return

        description = f"Sent by {message.author.mention} and reported by {interaction.user.mention}\nLink: {message.jump_url}\n"
        embed = discord.Embed(title = "Reported message", description=description, color=discord.Color.magenta())
        embed.add_field(name = "Message: ", value=f"\n{message.content}")

        await report_channel.send(embed=embed)
        await interaction.response.send_message("Thank you for reporting this message", ephemeral=True)
    

    # @app_commands.command(name="nick", description="Change the bot's nickname")
    # @app_commands.describe(nick = "Name to change to")
    # @app_commands.checks.has_permissions(manage_nicknames=True)
    # async def nick(self, interaction: discord.Interaction, nick: str):
    #     await interaction.guild.me.edit(nick=nick)
    #     await interaction.response.send_message(f"Nick changed", ephemeral=True)

    # @app_commands.command(name="change_username", description="Change the bot's username")
    # @app_commands.describe(username = "Username to change to")
    # @app_commands.checks.has_permissions(administrator=True)
    # async def change_username(self, interaction: discord.Interaction, username: str):
    #     await self.bot.user.edit(username=username)
    #     await interaction.response.send_message(f"Username changed", ephemeral=True)

    @app_commands.command(name="say", description="Send a custom message to the chat")
    @app_commands.describe(message = "Message to send")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def say(self, interaction: discord.Interaction, message: str):
        await interaction.channel.send(message)
        await interaction.response.send_message(f"Message Sent", ephemeral=True)


    @app_commands.command(name="dm", description="DM A specific user")
    @app_commands.describe(user = "User to DM")
    @app_commands.describe(message = "Message to send")
    async def dm(self, interaction: discord.Interaction, user: discord.Member, message: str):
        mod_msg = "No message set"
        try:
            channel = await user.create_dm()
            await channel.send(message)
        except Exception as e:
            await interaction.response.send_message(f"error: {e}", ephemeral=True)
            mod_msg = f"Unable to send dm to {user.mention}\nerror:\n> `{e}`\nmessage\n> `{message}`"
        else:
            await interaction.response.send_message(f"{user.mention} has been sent the message `{message}`", ephemeral=True)
            mod_msg = f"DM to user {user.mention}:\n> `{message}`"
        finally:
            mod_log_channel = discord.utils.get(interaction.guild.text_channels, id=v.MOD_LOG_CHANNEL_ID)
            if not mod_log_channel:
                print("NO MOD LOG CHANNEL FOUND")
                return
            await mod_log_channel.send(mod_msg)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if not message.guild:
        
            guild = await self.bot.fetch_guild(v.GUILD_ID)
            if not guild:
                print("GUID NOT FOUND")
                return
            mod_log_channel = await guild.fetch_channel(v.MOD_LOG_CHANNEL_ID)
            if not mod_log_channel:
                print("NO MOD LOG CHANNEL FOUND")
                return

            await mod_log_channel.send(f"DM Received from {message.author.mention}\n> `{message.content}`")

        await self.bot.process_commands(message)

async def setup(bot):
    await bot.add_cog(MessagesCog(bot))


