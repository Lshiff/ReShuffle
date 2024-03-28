import discord
from discord import app_commands
from discord.ext import commands

from database_commands import DatabaseCommands as db
import variables as v


#TODO Log Commands

class RehelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(name="rehelp", description="Choose help message to send")
    async def remod(self, interaction: discord.Interaction):
        view = HelpCategoryDropdownView()
        await interaction.response.send_message("Pick the category", view = view, ephemeral=True)



async def setup(bot):
    await bot.add_cog(RehelpCog(bot))




class HelpCategoryDropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(HelpCategoryDropdown())

class HelpCategoryDropdown(discord.ui.Select):
    def __init__(self):

        # Set the options that will be presented inside the dropdown
        options = []
        for category in v.message_dict:
            emoji = v.message_dict[category].get("emoji") or None
            options.append(discord.SelectOption(label=category, emoji=emoji))


        super().__init__(placeholder='Choose the category...', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):

        category = self.values[0]
        options = []
        for topic in v.message_dict[category]:
            if topic == "emoji":
                continue
            emoji = v.message_dict[category][topic].get("emoji") or None
            options.append(discord.SelectOption(label=topic, emoji=emoji))


        view = HelpTopicDropdownView(options, category)

        await interaction.response.send_message("Pick the topic", view = view, ephemeral=True)

class HelpTopicDropdownView(discord.ui.View):
    def __init__(self, options, category):
        super().__init__()
        self.category = category

        # Adds the dropdown to our view object.
        self.add_item(HelpTopicDropdown(options, category))

class HelpTopicDropdown(discord.ui.Select):
    def __init__(self, options, category):
        super().__init__(placeholder='Choose the topic...', min_values=1, max_values=1, options=options)
        self.category = category

    async def callback(self, interaction: discord.Interaction):

        topic = self.values[0]
        messages = v.message_dict[self.category][topic]["messages"]

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
