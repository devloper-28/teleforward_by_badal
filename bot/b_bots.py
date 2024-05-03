#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) @AlbertEinsteinTG

import logging
import asyncio

from typing import Union, Optional, AsyncGenerator

from pyrogram import Client, enums, __version__, types
from pyrogram.errors import FloodWait
from pyropatch import listen

from bot import Config, LOGGER

ID = 0

class BackupBots(Client):
    def __init__(self, bot_tokens: str):
        global ID
        super().__init__(
            f"BackupBot{ID}",
            bot_token=bot_tokens,
            api_hash=Config.API_HASH,
            api_id=Config.APP_ID,
            workers=200,
            no_updates=True,
        )
        self.LOGGER = LOGGER
        ID += 1

    async def start(self):
        await super().start()
        self.me = await self.get_me()
        self.LOGGER(__name__).info(
            f"BackupBot @{self.me.username}  started! "
        )
        return self

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped. Bye.")


    async def iter_messages(
        self,
        chat_id: Union[int, str],
        limit: int,
        offset: int = 0,
    ) -> Optional[AsyncGenerator["types.Message", None]]:
        """Iterate through a chat sequentially.
        This convenience method does the same as repeatedly calling :meth:`~pyrogram.Client.get_messages` in a loop, thus saving
        you from the hassle of setting up boilerplate code. It is useful for getting the whole chat messages with a
        single call.
        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).
                
            limit (``int``):
                Identifier of the last message to be returned.
                
            offset (``int``, *optional*):
                Identifier of the first message to be returned.
                Defaults to 0.
        Returns:
            ``Generator``: A generator yielding :obj:`~pyrogram.types.Message` objects.
        Example:
            .. code-block:: python
                for message in app.iter_messages("pyrogram", 1, 15000):
                    print(message.text)
        """
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

