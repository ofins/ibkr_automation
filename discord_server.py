import asyncio
import os
from typing import Optional

import discord
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

# Initialize FastAPI and Discord
app = FastAPI()
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

# Store bot instance
bot_instance: Optional[discord.Client] = None


class Message(BaseModel):
    content: str


@app.on_event("startup")
async def startup_event():
    global bot_instance
    bot_instance = bot
    asyncio.create_task(bot.start(TOKEN))


@app.get("/")
async def home():
    return {"status": "Discord Bot Server is Running!"}


@app.post("/send-message")
async def send_message(message: Message):
    if not bot_instance:
        raise HTTPException(status_code=503, detail="Discord bot not ready")

    try:
        channel = bot_instance.get_channel(CHANNEL_ID)
        if not channel:
            raise HTTPException(status_code=404, detail="Channel not found")

        await channel.send(message.content)
        return {"status": "Message sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("Bot is ready!")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.lower() == "!pug":
        await message.channel.send("what's the magic phrase?")


import uvicorn

if __name__ == "__main__":
    uvicorn.run("discord_server:app", host="0.0.0.0", port=8000, reload=True)
