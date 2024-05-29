import discord
from discord import app_commands
from discord.ext import commands

from database_commands import DatabaseCommands as db
from utils import discord_timestamp
import variables as v

class NotesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="note", description="Add a note to a user")
    @app_commands.describe(member = "The member to add the note to", note = "The note to add to the member")
    async def note(self, interaction: discord.Interaction, member: discord.Member, note: str):

        # db.create_user_moderation_log(
        db.add_note(
            user_discord_id = member.id,
            user_discord_username = member.name,
            punishment = "",
            note = note,
            sender_discord_id = interaction.user.id,
            sender_discord_username = interaction.user.name,
        )

        await interaction.response.send_message("Note saved", ephemeral=True)
         

    @app_commands.command(name="get_notes", description="Get all notes for a user")
    @app_commands.describe(member = "The member to get the notes from")
    async def get_notes(self, interaction: discord.Interaction, member: discord.Member):

        # notes = db.get_user_moderation_logs_by_discord_id(member.id)
        notes = db.get_notes_by_discord_id(member.id)

        embed = discord.Embed(title=f"Notes for {member.nick if member.nick else member.name}", description=f"{member.mention} has {len(notes)} notes", colour=discord.Colour.red())
        embed = discord.Embed(title=f"Notes for {member.nick if member.nick else member.name} ({len(notes)})", description=member.mention, colour=discord.Colour.pink())
        embed = discord.Embed(description=member.mention, colour=discord.Colour.pink())
        # embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
        # embed.set_image(url=member.avatar.url if member.avatar else None)
        embed.set_author(name=member.name, icon_url = member.avatar.url if member.avatar else None)
        embed.set_author(name=f"Notes for {member.nick if member.nick else member.name} ({len(notes)})", icon_url = member.avatar.url if member.avatar else None)
        for note in notes:
            disc_time = discord_timestamp(note.timestamp)
            sender = interaction.guild.get_member(note.sender_discord_id)
            embed.add_field(name = f"Added by {sender.nick or sender.name}", value = f"{note.note} – {disc_time}", inline=False)

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(NotesCog(bot))
