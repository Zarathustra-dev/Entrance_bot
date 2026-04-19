import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

ENTRANCE_ADMIN_ID = int(os.getenv('ENTRANCE_ADMIN_ID'))
ENTRANCE_MAIN_ID = int(os.getenv('ENTRANCE_MAIN_ID'))

@bot.event
async def on_ready():
    print(f"{bot.user.name} запущен и готов к работе")

# примерно так буду реализовывать логику вебхуков
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.id == ENTRANCE_ADMIN_ID:
        target_channel = bot.get_channel(ENTRANCE_MAIN_ID)
    elif message.channel.id == ENTRANCE_MAIN_ID:
        target_channel = bot.get_channel(ENTRANCE_ADMIN_ID)
    else:
        return

    files = []
    for attachment in message.attachments:
        files.append(await attachment.to_file())

    if not message.content and not files:
        return

    await target_channel.send(message.content, files=files)

    await bot.process_commands(message)

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
