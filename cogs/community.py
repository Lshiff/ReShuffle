import discord
from discord import app_commands
from discord.ext import commands

import json
import traceback

from database_commands import DatabaseCommands as db
import variables as v


class CommunityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rehelp_context_menu = app_commands.ContextMenu(
            name="Community",
            callback = self.rehelp_context_menu_callback
        )
        self.bot.tree.add_command(self.rehelp_context_menu)

    async def rehelp_context_menu_callback(self, interaction: discord.Interaction, message: discord.Message):
        with open('customer_support_messages/community.json', 'r') as f:
            message_dict = json.load(f)
        original_message = message
        view = HelpCategoryDropdownView(message_dict, original_message)
        await interaction.response.send_message("Pick the category", view = view, ephemeral=True)


    @app_commands.command(name="community", description="Choose community message to send")
    async def rehelp(self, interaction: discord.Interaction):
        with open('customer_support_messages/community.json', 'r') as f:
            message_dict = json.load(f)
        view = HelpCategoryDropdownView(message_dict)
        await interaction.response.send_message("Pick the category", view = view, ephemeral=True)


async def setup(bot):
    await bot.add_cog(CommunityCog(bot))


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

        await send_and_log_community_message(
            interaction = interaction,
            category = self.custom_category.value,
            problem = self.custom_problem.value,
            message = self.custom_message.value,
            notes = self.notes.value,
            is_custom=True,
            is_custom_category = True,
            is_custom_problem = True,
            is_custom_message = True,
            original_message = self.original_message
        )


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

        await send_and_log_community_message(
            interaction = interaction,
            category = self.category,
            problem = self.custom_question.value,
            message = self.custom_message.value,
            notes = self.notes.value,
            is_custom=True,
            is_custom_category = False,
            is_custom_problem = True,
            is_custom_message = True,
            original_message = self.original_message
        )


    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:

        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        print(type(error), error, error.__traceback__)


class CustomMessageModal(discord.ui.Modal, title="Custom Message"):

    def __init__(self, original_message, category, subcategory, question):
        super().__init__()
        self.original_message = original_message
        self.category = category
        self.subcategory = subcategory
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


        await send_and_log_community_message(
            interaction = interaction,
            category = self.category,
            problem = self.question,
            message = self.custom_message.value,
            notes = self.notes.value,
            subcategory = self.subcategory,
            is_custom=True,
            is_custom_category = False,
            is_custom_problem = False,
            is_custom_message = True,
            original_message = self.original_message
        )

class HelpCategoryDropdownView(discord.ui.View):
    def __init__(self, message_dict, original_message=None):
        super().__init__()
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
        subcategory = self.message_dict[self.category][question]["subcategory"]

        view = Choose(len(messages), self.original_message, self.category, subcategory, question) 

        msg="### Choose which message to send\n"
        for i, message in enumerate(messages, start=1):
            msg += f"\n{i}: {message}\n"

        await interaction.response.send_message(msg, view=view, ephemeral=True)
        await view.wait()

        if view.value == "custom":
            return

        message = messages[view.value - 1]

        # await view.interaction.response.send_message("TESZT THIS", ephemeral=True)

        await send_and_log_community_message(
            interaction = view.interaction,
            category = self.category,
            problem = question,
            message = message,
            # notes = self.notes.value,
            subcategory = subcategory,
            is_custom=False,
            is_custom_category = False,
            is_custom_problem = False,
            is_custom_message = False,
            original_message = self.original_message
        )



class ChooseButton(discord.ui.Button):
    def __init__(self, number: int):
        super().__init__(style=discord.ButtonStyle.green, label=str(number))
        self.number = number

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        # view: Choose = self.view
        view = self.view
        view.value = self.number
        view.stop()
        view.interaction = interaction
        # await interaction.response.send_message("Message sent!", view=NotesView(), ephemeral=True)

class CustomButton(discord.ui.Button):
    def __init__(self, original_message, category, subcategory, question):
        super().__init__(style=discord.ButtonStyle.blurple, label="Custom Message")
        self.original_message = original_message
        self.category = category
        self.subcategory = subcategory
        self.question = question

    async def callback(self, interaction: discord.Interaction):

        await interaction.response.send_modal(CustomMessageModal(self.original_message, self.category, self.subcategory, self.question))

        assert self.view is not None
        view = self.view
        view.value = "custom"
        # view.stop()

class Choose(discord.ui.View):
    def __init__(self, num_choices: int, original_message, category, subcategory, question):
        super().__init__()
        self.value = None

        for i in range(num_choices):
            self.add_item(ChooseButton(i+1))
        self.add_item(CustomButton(original_message, category, subcategory, question))



class AddNotesView(discord.ui.View):
    def __init__(self, community_log_id: int, mod_log_message: discord.Message):
        super().__init__()
        self.add_item(AddNotesButton(community_log_id, mod_log_message))

class AddNotesButton(discord.ui.Button):
    def __init__(self, community_log_id: int, mod_log_message: discord.Message):
        super().__init__(style=discord.ButtonStyle.blurple, label = 'Add Notes')
        self.community_log_id = community_log_id
        self.mod_log_message = mod_log_message

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(NotesModal(community_log_id=self.community_log_id, mod_log_message=self.mod_log_message))
        # self.stop() # but would really be self.view if i wanted that


class NotesModal(discord.ui.Modal, title="Add Notes"):
    def __init__(self, community_log_id: int, mod_log_message: discord.Message):
        super().__init__()
        self.community_log_id = community_log_id
        self.mod_log_message = mod_log_message

    notes = discord.ui.TextInput(
        label='Notes',
        style=discord.TextStyle.long,
        placeholder='Add notes about this interaction...',
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        print(f"submitted id: {self.custom_id}")
        db.update_community_log_notes(self.community_log_id, self.notes.value)
        # await interaction.response.send_message(f"Notes added!", ephemeral=True)
        await interaction.followup.send(f"Notes added!", ephemeral=True)

        mod_log_message = self.mod_log_message
        mod_log_embed = mod_log_message.embeds[0]
        mod_log_embed.add_field(name="Notes", value=self.notes.value, inline=False)
        await mod_log_message.edit(embed=mod_log_embed)


    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)
        traceback.print_exception(type(error), error, error.__traceback__)

async def send_and_log_community_message(
    interaction: discord.Interaction,
    category: str, 
    problem: str, 
    message: str, 
    notes: str = "", 
    subcategory: str = "",
    is_custom: bool = False, 
    is_custom_category: bool = False, 
    is_custom_problem: bool = False, 
    is_custom_message: bool = False, 
    original_message = None, 
    ):

    await interaction.response.defer(ephemeral=True, thinking=True)

    if original_message:
        response_message = await original_message.reply(message)
    else:
        response_message = await interaction.channel.send(message)

    mod_log_channel = await interaction.guild.fetch_channel(v.MOD_LOG_CHANNEL_ID)
     
    if not mod_log_channel:
        print("NO MOD LOG CHANNEL FOUND")
        return

    title = f"{'Custom' if is_custom else ''} Suport Message Log"
    embed = discord.Embed(title=title, description=f"Sent by {interaction.user.mention}", colour=discord.Color.teal())

    embed.add_field(name=f"{'Custom' if is_custom_category else ''} Category", value=category, inline=False)
    embed.add_field(name=f"{'Custom' if is_custom_problem else ''} Problem", value=problem, inline=False)
    embed.add_field(name=f"{'Custom' if is_custom_message else ''} Message", value=message, inline=False)

    if notes:
        embed.add_field(name="Notes", value=notes, inline=False)

    if original_message:
        embed.add_field(name="Original Message", value = f"Sent by {original_message.author.mention}\nLink: {original_message.jump_url}\nContent:\n> {original_message.content}")

    mod_log_message = await mod_log_channel.send(embed=embed)

    #save to db

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


    community_log_id = db.create_community_log(
        category = category,
        subcategory = subcategory,
        question = problem,
        message = message,
        notes = notes,
        is_custom = is_custom,
        is_custom_category = is_custom_category,
        is_custom_question = is_custom_problem,
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
        view = AddNotesView(community_log_id=community_log_id, mod_log_message=mod_log_message)
        await interaction.followup.send(f"Message has ben sent! This interaction has been logged in <#{v.MOD_LOG_CHANNEL_ID}> and in the database. To add notes to this interaction, press the button ↓", view=view, ephemeral=True)
    else:
        await interaction.followup.send("Message Sent", ephemeral=True)
