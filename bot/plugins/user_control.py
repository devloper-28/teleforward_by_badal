from pyrogram import Client, filters, enums, handlers
from pyrogram.types import InlineKeyboardButton, Message

from bot import Config, LOGGER
from bot.bot import app
from bot.database.database import Database

db = Database()
logger = LOGGER(__name__)


@Client.on_message(filters.command("add") & filters.user(Config.AUTH_USERS))
async def add_user_db(bot: Client, update: Message):

    if len(update.command) != 3:
        return await update.reply(
                "Invalid Format\n<code>/add [tire lvl] [user id]</code>")

    tire = update.command[1]
    user_id = update.command[2]

    await db.remove_user(user_id)
    await db.add_user(user_id, f"Tire-{tire}")
    await db.load_tire_users()

    try:
        await bot.send_message(
                user_id,
                f"You can now enjoy the benefits of Tire-{tire}...!\n\nYou just need to paste the channel link now with starting of /addsource and then LINK, for e.g. ('http://t.me/roughhardsex/12681').\n\nMake sure to add last chat id so it will give you all upcoming content.\n\nIf you are using the free tier, it will expire in 1 day, and only 1 channel is allowed in your subscription.\n\nUpgrade to a higher tier to enjoy more benefits:\n\nTire 2:\nAccess to 3 channels for 15 days\nPrice: ₹250\n\nTire 3:\nAccess to 10 channels for 30 days\nPrice: ₹500\n\nChoose your preferred plan and pay to continue messaging."
        )

    except Exception as e:
        logger.debug(e)

    await update.reply(
            f"User - {user_id} has been added to Tire-{tire} sucessfully...!")


@Client.on_message(filters.command("remove") & filters.user(Config.AUTH_USERS))
async def rm_user_db(bot: Client, update: Message):

    if len(update.command) != 2:
        return await update.reply("Invalid Format\n<code>/remove [user id]</code>")

    user_id = update.command[1]
    user_info = await db.get_user_info(user_id)

    await db.remove_user(user_id)
    await db.load_tire_users()

    await bot.send_message(
            user_id,
    
                    f"You were removed from {user_info['tire']} as your subscription has ended...!\n\n"
                    "Pay for a new subscription to continue using the bot:\n\n"
                    "Tire 2:\nAccess to 3 channels for 15 days\nPrice: ₹250\n\n"
                    "Tire 3:\nAccess to 10 channels for 30 days\nPrice: ₹500\n\n"
                    "Choose your preferred plan and pay to continue messaging.\n\n"  
                    "Please connect with admin or messege in group if you need membership"     
    )

    await update.reply(f"User - {user_id} was removed sucessfully...!")


@Client.on_message(
        filters.command("tireusers") & filters.user(Config.AUTH_USERS))
async def tire_users_list(bot: Client, update: Message):

    tire_users = Config.TIRE_USERS

    text = ""
    for tire in tire_users:
        text += f"<b>{tire} | Users - {len(tire_users[tire])}</b>\n"
        for user in tire_users[tire]:
            text += f"👤 <code>{user}</code>\n"
        text += "\n"

    await update.reply(text=text, parse_mode=enums.ParseMode.HTML)
