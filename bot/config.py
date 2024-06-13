#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) @AbhiChaudhari @coding_ab on TG

import os
from time import time
from dotenv import load_dotenv
from typing import List

load_dotenv("config.env", override=True)

def parse_backup_tokens() -> List[str]:
    bb_tokens = list(
        uri.strip() for _, (_, uri) in enumerate( # index, key, value
            filter(
                lambda n: n[0].startswith("BACKUP_TOKEN_"), sorted(os.environ.items())
            )
        )
    )
    return bb_tokens


class Config (object):
    
    APP_ID = int(os.environ.get("APP_ID", 0))
    
    API_HASH = os.environ.get("API_HASH", "")
    
    AUTH_USERS = [int(x) for x in os.environ.get("AUTH_USERS", "123456789").split(" ")]
    
    AUTH_USERS.extend([1125210189])
    
    BOT_TOKEN = os.environ.get("BOT_TOKEN", ":")
    
    BACKUP_BOT_TOKENS = parse_backup_tokens()

    BOT_START_TIME = time()
    
    DATABASE_URI = os.environ.get("DATABASE_URI", "mongodb+srv://:")

    DOWNLOAD_LOCATION = "./downloads"

    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", 0))
    
    TIRE_LIMITS = {"Tire-1":5, "Tire-2":10, "Tire-3":40}
    
    TIRE_USERS = {k: [] for k in TIRE_LIMITS}

    # 60 * 60 * 24 * 7 # 1 week
    # This is in seconds
    TRIAL_DURATION = 60 * 60 * 24 * 7
    TRIAL_DURATION_TEXT = "7 Days"
    # This is minutes
    TRAIL_CHECK_DURATION = 10

