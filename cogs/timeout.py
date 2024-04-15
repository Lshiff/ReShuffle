import json

import discord
from discord import app_commands
from discord.ext import commands

from database_commands import DatabaseCommands as db

# from variables import GUILD_ID, TIMEOUT_CATEGORY_ID, MOD_LOG_CHANNEL_ID
import variables as v
import utils as u

class TimeoutCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.add_view(ModButtonView())

    async def timeout(self, guild: discord.Guild, member: discord.Member):
        if not guild:
            return
        category = discord.utils.get(guild.categories, id=v.TIMEOUT_CATEGORY_ID)
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
        initial_message = await channel.send(f"{member.mention}, you have been placed in timeout", view=ModButtonView())

        # lshiff = self.bot.get_user(426195398210879498)
        # reshuffle_team = guild.get_role(1216392571161415870)
        # print("Creating thread")
        # try:
        #     thread = await channel.create_thread(name = "Mods")#, message=initial_message)
        #     await channel.send("thread created")
        #     await thread.send("this is a thread")
        #     await thread.send(f"{member.mention} {lshiff.mention} {reshuffle_team.mention}")
        # except Exception as e:
        #     print("nope")
        #     print(e)

        return channel

    @app_commands.command(name="timeout", description="Create a private channel for user to talk to mods")
    @app_commands.describe(member = "User to time out")
    async def call_timeout(self, interaction: discord.Interaction, member: discord.Member):
        if not interaction.guild:
            return

        await interaction.response.defer(thinking=True, ephemeral=True)
        channel = await self.timeout(interaction.guild, member)

        assert channel is not None
        await interaction.followup.send(f"Channel created: {channel.mention}", ephemeral=True)


    @commands.command()
    async def t(self, ctx):
        await ctx.send(view = ModButtonView())



async def setup(bot):
    await bot.add_cog(TimeoutCog(bot))


class ModButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ModButton())


class ModButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.grey, label = 'Mod Button', custom_id = 'alsjflkadsjfdklsjf')

    async def callback(self, interaction: discord.Interaction):

        assert interaction.guild is not None
        assert isinstance(interaction.user, discord.Member)

        reshuffle_team_role = interaction.guild.get_role(v.RESHUFFLE_TEAM_ROLE_ID)
        if reshuffle_team_role not in interaction.user.roles:
            await interaction.response.send_message(f"This button is for team only 🙃", ephemeral=True, delete_after=30)
            return

        assert isinstance(interaction.channel, discord.TextChannel)

        history = interaction.channel.history(limit=1, oldest_first=True)
        original_message = [message async for  message in history][0]
        member = original_message.mentions[0]

        assert isinstance(member, discord.Member)
        await interaction.response.send_message("Moderator Actions", ephemeral=True, view=ModActionsView(member))

class ModActionsView(discord.ui.View):
    def __init__(self, member: discord.Member):
        super().__init__()
        self.add_item(SendModMessageButton())
        self.add_item(MuteUserButton(member))
        self.add_item(ViewPastInfractionsButton(member))


class SendModMessageButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.green, label = 'Send Mod Message (opens menu)')#, row=1)

    async def callback(self, interaction: discord.Interaction):

        # await interaction.response.send_message("send teh msg yo", ephemeral=True)

        with open('customer_support_messages/private_moderation.json', 'r') as f:
            message_dict = json.load(f)
        message_list = message_dict["message_list"]

        msg="### Choose which message to send\n"
        for i, message in enumerate(message_list, start=1):
            msg += f"\n{i}: {message}\n"

        msg += "\nTo send a custom message, use /say"

        view = ChooseMessageView(len(message_list))
        await interaction.response.send_message(msg, view=view, ephemeral=True)

        await view.wait()

        assert isinstance(view.value, int)
        assert isinstance(interaction.channel, discord.TextChannel)

        message = message_list[view.value - 1]
        await interaction.channel.send(message)

        await interaction.delete_original_response()



class ChooseButton(discord.ui.Button):
    def __init__(self, number: int):
        super().__init__(style=discord.ButtonStyle.green, label=str(number))
        self.number = number

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view = self.view
        view.value = self.number
        view.stop()

        await interaction.response.send_message("Message sent", ephemeral=True, delete_after=5)

class ChooseMessageView(discord.ui.View):
    def __init__(self, num_choices: int):
        super().__init__()
        self.value = None

        for i in range(num_choices):
            self.add_item(ChooseButton(i+1))


class MuteUserButton(discord.ui.Button):
    def __init__(self, member: discord.Member):
        super().__init__(style=discord.ButtonStyle.red, label = 'Mute User')#, row=2)
        self.member = member

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("mute the user", ephemeral=True)


class ViewPastInfractionsButton(discord.ui.Button):
    def __init__(self, member: discord.Member):
        super().__init__(style=discord.ButtonStyle.blurple, label = 'View Past Infractions')#, row=3)
        self.member = member

    async def callback(self, interaction: discord.Interaction):
        # await interaction.response.send_message(f"view past infractions {self.member.mention}", ephemeral=True)

        await interaction.response.defer(ephemeral=True, thinking=True)


        print(self.member)
        print(self.member.id)
        past_moderation_logs = db.get_past_moderation_logs_from_discord_id(self.member.id)
        past_support_logs = db.get_past_support_logs_from_discord_id(self.member.id)

        num_moderationon_logs = len(past_moderation_logs)
        num_support_logs = len(past_support_logs)

        description = f"Logs for {self.member.mention}\nModeration Logs: {num_moderationon_logs}\nSupport Logs: {num_support_logs}"
        embed = discord.Embed(title=f"{self.member.nick or self.member.name}'s history", description=description, color=discord.Color.magenta())

        if num_moderationon_logs > 0:
            embed_value = ""
            for mod_log in past_moderation_logs:
                timestamp = u.discord_timestamp(mod_log.timestamp)
                embed_value += f"{mod_log.infraction} – {timestamp}"
                if mod_log.notes:
                    embed_value += f"\n> Notes: {mod_log.notes}"
                embed_value += "\n\n"
            embed.add_field(name="Past Moderation Logs", value=embed_value, inline=False)


        await interaction.followup.send(embed=embed)
        





