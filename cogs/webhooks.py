import discord
from discord import app_commands
from discord.ext import commands

import variables as v

class WebhooksCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_create_webhook(self, channel):
        webhooks = await channel.webhooks()
        for webhook in webhooks:
            if webhook.user == self.bot.user:
                return webhook

        return await channel.create_webhook(name="ReShuffle Bot Webhook")

    @app_commands.command(name="say_webhook", description="Sends a message as a character")
    @app_commands.describe(message="The message to send")
    @app_commands.choices(roles=v.role_choices)
    async def say_webhook(self, interaction: discord.Interaction, roles: app_commands.Choice[str], message:str):
        webhook = await self.get_create_webhook(interaction.channel)
        
        await webhook.send(message, username=v.role_users[roles.value]["name"], avatar_url=v.role_users[roles.value]["avatar_url"])
        await interaction.response.send_message("Message sent", ephemeral=True, delete_after=3)

    @app_commands.command(name="say_user", description="Sends a message as a server member")
    @app_commands.describe(member="The member to send the message as", message="The message to send")
    async def say_user(self, interaction: discord.Interaction, member: discord.Member, message:str):
        webhook = await self.get_create_webhook(interaction.channel)
       
        name = member.nick or member.name
        if member.avatar:
            avatar_url = member.avatar.url
        else:
            avatar_url = None
        await webhook.send(message, username=name, avatar_url=avatar_url)
        await interaction.response.send_message("Message sent", ephemeral=True, delete_after=3)



async def setup(bot):
    await bot.add_cog(WebhooksCog(bot))
