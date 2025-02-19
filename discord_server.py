import asyncio
import os
from fastapi import FastAPI

import discord
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

app = FastAPI()
intents = discord.Intents.default()
bot = discord.Client(intents=intents)


@app.route("/")
def home():
    return "Discord Bot Server is Running!"


@app.route("/send-message", methods=["POST"])
def send_message():
    print("Sending message")
    bot.send_message(CHANNEL_ID, "Hello, World!")
    return "Message sent!"

async def run():
    try:
        await bot.start(TOKEN)
    except KeyboardInterrupt:
        await bot.close()

asyncio.create_task(run())