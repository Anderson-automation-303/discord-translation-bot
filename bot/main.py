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
# DISCORD SETUP
# -----------------------------
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# -----------------------------
# RATE LIMITING
# -----------------------------
user_last_request = defaultdict(float)
RATE_LIMIT_SECONDS = 2.5

IGNORE_SET = {
    "lol", "omg", "ok", "okay", "haha", "xd", "lmao"
}

def is_rate_limited(user_id: int) -> bool:
    now = time.time()

    if now - user_last_request[user_id] < RATE_LIMIT_SECONDS:
        return True

    user_last_request[user_id] = now
    return False


def should_translate(text: str) -> bool:
    cleaned = text.strip()

    if not cleaned:
        return False

    if cleaned.startswith("!"):
        return False

    if cleaned.lower() in IGNORE_SET:
        return False

    if not any(c.isalpha() for c in cleaned):
        return False

    return True


# -----------------------------
# COMMANDS
# -----------------------------
async def handle_commands(message):
    parts = message.content.strip().split()
    command = parts[0].lower()

    # HELP
    if command == "!help":
        await message.channel.send(
            "🌐 **Interlingo Help**\n\n"
            "**Commands:**\n"
            "`!translate on/off` - Enable or disable translation\n"
            "`!setlang <code>` - Set language (EN, ES, FR, etc.)\n"
            "`!help` - Show this message\n\n"
            "**Support:**\n"
            "https://docs.google.com/forms/d/e/1FAIpQLSf7HeUhHDvtbKe0zbfDafSq7r6gLg8TIQR_r6lZZIdwcQCzlA/viewform"
        )
        return

    # SET LANGUAGE
    if command == "!setlang":
        if len(parts) != 2:
            await message.channel.send("Usage: !setlang EN")
            return

        lang = parts[1].upper()
        set_guild_language(message.guild.id, lang)

        await message.channel.send(f"✅ Language set to **{lang}**")

    # TOGGLE TRANSLATION
    elif command == "!translate":
        if len(parts) != 2:
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

    print("--------------------------------")
    print("Interlingo Bot Online")
    print(f"Logged in as: {client.user}")
    print("Ready for Top.gg submission")
    print("--------------------------------")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.author.bot:
        return

    if not message.guild:
        return

    content = message.content.strip()

    if is_rate_limited(message.author.id):
        return

    if content.startswith("!"):
        await handle_commands(message)
        return

    if not should_translate(content):
        return

    settings = get_guild_settings(message.guild.id)

    if settings["enabled"] == 0:
        return

    target_lang = settings["target_language"]

    translated, detected = translate_text(content, target_lang)

    if translated.strip() == content.strip():
        return

    await message.channel.send(translated)


# -----------------------------
# RUN BOT
# -----------------------------
client.run(TOKEN)