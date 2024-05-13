import discord
from discord import app_commands
from discord.ext import commands

from database_commands import DatabaseCommands as db
import variables as v

class AutomodCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot



    @commands.Cog.listener()
    async def on_automod_action(self, action: discord.AutoModAction):
        rule = await action.fetch_rule()

        assert isinstance(action.channel, discord.TextChannel)
        assert action.member is not None

        if db.is_duplicate_automod_log(action.member.id, action.channel.id, action.content):
            print("duplicate")
            return

        print("Adding to db")
        db.create_automod_log(
            user_discord_id = action.member.id,
            user_discord_username = action.member.name,
            content = action.content,
            matched_content = action.matched_content,
            automod_rule_name = rule.name,
            automod_rule_id = rule.id,
            channel_id = action.channel.id,
            channel_name = action.channel.name,
            timeout_duration = action.action.duration,
        )


        # automod_log_channel = discord.utils.get(action.guild.text_channels, id=v.AUTOMOD_LOG_ID)
        # if not automod_log_channel:
        #     print("NO AUTOMOD LOG CHANNEL FOUND")
        #     return
        # await automod_log_channel.send(f"DB: {action.member.mention} said `{action.content}`")




async def setup(bot):
    await bot.add_cog(AutomodCog(bot))
