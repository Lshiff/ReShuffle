import discord
from discord import app_commands
from discord.ext import commands

import json
import requests

from database_commands import DatabaseCommands as db
import variables as v


#TODO Log Commands

class RehelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(name="rehelp", description="Choose help message to send")
    async def remod(self, interaction: discord.Interaction):
        with open('cs_master.json', 'r') as f:
            message_dict = json.load(f)
        view = HelpCategoryDropdownView(message_dict)
        await interaction.response.send_message("Pick the category", view = view, ephemeral=True)


    @app_commands.command(name="update_help_from_spreadsheet", description="Updates the rehelp command from the spreadsehet. Can be done 200 times per month")
    async def update(self, interaction: discord.Interaction):
        headers = {
            "Authorization": "Bearer REFVPUkKoKgXg6xXG6bq3gybsi9Rezsw",
                }
        response = requests.get('https://api.sheety.co/3404605601848dcc35723dc42f596638/csChiefManualApril2024/onboardingNinja', headers=headers)
        print(response.text)

        onboarding_ninja = response.json()["onboardingNinja"]


        message_dict = {}

        category = ''
        category_dict = {}
        question = ''
        for row_dict in onboarding_ninja:
            print(row_dict)
            if row_dict['category'] and row_dict['category'] != category:
                if category != '':
                    message_dict[category] = category_dict
                category = row_dict['category'].strip()

                emoji = row_dict['categoryEmoji'].strip()
                category_dict = {"emoji": emoji}

            if row_dict['problem/question'] and row_dict['problem/question'] != question:
                subcategory = row_dict['subCategory (internal)'].strip()
                question = row_dict['problem/question'].strip()
                emoji = row_dict['problemEmoji'].strip()
                category_dict[question] = {"emoji": emoji, "subcategory": subcategory, "messages": []}

            category_dict[question]['messages'].append(row_dict['chiefMessage'].strip())

        message_dict[category] = category_dict #adds last category

        json_file = json.dumps(message_dict)
        with open('cs_master.json', 'w') as file:
            file.write(json_file)

        await interaction.response.send_message("Updated!", ephemeral=True)


async def setup(bot):
    await bot.add_cog(RehelpCog(bot))


class CustomCategoryModal(discord.ui.Modal, title="Custom Category/Message"):

    def __init__(self):
        super().__init__()

    custom_category = discord.ui.TextInput(
        label = "Category",
        placeholder= "Type the custom category here..."
    )

    custom_message = discord.ui.TextInput(
        label = "Message",
        placeholder= "Type the custom message here..."
    )

    notes = discord.ui.TextInput(
        label = "Notes",
        placeholder= "Notes about this interaction\n- Should we add this as a new category?",
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

        await mod_log_channel.send(f"Custom message sent by {interaction.user.mention}:\nCategory: {self.custom_category.value}\nMessage: {self.custom_message.value}\nNotes: {self.notes.value}")


    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:

        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        print(type(error), error, error.__traceback__)

 
class CustomMessageModal(discord.ui.Modal, title="Custom Message"):

    def __init__(self):
        super().__init__()

    custom_question = discord.ui.TextInput(
        label = "Question answering",
        placeholder= "The question/problem you are answering (optional)",
        required=False
    )
    custom_message = discord.ui.TextInput(
        label = "Message",
        placeholder= "Type the custom message here..."
    )

    notes = discord.ui.TextInput(
        label = "Notes",
        placeholder= "Notes about this interaction\n- Should we add this as a new option?",
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

        await mod_log_channel.send(f"Custom message sent by {interaction.user.mention}:\nMessage: {self.custom_message.value}\nNotes: {self.notes.value}")


    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:

        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        print(type(error), error, error.__traceback__)


class HelpCategoryDropdownView(discord.ui.View):
    def __init__(self, message_dict):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(HelpCategoryDropdown(message_dict))

class HelpCategoryDropdown(discord.ui.Select):
    def __init__(self, message_dict):
        self.message_dict = message_dict

        # Set the options that will be presented inside the dropdown
        options = []


        for category in message_dict:
            emoji = message_dict[category].get("emoji") or None
            options.append(discord.SelectOption(label=category, emoji=emoji))

        options.append(discord.SelectOption(label="Custom Category/Message", emoji="✍️"))


        super().__init__(placeholder='Choose the category...', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):

        category = self.values[0]

        if category == "Custom Category/Message":
            await interaction.response.send_modal(CustomCategoryModal())
            return


        options = []
        for question in self.message_dict[category]:
            if question == "emoji":
                continue
            emoji = self.message_dict[category][question].get("emoji") or None
            options.append(discord.SelectOption(label=question, emoji=emoji))

        options.append(discord.SelectOption(label="Custom Message", emoji="✍️"))


        view = HelpTopicDropdownView(options, category, self.message_dict)

        await interaction.response.send_message("Pick the topic", view = view, ephemeral=True)

class HelpTopicDropdownView(discord.ui.View):
    def __init__(self, options, category, message_dict):
        super().__init__()
        self.category = category

        # Adds the dropdown to our view object.
        self.add_item(HelpTopicDropdown(options, category, message_dict))

class HelpTopicDropdown(discord.ui.Select):
    def __init__(self, options, category, message_dict):
        super().__init__(placeholder='Choose the problem/question...', min_values=1, max_values=1, options=options)
        self.category = category
        self.message_dict = message_dict

    async def callback(self, interaction: discord.Interaction):

        question = self.values[0]

        if question == "Custom Message":
            await interaction.response.send_modal(CustomMessageModal())
            return

        messages = self.message_dict[self.category][question]["messages"]

        view = Choose(len(messages)) 

        msg="### Choose which message to send\n"
        for i, message in enumerate(messages, start=1):
            msg += f"\n{i}: {message}\n"

        await interaction.response.send_message(msg, view=view, ephemeral=True)
        await view.wait()
        message = messages[view.value - 1]
        await interaction.channel.send(message)


class ChooseButton(discord.ui.Button):
    def __init__(self, number: int):
        super().__init__(style=discord.ButtonStyle.green, label=str(number))
        self.number = number

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: Choose = self.view
        view.value = self.number
        view.stop()
        await interaction.response.send_message("Sent!", ephemeral=True)


class Choose(discord.ui.View):
    def __init__(self, num_choices: int):
        super().__init__()
        self.value = None

        for i in range(num_choices):
            self.add_item(ChooseButton(i+1))


# async def log_moderation(interaction: discord.Interaction, category: str, message: str):
#     channel_id = interaction.channel_id
#     channel_name = interaction.channel.name
#     sender_discord_id = interaction.user.id
#     sender_discord_username = interaction.user.name

#     db.create_moderation_log(
#         channel_id = channel_id,
#         channel_name = channel_name,
#         moderation_category = category,
#         moderation_message = message,
#         sender_discord_id = sender_discord_id,
#         sender_discord_username = sender_discord_username,
#     )

#     mod_log_channel = await interaction.guild.fetch_channel(v.MOD_LOG_CHANNEL_ID)
#     if not mod_log_channel:
#         print("NO MOD LOG CHANNEL FOUND")
#         return

#     embed = discord.Embed(title=f"Moderation logged", description=f"Modded by <@{sender_discord_id}>", colour=discord.Colour.teal())
#     embed.add_field(name="Channel", value=f"<#{channel_id}>")
#     embed.add_field(name="Category", value=category, inline=True)

#     await mod_log_channel.send(embed=embed)
