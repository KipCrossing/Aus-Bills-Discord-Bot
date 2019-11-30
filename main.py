import pandas as pd
import math

import asyncio
from discord.ext import commands
import discord
import os
# import ast

print("AusBills Discord Bot")

TOKEN = os.environ['AUS_BILLS_DISCORD_BOT_TOKEN']

client = commands.Bot(command_prefix='!')

# vars
server = None
LOWER_BILLS_CHANNEL_ID = None
UPPER_BILLS_CHANNEL_ID = None
ibdd_emojis = ['\u2611', '\u274E', '\U0001F48E', '\U0001F4CA']
BOT_ID = 647996922166247454
LOWER_HEADER = ',Short Title,Intro House,Passed House,Intro Senate,Passed Senate,Assent Date,Act No.'
UPPER_HEADER = ',Short Title,Intro Senate,Passed Senate,Intro House,Passed House,Assent Date,Act No.'

LOWER_CHANNEL_NAME = 'lower-house-bills'
UPPER_CHANNEL_NAME = 'upper-house-bills'
INTRO_HOUSE = "Intro House"
INTRO_SENATE = "Intro Senate"
DATA_DIR = 'data'
LOWER_FILE = "lower.csv"
UPPER_FILE = "upper.csv"
url = "https://www.aph.gov.au/Parliamentary_Business/Bills_Legislation/Bills_Lists/Details_page?blsId=legislation%2fbillslst%2fbillslst_c203aa1c-1876-41a8-bc76-1de328bdb726"

new_table_lower = None
old_table_lower = None
new_table_upper = None
old_table_upper = None


@client.event
async def on_ready():
    global server
    print('Bot ready!')
    await data_setup()
    await client.wait_until_ready()
    if len(client.guilds) == 1:
        server = client.guilds[0]  # gets first in list as there should be only one server
        await discord_server_setup(server)
        await post_new_lower_bill()
        await post_new_upper_bill()
        await remove_completed_lower()
        await remove_completed_upper()
        await asyncio.sleep(60)
        await data_save()
    elif len(client.guilds) > 1:
        print("Bot connected to multiple servers \nOnly use one...")
    else:
        print("No server connected...")
    await client.close()


async def data_setup():
    # Setup the discord server with channels etc.
    global new_table_lower
    global old_table_lower
    global new_table_upper
    global old_table_upper
    if LOWER_FILE not in os.listdir(DATA_DIR):
        f = open(DATA_DIR + '/' + LOWER_FILE, 'w')
        f.write(LOWER_HEADER)
        f.close()
    if UPPER_FILE not in os.listdir(DATA_DIR):
        f = open(DATA_DIR + '/' + UPPER_FILE, 'w')
        f.write(UPPER_HEADER)
        f.close()
    try:
        new_table_lower = pd.read_html(url, header=0)[0]
        new_table_upper = pd.read_html(url, header=0)[1]
    except ImportError as e:
        print('Error: Link may be broken, please check')
        print(e)
    old_table_lower = pd.read_csv(DATA_DIR + '/' + LOWER_FILE)
    old_table_upper = pd.read_csv(DATA_DIR + '/' + UPPER_FILE)


async def data_save():
    global new_table_lower
    global new_table_upper
    if (type(pd.DataFrame()) == type(new_table_lower)):
        new_table_upper.to_csv(DATA_DIR + '/' + LOWER_FILE)
    if (type(pd.DataFrame()) == type(new_table_upper)):
        new_table_upper.to_csv(DATA_DIR + '/' + UPPER_FILE)


async def discord_server_setup(server):
    global LOWER_BILLS_CHANNEL_ID
    global UPPER_BILLS_CHANNEL_ID
    lower_channel_exists = False
    upper_channel_exists = False
    for channel in server.channels:
        if channel.name == LOWER_CHANNEL_NAME:
            lower_channel = channel
            LOWER_BILLS_CHANNEL_ID = channel.id
            lower_channel_exists = True
        if channel.name == UPPER_CHANNEL_NAME:
            upper_channel = channel
            UPPER_BILLS_CHANNEL_ID = channel.id
            upper_channel_exists = True
    if not lower_channel_exists:
        lower_channel = await server.create_text_channel(LOWER_CHANNEL_NAME)
        LOWER_BILLS_CHANNEL_ID = lower_channel.id
    if not upper_channel_exists:
        upper_channel = await server.create_text_channel(UPPER_CHANNEL_NAME)
        UPPER_BILLS_CHANNEL_ID = upper_channel.id


async def clear_channel(channel):
    messages = []
    async for message in channel.history(limit=100):
        print(message.embeds[0].title)
        messages.append(message)
    await channel.delete_messages(messages)


# @client.event
# async def on_message(message):
#     if message.author.id == BOT_ID and (message.channel.id == LOWER_BILLS_CHANNEL_ID or message.channel.id == UPPER_BILLS_CHANNEL_ID):
#         for emoji in ibdd_emojis[:2]:
#             await message.add_reaction(emoji)


async def post_new_upper_bill():
    await client.wait_until_ready()
    channel = client.get_channel(UPPER_BILLS_CHANNEL_ID)
    await post_new_bill(channel, old_table_upper, new_table_upper, INTRO_SENATE)


async def post_new_lower_bill():
    await client.wait_until_ready()
    channel = client.get_channel(LOWER_BILLS_CHANNEL_ID)
    await post_new_bill(channel, old_table_lower, new_table_lower, INTRO_HOUSE)


def check_not_passed(table, row):
    ps = list(table["Passed Senate"])[row]
    ph = list(table["Passed House"])[row]
    passed_senate = False
    passed_house = False
    if isinstance(ps, float):
        if math.isnan(ps):
            passed_senate = True
    if isinstance(ph, float):
        if math.isnan(ph):
            passed_house = True
    passed = passed_house or passed_senate
    return(passed)


async def post_new_bill(channel, old_table, new_table, date_header):
    if (type(pd.DataFrame()) == type(new_table)):
        for i in range(len(list(new_table["Short Title"]))):
            tit = list(new_table["Short Title"])[i]
            date = list(new_table[date_header])[i]
            if tit not in list(old_table["Short Title"]) and check_not_passed(new_table, i):
                print(tit, date)
                Embed = discord.Embed(title=tit,
                                      description="Introduced on {}".format(date),
                                      colour=discord.Colour.purple())
                Embed.add_field(
                    name="Bill details:", value="[Click here]({})".format(url))
                message = await channel.send(embed=Embed)
                for emoji in ibdd_emojis[:2]:
                    await message.add_reaction(emoji)


async def remove_completed_lower():
    await client.wait_until_ready()
    channel = client.get_channel(LOWER_BILLS_CHANNEL_ID)
    messages = []
    if (type(pd.DataFrame()) == type(new_table_lower)):
        async for message in channel.history(limit=100):
            for i in range(len(list(new_table_lower["Short Title"]))):
                tit = list(new_table_lower["Short Title"])[i]

                if tit == message.embeds[0].title:
                    if not check_not_passed(new_table_lower, i):
                        print("Delete:", message.embeds[0].title)
                        messages.append(message)
        await channel.delete_messages(messages)


async def remove_completed_upper():
    await client.wait_until_ready()
    channel = client.get_channel(UPPER_BILLS_CHANNEL_ID)
    messages = []
    if (type(pd.DataFrame()) == type(new_table_upper)):
        async for message in channel.history(limit=100):
            for i in range(len(list(new_table_upper["Short Title"]))):
                tit = list(new_table_upper["Short Title"])[i]
                if tit == message.embeds[0].title:
                    if not check_not_passed(new_table_upper, i):
                        print("Delete:", message.embeds[0].title)
                        messages.append(message)
        await channel.delete_messages(messages)


try:
    client.run(TOKEN)
finally:
    asyncio.new_event_loop().run_until_complete(client.close())
