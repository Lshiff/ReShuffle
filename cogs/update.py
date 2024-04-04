import discord
from discord import app_commands
from discord.ext import commands

import requests
import json
import variables as v

class UpdateCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="update_from_spreadsheet", description="Updates Support and Moderation commands from the spreadsheet")
    async def update_from_spreadsheet(self, interaction: discord.Interaction):

        #MODERATION
        headers = {
            "Authorization": "Bearer REFVPUkKoKgXg6xXG6bq3gybsi9Rezsw",
                }
        response = requests.get('https://api.sheety.co/3404605601848dcc35723dc42f596638/csChiefManualApril2024/moderation', headers=headers)
        print(response.text)

        moderation = response.json()["moderation"]

        message_dict = {}

        infraction = ''
        infraction_dict = {}
        for row_dict in moderation:
            print(row_dict)
            if row_dict['infraction'] and row_dict['infraction'] != infraction:
                if infraction != '':
                    message_dict[infraction] = infraction_dict
                infraction = row_dict['infraction'].strip()

                emoji = row_dict['emoji'].strip()
                infraction_dict = {"emoji": emoji, "messages":[]}

            infraction_dict['messages'].append(row_dict['chiefMessage'].strip())

        message_dict[infraction] = infraction_dict #adds last category

        print(message_dict)

        json_file = json.dumps(message_dict)
        with open('moderation.json', 'w') as file:
            file.write(json_file)

        #SUPPORT
        headers = {
            "Authorization": "Bearer REFVPUkKoKgXg6xXG6bq3gybsi9Rezsw",
                }
        response = requests.get('https://api.sheety.co/3404605601848dcc35723dc42f596638/csChiefManualApril2024/support', headers=headers)
        print(response.text)

        support = response.json()["support"]


        message_dict = {}

        category = ''
        category_dict = {}
        question = ''
        for row_dict in support:
            print(row_dict)
            if row_dict['category'] and row_dict['category'] != category:
                if category != '':
                    message_dict[category] = category_dict
                category = row_dict['category'].strip()

                emoji = row_dict['categoryEmoji'].strip()
                category_dict = {"emoji": emoji}

            if row_dict['problem/question'] and row_dict['problem/question'] != question:
                subcategory = row_dict['subCategory (internal)'].strip()
                question = row_dict['problem/question'].strip()
                emoji = row_dict['problemEmoji'].strip()
                category_dict[question] = {"emoji": emoji, "subcategory": subcategory, "messages": []}

            category_dict[question]['messages'].append(row_dict['chiefMessage'].strip())

        message_dict[category] = category_dict

        json_file = json.dumps(message_dict)
        with open('support.json', 'w') as file:
            file.write(json_file)

        await interaction.response.send_message("Updated!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(UpdateCog(bot))
