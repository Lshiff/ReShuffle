from discord import app_commands
import csv

GUILD_ID = 1214938317141839903
MOD_LOG_CHANNEL_ID: int = 1216691948497141760
TIMEOUT_CATEGORY_ID = 1219249273229803571
REPORT_CHANNEL_ID = 1215239664756068442


role_users = {
    "tel_aviv": {
        "name": "Tel Aviv",
        "avatar_url": "https://img2.oastatic.com/img2/77048963/420x237r/variant.jpg"
    },
    "good_cop": {
        "name": "Good Cop",
        "avatar_url": "https://static.wikia.nocookie.net/villains/images/e/e0/Good_Cop-removebg-preview.png/revision/latest/scale-to-width-down/350?cb=20220718060946"
    },
    "bad_cop": {
        "name": "Bad Cop",
        "avatar_url": "https://static.wikia.nocookie.net/villains/images/0/03/BadCoprun.png/revision/latest/scale-to-width/360?cb=20131125013146"
    },
    "onboarding_ninja": {
        "name": "Onboarding Ninja 🚀",
        "avatar_url": "https://media.istockphoto.com/id/1403143477/vector/ninja-cartoon-character-with-katana-sword.jpg?s=612x612&w=0&k=20&c=NrS4W93Tn43xxFqwGO4QQHtmimZUxqeiij4d1aIm-II="
        }
}
role_choices = []
for role, info in role_users.items():
    name = info["name"]
    role_choices.append(app_commands.Choice(name=name, value=role))
    

message_dict = {}

with open('help_script.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    category = ''
    category_dict = {}
    topic = ''
    for row in reader:
        # print(row)
        # print(row['category'])
        if row['category'] and row['category'] != category:
            # print("new ", row['category'])
            if category != '':
                # print("adding ", category)
                # print(message_dict)
                message_dict[category] = category_dict
                # print(message_dict)
                # print("m", message_dict)
            category = row['category'].strip()

            emoji = row['category_emoji'].strip()
            category_dict = {"emoji": emoji}


        if row['topic'] and row['topic'] != topic:
            topic = row['topic'].strip()
            emoji = row['topic_emoji'].strip()
            category_dict[topic] = {"emoji": emoji, "messages": []}
            # category_dict.update(topic: {})
            # message_dict[category][topic] = topic
            # message_dict[category].update({topic: {"emoji": "", "messages": []}})

        category_dict[topic]['messages'].append(row['message'].strip())

    message_dict[category] = category_dict #adds last category
        # print(category_dict)

print(message_dict) 
for c in message_dict.items():
    print(c)
