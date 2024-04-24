import discord
from discord import app_commands
from discord.ext import commands

import requests
import json
import variables as v

class UpdateCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="update_from_cs_master", description="Updates Support and Moderation commands from the CS Master spreadsheet")
    async def update_from_spreadsheet(self, interaction: discord.Interaction):

        await interaction.response.defer(thinking=True, ephemeral=True)

        try:
            #MODERATION
            headers = {
                "Authorization": "Bearer REFVPUkKoKgXg6xXG6bq3gybsi9Rezsw",
                    }
            response = requests.get('https://api.sheety.co/3404605601848dcc35723dc42f596638/csChiefManualApril2024/moderation', headers=headers)
            print(response.text)
            # return

            moderation = response.json()["moderation"]

            message_dict_moderation = create_message_dict_moderation(moderation)
            print(message_dict_moderation)

            json_file = json.dumps(message_dict_moderation)
            with open('customer_support_messages/moderation.json', 'w') as file:
                file.write(json_file)

            #SUPPORT
            headers = {
                "Authorization": "Bearer REFVPUkKoKgXg6xXG6bq3gybsi9Rezsw",
                    }
            response = requests.get('https://api.sheety.co/3404605601848dcc35723dc42f596638/csChiefManualApril2024/support', headers=headers)
            print(response.text)

            support = response.json()["support"]

            message_dict_support = create_message_dict_support(support)

            json_file = json.dumps(message_dict_support)
            with open('customer_support_messages/support.json', 'w') as file:
                file.write(json_file)

            #COMMUNITY
            headers = {
                "Authorization": "Bearer REFVPUkKoKgXg6xXG6bq3gybsi9Rezsw",
                    }
            response = requests.get('https://api.sheety.co/3404605601848dcc35723dc42f596638/csChiefManualApril2024/community', headers=headers)
            print(response.text)

            community = response.json()["community"]

            #shoudlw ork for support and community
            message_dict_support = create_message_dict_support(community)

            json_file = json.dumps(message_dict_support)
            with open('customer_support_messages/community.json', 'w') as file:
                file.write(json_file)

            headers = {
                "Authorization": "Bearer REFVPUkKoKgXg6xXG6bq3gybsi9Rezsw",
                }
            response = requests.get('https://api.sheety.co/3404605601848dcc35723dc42f596638/csChiefManualApril2024/privateChannelModeration', headers=headers)
            print(response.text)

            private_channel_moderation = response.json()["privateChannelModeration"]

            message_list = []
            for row in private_channel_moderation:
                if row.get("messagesForPrivateChannel (afterSuspention)"):
                    message_list.append(row["messagesForPrivateChannel (afterSuspention)"])
                
            print(message_list)

            message_list_dict = {
                "message_list": message_list
            }
            json_file = json.dumps(message_list_dict)
            with open('customer_support_messages/private_moderation.json', 'w') as file:
                file.write(json_file)


            await interaction.followup.send("Updated!", ephemeral=True)

        except Exception as e:
            print(f"Error occured when updating: \n{e}")
            await interaction.followup.send(f"Something went wrong! Error:\n{e}", ephemeral=True)


def create_message_dict_moderation(moderation_json) -> dict:

    message_dict = {}

    infraction = ''
    infraction_dict = {}
    for row_dict in moderation_json:
        print(row_dict)
        if row_dict['infraction'] and row_dict['infraction'] != infraction:
            if infraction != '':
                message_dict[infraction] = infraction_dict
            infraction = row_dict['infraction'].strip()

            if row_dict['infraction'] == "END":
                return message_dict

            emoji = row_dict['emoji'].strip()
            infraction_dict = {"emoji": emoji, "messages":[]}

        infraction_dict['messages'].append(row_dict['chiefMessage'].strip())

    message_dict[infraction] = infraction_dict #adds last category
    return message_dict

def create_message_dict_support(support_json) -> dict:
    message_dict = {}

    category = ''
    category_dict = {}
    question = ''
    subcategory = ''
    for row_dict in support_json:
        print(row_dict)
        if row_dict['category'] and row_dict['category'] != category:
            if category != '':
                message_dict[category] = category_dict
            category = row_dict['category'].strip()

            emoji = row_dict['categoryEmoji'].strip()
            category_dict = {"emoji": emoji}

        if row_dict['subCategory (internal)'] and row_dict['subCategory (internal)'] != subcategory:
            subcategory = row_dict['subCategory (internal)'].strip()

        if row_dict['problem/question'] and row_dict['problem/question'] != question:
            subcategory = subcategory
            question = row_dict['problem/question'].strip()
            emoji = row_dict['problemEmoji'].strip()
            category_dict[question] = {"emoji": emoji, "subcategory": subcategory, "messages": []}

        category_dict[question]['messages'].append(row_dict['chiefMessage'].strip())

    message_dict[category] = category_dict

    return message_dict


async def setup(bot):
    await bot.add_cog(UpdateCog(bot))
