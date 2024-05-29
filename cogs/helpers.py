from typing import Optional
import discord
from discord import app_commands
from discord.ext import commands

import variables as v
from database_commands import DatabaseCommands as db

import json
import traceback

class HelperCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.add_view(StartHelperAppButtonView())
        self.bot.add_view(ModButtonView())

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        if not isinstance(message.channel, discord.TextChannel):
            return

        if message.channel.category_id != v.HELPER_APPLICATIONS_CATEGORY_ID:
            return

        channel_id = message.channel.id

        history = message.channel.history(limit=None, oldest_first=True)
        message_list = [msg async for msg in history]

        conversation_str = ""
        for msg in message_list:
            conversation_str += f"{msg.author.name}: {msg.content}\n"

        db.update_helper_application_log(
            channel_id = channel_id,
            conversation = conversation_str
        )
        print("Updating from message in helper app")

        await self.bot.process_commands(message)

    # @app_commands.command(name="helper_application_tools", description="Use to complete the process of a helper application")
    # async def test(self, interaction: discord.Interaction):

    #     if not v.HELPER_APPLICATIONS_CATEGORY_ID:
    #         await interaction.response.send_message("There is no helper application category id set in `variables.py`. Contact Vinleon or Lior so we can fix it :)", ephemeral=True)
    #         return

    #     if interaction.channel.category_id != v.HELPER_APPLICATIONS_CATEGORY_ID:

    #         await interaction.response.send_message(f"This command can only be used in a helepr application. The category ID for helper applications is stored as {v.HELPER_APPLICATIONS_CATEGORY_ID}. If that is not correct, the `variables.py` file must be updated accordingly", ephemeral=True)
    #         return

    #     history = interaction.channel.history(limit=1, oldest_first=True)
    #     original_message = [message async for  message in history][0]
    #     member = original_message.mentions[0]


    #     view = ButtonView(member)
    #     msg = f"""**Choose a button to complete the application process**"""
    #     await interaction.response.send_message(msg, view=view, ephemeral=True, delete_after=120)

    #     await view.wait()
    #     await interaction.delete_original_response()

    @app_commands.command(name="send_helper_application_button", description="Used to populate the #helper-applications channel with a button to start an app. Only used once")
    async def send_helper_application_button(self, interaction: discord.Interaction):

        assert isinstance(interaction.channel, discord.TextChannel)
        msg = f"""
## Apply here to become a <@&{v.HELPER_ROLE_ID}>!
### What is a helper?
A helper is a student who helps others to complete tasks or solve quest related dilemmas on the ReShuffle discord server. It could be content oriented, technical help, or anything else - helpers are the first people to answer.

### Am I qualified to become a helper?
If you feel confident in technology (Instagram, Discord, the ReShuffle portfolio), or if you feel great about the quality of your tasks, then yes!

### Why should I become a helper?
To help quest-mates in the server! Being a helper can be rewarding, as you get to help students from other schools use the platform and make awesome quests. Best of all, you get a cool green name. (There may be extra credit points involved too!)

### How do I apply to become a helper?
Push the “Apply Now” button below!
        """
        await interaction.channel.send(msg, view=StartHelperAppButtonView())
         

async def setup(bot):
    await bot.add_cog(HelperCog(bot))

async def create_helper_application_channel(guild: discord.Guild, member: discord.Member):
    if not guild:
        print("Timout: NO GUILD")
        return
    category = discord.utils.get(guild.categories, id=v.HELPER_APPLICATIONS_CATEGORY_ID)
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
    channel_name = f"{name}-helper-app"
    channel = await category.create_text_channel(channel_name, overwrites=overwrites)

    msg = f"""
Welcome, {member.mention}
 
We’re glad you’re interested in becoming a helper! Helpers are valuable members of our community.

If you have any questions, feel free to ask them here.

If you're ready to apply, answer these questions!

1. Tell us a bit about yourself! Where do you go to school, what are your hobbies, what do you do in your free time
2. Why do you think you would make a good helper?
"""
    initial_message = await channel.send(msg, view=ModButtonView())

    # description = f"""
# If you're ready to apply, answer these questions!
    # """
    # embed = discord.Embed(description=description, color=discord.Color.green())
    # embed.add_field(name = "Question 1", value = "Tell us a bit about yourself! Where do you go to school, what are your hobbies, what do you do in your free time", inline=False)
    # embed.add_field(name = "Question 2", value = "Why do you think you would make a good helper?", inline=False)

    # initial_message = await channel.send(msg, embed=embed, view=ModButtonView())

    return channel

# @app_commands.command(name="timeout", description="Create a private channel for user to talk to mods")
# @app_commands.describe(member = "User to time out")
# async def call_timeout(self, interaction: discord.Interaction, member: discord.Member):
#     assert interaction.guild is not None

#     await interaction.response.defer(thinking=True, ephemeral=True)
#     channel = await self.timeout(interaction.guild, member)

#     assert channel is not None
#     await interaction.followup.send(f"Channel created: {channel.mention}", ephemeral=True)

class StartHelperAppButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(StartHelperAppButton())


class StartHelperAppButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.green, emoji = '🚀', label = 'Apply Now', custom_id = 'lkdafasdfasdnaddhiwahsdf')

    async def callback(self, interaction: discord.Interaction):

        assert interaction.guild is not None
        assert isinstance(interaction.user, discord.Member)


        assert isinstance(interaction.channel, discord.TextChannel)

        await interaction.response.defer(thinking=True, ephemeral=True)

        existing_channel_id = db.user_has_open_helper_app(interaction.user.id)

        if existing_channel_id:
            channel = interaction.guild.get_channel(existing_channel_id)
            if isinstance(channel, discord.TextChannel):
                await interaction.followup.send(f"You already have an open helper application. Go to {channel.mention} to continue the application process. Feel free to reach out to the ReShuffle team if you need help")
                return


        channel = await create_helper_application_channel(interaction.guild, interaction.user)
        assert channel is not None
        await interaction.followup.send(f"Thanks for applying to become a helper! Go to {channel.mention} to start the application process")

        db.create_helper_application_log(
            user_discord_id = interaction.user.id,
            user_discord_username = interaction.user.name,
            channel_id = channel.id,
        )


class ModButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ModButton())


class ModButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.grey, label = 'Application Feedback', custom_id = 'alsjflkaoiuedsjfdklsjf')

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

        view = ButtonView(member)
        msg = f"""**Choose a button to complete the application process**"""
        await interaction.response.send_message(msg, view=view, ephemeral=True, delete_after=120)

        await view.wait()
        await interaction.delete_original_response()

class ButtonView(discord.ui.View):
    def __init__(self, member):
        super().__init__()
        self.add_item(AcceptButton(member))
        self.add_item(DenyButton(member))
        self.add_item(ArchiveButton())

class AcceptButton(discord.ui.Button):
    def __init__(self, member):
        super().__init__(style=discord.ButtonStyle.green, label = 'Accept as helper')
        self.member = member

    async def callback(self, interaction: discord.Interaction):


        with open('customer_support_messages/helper_application_feedback.json', 'r') as f:
            message_dict = json.load(f)

        #Get the accept message options
        accept_private_messages = message_dict["Accept Messages"]["Accept Private Message"]["messages"]
        accept_group_announcements = message_dict["Accept Messages"]["Accept Group Announcement"]["messages"]


        msg = f"Choose the quest that the applicant will be a helper for. The group announcement will be sent in that quest channel. If you choose None, the anouncement will be sent to <#{v.HELP_CHANNEL_ID}>"

        assert interaction.guild is not None
        guild = interaction.guild
        view = QuestDropdownView(guild)

        await interaction.response.send_message(msg, view=view, ephemeral=True, delete_after=180)
        
        self.view.stop() # Deletes the original buttons message

        await view.wait()

        previous_interaction = interaction
        interaction = view.interaction

        if view.value == None:
            quest_channel_id = None
            quest_name = ""
            quest_channel = None
        else:
            quest_channel_id = view.value
            quest_name = view.quest_name
            quest_channel = guild.get_channel(quest_channel_id)



        view = Choose(len(accept_private_messages)) 

        msg = "### Choose an accept message to send to this channel\n"
        for i, message in enumerate(accept_private_messages, start=1):
            msg += f"\n{i}: {message}\n"

        await interaction.response.send_message(msg, view=view, ephemeral=True, delete_after=180)

        await previous_interaction.delete_original_response()

        await view.wait()
        previous_interaction = interaction
        interaction = view.interaction

        if view.value == "custom":
            modal = CustomAcceptMessageModal()
            await interaction.response.send_modal(modal)
            await modal.wait()
            accept_private_message = modal.custom_message
            interaction = modal.interaction
        else:
            accept_private_message = accept_private_messages[view.value - 1]

        for i, message in enumerate(accept_group_announcements):
            accept_group_announcements[i] = message.replace("{member}", self.member.mention).replace("{quest}", quest_name)

        if quest_channel_id is not None:

            view = Choose(len(accept_group_announcements)) 

            msg = f"### Choose an accept announcement message to send to {quest_channel.mention}\n"
            for i, message in enumerate(accept_group_announcements, start=1):
                msg += f"\n{i}: {message}\n"

            await interaction.response.send_message(msg, view=view, ephemeral=True, delete_after=180)
            await previous_interaction.delete_original_response()
            await view.wait()
            previous_interaction = interaction
            interaction = view.interaction

            if view.value == "custom":
                modal = CustomGroupAcceptMessageModal()
                await interaction.response.send_modal(modal)
                await modal.wait()
                accept_group_announcement = modal.custom_message
                interaction = modal.interaction
            else:
                accept_group_announcement = accept_group_announcements[view.value - 1]

        msg = f"**Please confirm the following:**\n {self.member.mention} will be given the <@&{v.HELPER_ROLE_ID}> role\n\n"
        if quest_channel_id is not None:
            msg += f"Group announcement sent in {quest_channel.mention}:\n > **{accept_group_announcement}**\n\n"

        msg += f"Accept message sent in this channel:\n > **{accept_private_message}**\n\n"
        msg += "This will be logged in the database as an acceptence\n\n If anything here is wrong, press cancel, then start the acceptance process again."

        view = ConfirmButtonsView()
        await interaction.response.send_message(msg, view=view, ephemeral=True, delete_after=180)
        await previous_interaction.delete_original_response()
        await view.wait()
        previous_interaction = interaction
        interaction = view.interaction

        if view.value == False:
            await interaction.response.send_message("Cancelled. Click on the Mod Button, then Accept to restart this process", ephemeral=True, delete_after=30)
            return


        await interaction.channel.send(accept_private_message)
        if quest_channel_id is not None:
            await quest_channel.send(accept_group_announcement)


        await interaction.response.defer(ephemeral=True, thinking=True)
        response = ""

        assert interaction.guild is not None
        helper_role = interaction.guild.get_role(v.HELPER_ROLE_ID)
        assert helper_role is not None

        member = self.member

        try:
            await member.add_roles(helper_role)
        except:
            response += f"Something went wrong trying to give {member.mention} the {helper_role.mention} role\n\n**You can add the helper role manually by clicking on their profile picture, slecting +, and choosing Helper**"
            return
        else:
            response += f"{member.mention} has been given the {helper_role.mention} role!"


        assert isinstance(interaction.channel, discord.TextChannel)
        assert isinstance(interaction.user, discord.Member)
        mod_log_message = await log_helper_application(
            channel = interaction.channel,
            member = member,
            staff = interaction.user,
            accepted = True,
            reason = None,
            quest = quest_name
        )
        assert isinstance(mod_log_message, discord.Message)

        history = interaction.channel.history(limit=None, oldest_first=True)
        message_list = [message async for  message in history]

        conversation_str = ""
        for message in message_list:
            conversation_str += f"{message.author.name}: {message.content}\n"

        try:
            helper_application_log_id = db.accept_helper_application_log(
                channel_id = interaction.channel.id,
                conversation = conversation_str,
                moderator_discord_id = interaction.user.id,
                moderator_discord_username = interaction.user.name,
                quest = quest_name
                )

        except Exception as e:
            print(f"Something went wrong with adding the helper application to the database: {e}")
            response += f"\n\nSomething went wrong trying to log the application in the database:\n> {e}"
            helper_application_log_id = None
        else:
            response += f"\n\nThe helper application has been logged in the database"
            response += "\n\nYou can use the button below to add notes about this application"

        view = AddNotesView(helper_application_log_id, mod_log_message)
        await interaction.followup.send(response, view=view, ephemeral=True)
        # await previous_interaction.delete_original_response()


class DenyButton(discord.ui.Button):
    def __init__(self, member):
        super().__init__(style=discord.ButtonStyle.red, label = 'Deny')
        self.member = member

    async def callback(self, interaction: discord.Interaction):

        with open('customer_support_messages/helper_application_feedback.json', 'r') as f:
            message_dict = json.load(f)

        deny_dict = message_dict["Deny Private Message"]

        options = []

        for reason in message_dict["Deny Private Message"]:
            if reason == "emoji":
                continue
            emoji = message_dict["Deny Private Message"][reason].get("emoji") or None
            options.append(discord.SelectOption(label=reason, emoji=emoji))

        options.append(discord.SelectOption(label="Custom Reason", emoji="✍️"))

        view = DenyDropdownView(options)
        await interaction.response.send_message("Choose a reason", view=view, ephemeral=True)

        await view.wait()

        reason = view.value
        previous_interaction = interaction
        interaction = view.interaction

        if reason == "Custom Reason":
            modal = CustomReasonModal()
            await interaction.response.send_modal(modal)
            await modal.wait()
            reason = modal.custom_reason
            deny_message = modal.custom_message
            # notes = modal.notes
            interaction = modal.interaction
            # await interaction.response.send_message("Received", ephemeral=True, delete_after=15)

        else:
            messages = deny_dict[reason]["messages"]

            view = Choose(len(messages)) 

            msg = "### Choose an rejection message to send to this channel\n"
            for i, message in enumerate(messages, start=1):
                msg += f"\n{i}: {message}\n"

            await interaction.response.send_message(msg, view=view, ephemeral=True, delete_after=180)

            await previous_interaction.delete_original_response()

            await view.wait()
            previous_interaction = interaction
            interaction = view.interaction

            if view.value == "custom":
                modal = CustomDenyMessageModal()
                await interaction.response.send_modal(modal)
                await modal.wait()
                deny_message = modal.custom_message
                # notes = modal.notes
                interaction = modal.interaction
                # await interaction.response.send_message("Received", ephemeral=True, delete_after=15)
            else:
                deny_message = messages[view.value -1]

        await interaction.channel.send(deny_message)


        member = self.member

        await interaction.response.defer(ephemeral=True, thinking=True)


        assert isinstance(interaction.channel, discord.TextChannel)
        assert isinstance(interaction.user, discord.Member)
        mod_log_message = await log_helper_application(interaction.channel, member, interaction.user, False, reason)

        assert isinstance(mod_log_message, discord.Message)

        history = interaction.channel.history(limit=None, oldest_first=True)
        message_list = [message async for  message in history]

        conversation_str = ""
        for message in message_list:
            conversation_str += f"{message.author.name}: {message.content}\n"


        helper_application_log_id = db.deny_helper_application_log(
            channel_id = interaction.channel.id,
            conversation = conversation_str,
            rejection_reason = str(reason),
            moderator_discord_id = interaction.user.id,
            moderator_discord_username = interaction.user.name

                )

        view = AddNotesView(helper_application_log_id, mod_log_message)

        msg = f"""### Helper application for {member.mention} has been denied

Denial Reason: 
> **{reason}**

Rejection Message:
> **{deny_message}**

This has been logged to the database

Press the "Add Notes" button below to add notes about this helper application or rejection message
        """
        await interaction.followup.send(msg, view=view)

class ArchiveButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.gray, label = 'Archive Channel')

    async def callback(self, interaction: discord.Interaction):

        await interaction.response.defer(ephemeral=True, thinking=True)

        assert interaction.guild is not None
        assert isinstance(interaction.channel, discord.TextChannel)

        archive_category = interaction.guild.get_channel(v.HELPER_APPLICATIONS_ARCHIVE_CATEGORY_ID)
        if not isinstance(archive_category, discord.CategoryChannel) or not v.HELPER_APPLICATIONS_ARCHIVE_CATEGORY_ID:
            await interaction.followup.send("The helper applications archive category is not set properly in `variables.py`. It must be the ID of a category.")
            return

        try:
            await interaction.channel.move(category=archive_category, sync_permissions=False, beginning=True)
        except Exception as e:
            await interaction.followup.send(f"Something went wrong when trying to move this channel to the Archive category.\n\nError: {e}", ephemeral=True)
            

        await interaction.followup.send("This channel has been moved to the Archive. The applicant can still see this channel.", ephemeral=True)


class ChooseButton(discord.ui.Button):
    def __init__(self, number: int):
        super().__init__(style=discord.ButtonStyle.green, label=f"Choose {number}")
        self.number = number

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        # view: Choose = self.view
        view = self.view
        view.value = self.number
        view.stop()
        view.interaction = interaction
        # await interaction.response.send_message("Message sent!", ephemeral=True, delete_after = 10)#, view=NotesView())

class CustomButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Custom Message")

    async def callback(self, interaction: discord.Interaction):

        assert self.view is not None
        view = self.view
        view.interaction = interaction
        view.value = "custom"
        view.stop()

class Choose(discord.ui.View):
    def __init__(self, num_choices: int):
        super().__init__()
        self.value = None

        for i in range(num_choices):
            self.add_item(ChooseButton(i+1))
        self.add_item(CustomButton())

class CustomAcceptMessageModal(discord.ui.Modal, title="Custom Accept Message"):
    def __init__(self):
        super().__init__()
    custom_message = discord.ui.TextInput(
        label = "Accept Message",
        placeholder= "Type the custom accept message here...",
        style=discord.TextStyle.long
    )
    async def on_submit(self, interaction: discord.Interaction):
        self.interaction = interaction
        self.custom_message = self.custom_message.value
        self.stop()

class CustomGroupAcceptMessageModal(discord.ui.Modal, title="Custom Group Accept Message"):
    def __init__(self):
        super().__init__()
    custom_message = discord.ui.TextInput(
        label = "Group Accept Message",
        placeholder= "Type the custom message to send to the group here...",
        style=discord.TextStyle.long
    )
    async def on_submit(self, interaction: discord.Interaction):
        self.interaction = interaction
        self.custom_message = self.custom_message.value
        self.stop()

class CustomDenyMessageModal(discord.ui.Modal, title="Custom Rejection Message"):

    def __init__(self):
        super().__init__()

    custom_message = discord.ui.TextInput(
        label = "Rejection Message",
        placeholder= "Type the custom rejection message here...",
        style=discord.TextStyle.long
    )

    # notes = discord.ui.TextInput(
    #     label = "Notes",
    #     placeholder= "Notes about this interaction\n- Should we add this as a new message?",
    #     style=discord.TextStyle.long,
    #     required=False
    # )
    async def on_submit(self, interaction: discord.Interaction):
        self.custom_message = self.custom_message.value
        # self.notes = self.notes.value
        self.interaction = interaction
        self.stop()

class CustomReasonModal(discord.ui.Modal, title="Custom Denial Reason"):

    def __init__(self):
        super().__init__()

    custom_reason = discord.ui.TextInput(
        label = "Custom Rejection Reason",
        placeholder= "Type the reason for rejection here...",
    )
    custom_message = discord.ui.TextInput(
        label = "Message",
        placeholder= "Type the custom rejection message here...",
        style=discord.TextStyle.long
    )

    # notes = discord.ui.TextInput(
    #     label = "Notes",
    #     placeholder= "Notes about this interaction\n- Should we add this as a new option?",
    #     style=discord.TextStyle.long,
    #     required=False
    # )

    async def on_submit(self, interaction: discord.Interaction):
        self.custom_reason = self.custom_reason.value
        self.custom_message = self.custom_message.value
        # self.notes = self.notes.value
        self.interaction = interaction
        self.stop()


    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:

        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        print(type(error), error, error.__traceback__)

class ConfirmButtonsView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        # await interaction.response.send_message('Confirming', ephemeral=True)
        self.value = True
        self.interaction = interaction
        self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        # await interaction.response.send_message('Cancelling', ephemeral=True)
        self.value = False
        self.interaction = interaction
        self.stop()

class DenyDropdownView(discord.ui.View):
    def __init__(self, options):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(DenyDropdown(options))

class DenyDropdown(discord.ui.Select):
    def __init__(self, options):
        super().__init__(placeholder='Choose the reason for decline...', min_values=1, max_values=1, options=options)
        # self.deny_dict = deny_dict

    async def callback(self, interaction: discord.Interaction):

        reason = self.values[0]
        # await interaction.response.send_message(reason)

        view = self.view
        view.value = self.values[0]
        view.interaction = interaction
        view.stop()
        return


        if reason == "Custom Reason":
            # await interaction.response.send_modal(CustomReasonModal(self.original_message, self.category))
            return

        messages = self.deny_dict[reason]["messages"]

        view = Choose(len(messages), self.category, subcategory, question) 

        # msg="### Choose which message to send\n"
        # for i, message in enumerate(messages, start=1):
        #     msg += f"\n{i}: {message}\n"

        # await interaction.response.send_message(msg, view=view, ephemeral=True, delete_after=30)
        # await view.wait()

        # if view.value == "custom":
        #     return

        # message = messages[view.value - 1]

        # # await view.interaction.response.send_message("TESZT THIS", ephemeral=True)

        # await send_and_log_support_message(
        #     interaction = view.interaction,
        #     category = self.category,
        #     problem = question,
        #     message = message,
        #     # notes = self.notes.value,
        #     subcategory = subcategory,
        #     is_custom=False,
        #     is_custom_category = False,
        #     is_custom_problem = False,
        #     is_custom_message = False,
        #     original_message = self.original_message
        # )


class AddNotesView(discord.ui.View):
    def __init__(self, helper_log_id: Optional[int], mod_log_message: discord.Message):
        super().__init__(timeout=None)
        if helper_log_id is not None:
            self.add_item(AddNotesButton(helper_log_id, mod_log_message))

class AddNotesButton(discord.ui.Button):
    def __init__(self, helper_log_id: int, mod_log_message: discord.Message):
        super().__init__(style=discord.ButtonStyle.blurple, label = 'Add Notes')
        self.helper_log_id = helper_log_id
        self.mod_log_message = mod_log_message

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(NotesModal(helper_log_id=self.helper_log_id, mod_log_message=self.mod_log_message))
        # self.stop() # but would really be self.view if i wanted that


class NotesModal(discord.ui.Modal, title="Add Notes"):
    def __init__(self, helper_log_id: int, mod_log_message: discord.Message):
        super().__init__()
        self.helper_log_id = helper_log_id
        self.mod_log_message = mod_log_message

    notes = discord.ui.TextInput(
        label='Notes',
        style=discord.TextStyle.long,
        placeholder='Add notes about this interaction...',
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        print(f"submitted id: {self.custom_id}")
        db.update_helper_log_notes(self.helper_log_id, self.notes.value)
        # await interaction.response.send_message(f"Notes added!", ephemeral=True)
        await interaction.followup.send(f"Notes added!", ephemeral=True)

        mod_log_message = self.mod_log_message
        mod_log_embed = mod_log_message.embeds[0]
        mod_log_embed.add_field(name="Notes", value=self.notes.value, inline=False)
        await mod_log_message.edit(embed=mod_log_embed)


    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)
        traceback.print_exception(type(error), error, error.__traceback__)


class QuestDropdownView(discord.ui.View):
    def __init__(self, guild: discord.Guild):
        super().__init__()
        self.add_item(QuestDropdown(guild))

class QuestDropdown(discord.ui.Select):
    def __init__(self, guild: discord.Guild):

        # Set the options that will be presented inside the dropdown
        options = []

        quest_channels_category = guild.get_channel(v.QUEST_CHANNELS_CATEGORY_ID)
        if not isinstance(quest_channels_category, discord.CategoryChannel) or not v.QUEST_CHANNELS_CATEGORY_ID:
            # await interaction.followup.send("The helper applications archive category is not set properly in `variables.py`. It must be the ID of a category.")
            return

        for channel in quest_channels_category.text_channels:
            name = channel.name
            emoji=name[0]
            quest_name = name[1:].replace('-', ' ').replace('1', ' 1').replace('2', ' 2').title()
            options.append(discord.SelectOption(label=quest_name, emoji=emoji, value=str(channel.id)))

        options.append(discord.SelectOption(label="#help-channel", emoji='🙋', value=str(v.HELP_CHANNEL_ID)))
        options.append(discord.SelectOption(label="None (don't send a group message)", emoji='❌', value="None"))

        super().__init__(placeholder='Choose the quest...', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):


        view = self.view
        view.interaction = interaction

        quest = self.values[0]
        if quest == "None":
            view.value = None
            view.stop()

        quest_name = [option.label for option in self.options if option.value == self.values[0]][0]



        quest_channel_id = int(self.values[0])

        view.value = quest_channel_id
        view.quest_name = quest_name

        view.stop()

        # quest_channel = interaction.guild.get_channel(quest_channel_id)
        # await interaction.channel.send(quest_channel.mention)

        # await interaction.response.send_message(quest)





async def log_helper_application(
    *,
    channel: discord.TextChannel,
    member: discord.Member,
    staff: discord.Member,
    accepted: bool,
    reason: Optional[str] = None,
    quest: Optional[str] = None
    ):

    mod_log_channel = await channel.guild.fetch_channel(v.MOD_LOG_CHANNEL_ID)
     
    if not mod_log_channel:
        print("NO MOD LOG CHANNEL FOUND")
        return

    if accepted:
        title = f"Helper Application Acceptence"
        embed = discord.Embed(title=title, colour=discord.Color.green())
        embed.add_field(name=f"Member", value=member.mention, inline=False)
        embed.add_field(name=f"Accepted By", value=staff.mention, inline=False)
        embed.add_field(name=f"Quest", value=quest, inline=False)

    else:
        title = f"Helper Application Rejection"
        embed = discord.Embed(title=title, colour=discord.Color.brand_red())
        embed.add_field(name=f"Member", value=member.mention, inline=False)
        embed.add_field(name=f"Rejected By", value=staff.mention, inline=False)
        embed.add_field(name=f"Reason for rejection", value=reason, inline=False)


    embed.add_field(name=f"Application Channel", value=channel.mention, inline=False)

    mod_log_message = await mod_log_channel.send(embed=embed)
    return mod_log_message
