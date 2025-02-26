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
from my_module.logger import Logger
from my_module.order import place_bracket_order
from my_module.trading_app import TradingApp

nest_asyncio.apply()
load_dotenv()

# Config
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
logger = Logger.get_logger()


# Initialize
app = FastAPI()
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)
trading_app = TradingApp()
ib = IB()

# Store bot instance
# bot_instance: Optional[discord.Client] = None


class Message(BaseModel):
    content: str
    image_path: Optional[str] = None


# FastAPI Events
@app.on_event("startup")
async def startup_event():
    # global bot_instance
    # bot_instance = bot
    asyncio.create_task(bot.start(TOKEN))


@app.get("/")
async def home():
    return {"status": "Discord Bot Server is Running!"}


@app.post("/send-message")
async def send_message(message: Message):
    if not bot.is_ready():
        raise HTTPException(status_code=503, detail="Discord bot not ready")

    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    if message.image_path:
        # Check if the image exists at the given path
        if not os.path.exists(message.image_path):
            raise HTTPException(status_code=404, detail="Image file not found")

        # Send the message with the image file
        await channel.send(message.content, file=discord.File(message.image_path))
        # If no image, send the message only
        await channel.send(message.content)
    return {"status": "Message sent successfully"}


@bot.event
async def on_ready():
    logger.info(f"{bot.user} has connected to Discord!")
    await bot.get_channel(CHANNEL_ID).send("Bot is ready!")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    msg = message.content.lower()
    logger.info(msg)

    handlers = {
        r"!p\s+(long|short)\s+(\w+)\s+(\d+)\s+([\d.]+)/([\d.]+)/([\d.]+)": handle_trade_command,
        r"^!p\s+start": handle_start_command,
        r"^!p\s+stop": handle_stop_command,
        r"^!p\s+pos": handle_position_command,
    }

    for pattern, handler in handlers.items():
        if match := re.match(pattern, msg):
            await handler(message, match)
            break


# Order Status Callback
async def on_order_status(trade):
    status = trade.orderStatus.status
    logger.info(f"Order status: {status}")
    if status == "Filled":
        fill_msg = f"✔️ Order filled: {trade.order.action} {trade.order.totalQuantity} {trade.contract.symbol} @ {trade.orderStatus.avgFillPrice}"
        logger.info(fill_msg)
        await send_message(fill_msg)


# Command Handlers
async def handle_start_command(message, match=None):
    await connect_ib(ib)
    asyncio.create_task(trading_app.run())
    ib.orderStatusEvent += lambda trade: asyncio.create_task(on_order_status(trade))
    await message.channel.send("Trading application started! 🚀")


async def handle_stop_command(message, match=None):
    await trading_app.shutdown()
    await message.channel.send("Trading application stopped! 🛑")


async def handle_trade_command(message, match):
    direction, symbol, qty, entry, tp, sl = match.groups()
    direction, symbol = direction.upper(), symbol.upper()
    qty, entry, tp, sl = int(qty), float(entry), float(tp), float(sl)
    logger.info(f"Trade order received: {direction} {symbol} {qty} {entry} {tp} {sl}")

    if (direction == "LONG" and (tp < entry or sl > entry)) or (
        direction == "SHORT" and (tp > entry or sl < entry)
    ):
        await message.channel.send("Invalid trade parameters! 🛑")
        return

    response = f">>> 📢 **Trade Order**\n🟢 {direction}\n📈 {symbol}\n💰 {entry}\n📊 {qty}\n🎯 {tp}\n🛑 {sl}\n✅ **Yes/No?**"
    await message.channel.send(response)

    def check(m):
        return (
            m.content.lower() in ["yes", "no"]
            and m.channel == message.channel
            and m.author == message.author
        )

    try:
        confirmation = await bot.wait_for(
            "message",
            check=check,
            timeout=60,
        )

        if confirmation.content.lower() == "yes":
            await message.channel.send("Trade confirmed!🚀\nExecuting... ")
            contract = Stock(symbol, "SMART", "USD")
            place_bracket_order(
                ib,
                contract,
                "BUY" if direction == "LONG" else "SELL",
                qty,
                entry,
                tp,
                sl,
            )
            await message.channel.send("Trade executed! ✅")
        else:
            await message.channel.send("Trade cancelled! ❌")
    except asyncio.TimeoutError:
        await message.channel.send("Trade confirmation timed out! ⏰")


async def handle_position_command(message, match=None):
    positions = ib.positions()
    if not positions:
        await message.channel.send("No open positions!")
        return

    positions_lines = [
        f"{pos.contract.symbol}: Positions: {pos.position}, AvgCost: {pos.avgCost}"
        for pos in positions
    ]
    await message.channel.send(">>> 📊 Open Positions:\n" + "\n".join(positions_lines))


if __name__ == "__main__":
    uvicorn.run("discord_server:app", host="0.0.0.0", port=8000)
