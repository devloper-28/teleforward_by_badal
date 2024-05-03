#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) @AlbertEinsteinTG

from pyrogram.types import Message
from pyrogram.enums import MessageMediaType


def get_media_file_id(message: Message):

    media = message.audio or \
            message.document or \
            message.photo or \
            message.sticker or \
            message.video or \
            message.animation or \
            message.voice or \
            message.video_note

    if media and media.file_id:
        return media.file_id
    else:
        return None


def get_media_file_size(message: Message):
    media = message.audio or \
            message.document or \
            message.photo or \
            message.sticker or \
            message.video or \
            message.animation or \
            message.voice or \
            message.video_note

    if media and media.file_size:
        return media.file_size
    else:
        return None


def get_file_type(message: Message):
    if message.document:
        return "document"
    if message.video:
        return "video"
    if message.audio:
        return "audio"
    if message.photo:
        return "photo"

def get_media(message: Message):
    media = message.document or \
            message.photo or \
            message.video or \
            message.sticker or \
            message.animation or \
            message.voice or \
            message.video_note or\
            message.audio

    return media

def humanbytes(size):
    # https://stackoverflow.com/a/49361727/4723940
    # 2**10 = 1024
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'


def TimeFormatter(seconds: int) -> str:
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s") if seconds else "0s")
    return tmp


def get_message_media_type(msg):
    
    for i in [MessageMediaType.VIDEO, MessageMediaType.AUDIO, MessageMediaType.STICKER,
              MessageMediaType.DOCUMENT, MessageMediaType.PHOTO]:
        if getattr(msg, i):
            return i
    else:
        pass
    
def convert_size(size):
    units = ["B", "KB", "MB", "GB", "TB"]
    index = 0
    while size >= 1024 and index < len(units) - 1:
        size /= 1024
        index += 1
    return f"{size:.2f} {units[index]}"
