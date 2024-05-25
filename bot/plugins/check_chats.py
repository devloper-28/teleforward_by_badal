import os

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from pyrogram import Client, filters, enums
from pyrogram.types import Message
from pyrogram.errors import UserBlocked, UsernameNotOccupied, UserDeactivated, InputUserDeactivated, UserIsBlocked

from bot.bot import app
from bot import Config
from bot.database.database import Database
from bot.helpers.utils import get_file_type, get_media

db = Database()
SOURCES = set()
scheduler = AsyncIOScheduler(
    {"apscheduler.timezone": "UTC"},
    job_defaults={"misfire_grace_time": 5},
    daemon=True,
    run_async=True,
)


async def check_messages():
  global SOURCES
  temp = set()
  for i in (await db.get_all_sources()):
    temp.add(i)

  SOURCES = temp

  for i in SOURCES:

    notified = False
    offset = (await db.get_last_message(i)) + 1

    client_index = min(app.USAGES, key=app.USAGES.get)
    app.USAGES[client_index] += 1
    light_client = app.BOTS[client_index]
    try:
        async for message in light_client.iter_messages(i, offset=offset, limit=offset + 50):
            message: Message
            is_restricted = False
            if message.empty:
                continue

            if message.chat.has_protected_content:
                is_restricted = True

            if message.text:
                for user in (await db.get_listners(i)):
                    # Notifying of the source if not done before
                    try:
                        if not notified:
                            await app.send_message(
                                user, f"New message in {message.chat.title}\n")
                        await app.send_message(chat_id=user,
                                                text=message.text.html,
                                                parse_mode=enums.ParseMode.HTML)
                    except UserBlocked:
                        await db.remove_user(user)
                        continue

                    except UserIsBlocked:
                        await db.remove_user(user)
                        continue

                    except UserDeactivated:
                        await db.remove_user(user)
                        continue

                    except InputUserDeactivated:
                        await db.remove_user(user)
                        continue


            elif message.media:
                if is_restricted:
                    client_index = min(app.USAGES, key=app.USAGES.get)
                    app.USAGES[client_index] += 1
                    light_client = app.BOTS[client_index]

                    f = await light_client.get_messages(chat_id=i,
                                                        message_ids=message.id)
                    thumb = get_media(f)
                    # if not type(thumb) == enums.MessageMediaT)ype.PHOTO:
                    #     thumb = await fastest_client.download_media(message=thumb.thumbs[0].file_id)
                    dl = await f.download()

                    app.USAGES[client_index] -= 1
                    send_msg = False
                    for user in await db.get_listners(i):
                        try:
                            # Notifying of the source if not done before
                            if not notified:
                                await app.send_message(
                                    user, f"New message in {message.chat.title}\n")

                            # Caching the media uplaoding
                            if not send_msg:
                                if get_file_type(f) == "document":
                                    thumb = await light_client.download_media(
                                        message=thumb.thumbs[0].file_id)
                                    send_msg = await app.send_document(
                                        chat_id=user,
                                        document=dl,
                                        thumb=thumb,
                                        caption=message.caption.html,
                                        parse_mode=enums.ParseMode.HTML)

                                elif get_file_type(f) == "video":
                                    thumb = await light_client.download_media(
                                        message=thumb.thumbs[0].file_id)
                                    send_msg = await app.send_video(
                                        chat_id=user,
                                        video=dl,
                                        thumb=thumb,
                                        caption=message.caption.html,
                                        parse_mode=enums.ParseMode.HTML)

                                elif get_file_type(f) == "photo":
                                    send_msg = await app.send_photo(
                                        user,
                                        photo=dl,
                                        caption=message.caption.html,
                                        parse_mode=enums.ParseMode.HTML)
                                else:
                                    await send_msg.copy(chat_id=user,
                                                        caption=message.caption.html,
                                                        parse_mode=enums.ParseMode.HTML)
                        except UserBlocked:
                            await db.remove_user(user)
                            continue
                        
                        except UserIsBlocked:
                            await db.remove_user(user)
                            continue

                        except UserDeactivated:
                            await db.remove_user(user)
                            continue

                        except InputUserDeactivated:
                            await db.remove_user(user)
                            continue
                    else:
                        # Remove downloaded file and thumb
                        os.remove(dl)
                        if isinstance(thumb, str):
                            os.remove(thumb)
           
                else:
                    for user in await db.get_listners(i):
                        try:
                            await app.copy_message(chat_id=user,
                                                from_chat_id=i,
                                                message_id=message.id)
                        except UserBlocked:
                            await db.remove_user(user)
                            continue

                        except UserIsBlocked:
                            await db.remove_user(user)
                            continue

                        except UserDeactivated:
                            await db.remove_user(user)
                            continue

                        except InputUserDeactivated:
                            await db.remove_user(user)
                            continue

            else:
                pass

            # Mark source's new message as notified
            notified = True
            await db.set_last_message(i, message.id)
    except UsernameNotOccupied:
      continue
    app.USAGES[client_index] -= 1


scheduler.add_job(check_messages, "interval", minutes=30)

scheduler.start()
