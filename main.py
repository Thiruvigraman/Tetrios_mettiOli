import os
import asyncio

import discord
from discord import app_commands
from dotenv import load_dotenv
from mcstatus import BedrockServer

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
SERVER_ADDRESS = os.getenv("SERVER_ADDRESS")
STATUS_CHANNEL_ID = int(os.getenv("STATUS_CHANNEL_ID"))

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
            server = BedrockServer.lookup(SERVER_ADDRESS)
            status = await server.async_status()

            current_state = "online"

            if last_state != current_state:
                await channel.send(
                    f"🟢 **Server Online**\n"
                    f"Players: {status.players_online}"
                )

            last_state = current_state

        except Exception:
            current_state = "offline"

            if last_state != current_state:
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
        server = BedrockServer.lookup(SERVER_ADDRESS)
        result = await server.async_status()

        await interaction.response.send_message(
            f"🟢 **Online**\n"
            f"Players: {result.players_online}\n"
            f"Address: `{SERVER_ADDRESS}`"
        )

    except Exception:
        await interaction.response.send_message(
            "🔴 **Server Offline**"
        )


@tree.command(
    name="ip",
    description="Show server address"
)
async def ip(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"🌐 `{SERVER_ADDRESS}`"
    )


@tree.command(
    name="help",
    description="Show commands"
)
async def help_command(interaction: discord.Interaction):
    await interaction.response.send_message(
        "**Available Commands**\n"
        "/status\n"
        "/ip\n"
        "/help"
    )


client.run(TOKEN)