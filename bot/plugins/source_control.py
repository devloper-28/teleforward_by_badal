

from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, Message

from bot import Config
from bot.database.database import Database
import re


db = Database()

# List all sources


@Client.on_message(filters.command("addsource") & filters.private)
async def add_source(bot: Client, update: Message):
    
    user_id = update.from_user.id
    if not user_id in (Config.TIRE_USERS["Tire-1"] + Config.TIRE_USERS["Tire-2"] + Config.TIRE_USERS["Tire-3"]):
        return
    
    if len(update.command) != 2:
        return await update.reply(text="Wrong Syntax\n<code>/addsource link</code>", parse_mode=enums.ParseMode.HTML)
    
    link = update.command[1]
    
    user_info = await db.get_user_info(user_id=user_id)
    if user_info["tire"] == "Tire-1":
        if len(user_info["targets"]) == Config.TIRE_LIMITS["Tire-1"]:
            await update.reply(text="Sorry...! You hit your limit...!\nUpgrade to Tire-1 or a higher Tire-lvl to add more channels")
            return
    
    elif user_info["tire"] == "Tire-2":
        if len(user_info["targets"]) == Config.TIRE_LIMITS["Tire-2"]:
            await update.reply(text="Sorry...! You hit your limit...!\nUpgrade to Tire-2 or a higher Tire-lvl to add more channels")
            return

    elif user_info["tire"] == "Tire-3":
        if len(user_info["targets"]) == Config.TIRE_LIMITS["Tire-3"]:
            await update.reply(text="Sorry...! You hit your limit...!\nUpgrade to a higher Tire-lvl to add more channels")
            return
    
    else:
        return
    
    regex = r"(?:https?://)?(?:www\.)?(?:t\.me|telegram\.me|telegram\.dog)/([a-zA-Z0-9_]{5,32})/(\d+)"

    match = re.search(regex, link)
    if match:
        channel_username = match.group(1)
        message_id = int(match.group(2))
    else:
        await update.reply(
            text="Invalid link format\nLink should be in the format of\n<code>https://t.me/channel/1234</code>", 
            parse_mode=enums.ParseMode.HTML
        )
        return
    
    for i in user_info["targets"]:
        if i["chat_id"] == channel_username:
            return await update.reply(text="Already subscribed to this channel.⚠️")
    
    await db.add_new_chat(user_id, channel_username, message_id)
    
    chat = await bot.get_chat(channel_username)
    
    await update.reply(text=f"<code>{chat.title}</code> subscribed to this channel successfully.✅", parse_mode=enums.ParseMode.HTML)


@Client.on_message(filters.command("delsource") & filters.private)
async def del_source(bot: Client, update: Message):
    
    user_id = update.from_user.id
    if not user_id in (Config.TIRE_USERS["Tire-1"] + Config.TIRE_USERS["Tire-2"] + Config.TIRE_USERS["Tire-3"]):
        return

    if len(update.command) != 2:
        return await update.reply(text="Wrong Syntax\n<code>/delsource link</code>", parse_mode=enums.ParseMode.HTML)
    
    link = update.command[1]
    user_info = await db.get_user_info(user_id=user_id)
    
    if user_info["tire"] == "Tire-1":
        return await update.reply(text="You are not elgible to remove sources")
    
    regex = r"(?:https?://)?(?:www\.)?(?:t\.me|telegram\.me|telegram\.dog)/([a-zA-Z0-9_]{5,32})(?:/\d+)?"

    match = re.search(regex, link)
    if match:
        channel_username = match.group(1)
    else:
        await update.reply(
            text="Invalid link format\nLink should be in the format of\n<code>https://t.me/channel</code>", 
            parse_mode=enums.ParseMode.HTML
        )
        return
    
    for i in user_info["targets"]:
        if i["chat_id"] == channel_username:
            await db.rm_user_chat(user_id, channel_username)
            break
    else:
        return await update.reply(text="Channel not found in your watchlist")
    
    chat = await bot.get_chat(channel_username)
    await update.reply(text=f"<code>{chat.title}</code> was removed from the watchlist", parse_mode=enums.ParseMode.HTML)


@Client.on_message(filters.command("listsources") & filters.private)
async def list_sources(bot: Client, update: Message):
    
    user_id = update.from_user.id
    if not user_id in (Config.TIRE_USERS["Tire-1"] + Config.TIRE_USERS["Tire-2"] + Config.TIRE_USERS["Tire-3"]):
        return
    
    user_info = await db.get_user_info(user_id=user_id)
    if not user_info or not user_info["targets"]:
        return await update.reply(text="No channels in your watchlist")
    
    text = "<b>Channels in the watchlist</b>\n\n"
    for i, j in enumerate(user_info["targets"]):
        chat = await bot.BOTS[i%len(bot.BOTS)].get_chat(j["chat_id"])
        text += f"• <code>{chat.title}</code>\n"
    
    await update.reply(text=text, parse_mode=enums.ParseMode.HTML)
    
