import os
import time
from collections import defaultdict

import discord
from dotenv import load_dotenv

from bot.services.database import (
    init_db,
    get_guild_settings,
    set_guild_enabled,
    set_guild_language,
)
from bot.services.translator import translate_text

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is missing.")

# -----------------------------
# Discord Setup
# -----------------------------
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# -----------------------------
# Rate Limiting
# -----------------------------
user_last_request = defaultdict(float)
RATE_LIMIT_SECONDS = 2.5

IGNORE_SET = {
    "lol",
    "omg",
    "ok",
    "okay",
    "haha",
    "xd",
    "lmao",
}


def is_rate_limited(user_id: int) -> bool:
    now = time.time()

    if now - user_last_request[user_id] < RATE_LIMIT_SECONDS:
        return True

    user_last_request[user_id] = now
    return False


def should_translate(text: str) -> bool:
    """
    Prevent translating spam, commands, emojis,
    and very small reaction messages.
    """

    cleaned = text.strip()

    if not cleaned:
        return False

    # Ignore commands
    if cleaned.startswith("!"):
        return False

    # Ignore common reactions
    if cleaned.lower() in IGNORE_SET:
        return False

    # Ignore emoji/symbol-only messages
    if not any(char.isalpha() for char in cleaned):
        return False

    return True


# -----------------------------
# Commands
# -----------------------------
async def handle_commands(message):
    parts = message.content.strip().split()
    command = parts[0].lower()

    if command == "!setlang":

        if len(parts) != 2:
            await message.channel.send(
                "Usage: !setlang EN | ES | FR | DE | IT | PT | NL | PL | JA"
            )
            return

        language = parts[1].upper()

        set_guild_language(message.guild.id, language)

        await message.channel.send(
            f"✅ Translation language set to **{language}**"
        )

    elif command == "!translate":

        if len(parts) != 2:
            await message.channel.send("Usage: !translate on/off")
            return

        state = parts[1].lower()

        if state == "on":
            set_guild_enabled(message.guild.id, True)
            await message.channel.send("✅ Translation Enabled")

        elif state == "off":
            set_guild_enabled(message.guild.id, False)
            await message.channel.send("❌ Translation Disabled")

        else:
            await message.channel.send("Use: !translate on/off")


# -----------------------------
# Events
# -----------------------------
@client.event
async def on_ready():
    init_db()

    print("--------------------------------")
    print("Discord Translation Bot Online")
    print(f"Logged in as: {client.user}")
    print("--------------------------------")


@client.event
async def on_message(message):

    # Ignore ourselves
    if message.author == client.user:
        return

    # Ignore all bots
    if message.author.bot:
        return

    # Ignore DMs
    if not message.guild:
        return

    content = message.content.strip()

    # Rate limiting
    if is_rate_limited(message.author.id):
        return

    # Commands
    if content.startswith("!"):
        await handle_commands(message)
        return

    # Ignore junk
    if not should_translate(content):
        return

    # Server configuration
    settings = get_guild_settings(message.guild.id)

    if settings["enabled"] == 0:
        return

    target_lang = settings["target_language"]

    print(f"\n[{message.guild.name}]")
    print(f"User: {message.author}")
    print(f"Message: {content}")

    translated, detected = translate_text(
        content,
        target_lang
    )

    print(f"Detected: {detected}")
    print(f"Target: {target_lang}")
    print(f"Translation: {translated}")

    # Don't send identical messages back
    if translated.strip() == content.strip():
        return

    await message.channel.send(translated)


# -----------------------------
# Start Bot
# -----------------------------
client.run(TOKEN)