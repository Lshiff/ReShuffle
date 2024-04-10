import discord
from discord import app_commands
from discord.ext import commands

import json

from database_commands import DatabaseCommands as db
import variables as v


#TODO Log Commands

class RehelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rehelp_context_menu = app_commands.ContextMenu(
            name="Support",
            callback = self.rehelp_context_menu_callback
        )
        self.bot.tree.add_command(self.rehelp_context_menu)

    async def rehelp_context_menu_callback(self, interaction: discord.Interaction, message: discord.Message):
        with open('customer_support_messages/support.json', 'r') as f:
            message_dict = json.load(f)
        original_message = message
        view = HelpCategoryDropdownView(message_dict, original_message)
        await interaction.response.send_message("Pick the category", view = view, ephemeral=True)


    @app_commands.command(name="support", description="Choose help message to send")
    async def rehelp(self, interaction: discord.Interaction):
        with open('customer_support_messages/support.json', 'r') as f:
            message_dict = json.load(f)
        view = HelpCategoryDropdownView(message_dict)
        await interaction.response.send_message("Pick the category", view = view, ephemeral=True)


async def setup(bot):
    await bot.add_cog(RehelpCog(bot))


class CustomCategoryModal(discord.ui.Modal, title="Custom Category/Message"):

    def __init__(self, original_message=None):
        super().__init__()
        self.original_message = original_message

    custom_category = discord.ui.TextInput(
        label = "Category",
        placeholder= "Type the custom category here..."
    )

    custom_problem = discord.ui.TextInput(
        label = "Problem/Question",
        placeholder= "Type the custom problem/question here...",
        # required=False
    )

    custom_message = discord.ui.TextInput(
        label = "Message",
        placeholder= "Type the custom message here...",
        style=discord.TextStyle.long
    )

    notes = discord.ui.TextInput(
        label = "Notes",
        placeholder= "Notes about this interaction\n- Should we add this as a new category?",
        style=discord.TextStyle.long,
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):

        # await interaction.response.send_message("Message Sent", ephemeral=True)

        # if self.original_message:
        #     await self.original_message.reply(self.custom_message.value)
        # else:
        #     await interaction.channel.send(self.custom_message.value)

        # if self.notes.value:
        #     notes = self.notes.value
        # else:
        #     notes = ""

        await support_message_embed_send(
            interaction = interaction,
            category = self.custom_category.value,
            problem = self.custom_problem.value,
            message = self.custom_message.value,
            notes = self.notes.value,
            is_custom=True,
            custom_category = True,
            custom_problem = True,
            custom_message = True,
            original_message = self.original_message
        )


        # mod_log_channel = await interaction.guild.fetch_channel(v.MOD_LOG_CHANNEL_ID)
        # if not mod_log_channel:
        #     print("NO MOD LOG CHANNEL FOUND")
        #     return

        # embed = discord.Embed(title="Custom Support Message", description=f"Sent by {interaction.user.mention}", colour=discord.Color.teal())
        # embed.add_field(name="Custom Category", value=self.custom_category.value, inline=False)

        # if self.custom_problem.value:
        #     embed.add_field(name="Custom Problem/Question", value=self.custom_problem.value, inline=False)

        # embed.add_field(name="Custom Message", value=self.custom_message.value, inline=False)

        # if self.notes.value:
        #     embed.add_field(name="Notes", value=self.notes.value, inline=False)

        # if self.original_message:
        #     embed.add_field(name="Original Message", value = f"Sent by {self.original_message.author.mention}\nLink: {self.original_message.jump_url}\nContent:\n> {self.original_message.content}")

        # await mod_log_channel.send(embed=embed)
        # await mod_log_channel.send(f"Custom message sent by {interaction.user.mention}:\nCategory: {self.custom_category.value}\nMessage: {self.custom_message.value}\nNotes: {self.notes.value}")


    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:

        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        print(type(error), error, error.__traceback__)

 
class CustomProblemModal(discord.ui.Modal, title="Custom Message"):

    def __init__(self, original_message=None, category=None):
        super().__init__()
        self.original_message = original_message
        self.category = category

    custom_question = discord.ui.TextInput(
        label = "Custom Problem/Question",
        placeholder= "Type the question/problem you are answering here...",
    )
    custom_message = discord.ui.TextInput(
        label = "Message",
        placeholder= "Type the custom message here...",
        style=discord.TextStyle.long
    )

    notes = discord.ui.TextInput(
        label = "Notes",
        placeholder= "Notes about this interaction\n- Should we add this as a new option?",
        style=discord.TextStyle.long,
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):

#         await interaction.response.send_message("Message Sent", ephemeral=True)

#         if self.original_message:
#             await self.original_message.reply(self.custom_message.value)
#         else:
#             await interaction.channel.send(self.custom_message.value)

        await support_message_embed_send(
            interaction = interaction,
            category = self.category,
            problem = self.custom_question.value,
            message = self.custom_message.value,
            notes = self.notes.value,
            is_custom=True,
            custom_category = False,
            custom_problem = True,
            custom_message = True,
            original_message = self.original_message
        )

        # mod_log_channel = await interaction.guild.fetch_channel(v.MOD_LOG_CHANNEL_ID)
        # if not mod_log_channel:
        #     print("NO MOD LOG CHANNEL FOUND")
        #     return

        # embed = discord.Embed(title="Custom Support Message", description=f"Sent by {interaction.user.mention}", colour=discord.Color.teal())
        # embed.add_field(name="Category", value=self.category, inline=False)

        # embed.add_field(name="Custom Problem/Question", value=self.custom_question.value, inline=False)
        # embed.add_field(name="Custom Message", value=self.custom_message.value, inline=False)

        # if self.notes.value:
        #     embed.add_field(name="Notes", value=self.notes.value, inline=False)

        # await mod_log_channel.send(embed=embed)
        # await mod_log_channel.send(f"Custom message sent by {interaction.user.mention}:\nMessage: {self.custom_message.value}\nNotes: {self.notes.value}")


    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:

        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        print(type(error), error, error.__traceback__)


class CustomMessageModal(discord.ui.Modal, title="Custom Message"):

    def __init__(self, original_message, category, question):
        super().__init__()
        self.original_message = original_message
        self.category = category
        self.question = question

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

        # await interaction.response.send_message("Message Sent", ephemeral=True)

        # if self.original_message:
        #     await self.original_message.reply(self.custom_message.value)
        # else:
        #     await interaction.channel.send(self.custom_message.value)

        await support_message_embed_send(
            interaction = interaction,
            category = self.category,
            problem = self.question,
            message = self.custom_message.value,
            notes = self.notes.value,
            is_custom=True,
            custom_category = False,
            custom_problem = False,
            custom_message = True,
            original_message = self.original_message
        )

        # mod_log_channel = await interaction.guild.fetch_channel(v.MOD_LOG_CHANNEL_ID)
        # if not mod_log_channel:
        #     print("NO MOD LOG CHANNEL FOUND")
        #     return

        # embed = discord.Embed(title="Custom Support Message", description=f"Sent by {interaction.user.mention}", colour=discord.Color.teal())
        # embed.add_field(name="Category", value=self.category, inline=False)
        # embed.add_field(name="Custom Problem/Question", value=self.question, inline=False)

        # embed.add_field(name="Custom Message", value=self.custom_message.value, inline=False)

        # if self.notes.value:
        #     embed.add_field(name="Notes", value=self.notes.value, inline=False)

        # await mod_log_channel.send(embed=embed)

        # await mod_log_channel.send(f"Custom moderation message sent by {interaction.user.mention}:\nMessage: {self.custom_message.value}\nNotes: {self.notes.value}")

class HelpCategoryDropdownView(discord.ui.View):
    def __init__(self, message_dict, original_message=None):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(HelpCategoryDropdown(message_dict, original_message))

class HelpCategoryDropdown(discord.ui.Select):
    def __init__(self, message_dict, original_message=None):
        self.message_dict = message_dict
        self.original_message = original_message

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
            await interaction.response.send_modal(CustomCategoryModal(self.original_message))
            return


        options = []
        for question in self.message_dict[category]:
            if question == "emoji":
                continue
            emoji = self.message_dict[category][question].get("emoji") or None
            options.append(discord.SelectOption(label=question, emoji=emoji))

        options.append(discord.SelectOption(label="Custom Problem/Question", emoji="✍️"))


        view = HelpTopicDropdownView(options, category, self.message_dict, self.original_message)

        await interaction.response.send_message("Pick the problem/question", view = view, ephemeral=True)

class HelpTopicDropdownView(discord.ui.View):
    def __init__(self, options, category, message_dict, original_message=None):
        super().__init__()
        self.category = category

        # Adds the dropdown to our view object.
        self.add_item(HelpTopicDropdown(options, category, message_dict, original_message))

class HelpTopicDropdown(discord.ui.Select):
    def __init__(self, options, category, message_dict, original_message=None):
        super().__init__(placeholder='Choose the problem/question...', min_values=1, max_values=1, options=options)
        self.category = category
        self.message_dict = message_dict
        self.original_message = original_message

    async def callback(self, interaction: discord.Interaction):

        question = self.values[0]

        if question == "Custom Problem/Question":
            await interaction.response.send_modal(CustomProblemModal(self.original_message, self.category))
            return

        messages = self.message_dict[self.category][question]["messages"]

        view = Choose(len(messages), self.original_message, self.category, question) 

        msg="### Choose which message to send\n"
        for i, message in enumerate(messages, start=1):
            msg += f"\n{i}: {message}\n"

        await interaction.response.send_message(msg, view=view, ephemeral=True)
        await view.wait()

        if view.value == "custom":
            return

        message = messages[view.value - 1]

        # if self.original_message:
        #     await self.original_message.reply(message)
        # else:
        #     await interaction.channel.send(message)

        await support_message_embed_send(
            interaction = interaction,
            category = self.category,
            problem = question,
            message = message,
            # notes = self.notes.value,
            is_custom=False,
            custom_category = False,
            custom_problem = False,
            custom_message = False,
            original_message = self.original_message
        )


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

class CustomButton(discord.ui.Button):
    def __init__(self, original_message, category, question):
        super().__init__(style=discord.ButtonStyle.blurple, label="Custom Message")
        self.original_message = original_message
        self.category = category
        self.question = question

    async def callback(self, interaction: discord.Interaction):

        await interaction.response.send_modal(CustomMessageModal(self.original_message, self.category, self.question))

        assert self.view is not None
        view: Choose = self.view
        view.value = "custom"
        # view.stop()

class Choose(discord.ui.View):
    def __init__(self, num_choices: int, original_message, category, question):
        super().__init__()
        self.value = None

        for i in range(num_choices):
            self.add_item(ChooseButton(i+1))
        self.add_item(CustomButton(original_message, category, question))


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



async def support_message_embed_send(
    interaction: discord.Interaction,
    category: str, 
    problem: str, 
    message: str, 
    notes: str = "", 
    is_custom: bool = False, 
    custom_category: bool = False, 
    custom_problem: bool = False, 
    custom_message: bool = False, 
    original_message = None, 

    ):

    if not interaction.response.is_done():
        await interaction.response.send_message("Message Sent", ephemeral=True)

    if original_message:
        await original_message.reply(message)
    else:
        await interaction.channel.send(message)

    mod_log_channel = await interaction.guild.fetch_channel(v.MOD_LOG_CHANNEL_ID)
     
    if not mod_log_channel:
        print("NO MOD LOG CHANNEL FOUND")
        return

    title = f"{'Custom' if is_custom else ''} Suport Message Log"
    embed = discord.Embed(title=title, description=f"Sent by {interaction.user.mention}", colour=discord.Color.teal())

    embed.add_field(name=f"{'Custom' if custom_category else ''} Category", value=category, inline=False)
    embed.add_field(name=f"{'Custom' if custom_problem else ''} Problem", value=problem, inline=False)
    embed.add_field(name=f"{'Custom' if custom_message else ''} Message", value=message, inline=False)

    if notes:
        embed.add_field(name="Notes", value=notes, inline=False)

    if original_message:
        embed.add_field(name="Original Message", value = f"Sent by {original_message.author.mention}\nLink: {original_message.jump_url}\nContent:\n> {original_message.content}")

    await mod_log_channel.send(embed=embed)
