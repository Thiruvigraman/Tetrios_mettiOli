import os
import asyncio

import discord
from discord import app_commands
from dotenv import load_dotenv
from mcstatus import BedrockServer

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
SERVER_ADDRESS = os.getenv("SERVER_ADDRESS")
SERVER_PORT = os.getenv("SERVER_PORT", "26104")
STATUS_CHANNEL_ID = int(os.getenv("STATUS_CHANNEL_ID", "0"))

intents = discord.Intents.default()

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

status_message = None


async def get_server_status():
    try:
        server = BedrockServer.lookup(
            f"{SERVER_ADDRESS}:{SERVER_PORT}"
        )

        status = await server.async_status()

        return {
            "online": True,
            "players": status.players_online,
            "max_players": getattr(status, "players_max", "?"),
            "player_names": []
        }

    except Exception:
        return {
            "online": False
        }


async def monitor_server():
    global status_message

    await client.wait_until_ready()

    channel = client.get_channel(STATUS_CHANNEL_ID)

    if not channel:
        return

    while not client.is_closed():

        data = await get_server_status()

        if data["online"]:

            content = (
                "🟢 **SERVER ONLINE**\n\n"
                f"👥 Players: {data['players']}/{data['max_players']}\n"
                f"🌍 `{SERVER_ADDRESS}`\n"
                f"🔌 `{SERVER_PORT}`"
            )

        else:

            content = (
                "🔴 **SERVER OFFLINE**\n\n"
                f"🌍 `{SERVER_ADDRESS}`\n"
                f"🔌 `{SERVER_PORT}`"
            )

        try:

            if status_message is None:

                status_message = await channel.send(content)

            else:

                await status_message.edit(content=content)

        except Exception:
            pass

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
    name="ip",
    description="Show server information"
)
async def ip(interaction: discord.Interaction):

    data = await get_server_status()

    if data["online"]:
        status = "🟢 Online"
    else:
        status = "🔴 Offline"

    await interaction.response.send_message(
        f"{status}\n\n"
        f"🌍 Address: `{SERVER_ADDRESS}`\n"
        f"🔌 Port: `{SERVER_PORT}`"
    )


@tree.command(
    name="status",
    description="Show detailed server status"
)
async def status(interaction: discord.Interaction):

    data = await get_server_status()

    if not data["online"]:

        await interaction.response.send_message(
            "🔴 **Server Offline**"
        )

        return

    player_text = "No player list available"

    await interaction.response.send_message(
        f"🟢 **Server Online**\n\n"
        f"👥 Players: {data['players']}/{data['max_players']}\n\n"
        f"{player_text}"
    )


@tree.command(
    name="help",
    description="Show commands"
)
async def help_command(interaction: discord.Interaction):

    await interaction.response.send_message(
        "**Tetrios Commands**\n\n"
        "🌍 /ip\n"
        "📊 /status\n"
        "❓ /help"
    )


client.run(TOKEN)