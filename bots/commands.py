import os
import typing

import hikari

bot = hikari.GatewayBot(
    token=os.environ["BOT_TOKEN"],
)


@bot.listen()
async def register_commands(event: hikari.StartingEvent) -> None:
    """Register commands."""
    application = await bot.rest.fetch_application()

    ping = bot.rest.slash_command_builder("ping", "The bot's ping!")
    info = bot.rest.context_menu_command_builder(hikari.CommandType.USER, "User Info")
    react = bot.rest.context_menu_command_builder(hikari.CommandType.MESSAGE, "React!")

    await bot.rest.set_application_commands(
        application.id,
        [ping, info, react],
    )


CommandCallbackT = typing.Callable[[hikari.CommandInteraction], typing.Awaitable[None]]


commands: typing.Dict[str, CommandCallbackT] = {}


def command(name: str) -> typing.Callable[[CommandCallbackT], CommandCallbackT]:
    def decorate(func: CommandCallbackT) -> CommandCallbackT:
        commands[name] = func
        return func

    return decorate


@bot.listen()
async def handle_interactions(event: hikari.InteractionCreateEvent) -> None:
    """Listen for commands being executed."""
    inter = event.interaction
    if not isinstance(inter, hikari.CommandInteraction):
        # Only listen to command interactions, no others!
        return

    if commands.get(inter.command_name):
        await commands[inter.command_name](inter)


@command("ping")
async def ping(inter: hikari.CommandInteraction) -> None:
    await inter.create_initial_response(
        hikari.ResponseType.MESSAGE_CREATE,
        f"Pong! {bot.heartbeat_latency * 1_000:.0f}ms.",
    )


EMBED_COLOR = hikari.Color.from_rgb(255, 80, 129)


@command("User Info")
async def user_info(inter: hikari.CommandInteraction) -> None:
    member = inter.resolved.members[inter.target_id]  # type: ignore [union-attr, index]

    created_at = int(member.created_at.timestamp())
    joined_at = int(member.joined_at.timestamp())

    embed = (
        hikari.Embed(
            title=member,
            description=f"ID: `{member.id}`",
            color=EMBED_COLOR,
            timestamp=inter.created_at,
        )
        .set_thumbnail(member.display_avatar_url)
        .set_footer(f"Invoked by {inter.user}", icon=inter.user.display_avatar_url)
        .add_field(
            "Bot?",
            "Yes" if member.is_bot else "No",
            inline=True,
        )
        .add_field(
            "Created account on",
            f"<t:{created_at}:d>\n(<t:{created_at}:R>)",
            inline=True,
        )
        .add_field(
            "Joined server on",
            f"<t:{joined_at}:d>\n(<t:{joined_at}:R>)",
            inline=True,
        )
        .add_field(
            "Roles",
            ", ".join(f"<@&{id_}>" for id_ in member.role_ids),
            inline=False,
        )
    )

    await inter.create_initial_response(
        hikari.ResponseType.MESSAGE_CREATE,
        embed,
    )

    print(f"Displaying {member}'s info for {inter.user}")


@command("React!")
async def react(inter: hikari.CommandInteraction) -> None:
    await inter.create_initial_response(
        hikari.ResponseType.DEFERRED_MESSAGE_CREATE,
        flags=hikari.MessageFlag.EPHEMERAL,
    )
    await inter.app.rest.add_reaction(
        inter.channel_id,
        inter.target_id,  # type: ignore [arg-type]
        "✨",
    )
    message = inter.resolved.messages[inter.target_id]  # type: ignore [union-attr, index]
    await inter.edit_initial_response(
        f"Reacted to [this]({message.make_link(inter.guild_id)})"
        f" message sent by {message.author.mention}!",
    )

    print(f"Message now has {len(message.reactions)+1} reaction(s)!")


bot.run()
