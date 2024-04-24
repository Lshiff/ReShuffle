import json
from datetime import timedelta, datetime
import traceback

import discord
from discord import app_commands
from discord.ext import commands

from database_commands import DatabaseCommands as db

import variables as v
import utils as u

class TimeoutCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.add_view(ModButtonView())
        self.timeout_context_menu = app_commands.ContextMenu(
            name = "Timeout",
            callback = self.timeout_context_menu_callback
        )
        self.bot.tree.add_command(self.timeout_context_menu)

    async def timeout_context_menu_callback(self, interaction: discord.Interaction, member: discord.Member):
        assert interaction.guild is not None

        await interaction.response.defer(thinking=True, ephemeral=True)
        channel = await self.timeout(interaction.guild, member)

        assert channel is not None
        await interaction.followup.send(f"Channel created: {channel.mention}", ephemeral=True)



    async def timeout(self, guild: discord.Guild, member: discord.Member):
        if not guild:
            print("Timout: NO GUILD")
            return
        category = discord.utils.get(guild.categories, id=v.TIMEOUT_CATEGORY_ID)
        if not category:
            print("Timeout: No timeout category")
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

        return channel

    @app_commands.command(name="timeout", description="Create a private channel for user to talk to mods")
    @app_commands.describe(member = "User to time out")
    async def call_timeout(self, interaction: discord.Interaction, member: discord.Member):
        assert interaction.guild is not None

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
        super().__init__(timeout=None)
        self.add_item(SendModMessageButton())
        self.add_item(TimeoutUserMenuButton(member))
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


class ChooseMessageView(discord.ui.View):
    def __init__(self, num_choices: int):
        super().__init__()
        self.value = None

        for i in range(num_choices):
            self.add_item(ChooseButton(i+1))

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


class TimeoutUserMenuButton(discord.ui.Button):
    def __init__(self, member: discord.Member):
        super().__init__(style=discord.ButtonStyle.red, label = 'Timeout User')#, row=2)
        self.member = member

    async def callback(self, interaction: discord.Interaction):

        view = TimeoutUserView(self.member)
        await interaction.response.send_message(f"Choose an option to timeout {self.member.mention}", view=view, ephemeral=True)
        await view.wait()

        assert isinstance(interaction.channel, discord.TextChannel)

        duration_str = view.duration_str
        duration_timedelta = view.duration_timedelta

        try:
            await self.member.timeout(duration_timedelta)
        except Exception as e:
            await view.interaction.response.send_message(f"Timeout failed. Error: {e}", ephemeral=True)
            return
            # await view.interaction.response.send_message(f"{self.member.mention} has been timed out for {view.duration_str}", ephemeral=True)

        if not self.member.is_timed_out():
            await view.interaction.response.send_message("Something went wrong. The timeout didn't go through. Please try again or do it manually", ephemeral=True)
            return

        discord_timestamp = u.discord_timestamp_from_timedelta(duration_timedelta) # Format: 'In 30 minutes' or 'In 1 day'
        timeout_message = f"**{self.member.mention} you have been timed out for {duration_str}**\n\nYou will be able to talk again {discord_timestamp}" 
        await interaction.channel.send(f"**{self.member.mention} you have been timed out for {duration_str}**\n\nYou will be able to talk again {discord_timestamp}")

        try:
            timeout_log_id = db.create_timeout_log(
                user_discord_id = self.member.id,
                user_discord_username = self.member.name,
                moderator_discord_id = interaction.user.id,
                moderator_discord_username = interaction.user.name,
                timestamp = datetime.now(),
                duration_of_timeout = duration_str
            )
        except Exception as e:
            await view.interaction.response.send_message(f"Could not add timeout log to database. \nError: {e}", ephemeral=True)
            return


        mod_log_channel = await interaction.guild.fetch_channel(v.MOD_LOG_CHANNEL_ID)
        if not mod_log_channel:
            print("NO MOD LOG CHANNEL FOUND")

        description = f"{self.member.mention} has been timed out by {interaction.user.mention} for {duration_str}"
        embed = discord.Embed(title="Timeout Log", description= description, colour=discord.Color.brand_red())

        mod_log_message = await mod_log_channel.send(embed=embed)


        notes_view = AddNotesView(timeout_log_id, mod_log_message)
        await view.interaction.response.send_message(f"{self.member.mention} has been timed out for {duration_str}\n\nThis timeout has been logged in the database. To add notes about this, click the Add Notes Button", view = notes_view, ephemeral=True)





class TimeoutUserView(discord.ui.View):
    def __init__(self, member: discord.Member):
        super().__init__()
        self.add_item(TimeoutUserButton(member, "30 Minutes", timedelta(minutes=30)))
        self.add_item(TimeoutUserButton(member, "24 Hours", timedelta(days=1)))
        # self.value = None


class TimeoutUserButton(discord.ui.Button):
    def __init__(self, member: discord.Member, duration_str: str, duration_timedelta: timedelta):
        super().__init__(style=discord.ButtonStyle.red, label = duration_str)
        self.duration_str = duration_str
        self.duration_timedelta = duration_timedelta

    async def callback(self, interaction: discord.Interaction):
        # await interaction.response.send_message(f"Timeout the user for {self.duration_timedelta}", ephemeral=True)

        assert self.view is not None
        view = self.view
        view.duration_timedelta = self.duration_timedelta
        view.duration_str = self.duration_str
        view.interaction = interaction
        view.stop()


class ViewPastInfractionsButton(discord.ui.Button):
    def __init__(self, member: discord.Member):
        super().__init__(style=discord.ButtonStyle.blurple, label = 'View History')#, row=3)
        self.member = member

    async def callback(self, interaction: discord.Interaction):
        # await interaction.response.send_message(f"view past infractions {self.member.mention}", ephemeral=True)

        await interaction.response.defer(ephemeral=True, thinking=True)


        print(self.member)
        print(self.member.id)
        past_moderation_logs = db.get_past_moderation_logs_from_discord_id(self.member.id)
        past_support_logs = db.get_past_support_logs_from_discord_id(self.member.id)
        past_timeout_logs = db.get_past_timeout_logs_from_discord_id(self.member.id)

        num_moderationon_logs = len(past_moderation_logs)
        num_support_logs = len(past_support_logs)
        num_timeout_logs = len(past_timeout_logs)

        description = f"Logs for {self.member.mention}\nModeration Logs: {num_moderationon_logs}\nSupport Logs: {num_support_logs}\nTimeout Logs: {num_timeout_logs}"
        embed = discord.Embed(title=f"{self.member.nick or self.member.name}'s history", description=description, color=discord.Color.magenta())

        if num_timeout_logs >0 :
            embed_value = ""
            for timeout_log in past_timeout_logs:
                timestamp = u.discord_timestamp(timeout_log.timestamp)
                embed_value += f"{timeout_log.duration_of_timeout} – {timestamp}"
                if timeout_log.notes:
                    embed_value += f"\n> Notes: {timeout_log.notes}"
                embed_value += "\n\n"
            embed.add_field(name="Past Timeout Logs", value=embed_value, inline=False)

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
        





class AddNotesView(discord.ui.View):
    def __init__(self, timeout_log_id: int, mod_log_message: discord.Message):
        super().__init__(timeout = None)
        self.add_item(AddNotesButton(timeout_log_id, mod_log_message))

class AddNotesButton(discord.ui.Button):
    def __init__(self, timeout_log_id: int, mod_log_message: discord.Message):
        super().__init__(style=discord.ButtonStyle.blurple, label = 'Add Notes')
        self.timeout_log_id = timeout_log_id
        self.mod_log_message = mod_log_message

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(NotesModal(timeout_log_id=self.timeout_log_id, mod_log_message=self.mod_log_message))
        # self.stop() # but would really be self.view if i wanted that


class NotesModal(discord.ui.Modal, title="Add Notes"):
    def __init__(self, timeout_log_id: int, mod_log_message: discord.Message):
        super().__init__()
        self.timeout_log_id = timeout_log_id
        self.mod_log_message = mod_log_message

    notes = discord.ui.TextInput(
        label='Notes',
        style=discord.TextStyle.long,
        placeholder='Add notes about this timeout...',
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        print(f"submitted id: {self.custom_id}")
        print("supposed to be calling update mod log notes")
        try:
            db.update_timeout_log_notes(self.timeout_log_id, self.notes.value)
        except Exception as e:
            await interaction.followup.send(f"Something went wrong. Could not add notes to database.\nError: {e}")
        else:
            await interaction.followup.send(f"Notes added!", ephemeral=True)

        mod_log_message = self.mod_log_message
        mod_log_embed = mod_log_message.embeds[0]
        mod_log_embed.add_field(name="Notes", value=self.notes.value, inline=False)
        await mod_log_message.edit(embed=mod_log_embed)


    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)
        traceback.print_exception(type(error), error, error.__traceback__)
