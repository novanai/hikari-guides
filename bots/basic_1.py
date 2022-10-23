import os

import hikari

bot = hikari.GatewayBot(
    token=os.environ["BOT_TOKEN"],
)

bot.run()
