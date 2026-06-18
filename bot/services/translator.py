import discord
from discord import app_commands
from translator import translate_text  # <-- your file

TOKEN = "YOUR_BOT_TOKEN_HERE"

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@tree.command(name="translate", description="Translate text using DeepL")
@app_commands.describe(
    text="Text to translate",
    language="Target language (e.g. EN, ES, FR, DE)"
)
async def translate(interaction: discord.Interaction, text: str, language: str = "EN"):

    await interaction.response.defer()  # prevents timeout

    translated, detected = translate_text(text, language.upper())

    await interaction.followup.send(
        f"🌍 **Translated:** {translated}\n"
        f"🔎 **Detected Language:** {detected}"
    )


@client.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {client.user}")


client.run(TOKEN)