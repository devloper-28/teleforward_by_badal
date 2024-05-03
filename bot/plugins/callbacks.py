#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) @AlbertEinsteinTG

from bot import LOGGER
from bot.config import Config
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import Client, filters, enums

logger = LOGGER(__name__)

@Client.on_callback_query()
async def callbacks(bot: Client, update: CallbackQuery):
    
    logger.info(update.data)
    try:
        await update.answer("")
    except:
        pass


