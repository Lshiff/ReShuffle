import discord
from discord import app_commands
from discord.ext import commands

import variables as v
from database_commands import DatabaseCommands as db

import traceback

class HelperCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="helper_application_tools", description="Use to complete the process of a helper application")
    async def test(self, interaction: discord.Interaction):

        if not v.HELPER_APPLICATIONS_CATEGORY_ID:
            await interaction.response.send_message("There is no helper application category id set in `variables.py`. Contact Vinleon or Lior so we can fix it :)", ephemeral=True)
            return

        if interaction.channel.category_id != v.HELPER_APPLICATIONS_CATEGORY_ID:

            await interaction.response.send_message(f"This command can only be used in a helepr application. The category ID for helper applications is stored as {v.HELPER_APPLICATIONS_CATEGORY_ID}. If that is not correct, the `variables.py` file must be updated accordingly", ephemeral=True)
            return

        history = interaction.channel.history(limit=1, oldest_first=True)
        original_message = [message async for  message in history][0]
        member = original_message.mentions[0]


        view = ButtonView(member)
        msg = f"""
Choose a button to complete the application process.

Accept: Marks the application as accepted, and gives the user the <@&{v.HELPER_ROLE_ID}> role
Deny: Marks the application as denied.
Archive: Moves the channel to the Closed Helper Applications category. The applicant will still be able to see this channel.
        """
        await interaction.response.send_message(msg, view=view, ephemeral=True)
         

async def setup(bot):
    await bot.add_cog(HelperCog(bot))

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

        await interaction.response.defer(ephemeral=True, thinking=True)
        response = ""

        assert interaction.guild is not None
        helper_role = interaction.guild.get_role(v.HELPER_ROLE_ID)
        assert helper_role is not None

        try:
            await self.member.add_roles(helper_role)
        except:
            response += f"Something went wrong trying to give {self.member.mention} the {helper_role.mention} role\n\n**You can add the helper role manually by clicking on their profile picture, slecting +, and choosing Helper**\n\n"
            return
        else:
            response += f"{self.member.mention} has been given the {helper_role.mention} role!\n\n**Please make sure they are notified of their acceptence**\n\n"
        finally:
            response += "You can use the button below to add notes about this application"


        member = self.member

        mod_log_message = await log_helper_application(interaction.guild, member, "accepted")
        assert isinstance(mod_log_message, discord.Message)

        history = interaction.channel.history(limit=None, oldest_first=True)
        message_list = [message async for  message in history]

        conversation_str = ""
        for message in message_list:
            conversation_str += f"{message.author.name}: {message.content}\n"

        helper_application_log_id = db.create_helper_application_log(
            user_discord_id = member.id,
            user_discord_username = member.name,
            conversation = conversation_str,
            result = "accepted",
            notes = "",
            )

        view = AddNotesView(helper_application_log_id, mod_log_message)
        await interaction.followup.send(response, view=view, ephemeral=True)


class DenyButton(discord.ui.Button):
    def __init__(self, member):
        super().__init__(style=discord.ButtonStyle.red, label = 'Deny')
        self.member = member

    async def callback(self, interaction: discord.Interaction):

        await interaction.response.defer(ephemeral=True, thinking=True)

        member = self.member

        assert interaction.guild is not None
        mod_log_message = await log_helper_application(interaction.guild, member, "denied")
        assert isinstance(mod_log_message, discord.Message)

        history = interaction.channel.history(limit=None, oldest_first=True)
        message_list = [message async for  message in history]

        conversation_str = ""
        for message in message_list:
            conversation_str += f"{message.author.name}: {message.content}\n"

        helper_application_log_id = db.create_helper_application_log(
            user_discord_id = member.id,
            user_discord_username = member.name,
            conversation = conversation_str,
            result = "denied",
            notes = "",
        )

        view = AddNotesView(helper_application_log_id, mod_log_message)
        await interaction.followup.send(f"{self.member.mention} has not been given the helper role\n\nUse the button below if you want to add notes about this application", view=view)

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



class AddNotesView(discord.ui.View):
    def __init__(self, helper_log_id: int, mod_log_message: discord.Message):
        super().__init__(timeout=None)
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


async def log_helper_application(guild: discord.Guild, member: discord.Member, result: str):

    mod_log_channel = await guild.fetch_channel(v.MOD_LOG_CHANNEL_ID)
     
    if not mod_log_channel:
        print("NO MOD LOG CHANNEL FOUND")
        return

    title = f"Helper Application Log"
    embed = discord.Embed(title=title, colour=discord.Color.orange())# description=f"Sent by {interaction.user.mention}", 

    embed.add_field(name=f"User", value=member.mention, inline=False)
    embed.add_field(name=f"Result", value=result, inline=False)

    mod_log_message = await mod_log_channel.send(embed=embed)
    return mod_log_message
