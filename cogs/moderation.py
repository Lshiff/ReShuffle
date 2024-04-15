from typing import Optional
import discord
from discord import app_commands
from discord.ext import commands

import json
import traceback

from database_commands import DatabaseCommands as db
import variables as v

class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rehelp_context_menu = app_commands.ContextMenu(
            name="Moderation",
            callback = self.remod_context_menu_callback
        )
        self.bot.tree.add_command(self.rehelp_context_menu)

    async def remod_context_menu_callback(self, interaction: discord.Interaction, message: discord.Message):
        with open('customer_support_messages/moderation.json', 'r') as f:
            message_dict = json.load(f)
        original_message = message
        view = RemodDropdownView(message_dict, original_message)
        await interaction.response.send_message("Pick the category", view = view, ephemeral=True)

    @app_commands.command(name="moderation", description="Choose moderation message to send")
    async def remod(self, interaction: discord.Interaction):
        with open('customer_support_messages/moderation.json', 'r') as f:
            message_dict = json.load(f)
        view = RemodDropdownView(message_dict)
        await interaction.response.send_message("Pick the category", view = view, ephemeral=True)#, delete_after=30)


async def setup(bot):
    await bot.add_cog(ModerationCog(bot))


class CustomInfractionModal(discord.ui.Modal, title="Custom Infraction"):

    def __init__(self, original_message):
        self.original_message = original_message
        super().__init__()

    custom_infraction = discord.ui.TextInput(
        label = "Infraction",
        placeholder= "Type the custom infraction here..."
    )

    custom_message = discord.ui.TextInput(
        label = "Message",
        placeholder= "Type the custom message here...",
        style=discord.TextStyle.long
    )

    notes = discord.ui.TextInput(
        label = "Notes",
        placeholder= "Notes about this interaction\n- Should we add this as a new infraction?",
        style=discord.TextStyle.long,
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):


        await send_and_log_moderation_message(
            interaction = interaction,
            infraction = self.custom_infraction.value,
            message = self.custom_message.value,
            notes = self.notes.value,
            is_custom = True,
            is_custom_infraction = True,
            is_custom_message = True,
            original_message = self.original_message
        )


class CustomMessageModal(discord.ui.Modal, title="Custom Message"):

    def __init__(self, original_message, infraction):
        self.original_message = original_message
        self.infraction = infraction
        super().__init__()

    custom_message = discord.ui.TextInput(
        label = "Message",
        placeholder= "Type the custom message here...",
        style=discord.TextStyle.long
    )

    notes = discord.ui.TextInput(
        label = "Notes",
        placeholder= "Notes about this interaction\n- Should we add this as a new message?",
        style=discord.TextStyle.long,
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):

        await send_and_log_moderation_message(
            interaction = interaction,
            infraction = self.infraction,
            message = self.custom_message.value,
            notes = self.notes.value,
            is_custom = True,
            is_custom_infraction = False,
            is_custom_message = True,
            original_message = self.original_message
        )


    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:

        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        print(type(error), error, error.__traceback__)

class RemodDropdown(discord.ui.Select):
    def __init__(self, message_dict, original_message):
        self.message_dict = message_dict
        self.original_message = original_message

        options = []
    
        for infraction in message_dict:
            emoji = message_dict[infraction].get("emoji") or None
            options.append(discord.SelectOption(label=infraction, emoji=emoji))

        options.append(discord.SelectOption(label="Custom Infraction", emoji="✍️"))

        super().__init__(placeholder='Choose the category...', min_values=1, max_values=1, options=options)


    async def callback(self, interaction: discord.Interaction):

        infraction = self.values[0]

        if infraction == "Custom Infraction":
            await interaction.response.send_modal(CustomInfractionModal(self.original_message))
            return

        messages = self.message_dict[infraction]["messages"]

        msg="### Choose which message to send\n"
        for i, message in enumerate(messages, start=1):
            msg += f"\n{i}: {message}\n"
            
        view = Choose(len(messages), self.original_message, infraction)

        await interaction.response.send_message(msg, view=view, ephemeral=True)
        await view.wait()
        # await interaction.delete_original_response()
        if not view.value:
            return

        if view.value == "custom":
            return

        message = messages[view.value - 1]


        await send_and_log_moderation_message(
            interaction = view.interaction,
            infraction = infraction,
            message = message,
            # notes = notes,
            is_custom = False,
            is_custom_infraction = False,
            is_custom_message = False,
            original_message = self.original_message
        )


class RemodDropdownView(discord.ui.View):
    def __init__(self, message_dict, original_message=None):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(RemodDropdown(message_dict, original_message))

class ChooseButton(discord.ui.Button):
    def __init__(self, number: int):
        super().__init__(style=discord.ButtonStyle.green, label=str(number))
        self.number = number

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view = self.view
        view.value = self.number
        view.interaction = interaction
        view.stop()

class CustomButton(discord.ui.Button):
    def __init__(self, original_message, infraction):
        self.original_message = original_message
        self.infraction = infraction
        super().__init__(style=discord.ButtonStyle.blurple, label="Custom Message")

    async def callback(self, interaction: discord.Interaction):

        await interaction.response.send_modal(CustomMessageModal(self.original_message, self.infraction))


        assert self.view is not None
        view = self.view
        view.value = "custom"
        view.stop()

class Choose(discord.ui.View):
    def __init__(self, num_choices: int, original_message, infraction):
        super().__init__()
        self.value = None

        for i in range(num_choices):
            self.add_item(ChooseButton(i+1))
        self.add_item(CustomButton(original_message, infraction))

class AddNotesView(discord.ui.View):
    def __init__(self, moderation_log_id: int, mod_log_message: discord.Message):
        super().__init__()
        self.add_item(AddNotesButton(moderation_log_id, mod_log_message))

class AddNotesButton(discord.ui.Button):
    def __init__(self, moderation_log_id: int, mod_log_message: discord.Message):
        super().__init__(style=discord.ButtonStyle.blurple, label = 'Add Notes')
        self.moderation_log_id = moderation_log_id
        self.mod_log_message = mod_log_message

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(NotesModal(moderation_log_id=self.moderation_log_id, mod_log_message=self.mod_log_message))
        # self.stop() # but would really be self.view if i wanted that


class NotesModal(discord.ui.Modal, title="Add Notes"):
    def __init__(self, moderation_log_id: int, mod_log_message: discord.Message):
        super().__init__()
        self.moderation_log_id = moderation_log_id
        self.mod_log_message = mod_log_message

    notes = discord.ui.TextInput(
        label='Notes',
        style=discord.TextStyle.long,
        placeholder='Add notes about this interaction...',
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        print(f"submitted id: {self.custom_id}")
        print("supposed to be calling update mod log notes")
        db.update_moderation_log_notes(self.moderation_log_id, self.notes.value)
        # await interaction.response.send_message(f"Notes added!", ephemeral=True)
        await interaction.followup.send(f"Notes added!", ephemeral=True)

        mod_log_message = self.mod_log_message
        mod_log_embed = mod_log_message.embeds[0]
        mod_log_embed.add_field(name="Notes", value=self.notes.value, inline=False)
        await mod_log_message.edit(embed=mod_log_embed)


    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)
        traceback.print_exception(type(error), error, error.__traceback__)

async def send_and_log_moderation_message(
    *,
    interaction: discord.Interaction,
    infraction: str,
    message: str,
    notes: str = "",
    is_custom: bool = False,
    is_custom_infraction: bool = False,
    is_custom_message: bool = False,
    original_message: Optional[discord.Message] = None,
):

    await interaction.response.defer(ephemeral=True, thinking=True)

    if original_message:
        await original_message.reply(message)
    else:
        await interaction.channel.send(message)

    mod_log_channel = await interaction.guild.fetch_channel(v.MOD_LOG_CHANNEL_ID)
    if not mod_log_channel:
        print("NO MOD LOG CHANNEL FOUND")
        return

    title = f"{'Custom' if is_custom else ''} Moderation Message Log"
    description = f"Sent by {interaction.user.mention}"

    embed = discord.Embed(title=title, description= description, colour=discord.Color.magenta())
    embed.add_field(name=f"{'Custom' if is_custom_infraction else ''} Infraction", value=infraction, inline=False)
    embed.add_field(name=f"{'Custom' if is_custom_message else ''} Message", value=message, inline=False)

    if notes:
        embed.add_field(name="Notes", value=notes, inline=False)

    if original_message:
        embed.add_field(name="Original Message", value = f"Sent by {original_message.author.mention}\nLink: {original_message.jump_url}\nContent:\n> {original_message.content}")

    mod_log_message = await mod_log_channel.send(embed=embed)

    if original_message:
        original_message_id = original_message.id
        original_message_content = original_message.content
        original_message_sender_id = original_message.author.id
        original_message_sender_discord_username = original_message.author.name
    else:
        original_message_id = None
        original_message_content = None
        original_message_sender_id = None
        original_message_sender_discord_username = None

    moderation_log_id = db.create_moderation_log(
        infraction = infraction,
        message = message,
        notes = notes,
        is_custom = is_custom,
        is_custom_infraction = is_custom_infraction,
        is_custom_message = is_custom_message,
        channel_id = interaction.channel_id,
        channel_name = interaction.channel.name,
        original_message_id = original_message_id,
        original_message_content = original_message_content,
        original_message_sender_id = original_message_sender_id,
        original_message_sender_discord_username = original_message_sender_discord_username,
        sender_discord_id = interaction.user.id,
        sender_discord_username = interaction.user.name,
    )

    if not is_custom:
        view = AddNotesView(moderation_log_id=moderation_log_id, mod_log_message=mod_log_message)
        await interaction.followup.send(f"Message has ben sent! This interaction has been logged in <#{v.MOD_LOG_CHANNEL_ID}> and in the database. To add notes to this interaction, press the button ↓", view=view, ephemeral=True)
        # await interaction.channel.send(f"id: {support_log_id}")
    else:
        await interaction.followup.send("Message Sent", ephemeral=True)
