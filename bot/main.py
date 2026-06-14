import discord
import os
from dotenv import load_dotenv

from bot.services.database import (
    init_db,
    get_guild_settings,
    set_guild_language,
    set_guild_enabled
)

from bot.services.translator import translate_text

import time
from collections import defaultdict
import re

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# -----------------------------
# RATE LIMITING
# -----------------------------
user_last_request = defaultdict(float)
RATE_LIMIT_SECONDS = 2.5


def is_rate_limited(user_id: int) -> bool:
    now = time.time()
    last = user_last_request[user_id]

    if now - last < RATE_LIMIT_SECONDS:
        return True

    user_last_request[user_id] = now
    return False


# -----------------------------
# FILTER
# -----------------------------
IGNORE_SET = {"lol", "omg", "ok", "okay", "haha", "xd", "lmao"}


def should_translate(text: str) -> bool:
    cleaned = text.lower().strip()

    if cleaned.startswith("!"):
        return False

    if cleaned in IGNORE_SET:
        return False

    if len(cleaned) < 4:
        return False

    if not re.search(r"[a-zA-Záéíóúñ]", cleaned):
        return False

    return True


# -----------------------------
# COMMAND HANDLER
# -----------------------------
async def handle_commands(message):
    parts = message.content.strip().split()
    command = parts[0].lower()

    if command == "!setlang":
        if len(parts) < 2:
            await message.channel.send("Usage: !setlang EN / ES / FR")
            return

        lang = parts[1].upper()
        set_guild_language(message.guild.id, lang)

        await message.channel.send(f"✅ Language set to {lang}")

    elif command == "!translate":
        if len(parts) < 2:
            await message.channel.send("Usage: !translate on/off")
            return

        state = parts[1].lower()

        if state == "on":
            set_guild_enabled(message.guild.id, True)
            await message.channel.send("✅ Translation enabled")

        elif state == "off":
            set_guild_enabled(message.guild.id, False)
            await message.channel.send("❌ Translation disabled")

        else:
            await message.channel.send("Use on/off")


# -----------------------------
# EVENTS
# -----------------------------
@client.event
async def on_ready():
    init_db()
    print(f"Logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.author.bot:
        return

    if not message.guild:
        return

    content = message.content.strip()

    # rate limit
    if is_rate_limited(message.author.id):
        return

    # commands
    if content.startswith("!"):
        await handle_commands(message)
        return

    # filter
    if not should_translate(content):
        return

    # server settings
    settings = get_guild_settings(message.guild.id)

    if settings["enabled"] == 0:
        return

    target_lang = settings["target_language"]

    print(f"[{message.guild.name}] {message.author}: {content}")

    try:
        translated, detected = translate_text(content, target_lang)
    except Exception as e:
        print("Translation error:", e)
        return

    print(f"Detected: {detected} → Target: {target_lang}")

    await message.channel.send(translated)


# -----------------------------
# RUN
# -----------------------------
client.run(TOKEN)