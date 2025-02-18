import os

import discord
from dotenv import load_dotenv

from my_module.trade_input import WATCH_STOCK


class DiscordBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        load_dotenv()
        self.DISCORD_BOT_TOKEN = os.getenv("DISCORD_TOKEN")
        self.DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")

    async def send_message(self, text):
        channel = self.get_channel(int(self.DISCORD_CHANNEL_ID))
        if channel:
            await channel.send(text)

    async def on_ready(self):
        # logger.info(f"Logged in as {self.user}")
        #         message = """
        #         **🔔 Reversal Signal:**```yaml
        # 🔠 **Symbol**:        AAPL
        # 🎯 *Target Price*:    $245.00  (+$4.00 📈 )
        # 🛑 Stop Loss:         $240.45  (-$0.55 📉 )
        # 🔼 Direction          Long
        #         ```"""

        await self.send_message(f"Bot session connected: {WATCH_STOCK}")

    def run(self):
        super().run(self.DISCORD_BOT_TOKEN)


bot = DiscordBot(intents=discord.Intents.default())

if __name__ == "__main__":
    bot = DiscordBot(intents=discord.Intents.default())
    bot.run()
