# import discord
# from discord import app_commands
# from discord.ext import commands

# import variables as v

# class QuestCog(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot

#     # @app_commands.command(name="test")
#     # async def test(self, interaction: discord.Interaction):
#     #     await interaction.response.send_message("test")
         
#     @commands.command()
#     async def hello(self, ctx):
#         await ctx.send("hiiiiiii")

#     @bot.tree.command(name="quest_role", description="Give user a role based on their current quest", guild=discord.Object(id=GUILD_ID))
#     @app_commands.describe(member = "The member to give the roll to")
#     async def quest_role(interaction: discord.Interaction, member: discord.Member):

#         await interaction.response.defer(thinking=True, ephemeral=True)

#         result = await update_quest_role(member)

#         await interaction.followup.send(result)



#     async def update_quest_role(member: discord.Member):

#         result = db.get_current_quest_from_discord(member.name)

#         quest_names = ["Acting1", "Cooking1", "Cooking2", "Eco-Consulting1", "Fashion1", "Interior-Design1", "Marketing1", "Medicine1", "Music1", "Sports1", "Sports2"]

#         if result not in quest_names:
#             return result
#         role_name = result
        
#         quest_roles = [role for role in member.guild.roles if role.name in quest_names]
        
#         previous_role = None
#         quest_role = None
#         for role in quest_roles:
#             if role in member.roles:
#                 await member.remove_roles(role)
#                 previous_role = role
#             if role.name == role_name:
#                 await member.add_roles(role)
#                 quest_role = role

#         return f"{member.mention} has been given the role {quest_role.mention}{f' replacing {previous_role.mention}' if previous_role else ''}"





# async def setup(bot):
#     await bot.add_cog(TestCog(bot))



# import discord
# from discord import HTTPException, app_commands
# from discord.ext import commands

# from dotenv import load_dotenv
# import os

# import math
# import time

# from datetime import datetime

# from database_commands import DatabaseCommands as db

# @bot.event
# async def on_member_join(member):

#     result = await update_quest_role(member)
    
#     mod_log_channel = discord.utils.get(member.guild.text_channels, id=MOD_LOG_CHANNEL_ID)
#     if not mod_log_channel:
#         print("NO MOD LOG CHANNEL FOUND")
#         return
#     print(f"sending result to mod channel: {result}")
#     await mod_log_channel.send(result)

