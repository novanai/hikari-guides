import os

import hikari

bot = hikari.GatewayBot(
    token=os.environ["BOT_TOKEN"],
    intents=hikari.Intents.ALL_MESSAGES,
)


@bot.listen()
async def register_commands(event: hikari.StartingEvent) -> None:
    """Register ping command."""
    application = await bot.rest.fetch_application()

    ping = bot.rest.slash_command_builder("ping", "The bot's ping!")

    await bot.rest.set_application_commands(
        application.id,
        [ping],
    )


@bot.listen()
async def handle_interactions(event: hikari.InteractionCreateEvent) -> None:
    """Listen for slash commands being executed."""
    if not isinstance(event.interaction, hikari.CommandInteraction):
        # Only listen to command interactions, no others!
        return

    if event.interaction.command_name == "ping":
        await event.interaction.create_initial_response(
            hikari.ResponseType.MESSAGE_CREATE,
            f"Pong! {bot.heartbeat_latency * 1_000:.0f}ms.",
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
