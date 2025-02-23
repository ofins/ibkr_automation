import asyncio
import os
import re
from typing import Optional

import discord
import nest_asyncio
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from ib_insync import IB, Stock
from pydantic import BaseModel

from my_module.connect import connect_ib, disconnect_ib
from my_module.order import place_bracket_order
from my_module.trading_app import TradingApp

nest_asyncio.apply()
# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

# Initialize FastAPI and Discord
app = FastAPI()
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)
trading_app = TradingApp()
ib = IB()

# Store bot instance
bot_instance: Optional[discord.Client] = None


class Message(BaseModel):
    content: str
    image_path: Optional[str] = None


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
        if message.image_path:
            # Check if the image exists at the given path
            if not os.path.exists(message.image_path):
                raise HTTPException(status_code=404, detail="Image file not found")

            # Send the message with the image file
            await channel.send(message.content, file=discord.File(message.image_path))
        else:
            # If no image, send the message only
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

    msg = message.content.lower()
    print(msg)

    patterns = {
        "trade": {
            "pattern": r"!p\s+(long|short)\s+(\w+)\s+(\d+)\s+([\d.]+)/([\d.]+)/([\d.]+)",
            "handler": handle_trade_command,
        },
        "start": {"pattern": r"^!p\s+start", "handler": handle_start_command},
        "stop": {"pattern": r"^!p\s+stop", "handler": handle_stop_command},
    }

    for key, value in patterns.items():
        match = re.match(value["pattern"], msg)
        if match:
            await value["handler"](message, match)
            break


async def handle_start_command(message, match=None):
    await connect_ib(ib)
    asyncio.create_task(trading_app.run())
    await message.channel.send("Trading application started! 🚀")


async def handle_stop_command(message, match=None):
    await trading_app.shutdown()
    await message.channel.send("Trading application stopped! 🛑")


async def handle_trade_command(message, trade_match):
    direction = trade_match.group(1).upper()
    symbol = trade_match.group(2).upper()
    quantity = int(trade_match.group(3))
    entry = float(trade_match.group(4))
    take_profit = float(trade_match.group(5))
    stop_loss = float(trade_match.group(6))

    print(
        f"Trade order received: {direction} {symbol} {quantity} {entry} {take_profit} {stop_loss}"
    )
    if direction == "LONG" and (take_profit < entry or stop_loss > entry):
        await message.channel.send("Invalid trade parameters! 🛑")
        return
    elif direction == "SHORT" and (take_profit > entry or stop_loss < entry):
        await message.channel.send("Invalid trade parameters! 🛑")
        return

    response = (
        f">>> 📢 **Trade Order Received**\n\n"
        f"🟢 **Direction:** {direction.upper()}\n"
        f"📈 **Symbol:** {symbol.upper()}\n"
        f"💰 **Entry Price:** {entry}\n"
        f"📊 **Quantity:** {quantity}\n"
        f"🎯 **Exit Price:** {take_profit}\n"
        f"🛑 **Stop Loss:** {stop_loss}\n\n"
        f"✅ **Type 'yes' to execute the trade, or 'no' to abort.**"
    )

    await message.channel.send(response)

    def check(m):
        return (
            m.content.lower() in ["yes", "no"]
            and m.channel == message.channel
            and m.author == message.author
        )

    try:
        confirmation = await bot.wait_for("message", check=check, timeout=60)
        if confirmation.content.lower() == "yes":
            await message.channel.send("Trade confirmed!🚀\nExecuting... ")

            contract = Stock(symbol, "SMART", "USD")
            place_bracket_order(
                ib,
                contract,
                "BUY" if direction == "LONG" else "SELL",
                quantity,
                entry,
                take_profit,
                stop_loss,
            )

            await message.channel.send("Trade executed! ✅")
        else:
            await message.channel.send("Trade cancelled! ❌")
    except asyncio.TimeoutError:
        await message.channel.send("Trade confirmation timed out! ⏰")


if __name__ == "__main__":
    uvicorn.run("discord_server:app", host="0.0.0.0", port=8000)
