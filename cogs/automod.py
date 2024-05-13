import discord
from discord import app_commands
from discord.ext import commands

from database_commands import DatabaseCommands as db
import variables as v

class AutomodCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot



    # @commands.Cog.listener()
    # async def on_automod_action(self, action: discord.AutoModAction):
        # rule = await action.fetch_rule()

        # assert isinstance(action.channel, discord.TextChannel)
        # assert action.member is not None

        # await action.channel.send(f"{action.member.mention} triggered {rule.name} for saying {action.content}")
        # s = f"""
# member: {action.member.mention}
# member_id: {action.member.id}
# member_username: {action.member.name}
# content: {action.content}
# matched_content: {action.matched_content}
# automod_rule_name: {rule.name}
# automod_rule_id: {rule.id}
# channel: {action.channel.mention}
# channel_id: {action.channel_id}
# channel_name: {action.channel.name}
# timeout duration: {action.action.duration}

# {action.message_id}
# """
        # await action.channel.send(s)

        # db.create_automod_log(
        #     user_discord_id = action.member.id,
        #     user_discord_username = action.member.name,
        #     content = action.content,
        #     matched_content = action.matched_content,
        #     automod_rule_name = rule.name,
        #     automod_rule_id = rule.id,
        #     channel_id = action.channel.id,
        #     channel_name = action.channel.name,
        #     timeout_duration = action.action.duration,
        # )

        # await action.channel.send("added to db ig")



async def setup(bot):
    await bot.add_cog(AutomodCog(bot))
