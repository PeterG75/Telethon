#!/usr/bin/env python3
"""
A example script to automatically send messages based on certain triggers.

NOTE: To run this script you MUST have 'TG_API_ID' and 'TG_API_HASH' in
      your environment variables. This is a good way to use these private
      values. See https://superuser.com/q/284342.

This script assumes that you have certain files on the working directory,
such as "xfiles.m4a" or "anytime.png" for some of the automated replies.
"""
import re
from collections import defaultdict
from datetime import datetime, timedelta
from os import environ

from telethon import TelegramClient, events

"""Uncomment this for debugging
import logging
logging.basicConfig(level=logging.DEBUG)
logging.debug('dbg')
logging.info('info')
"""

REACTS = {'emacs': 'Needs more vim',
          'chrome': 'Needs more Firefox'}

# A list of dates of reactions we've sent, so we can keep track of floods
recent_reacts = defaultdict(list)


# TG_API_ID and TG_API_HASH *must* exist or this won't run!
session_name = environ.get('TG_SESSION', 'session')
client = TelegramClient(
    session_name, int(environ['TG_API_ID']), environ['TG_API_HASH'],
    proxy=None
)


@client.on(events.NewMessage)
async def my_handler(event: events.NewMessage.Event):
    global recent_reacts

    # Through event.raw_text we access the text of messages without format
    words = re.split('\W+', event.raw_text)

    # Try to match some reaction
    for trigger, response in REACTS.items():
        if len(recent_reacts[event.chat_id]) > 3:
            # Silently ignore triggers if we've recently sent 3 reactions
            break

        if trigger in words:
            # Remove recent replies older than 10 minutes
            recent_reacts[event.chat_id] = [
                a for a in recent_reacts[event.chat_id] if
                datetime.now() - a < timedelta(minutes=10)
            ]
            # Send a reaction as a reply (otherwise, event.respond())
            await event.reply(response)
            # Add this reaction to the list of recent actions
            recent_reacts[event.chat_id].append(datetime.now())

    # Automatically send relevant media when we say certain things
    # When invoking requests, get_input_entity needs to be called manually
    if event.out:
        chat = await event.get_input_chat()
        if event.raw_text.lower() == 'x files theme':
            await client.send_file(chat, 'xfiles.m4a',
                                   reply_to=event.message.id, voice_note=True)
        if event.raw_text.lower() == 'anytime':
            await client.send_file(chat, 'anytime.png',
                                   reply_to=event.message.id)
        if '.shrug' in event.text:
            await event.edit(event.text.replace('.shrug', r'¯\_(ツ)_/¯'))


with client.start():
    print('(Press Ctrl+C to stop this)')
    client.run_until_disconnected()
