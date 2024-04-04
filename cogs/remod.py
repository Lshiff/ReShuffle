import discord
from discord import app_commands
from discord.ext import commands

import json

from database_commands import DatabaseCommands as db
import variables as v

class RemodCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(name="moderation", description="Choose moderation message to send")
    async def remod(self, interaction: discord.Interaction):
        with open('moderation.json', 'r') as f:
            message_dict = json.load(f)
        view = RemodDropdownView(message_dict)
        await interaction.response.send_message("Pick the category", view = view, ephemeral=True)#, delete_after=30)


async def setup(bot):
    await bot.add_cog(RemodCog(bot))


# message_dict = {
#     'Having an unrelated conversation in a quest channel': {
#         'emoji': '',
#         'messages': [
#             'Hey there! Please keep in mind that this channel is specifically for the quest. Feel free to continue this conversation in <#1047853378266472499>!',
#             "Let's keep this channel for quest-related discussions. Please switch to the #<1047853378266472499>! Thanks! ↩"
#         ]

# }, 'Innapropriate language': {'emoji': '', 'messages': ['The ReShuffle server is friendly and supportive – please keep language appropriate! 🤗', "Let's keep messages appropriate 🙃"]}, 'Not speaking English': {'emoji': '', 'messages': ["Let's keep the chat in English – It's a great way to practice your skills!", "Learning English is one of the main goals of ReShuffle, so let's refrain from using other languages here"]}, 'Spam': {'emoji': '', 'messages': ["Please don't spam messages in this server 🤫", "Feel free to talk here, but please don't spam! ❌"]}, 'Advertisements': {'emoji': '', 'messages': ['Advertisments are not allowed in this server, please remove it and refrain from advertising! ❌', "Please don't advertise in this server! ❌"]}, 'Negative Language': {'emoji': '', 'messages': ['The ReShuffle community allows positive discussions only - Please avoid negative language! 🤐', "Let's keep messages positive 🙃", 'This Discord server is an environment where we all support each other. Please keep things positive! 🙌']}}


class CustomInfractionModal(discord.ui.Modal, title="Custom Infraction"):

    def __init__(self):
        super().__init__()

    custom_category = discord.ui.TextInput(
        label = "Infraction",
        placeholder= "Type the custom infraction here..."
    )

    custom_message = discord.ui.TextInput(
        label = "Message",
        placeholder= "Type the custom message here..."
    )

    notes = discord.ui.TextInput(
        label = "Notes",
        placeholder= "Notes about this interaction\n- Should we add this as a new infraction?",
        style=discord.TextStyle.long,
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):

        await interaction.response.send_message("Message Sent", ephemeral=True)
        await interaction.channel.send(self.custom_message.value)
        mod_log_channel = await interaction.guild.fetch_channel(v.MOD_LOG_CHANNEL_ID)
        if not mod_log_channel:
            print("NO MOD LOG CHANNEL FOUND")
            return

        await mod_log_channel.send(f"Custom moderation message sent by {interaction.user.mention}:\nInfraction: {self.custom_category.value}\nMessage: {self.custom_message.value}\nNotes: {self.notes.value}")

class CustomMessageModal(discord.ui.Modal, title="Custom Message"):

    def __init__(self):
        super().__init__()

    custom_message = discord.ui.TextInput(
        label = "Message",
        placeholder= "Type the custom message here..."
    )

    notes = discord.ui.TextInput(
        label = "Notes",
        placeholder= "Notes about this interaction\n- Should we add this as a new message?",
        style=discord.TextStyle.long,
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):

        await interaction.response.send_message("Message Sent", ephemeral=True)
        await interaction.channel.send(self.custom_message.value)
        mod_log_channel = await interaction.guild.fetch_channel(v.MOD_LOG_CHANNEL_ID)
        if not mod_log_channel:
            print("NO MOD LOG CHANNEL FOUND")
            return

        await mod_log_channel.send(f"Custom moderation message sent by {interaction.user.mention}:\nMessage: {self.custom_message.value}\nNotes: {self.notes.value}")

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:

        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        print(type(error), error, error.__traceback__)

class RemodDropdown(discord.ui.Select):
    def __init__(self, message_dict):
        self.message_dict = message_dict

        # Set the options that will be presented inside the dropdown
        # options = [
        #     discord.SelectOption(label='Off Topic', emoji='🐔'),
        #     discord.SelectOption(label='Swearing', emoji='🤬'),
        #     discord.SelectOption(label='Innapropriate', emoji='🍆'),
        #     discord.SelectOption(label='Not English', emoji='🇮🇱'),
        #     discord.SelectOption(label='Spam', emoji='🫨'),
        #     discord.SelectOption(label='Negative Language', emoji='😤'),
        #     discord.SelectOption(label='Advertisements', emoji='🤑'),
        # ]

        options = []
    
        for infraction in message_dict:
            emoji = message_dict[infraction].get("emoji") or None
            options.append(discord.SelectOption(label=infraction, emoji=emoji))

        options.append(discord.SelectOption(label="Custom Infraction", emoji="✍️"))

        super().__init__(placeholder='Choose the category...', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):

        # messages = {
        #     'Off Topic': ['Hey there! Please keep in mind that this channel is specifically for the quest. Feel free to continue this conversation in <#1047853378266472499>!', 'Just a reminder to keep this channel for discussions relating to the quest! Move to <#1047853378266472499> topic to continue your convo'],
        #     'Swearing': ['This is a community server for all – please refrain from swearing 🤐', "Let's keep messages positive and appropriate 🙃"],
        #     'Innapropriate': ['This is a community server for all – please keep language appropriate', "Let's keep messages appropriate 🙃"],
        #     'Not English': ["Let's keep the chat in English – It's a great way to practice your skills!", "Learning English is one of the main goals of ReShuffle, so let's refrain from using other languages here"],
        #     'Spam': ["Please don't spam messages in this server 🤫", "Feel free to talk here, but please don't spam!"],
        #     'Negative Language': ["This Discord server is a positive environment where we all support each other. Please keep things positive!", "The ReShuffle Discord server is meant to act as a free, open and informative space for all ReShufflers! Keep all communications positive 🙌"],
        #     'Advertisements': ["Please don't advertise in this server"]
        # }

        infraction = self.values[0]

        if infraction == "Custom Infraction":
            await interaction.response.send_modal(CustomInfractionModal())
            return

        messages = self.message_dict[infraction]["messages"]

        msg="### Choose which message to send\n"
        for i, message in enumerate(messages, start=1):
            msg += f"\n{i}: {message}\n"
            
        view = Choose(len(messages))

        await interaction.response.send_message(msg, view=view, ephemeral=True)
        await view.wait()
        # await interaction.delete_original_response()
        if not view.value:
            return

        if view.value == "custom":
            return

        await interaction.channel.send(messages[view.value - 1])
        
        # category = self.values[0]
        # message = category[view.value - 1]
        # await log_moderation(interaction, category, message)


class RemodDropdownView(discord.ui.View):
    def __init__(self, message_dict):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(RemodDropdown(message_dict))

class ChooseButton(discord.ui.Button):
    def __init__(self, number: int):
        super().__init__(style=discord.ButtonStyle.green, label=str(number))
        self.number = number

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: Choose = self.view
        view.value = self.number
        view.stop()

class CustomButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Custom Message")

    async def callback(self, interaction: discord.Interaction):

        await interaction.response.send_modal(CustomMessageModal())


        assert self.view is not None
        view: Choose = self.view
        view.value = "custom"
        view.stop()

class Choose(discord.ui.View):
    def __init__(self, num_choices: int):
        super().__init__()
        self.value = None

        for i in range(num_choices):
            self.add_item(ChooseButton(i+1))
        self.add_item(CustomButton())

async def log_moderation(interaction: discord.Interaction, category: str, message: str):

    channel_id = interaction.channel_id
    channel_name = interaction.channel.name
    sender_discord_id = interaction.user.id
    sender_discord_username = interaction.user.name

    db.create_moderation_log(
        channel_id = channel_id,
        channel_name = channel_name,
        moderation_category = category,
        moderation_message = message,
        sender_discord_id = sender_discord_id,
        sender_discord_username = sender_discord_username,
    )

    mod_log_channel = await interaction.guild.fetch_channel(v.MOD_LOG_CHANNEL_ID)
    if not mod_log_channel:
        print("NO MOD LOG CHANNEL FOUND")
        return

    embed = discord.Embed(title=f"Moderation logged", description=f"Modded by <@{sender_discord_id}>", colour=discord.Colour.teal())
    embed.add_field(name="Channel", value=f"<#{channel_id}>")
    embed.add_field(name="Category", value=category, inline=True)

    await mod_log_channel.send(embed=embed)
