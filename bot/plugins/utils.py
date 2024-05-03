#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) @AlbertEinsteinTG

import os
import requests

from pyrogram import Client, filters, enums
from pyrogram.types import Message

from bot import Config


@Client.on_message(filters.command("id") & filters.private)
async def reply_user_id(bot: Client, update: Message):
    if update.reply_to_message:
        await update.reply_text(f"User ID from replied message: <code>{update.reply_to_message.from_user.id}</code>", parse_mode=enums.ParseMode.HTML)
    else:
        await update.reply_text(f"Your User ID: <code>{update.from_user.id}</code>", parse_mode=enums.ParseMode.HTML)


