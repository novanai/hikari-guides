import os

import hikari

bot = hikari.GatewayBot(
    token=os.environ["BOT_TOKEN"],
)


@bot.listen()
async def register_commands(event: hikari.StartingEvent) -> None:
    """Register ping command."""
    application = await bot.rest.fetch_application()

    ping = bot.rest.slash_command_builder("ping", "The bot's ping!")
    info = bot.rest.context_menu_command_builder(hikari.CommandType.USER, "User Info")
    react = bot.rest.context_menu_command_builder(hikari.CommandType.MESSAGE, "React!")

    await bot.rest.set_application_commands(
        application.id,
        [ping, info, react],
    )


@bot.listen()
async def handle_interactions(event: hikari.InteractionCreateEvent) -> None:
    """Listen for commands being executed."""
    inter = event.interaction
    if not isinstance(inter, hikari.CommandInteraction):
        # Only listen to command interactions, no others!
        return

    if inter.command_name == "ping":
        await inter.create_initial_response(
            hikari.ResponseType.MESSAGE_CREATE,
            f"Pong! {bot.heartbeat_latency * 1_000:.0f}ms.",
        )
    elif inter.command_name == "User Info":
        member = inter.resolved.members[inter.target_id]

        created_at = int(member.created_at.timestamp())
        joined_at = int(member.joined_at.timestamp())

        roles = (await member.fetch_roles())[1:]  # All but @everyone
        roles = sorted(roles, key=lambda role: role.position, reverse=True)

        embed = (
            hikari.Embed(
                title=member,
                description=f"ID: `{member.id}`",
                color=hikari.Color.from_rgb(255, 80, 129),
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
                ", ".join(r.mention for r in roles),
                inline=False,
            )
        )

        await inter.create_initial_response(
            hikari.ResponseType.MESSAGE_CREATE,
            embed,
        )

        print(f"Displaying {member}'s info for {inter.user}")

    elif inter.command_name == "React!":
        await inter.create_initial_response(
            hikari.ResponseType.DEFERRED_MESSAGE_CREATE,
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        await inter.app.rest.add_reaction(
            inter.channel_id,
            inter.target_id,
            "✨",
        )
        message = inter.resolved.messages[inter.target_id]
        await inter.edit_initial_response(
            f"Reacted to [this]({message.make_link(inter.guild_id)})"
            f" message sent by {message.author.mention}!",
        )

        print(f"Message now has {len(message.reactions)+1} reactions!")


bot.run()
