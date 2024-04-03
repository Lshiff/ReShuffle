import json
import requests

headers = {
    "Authorization": "Bearer REFVPUkKoKgXg6xXG6bq3gybsi9Rezsw",
        }
# response = requests.get('https://api.sheety.co/3404605601848dcc35723dc42f596638/reShuffleCsScript (2024)/masterList', headers=headers)
response = requests.get('https://api.sheety.co/3404605601848dcc35723dc42f596638/csChiefManualApril2024/onboardingNinja', headers=headers)
# print(response.text)

# response = {
#   "onboardingNinja": [
#     {
#       "categoryEmoji": "🚀",
#       "category": "Onboarding",
#       "subCategory (internal)": "Registration",
#       "problemEmoji": "",
#       "problem/question": "Student asks how to register",
#       "chiefMessage": "Thanks for reaching out! Head to @reshuffle.education on Instagram, DM 'Hi!' and follow the instructions. Enjoy and good luck!",
#       "id": 2
#     },
#     {
#       "categoryEmoji": "",
#       "category": "",
#       "subCategory (internal)": "",
#       "problemEmoji": "",
#       "problem/question": "Student gets stuck in the registration ",
#       "chiefMessage": "Something's wrong. Make sure your right class code is correct.",
#       "id": 3
#     },
#     {
#       "categoryEmoji": "",
#       "category": "",
#       "subCategory (internal)": "",
#       "problemEmoji": "",
#       "problem/question": "Student asks why they haven’t accepted their follow request yet. ",
#       "chiefMessage": "Sorry to keep you waiting... The verification process might take some time. We'll approve it as soon as possible so you can enter your quest and start ReShuffling!",
#       "id": 4
#     },
#     {
#       "categoryEmoji": "",
#       "category": "",
#       "subCategory (internal)": "Choosing a quest",
#       "problemEmoji": "",
#       "problem/question": "Student requests to change a quest.",
#       "chiefMessage": "Want to switch quests? Click the three dots in your portfolio and select 'change a quest'. Follow your intuition and choose right to maximise the value from your quest. Check our Discord FAQ for more info. Good luck!",
#       "id": 5
#     },
#     {
#       "categoryEmoji": "",
#       "category": "",
#       "subCategory (internal)": "",
#       "problemEmoji": "",
#       "problem/question": "Student needs help choosing a topic",
#       "chiefMessage": "My best advise is ",
#       "id": 6
#     },
#     {
#       "categoryEmoji": "",
#       "category": "",
#       "subCategory (internal)": "",
#       "problemEmoji": "",
#       "problem/question": "Student asks - what am I supposed to do?",
#       "chiefMessage": "[PLACEHOLDER]",
#       "id": 7
#     },
#     {
#       "categoryEmoji": "",
#       "category": "",
#       "subCategory (internal)": "Submiotting tasks in the wrong Discord Channel",
#       "problemEmoji": "",
#       "problem/question": "[PLACEHOLDER] 1",
#       "chiefMessage": "Oops, it seems you've shared your task in the wrong quest channel...",
#       "id": 8
#     },
#     {
#       "categoryEmoji": "",
#       "category": "Questions (Inbound)",
#       "subCategory (internal)": "Personal concern",
#       "problemEmoji": "",
#       "problem/question": "Student feel uncomfortable submitting in the Discord group. ",
#       "chiefMessage": "I get it, sharing tasks can be tough. But it's key to our process and helps you grow and get feedback. Our group chats are supportive and non-judgmental! Plus, bonus points for sharing on Discord 👍",
#       "id": 9
#     },
#     {
#       "categoryEmoji": "",
#       "category": "",
#       "subCategory (internal)": "",
#       "problemEmoji": "",
#       "problem/question": "Student still don't want to submit on Discord.",
#       "chiefMessage": "If you're uneasy, I get it and it's not a must. But for your growth, give submitting in Discord a shot and see how it feels ❤️",
#       "id": 10
#     },
#     {
#       "categoryEmoji": "",
#       "category": "",
#       "subCategory (internal)": "Earning points",
#       "problemEmoji": "",
#       "problem/question": "If I submitted late, do I lose points?",
#       "chiefMessage": "Hey, late submissions might deduct points (up to your teacher), but you can still score by helping others! Share your work for a +5 bonus 🚀 and comment on 5 mates' work for another +5 🙌. Check the Discord FAQ to learn more!",
#       "id": 11
#     },
#     {
#       "categoryEmoji": "",
#       "category": "",
#       "subCategory (internal)": "",
#       "problemEmoji": "",
#       "problem/question": "",
#       "chiefMessage": "Welcome to your first ReShuffle quest! Start by checking out the highlights on your Instagram quest page 🧐 each one represents a phase in your project. Dive into the stories, follow the links, understand your tasks, and get them done. Once completed, submit in your quest channel on Discord and update your Portfolio 🎯 Keep this up for all 7 project steps. You can find more details in the FAQ channel. Feel free to reach out if you have any questions!",
#       "id": 12
#     },
#     {
#       "categoryEmoji": "",
#       "category": "",
#       "subCategory (internal)": "Viewing tasks",
#       "problemEmoji": "",
#       "problem/question": "Students ask where the tasks appear",
#       "chiefMessage": "The tasks appear at the end of each Instagram highlight, with the title 'Task' at the top.",
#       "id": 13
#     },
#     {
#       "categoryEmoji": "",
#       "category": "Suggestions (Outbound)",
#       "subCategory (internal)": "Discord Issues",
#       "problemEmoji": "",
#       "problem/question": "[PLACEHOLDER] 1",
#       "chiefMessage": "PROACTIVE: Hey everybody, to everyone who's already submitted a task and shared it with the group, great job! Well done for jumping in headfirst and leading the way. 🏊\nTo those who haven't yet, be inspired by your fellow ReShufflers and share your tasks!\nThe Helpers and us are here to answer any questions you might have (:",
#       "id": 15
#     },
#     {
#       "categoryEmoji": "",
#       "category": "",
#       "subCategory (internal)": "",
#       "problemEmoji": "",
#       "problem/question": "",
#       "chiefMessage": "PROACTIVE: Hey everyone! Just reminding you guys to share your tasks here on the Discord channel. Really looking forward to seeing your ___ task!\nFeel free to contact us with any questions.",
#       "id": 16
#     },
#     {
#       "categoryEmoji": "",
#       "category": "",
#       "subCategory (internal)": "",
#       "problemEmoji": "",
#       "problem/question": "[PLACEHOLDER] 2",
#       "chiefMessage": "Student submitted a task the wrong Discord group ",
#       "id": 17
#     },
#     {
#       "categoryEmoji": "",
#       "category": "",
#       "subCategory (internal)": "Reminder to submit tasks ",
#       "problemEmoji": "",
#       "problem/question": "[PLACEHOLDER] 3",
#       "chiefMessage": "PROACTIVE: Hey everyone, kudos to those who submitted tasks #1 and #2 and shared them! 🏆 \nFor those who haven't yet, it's not too late. ⏰ \nWe’re waiting to see tasks 3# and 4# this week.\nFeel free to ask us anything (:",
#       "id": 18
#     },
#     {
#       "categoryEmoji": "",
#       "category": "",
#       "subCategory (internal)": "",
#       "problemEmoji": "",
#       "problem/question": "",
#       "chiefMessage": "PROACTIVE: Hey everyone! Just reminding you guys to share your tasks here on the Discord channel. Really looking forward to seeing your first tasks! 🥇 \nFeel free to contact us with any questions.",
#       "id": 19
#     },
#     {
#       "categoryEmoji": "",
#       "category": "",
#       "subCategory (internal)": "Students get stuck in the registration process and do not respond",
#       "problemEmoji": "",
#       "problem/question": "[PLACEHOLDER] 4",
#       "chiefMessage": "PROACTIVE: Hey everyone, ReShuffle's team would like to remind you that they're there for you if you have any questions about the quests or the registration. \nTo register, go to @reshuffle.education on Instagram, enter the page’s DM (direct messaging) type joinreshuffle, and answer the questions from there.\nTo better understand the process, you’re welcome to watch this short video: {insert video link here}\nGood luck and have fun! ",
#       "id": 20
#     },
#     {
#       "categoryEmoji": "",
#       "category": "",
#       "subCategory (internal)": "Encourage students to contact a helper",
#       "problemEmoji": "",
#       "problem/question": "[PLACEHOLDER] 5",
#       "chiefMessage": "PROACTIVE: Hey everyone! Just a reminder that if you need help with a task, you can go to the #help-channel, or contact a Helper. Good luck and have fun!",
#       "id": 21
#     },
#     {
#       "categoryEmoji": "",
#       "category": "",
#       "subCategory (internal)": "When a student becomes a helper",
#       "problemEmoji": "",
#       "problem/question": "[PLACEHOLDER] 6",
#       "chiefMessage": "PROACTIVE: @(user name) just took on the *helper* role and can help you if you need it.\nFeel free to reach out to our helpers, or to ReShuffle team.\nGood luck and happy questing 🤩",
#       "id": 22
#     }
#   ]
# }



onboarding_ninja = response.json()["onboardingNinja"]


message_dict = {}

category = ''
category_dict = {}
subcategory = ''
topic = ''
question = ''
for row_dict in onboarding_ninja:
    print(row_dict)
    # print(row['category'])
    if row_dict['category'] and row_dict['category'] != category:
        # print("new ", row['category'])
        if category != '':
            # print("adding ", category)
            # print(message_dict)
            message_dict[category] = category_dict
            # print(message_dict)
            # print("m", message_dict)
        category = row_dict['category'].strip()

        emoji = row_dict['categoryEmoji'].strip()
        category_dict = {"emoji": emoji}

    # if row_dict['subCategory (internal)'] and row_dict['subCategory (internal)'] != subcategory
    #     subcategory = row_dict['subCategory (internal)'].strip()
    #     category_dict[topic] = {"emoji": emoji, "messages": []}
    #     # category_dict.update(topic: {})
    #     # message_dict[category][topic] = topic
    #     # message_dict[category].update({topic: {"emoji": "", "messages": []}})

    if row_dict['problem/question'] and row_dict['problem/question'] != question:
        subcategory = row_dict['subCategory (internal)'].strip()
        question = row_dict['problem/question'].strip()
        emoji = row_dict['problemEmoji'].strip()
        category_dict[question] = {"emoji": emoji, "subcategory": subcategory, "messages": []}
        # category_dict.update(topic: {})
        # message_dict[category][topic] = topic
        # message_dict[category].update({topic: {"emoji": "", "messages": []}})

    category_dict[question]['messages'].append(row_dict['chiefMessage'].strip())

message_dict[category] = category_dict #adds last category

print(message_dict)


json = json.dumps(message_dict)
with open('cs_master.json', 'w') as file:
    file.write(json)





