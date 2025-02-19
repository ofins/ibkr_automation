import asyncio
import os
import threading

import discord
from dotenv import load_dotenv
from flask import Flask, jsonify, request

# Load environment variables
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

# Initialize Flask app
app = Flask(__name__)

# Create a Discord bot client
intents = discord.Intents.default()
bot = discord.Client(intents=intents)


# Start the bot in a separate thread
def run_discord_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(bot.start(TOKEN))


# Running the Discord bot in a separate thread
threading.Thread(target=run_discord_bot, daemon=True).start()


@app.route("/")
def home():
    return "Discord Bot Server is Running!"


@app.route("/send-message", methods=["POST"])
def send_message():
    try:
        data = request.json
        message = data.get("message", "")

        if not message:
            return jsonify({"error": "Message is required"}), 400

        async def send_to_discord():
            channel = bot.get_channel(CHANNEL_ID)
            if channel:
                await channel.send(message)
                return jsonify({"status": "Message sent!"}), 200
            else:
                return jsonify({"error": "Invalid channel ID"}), 500

        # Create a new asyncio task to handle the async function
        asyncio.create_task(send_to_discord())

        return jsonify({"status": "Message sent!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Run Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
