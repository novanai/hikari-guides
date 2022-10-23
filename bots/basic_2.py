import os

import hikari

bot = hikari.GatewayBot(
    token=os.environ["BOT_TOKEN"],
    intents=hikari.Intents.ALL_MESSAGES,
)


@bot.listen()
async def on_message(event: hikari.MessageCreateEvent) -> None:
    """Listen for messages being created."""
    if not event.is_human:
        # Do not respond to bots or webhooks!
        return

    if not event.content:
        # The message does not contain any content
        return

    me = bot.get_me()
    if not me:
        # get_me() will not be available before hikari.StartingEvent
        # has been fired, but should always be available after that
        return

    if event.content == f"<@{me.id}> ping":
        await event.message.respond(f"Pong! {bot.heartbeat_latency * 1_000:.0f}ms.")


bot.run()
