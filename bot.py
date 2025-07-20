import discord
from discord.ext import commands, tasks
import random
import threading
from flask import Flask
import os
import aiohttp
import asyncio

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Bonus Loot Tables
def roll_bonus(name):
    tables = {
        "Mega Stone Loot Table A": [
            "Scizorite", "Heracrossite", "Pinsirite", "Beedrillite", "Sceptilite", "Venusaurite",
            "Lopunnite", "Pidgeotite", "Alakazite", "Slowbronite", "Gardevoirite", "Manectite",
            "Glalitite", "Abomasite", "Zoroarkite", "Shedinjanite", "Ariadosite"
        ],
        "Mega Stone Loot Table B": [
            "Steelixite", "Metagrossite", "Aggronite", "Mawilite", "Aerodactylite", "Cameruptite",
            "Lucarionite", "Blazikenite", "Houndoominite", "Absolite", "Galladeite", "Medichamite",
            "Audinite"
        ],
        "Mega List C": [
            "Charizardite X", "Charizardite Y", "Salamencite", "Garchompite", "Tyranitarite",
            "Kangaskhanite", "Altarianite", "Ampharosite", "Gengarite", "Banettite", "Sablenite",
            "Aegislashite"
        ],
        "Mega Stone": ["Gyaradosite", "Blastoisite", "Sharpedonite", "Marshtompite"],
        "Fossil (Fossil Table)": [
            "Root Fossil", "Dome Fossil", "Helix Fossil", "Claw Fossil", "Drake Fossil",
            "Plume Fossil", "Jaw Fossil", "Skull Fossil", "Dino Fossil", "Bird Fossil",
            "Cover Fossil", "Sail Fossil", "Armor Fossil", "Fish Fossil", "Old Amber",
            "Evolution Fossil"
        ],
        "Evolution Item Loot Table A": [
            "Thunder Stone", "Ice Stone", "Dusk Stone", "Sun Stone", "Shiny Stone", "Fire Stone",
            "Leaf Stone", "Dawn Stone", "Moon Stone", "Mantis Claw"
        ],
        "Evolution Item Wheel": [
            ["Deep Sea Scale", "Deep Sea Tooth", "Dragon Scale", "Dragon Tooth", "Dubious Disc"],
            ["Electirizer", "King’s Rock", "Magmarizer", "Metal Coat", "Oval Stone"],
            ["Prism Scale", "Protector", "Black Sludge", "Razor Claw", "Razor Fang"],
            ["Gimmighoul Coin", "Reaper Cloth", "Sachet", "Upgrade", "Whipped Cream"],
            ["Sweet", "Black Belt", "Soft Sand", "Auspicious Armour", "Malicious Armour"],
            ["Rainbow Feather", "Black Augurite", "Chipped Pot", "Cracked Pot", "Galarica Cuff"],
            ["Galarica Wreath", "Masterpiece Teacup", "Metal Alloy", "Peat Block", "Sweet Apple"],
            ["Syrupy Apple", "Tart Apple", "Unremarkable Teacup", "Scroll of Darkness", "Scroll of Waters"]
        ],
        "Common Fishing Encounter": [
            "Magikarp", "Magikarp", "Magikarp", "Magikarp", "Magikarp",
            "Tentacool", "Tentacool", "Tentacool", "Tentacool", "Tentacool",
            "Basculin", "Basculin", "Basculin", "Feebas", "Feebas"
        ],
        "Rare Fishing Encounter": [
            "Finneon", "Chinchou", "Corphish", "Spheal", "Mareanie",
            "Buizel", "Frillish", "Tympole"
        ],
        "Legendary Fishing Encounter": [
            "Gyarados", "Gyarados", "Gyarados", "Gyarados", "Gyarados",
            "Lapras", "Lapras", "Lapras", "Lapras", "Dratini"
        ],
    }

    if name == "Evolution Item Wheel":
        group_num = random.randint(1, 8)
        group_items = tables["Evolution Item Wheel"][group_num - 1]
        return f"Evolution Wheel - Group {group_num}:\n" + "\n".join(f"• {item}" for item in group_items)

    if name in tables:
        return f"{name} result: {random.choice(tables[name])}"

    return name

# Loot Tables
locations = {
    1: [  # Werdun Hive's Burrows
        (1, 10, "You trip over a web, alerting the cave’s bugs to your presence, you flee before they have a chance to surround you."),
        (11, 40, "2x Pokéballs"),
        (41, 60, "2x Potions"),
        (61, 80, "1x Dusk Ball"),
        (81, 90, "Evolution Item Loot Table A"),
        (91, 100, "Mega Stone Loot Table A"),
    ],
    2: [  # Hinterland’s Mines
        (1, 25, "You get caught in an Onyx’s burrowing frenzy and are forced to flee before it caves in."),
        (26, 45, "2x Pokéballs"),
        (46, 65, "1x Revive"),
        (66, 75, "1x Quick Ball"),
        (76, 80, "1x Great Ball"),
        (81, 90, "Fossil (Fossil Table)"),
        (91, 100, "Mega Stone Loot Table B"),
    ],
    3: [  # Hot Chamber’s Crystal Caverns
        (1, 60, "You get confronted by a raging Dragon Pokémon and are forced to flee."),
        (61, 70, "1x Ultra Ball"),
        (71, 80, "1x Blank TM"),
        (81, 85, "Dragon Scale"),
        (86, 90, "Dragon Tooth"),
        (91, 100, "Mega List C"),
    ],
    4: [  # Underworld Fishing
        (1, 20, "A figure from under the water snatches your lure away."),
        (21, 40, "2x Lure Ball"),
        (41, 60, "2x Dive Ball"),
        (61, 75, "Treasure Chest with 1000₱"),
        (76, 80, "Water Stone"),
        (81, 90, "Common Fishing Encounter"),
        (91, 100, "Mega Stone"),
        (101, 110, "Rare Fishing Encounter"),
        (111, 120, "Legendary Fishing Encounter"),
    ],
    5: [  # Utopia Carnival Games
        (1, 40, "You’ve fallen for the scam. Unlucky."),
        (41, 60, "500₱"),
        (61, 75, "1x Ultra Ball"),
        (76, 80, "Blank TM"),
        (81, 98, "Evolution Item Wheel"),
        (99, 100, "Shiny Pokémon Egg"),
    ],
    6: [  # The Dojo
        (0, 70, "Nothing"),
        (71, 75, "Veil Style (Ping Professor)"),
        (76, 80, "Ruin Style (Ping Professor)"),
        (81, 85, "Divine Style (Ping Professor)"),
        (86, 90, "Wrath Style (Ping Professor)"),
        (91, 95, "Arcana Style (Ping Professor)"),
        (96, 100, "Shadow Style (Ping Professor)"),
    ],
}

location_names = {
    1: "Werdun Hives",
    2: "Hinterland Mines",
    3: "Hot Chambers",
    4: "Underworld Fishing",
    5: "Carnival Games",
    6: "The Dojo"
}

def find_overlapping_groups(ranges, low, high, location, natural_roll):
    overlapping = []
    for (start, end, name) in ranges:
        print(f"[DEBUG] Checking {start}-{end} ({name}) against range {low}-{high}")
        if location == 5 and name == "Shiny Pokémon Egg":
            if natural_roll in [99, 100]:
                overlapping.append(name)
            continue
        if not (end < low or start > high):
            overlapping.append(name)
    return overlapping

@bot.command(name='forage')
async def forage(ctx, location: int = None, modifier: int = None):
    if location is None or modifier is None:
        menu = "**Foraging Locations:**\n" + "\n".join(
            f"[{num}] {name}" for num, name in location_names.items()
        )
        await ctx.send(
            f"{menu}\n\nUsage: `!forage <location_number> <modifier>`\nExample: `!forage 2 5`"
        )
        return

    if location not in locations:
        await ctx.send("Invalid location. Please enter a number between 1 and 6.")
        return

    d100 = random.randint(1, 100)
    min_roll = max(1, d100 - modifier)
    max_roll = d100 + modifier  # Allow going beyond 100!
    

    groups = find_overlapping_groups(locations[location], min_roll, max_roll, location, d100)

    location_label = location_names.get(location, "Unknown Location")
    if groups:
        output = []
        for item in groups:
            result = roll_bonus(item)
            output.append(f"- {result}")

        response = (
            f"**Location:** {location_label}\n"
            f"**Roll:** {d100}\n"
            f"**Modified Range:** {min_roll} to {max_roll}\n"
            f"**Your roll could be:**\n" + "\n".join(output)
        )
    else:
        response = (
            f"**Location:** {location_label}\n"
            f"**Roll:** {d100}\n"
            f"**Modified Range:** {min_roll} to {max_roll}\n"
            "**Your roll is nothing! (probably an error!)**"
        )

    await ctx.send(response)

@bot.command(name='ping')
async def ping(ctx):
    await ctx.send("pong!")

PING_CHANNEL_ID = 1395390696361296043  # replace with your target channel ID

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    send_beep.start()
    keep_alive_ping.start()

@tasks.loop(minutes=12)
async def send_beep():
    channel = bot.get_channel(PING_CHANNEL_ID)
    if channel:
        await channel.send("beep")
    else:
        print("Channel not found, cannot send beep.")

@tasks.loop(minutes=5)
async def keep_alive_ping():
    url = "https://pkmnforager.onrender.com"  # Change this to your public URL if needed
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    print("Keep-alive ping success")
                else:
                    print(f"Keep-alive ping failed: {resp.status}")
    except Exception as e:
        print(f"Keep-alive ping error: {e}")

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Start the Flask thread
threading.Thread(target=run).start()

# Start the bot
bot.run(TOKEN)
