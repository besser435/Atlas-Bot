import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import discord
import asyncio
import csv

import bot_config
from bot_config import log

# Config
BOT_TOKEN = bot_config.BOT_TOKEN
GUILD_ID = bot_config.GUILD_ID
CHANNEL_ID = bot_config.CHANNEL_ID
MESSAGE_IDS = bot_config.MESSAGE_IDS

# Intents
intents = discord.Intents.default()
intents.members = True
intents.reactions = True
intents.guilds = True

client = discord.Client(intents=intents)


def _save_to_csv(kicked_members: list[discord.Member]) -> None:
    with open("kicked_members.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["user_id", "username", "display_name"])
        for m in kicked_members:
            writer.writerow([m.id, m.name, m.display_name])


async def _dm_and_kick(member: discord.Member, reason="Inactivity (Kicked by AtlasBot)") -> bool:
    """Send a DM to the user then attempts to kick them from the server."""
    # Send DM first
    try:
        dm_message = (
            f"Hi {member.display_name},\n\n"
            "You might have been removed from the **AtlasCivs** server due to inactivity "
            "(for not reacting to the verification messages). "
            "You can always rejoin at any time here: https://discord.gg/43cUrmbmsb"
        )
        await member.send(dm_message)
        log.debug(f"Messaged {member.display_name}")
    except discord.Forbidden:
        log.info(f"Couldn't DM {member.display_name} (DMs closed)")
    except Exception as e:
        log.error(f"Unexpected error sending DM to {member.display_name}: {e}")

    # Then kick
    try:
        await member.kick(reason=reason)
        log.debug(f"Kicked {member.display_name}")
        return True

    except discord.Forbidden:
        log.error(f"Missing permission to kick {member.display_name}")
    except Exception as e:
        log.error(f"Unexpected error kicking {member.display_name}: {e}")

    return False


async def _fetch_reacted_members(channel: discord.TextChannel, message_ids: list[int]) -> set[discord.Member]:
    """Fetch all members who reacted to any of the specified messages."""
    reacted_members = set()

    log.debug("Fetching messages and collecting reacted members...")
    for msg_id in message_ids:
        try:
            message = await channel.fetch_message(msg_id)
        except discord.NotFound:
            log.warning(f"Message ID {msg_id} not found")
            continue
        except discord.HTTPException as e:
            log.error(f"Failed to fetch message {msg_id}: {e}")
            continue

        for reaction in message.reactions:
            async for user in reaction.users():
                if not user.bot:
                    reacted_members.add(user)

    log.debug(f"Collected {len(reacted_members)} unique member reactions")
    return reacted_members


@client.event
async def on_ready():
    log.info(f"Logged in as {client.user}")

    # Safety checks
    guild = client.get_guild(GUILD_ID)
    if guild is None:
        log.critical("Guild not found. Check GUILD_ID")
        await client.close()
        return

    channel = guild.get_channel(CHANNEL_ID)
    if channel is None:
        log.critical("Channel not found. Check CHANNEL_ID")
        await client.close()
        return

    
    # Kick and DM logic
    reacted_members = await _fetch_reacted_members(channel, MESSAGE_IDS)

    all_members = [m for m in guild.members if not m.bot]
    kicked_members = []

    log.info("Kicking members who haven't reacted (will take some time)...")
    for member in all_members:
        if member not in reacted_members:
            kicked = await _dm_and_kick(member)
            if kicked:
                kicked_members.append(member)
    #await asyncio.sleep(1)  # DiscordPy should handle rate limits automatically, but if not, add this back.

    _save_to_csv(kicked_members)
    log.info(f"Done. Kicked {len(kicked_members)} members. Logged to kicked_members.csv")

    await client.close()


client.run(BOT_TOKEN)
