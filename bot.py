from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters, ChatMemberHandler
import requests
import json
import random
import asyncio
import csv
import logging

# Update Credentials here
TOKEN = ""  # Replace with your bot's token from BotFather
owner = 5631537532 # Replace with your Telegram user ID
botusername = "CRUNCHYROLL_NEWSBOT" # Replace with your bot's username without @

pinnedmsges = []

async def error_handler(update : Update, context : ContextTypes.DEFAULT_TYPE):
    logging.error(f"Error occurred: {context.error}\n\n")

async def start(update : Update, context : ContextTypes.DEFAULT_TYPE):
    chattype = update.message.chat.type

    if chattype != "private":
        return

    startbutton = [
        [InlineKeyboardButton("</ 𝙳𝚎𝚟𝚎𝚕𝚘𝚙𝚎𝚛 >",url="https://t.me/amitispro")],
        [InlineKeyboardButton("🌐 Mᴀɪɴ Cʜᴀɴɴᴇʟ",url="https://t.me/+uRexADKq_rljYjVl"), InlineKeyboardButton("💬 Cʜᴀᴛ",url="https://t.me/+p8ZIdF9xfoBhYTk9")],
        [InlineKeyboardButton("➕ Aᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴘ",url=f"https://t.me/{botusername}?startgroup=true")]
    ]

    await update.message.reply_photo(
        photo = "https://a.storyblok.com/f/178900/1920x1080/3143fbd5c7/ntxcr.jpg",
        caption = '''🤖 <b>This bot brings you the latest articles and updates from the official website of Crunchyroll by Scraping the website : https://www.crunchyroll.com/news/latest</b>


🤔 <b>What do the bot does ?</b>

<blockquote><b>This bot sends the latest anime articles from Crunchyroll official website directly to your group.

🥐 Add the bot as a <b>administrator</b> to your group Now! to start sending the latest anime articles.</b></blockquote>
''',
        parse_mode = "HTML",
        reply_markup = InlineKeyboardMarkup(startbutton)
    )

def getnews():
    randompage = random.randint(1,5)

    headlinesurl = f"https://cr-news-api-service.prd.crunchyrollsvc.com/v1/en-US/stories/search?category=Announcements,News,News&page_size=16&page={randompage}"

    try:
        articledata = {}
        response1 = requests.get(headlinesurl, timeout=10)
        heads = response1.json()

        randomstory = heads["stories"][random.randint(0,len(heads["stories"]))]

        try:
            articleurl = f"https://cr-news-api-service.prd.crunchyrollsvc.com/v1/en-US/stories?slug={randomstory['slug'].replace('/','%2F')}"

            response2 = requests.get(articleurl, timeout=10)
            data = response2.json() 
    
            articledata["image"] = data["story"]["content"]["thumbnail"]["filename"]
            articledata["tags"] = data["story"]["tag_list"]
            articledata["title"] = data["story"]["content"]["seo"]["title"]
            articledata["description"] = data["story"]["content"]["seo"]["description"]
            articledata["lead"] = data["story"]["content"]["lead"].strip('"')
            articledata["posted"] = data["story"]["content"]["article_date"]
            articledata["article-url"] = f"https://www.crunchyroll.com/news/{data['story']['slug']}"
            articledata["api-url"] = articleurl

            return articledata
        except Exception as Error:
            return Error
    except Exception as Error:
        return Error

async def send_news(context, text, imageurl, articleurl):
    global pinnedmsges

    if len(pinnedmsges) > 0:
        for msg in pinnedmsges:
            try:
                bot = context.bot
    
                await bot.unpin_chat_message(
                    chat_id = msg["chat"],
                    message_id= msg["id"]
                )
            except Exception as error:
                print(f"Can't unpin the msg id : {msg["id"]}")
        pinnedmsges = []

    with open("chats.csv","r",newline="") as fil:
        reader = csv.reader(fil)
        next(reader)

        button = [
            [InlineKeyboardButton("📖 𝙍𝙚𝙖𝙙 𝙈𝙤𝙧𝙚",url= articleurl)]
        ]

        for chatid in reader:
            bot = context.bot

            try:
                sentnews = await bot.send_photo(
                    chat_id = int(chatid[0]),
                    photo= imageurl,
                    caption = text,
                    parse_mode = "HTML",
                    reply_markup = InlineKeyboardMarkup(button)
                )
    
                await bot.pin_chat_message(
                    chat_id = int(chatid[0]),
                    message_id= sentnews.id
                )

                msglocation = {
                    "chat" : chatid,
                    "id" : sentnews.id
                }
                pinnedmsges.append(msglocation)
            except Exception as error:
                print(f"Can't send the news to chat : {chatid[0]}\nError : {error}")

async def create_news(context: ContextTypes.DEFAULT_TYPE):
    global lastmsgid
    global owner
    bot = context.bot

    try:
        news = getnews()
        tags = "\n".join([f"<a href='https://t.me/+uRexADKq_rljYjVl'>❖</a> <b>{tag}</b>" for tag in news["tags"]])

        text = f'''⚡ <b>{news["title"]}</b>

📅 <code>{news["posted"]}</code>
<blockquote><b>{news["description"]}</b></blockquote>

🍿 <b><i>{news["lead"]}</i></b>

🏷️ <b>Tags</b>
{tags}
'''
        asyncio.create_task(send_news(context,text,news["image"],news["article-url"]))
    except Exception as error:
        await bot.send_message(
            chat_id= owner,
            text = f"🚩 <b>Error Occured sending News :</b> \n\n<code>{getnews()}</code>\n\n<blockquote>Error: {error}</blockquote>",
            parse_mode= "HTML"
        )

async def chat_member_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    member = update.my_chat_member
    user_id = update.effective_user.id

    if member:
        if member.new_chat_member.user.id == context.bot.id and member.new_chat_member.status == 'administrator':

            with open("chats.csv","a",newline="") as fil:
                writer = csv.writer(fil)
                writer.writerow([member.chat.id ,member.chat.title])

            await context.bot.send_message(
                chat_id= member.chat.id,
                text = f"✅ <b>Successfully registered this group to receive Crunchyroll News !</b>\n\n<blockquote><i><b>You will receive the latest articles in every 30 minutes.</b></i></blockquote>",
                parse_mode= "HTML"
            )

        elif member.new_chat_member.user.id == context.bot.id and member.new_chat_member.status in ['left','kicked','banned']:
            chats = []
            with open("chats.csv","r",newline="") as fil:
                reader = csv.reader(fil)
                next(reader)

                for chat in reader:
                    if str(member.chat.id) != chat[0]:
                        chats.append(chat)

            with open("chats.csv","w",newline="") as fil:
                writer = csv.writer(fil)
                writer.writerow(["chat","title"])
                writer.writerows(chats)
            try:
                await context.bot.send_message(
                    chat_id= user_id,
                    text = f"❌ <b>The bot was removed from the group {member.chat.title} [{member.chat.id}] and unregistered from receiving news.</b>\n\n<blockquote><i>If you want to re-register the group, add the bot again and promote as admin. Hoping to see you soon 🌹!</i></blockquote>",
                    parse_mode= "HTML"
                )
                
            except Exception as error:
                print(f"Can't send the message to the user. Error: {error}")

        else:
            try:
                await context.bot.send_message(
                    chat_id = member.chat.id,
                    text = "🥰 <b>Thanks for adding the bot to the group. Please promote the bot as an administrator to start receiving the news.</b>",
                    parse_mode = "HTML"
                )

            except Exception as error:
                print(f"Can't send the message to the group. Error: {error}")

                try:
                    await context.bot.send_message(
                        chat_id = user_id,
                        text = f"🥰 <b>Thanks for adding the bot to the group {member.chat.title}. Please promote the bot as an administrator to start receiving the news.</b>",
                        parse_mode = "HTML"
                    )
                except Exception as error:
                    print(f"Can't send the message to the user. Error: {error}")

if __name__ == "__main__":
    application = Application.builder().token(TOKEN).build()

    application.add_error_handler(error_handler)
    application.job_queue.run_repeating(callback = create_news, interval = 1800, first = 10)
    application.add_handler(CommandHandler("start",start))
    application.add_handler(ChatMemberHandler(chat_member_update, chat_member_types= ["my_chat_member"]))

    print("Bot is running")
    application.run_polling()