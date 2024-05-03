#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) @AlbertEinsteinTG

import motor.motor_asyncio
from pymongo.collection import Collection
from bot import Config, LOGGER

logger = LOGGER(__name__)
CACHE = {}


class Database:
    def __init__(self):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(Config.DATABASE_URI)
        self.db = self._client["FileLeechBot"]
        self.col = self.db["Users"]
        self.cache = {}

    async def load_tire_users(self):

        # load each tire users
        for tire in Config.TIRE_USERS:
            Config.TIRE_USERS[tire] = []
            async for user in self.col.find({"tire": tire}):
                Config.TIRE_USERS[tire].append(user["_id"])
        logger.info("Tire users loaded successfully")


    async def new_user(self, **args):
        return dict(
            _id = args["user_id"],
            targets=[
                # {
                #     "chat_id": -100123456789, "last_msg_id": 999
                # }
            ],
            tire="Tire-1"
        )


    async def add_user(self, user_id: int, Tire="Tire-1"):
        await self.col.insert_one({"_id": int(user_id), "targets":[],"tire":Tire})
        
    async def remove_user(self, user_id: int):
        await self.col.delete_one({"_id": int(user_id)})
        
    async def add_new_chat(self, user_id: int, target_chat: int, last_msg_id: int):
        await self.col.update_one({"_id": int(user_id)}, {"$push": {"targets":{"chat_id": target_chat, "last_msg_id": last_msg_id}}}, upsert=True)

    async def rm_user_chat(self, user_id: int, chat_id: int):
        await self.col.update_one({"_id": int(user_id)}, {"$pull":{"targets":{"chat_id": chat_id}}})
        
    async def get_user_info(self, user_id: int):
        return await self.col.find_one({"_id": int(user_id)})
    
    async def get_all_sources(self):
        pipeline = [
            {"$unwind": "$targets"},  # Deconstruct the target array
            {"$group": {"_id": None, "chat_ids": {"$addToSet": "$targets.chat_id"}}}  # Collect unique chat_ids
        ]
        result = await self.col.aggregate(pipeline).to_list(None)
        if result:
            return result[0]['chat_ids']
        return []

    async def get_last_message(self, chat_id: int):
        # Query to fetch documents where target.chat_id matches chat_id_search
        result = await self.col.find_one(
            {"targets.chat_id": chat_id},
            {"_id": 0, "targets.$": 1}
        )
        if result and 'targets' in result:
            # Extract last_msg_id
            last_msg_id = result['targets'][0]['last_msg_id']
            return last_msg_id
        return None

    async def set_last_message(self, chat_id: int, last_msg_id: int):
        update_result = await self.col.update_many(
            {"targets.chat_id": chat_id},
            {"$set": {"targets.$.last_msg_id": last_msg_id}}
        )
        return update_result.modified_count

    async def get_listners(self, chat_id: int):
        users = []
        # Query to find documents where target.chat_id matches chat_id_search
        cursor = self.col.find({"targets.chat_id": chat_id}, {"_id": 1})
        async for document in cursor:
            # Collect _id values
            users.append(int(document['_id']))
        return users

    async def get_db_size(self):
        return (await self.db.command("dbstats"))['dataSize']


