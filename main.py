import os
import asyncio

import discord
from discord import app_commands
from dotenv import load_dotenv
from mcstatus import BedrockServer

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
SERVER_ADDRESS = os.getenv("SERVER_ADDRESS")
SERVER_PORT = os.getenv("SERVER_PORT", "34622")
STATUS_CHANNEL_ID = int(os.getenv("STATUS_CHANNEL_ID", "0"))

intents = discord.Intents.default()

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

last_state = None


async def monitor_server():
    global last_state

    await client.wait_until_ready()

    channel = client.get_channel(STATUS_CHANNEL_ID)

    while not client.is_closed():
        try:
            server = BedrockServer.lookup(
                f"{SERVER_ADDRESS}:{SERVER_PORT}"
            )

            status = await server.async_status()

            current_state = "online"

            if last_state != current_state and channel:
                await channel.send(
                    f"🟢 **Server Online**\n"
                    f"👥 Players: {status.players_online}"
                )

            last_state = current_state

        except Exception:
            current_state = "offline"

            if last_state != current_state and channel:
                await channel.send(
                    "🔴 **Server Offline**"
                )

            last_state = current_state

        await asyncio.sleep(60)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

    try:
        synced = await tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)

    asyncio.create_task(monitor_server())


@tree.command(
    name="status",
    description="Check Minecraft server status"
)
async def status(interaction: discord.Interaction):
    try:
        server = BedrockServer.lookup(
            f"{SERVER_ADDRESS}:{SERVER_PORT}"
        )

        result = await server.async_status()

        await interaction.response.send_message(
            f"🟢 **Server Online**\n"
            f"👥 Players: {result.players_online}\n"
            f"🌐 Address: `{SERVER_ADDRESS}`\n"
            f"🔌 Port: `{SERVER_PORT}`"
        )

    except Exception:
        await interaction.response.send_message(
            f"🔴 **Server Offline**\n"
            f"🌐 Address: `{SERVER_ADDRESS}`\n"
            f"🔌 Port: `{SERVER_PORT}`"
        )


@tree.command(
    name="players",
    description="Show online player count"
)
async def players(interaction: discord.Interaction):
    try:
        server = BedrockServer.lookup(
            f"{SERVER_ADDRESS}:{SERVER_PORT}"
        )

        result = await server.async_status()

        await interaction.response.send_message(
            f"👥 Players Online: **{result.players_online}**"
        )

    except Exception:
        await interaction.response.send_message(
            "🔴 Server Offline"
        )


@tree.command(
    name="ip",
    description="Show server IP and port"
)
async def ip(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"🌐 **Server Information**\n"
        f"Address: `{SERVER_ADDRESS}`\n"
        f"Port: `{SERVER_PORT}`"
    )


@tree.command(
    name="help",
    description="Show commands"
)
async def help_command(interaction: discord.Interaction):
    await interaction.response.send_message(
        "**Available Commands**\n"
        "📊 /status\n"
        "👥 /players\n"
        "🌐 /ip\n"
        "❓ /help"
    )


client.run(TOKEN)