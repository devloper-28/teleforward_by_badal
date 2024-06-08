#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) @AlbertEinsteinTG

import os
import asyncio
import time
import sys
import psutil

from pyrogram import Client, filters, enums
from pyrogram.types import Message

from bot import LOGGER, Config
from bot.database.database import Database
from bot.helpers.utils import humanbytes, convert_size

from datetime import datetime, timedelta


logger = LOGGER(__name__)
db = Database()


@Client.on_message(filters.command(["start"]))
async def start (bot, update):
    
    await update.reply_text("""
🚀 Let's get started!

To begin receiving messages from a channel or group, simply send me its link (ensure it's a public channel). This way, you can conveniently read all your channels within the bot in one feed.

If you wish to start copying new messages or copying history from a channel, group, or bot to your own channel, group, or any private chat, use the corresponding button.

Steps to follow:

1) Congratulations..✅ You got tire 1 access for free.
2) Type /id & Join this group: [https://t.me/+UYpaPybMaaxjNTY1] if you need paid membership.
3) Paste your ID along with your name (e.g., Yourname: Yourid(12345)) if need to upgrade tire2 and tire3.
4) Once you gain free or paid access, simply paste the link in the following format:
/addsource http://t.me/sadf626/555.
5) Once you get successfully subscribed to this channel message, you won't need to do anything further. Just wait, and all new public upcoming content will automatically load in the bot.
6) Note :- Tire 1 members can able to add just one channel, Paid members can able to add more then one channel. 
""")


    
    user_id = update.from_user.id
    print("handle_user_trial: {}".format(user_id))
    # Check if the user's trial information exists
    trial_exists = await db.user_trial_exists(user_id)
    user_info = await db.get_user_info(user_id=user_id)

    if not trial_exists and not user_info:
        # Save user's trial information if not already exists
        trial_id = await db.save_user_trial(user_id)
        print(f"Trial information saved with ID: {trial_id}")
        await db.remove_user(user_id)
        await db.add_user(user_id, f"Tire-1")
        await db.load_tire_users()

        await asyncio.sleep(2)

        try:
            await bot.send_message(
                user_id,
                f"You can now enjoy the benefits of Tire-1 trial...!\n\nYou just need to paste the channel link now with starting of /addsource and then LINK, for e.g. ('http://t.me/roughhardsex/12681').\n\nMake sure to add last chat id so it will give you all upcoming content.\n\nIf you are using the free tier, it will expire in {Config.TRIAL_DURATION_TEXT}, and only 1 channel is allowed in your subscription.\n\nUpgrade to a higher tier to enjoy more benefits:\n\nTire 2:\nAccess to 3 channels for 15 days\nPrice: ₹250\n\nTire 3:\nAccess to 10 channels for 30 days\nPrice: ₹500\n\nChoose your preferred plan and pay to continue messaging."
            )
        except:
            pass
    else:
        trial_info = await db.get_user_trial(user_id)
        if trial_info:
            start_date = trial_info.get("start_date")
            if start_date:
                expiry_date = start_date + timedelta(seconds=Config.TRIAL_DURATION)
                if datetime.utcnow() > expiry_date:
                    user_info = await db.get_user_info(user_id)
                    if user_info:
                        await db.remove_user(user_id)
                        await db.load_tire_users()

                        try:
                            await bot.send_message(
                                    user_id,
                            
                                            f"You were removed from Trail as your subscription has ended...!\n\n"
                                            "Pay for a new subscription to continue using the bot:\n\n"
                                            "Tire 2:\nAccess to 3 channels for 15 days\nPrice: ₹250\n\n"
                                            "Tire 3:\nAccess to 10 channels for 30 days\nPrice: ₹500\n\n"
                                            "Choose your preferred plan and pay to continue messaging.\n\n"  
                                            "Please connect with admin or messege in group if you need membership"     
                            )
                            print("Trial expired, user removed")
                        except:
                            pass


@Client.on_message(filters.private & filters.command(["help"]) & filters.user(Config.AUTH_USERS))
async def help(bot, update):
    
    await update.reply_text(
        "Avaliable Commands:\n\n"\
        "/start - Check if bot alive\n"\
        "/help - Show this menu\n\n" + \
        
        ("/stats - Show bot statistics\n"\
        "/restart - Restart the bot\n"\
        "/logs - Get bot logs\n\n" if update.from_user.id in Config.AUTH_USERS else "" )+ \
            
        ("/add - Add user to database\n"\
        "/remove - Remove user from database\n"\
        "/tireusers - List all users in database\n\n" if update.from_user.id in Config.AUTH_USERS else "" )+ \
        
        "/addsource - Add a source to the bot\n"\
        "/delsource - Remove a source from the bot\n"\
        "/listsources - List all sources in the bot\n\n"\
        
        "/id - Get your Telegram ID\n"
    )


@Client.on_message(filters.private & filters.command(["stats"]) & filters.user(Config.AUTH_USERS))
async def stats(bot, update):


    msg = await bot.send_message(
        chat_id=update.chat.id,
        text="__Processing...__",
        parse_mode=enums.ParseMode.MARKDOWN
    )

    currentTime = time.strftime("%Hh%Mm%Ss", time.gmtime(
        time.time() - Config.BOT_START_TIME))
    cpu_usage = psutil.cpu_percent()

    memory = psutil.virtual_memory()
    storage = psutil.disk_usage('/')

    memory_stats = f"RAM Usage: {convert_size(memory.used)} / {convert_size(memory.total)} ({memory.percent}%)"
    storage_stats = f"Storage Usage: {convert_size(storage.used)} / {convert_size(storage.total)} ({storage.percent}%)"


    size = await db.get_db_size()
    free = 536870912 - size
    size = humanbytes(size)
    free = humanbytes(free)


    ms_g = f"<b><u>Bot Stats</b></u>\n" \
        f"<code>Uptime: {currentTime}</code>\n"\
        f"<code>CPU Usage: {cpu_usage}%</code>\n"\
        f"<code>{memory_stats}</code>\n"\
        f"<code>{storage_stats}</code>\n\n" \
        f"<b><u>Mongodb Stats</b></u>\n"\
        f"<b>᚛› Used Storage : <code>{size}</code></b>\n"\
        f"<b>᚛› Free Storage : <code>{free}</code></b>"

    await msg.edit_text(
        text=ms_g,
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_message(filters.private & filters.command(["restart"]) & filters.user(Config.AUTH_USERS))
async def restart(bot, update):

    b = await bot.send_message(
        chat_id=update.chat.id,
        text="__Restarting.....__",
        parse_mode=enums.ParseMode.MARKDOWN
    )
    await asyncio.sleep(3)
    await b.delete()
    os.system("git pull")
    os.remove("logs.txt")
    os.execl(sys.executable, sys.executable, "-m", "bot")


@Client.on_message(filters.command(['logs']) & filters.user(Config.AUTH_USERS))
async def send_logs(_, m):
    await m.reply_document(
        "logs.txt",
        caption='Logs'
    )

