#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) @AlbertEinsteinTG

import logging
import asyncio

from collections import defaultdict
from typing import Dict, List

from typing import Union, Optional, AsyncGenerator

from pyrogram import Client, enums, __version__, types
from pyrogram.errors import FloodWait
from pyropatch import listen, flood_handler

from bot import LOGGER, Config
from bot.database.database import Database
from bot.b_bots import BackupBots

db = Database()

class Bot(Client):
    
    BOTS: List[BackupBots] = []

    USAGES = defaultdict(int)
    
    def __init__(self):
        super().__init__(
            "bot",
            api_id=Config.APP_ID,
            api_hash=Config.API_HASH,
            plugins={
                "root": "bot/plugins"
            },
            workers=400,
            bot_token=Config.BOT_TOKEN
        )
        self.LOGGER = LOGGER

    async def start(self):
        await super().start()
        self.me = await self.get_me()
        self.set_parse_mode(enums.ParseMode.HTML)
        self.LOGGER(__name__).info(
            f"MainBot @{self.me.username}  started! "
        )

        for i, tokens in enumerate(Config.BACKUP_BOT_TOKENS):
            bot = await BackupBots(tokens).start()
            self.BOTS.append(bot)
            self.USAGES[i] = 0

        self.BOTS.append(self)
        self.USAGES[len(self.BOTS)-1] = 0
        print("Loading Tire Users")
        await db.load_tire_users()

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped. Bye.")


    async def iter_messages(
        self,
        chat_id: Union[int, str],
        limit: int,
        offset: int = 0,
    ) -> Optional[AsyncGenerator["types.Message", None]]:
        current = offset
        while True:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            try:
                messages = await self.get_messages(chat_id, list(range(current, current+new_diff+1)))
            except FloodWait as e:
                logging.info(f"Sleeping for {e.value} seconds")
                await asyncio.sleep(e.value)
                messages = await self.get_messages(chat_id, list(range(current, current+new_diff+1)))

            for message in messages:
                yield message
                current += 1

    
app = Bot()