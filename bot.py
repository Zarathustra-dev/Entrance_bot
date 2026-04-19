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
ADMIN_AVATAR_URL = os.getenv('ADMIN_AVATAR_URL')
ADMIN_NAME = os.getenv('ADMIN_NAME')
ADMIN_ROLE = os.getenv('ADMIN_ROLE')
APPROVED_ROLE = os.getenv('APPROVED_ROLE')

@bot.event
async def on_ready():
    print(f"{bot.user.name} запущен и готов к работе")

@bot.event
async def on_message(message):
    await bot.process_commands(message)

    if message.author.bot or message.content.startswith('!'):
        return

    if message.channel.id == ENTRANCE_ADMIN_ID:
        target_channel = bot.get_channel(ENTRANCE_MAIN_ID)
        webhooks = await target_channel.webhooks()
        webhook = discord.utils.get(webhooks, name="ENTRANCE_ADMIN")
        if webhook is None:
            webhook = await target_channel.create_webhook(name="ENTRANCE_ADMIN")
            
        # Собираем файлы из сообщения
        files = [await a.to_file() for a in message.attachments]
        
        await webhook.send(
            content = message.content,
            username = message.author.display_name,
            avatar_url = message.author.display_avatar.url,
            files = files
        )
    elif message.channel.id == ENTRANCE_MAIN_ID:
        target_channel = bot.get_channel(ENTRANCE_ADMIN_ID)
        webhooks = await target_channel.webhooks()
        webhook = discord.utils.get(webhooks, name="ENTRANCE_MAIN")
        if webhook is None:
            webhook = await target_channel.create_webhook(name="ENTRANCE_MAIN")
            
        # Собираем файлы из сообщения
        files = [await a.to_file() for a in message.attachments]
            
        await webhook.send(
            content = message.content,
            username = ADMIN_NAME + " " + str(message.author.id)[-3:],
            avatar_url = ADMIN_AVATAR_URL,
            files = files
        )
    else:
        return

@bot.command()
async def одобрить(ctx, user: discord.Member):
    if any(r.name == ADMIN_ROLE for r in ctx.author.roles):
        try:
            await user.add_roles(discord.utils.get(ctx.guild.roles, name=APPROVED_ROLE))
            await ctx.send(f"Пользователь {user.display_name} был одобрен.")
        except discord.Forbidden:
            await ctx.send("Ошибка: У меня нет прав на это.")
    else:
        await ctx.send("У вас нет прав на одобрение пользователей.")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
