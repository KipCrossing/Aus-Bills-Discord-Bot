import pandas as pd


import asyncio
from discord.ext import commands
import discord
import os
# import ast

print("AusBills Discord Bot")

TOKEN = os.environ['AUS_BILLS_DISCORD_BOT_TOKEN']

client = commands.Bot(command_prefix='!')

# vars
SERVER_ID = 551999201714634752
LOWER_BILLS_CHANNEL_ID = 648007317715025932
UPPER_BILLS_CHANNEL_ID = 648840494008369163
ibdd_emojis = ['\u2611', '\u274E', '\U0001F48E', '\U0001F4CA']
BOT_ID = 647996922166247454


@client.event
async def on_ready():
    print('Bot ready!')
    await client.wait_until_ready()
    await post_new_lower_bill()
    await post_new_upper_bill()
    await asyncio.sleep(20)
    await client.close()


@client.event
async def on_message(message):
    if message.author.id == BOT_ID and (message.channel.id == LOWER_BILLS_CHANNEL_ID or message.channel.id == UPPER_BILLS_CHANNEL_ID):
        for emoji in ibdd_emojis[:2]:
            await message.add_reaction(emoji)


# This URL will work on a local Jupyter Notebook.
# url="https://en.wikipedia.org/wiki/List_of_Academy_Award-winning_films"

# Here we'll use a local copy instead.
# Use the local copy instead.
url = "https://www.aph.gov.au/Parliamentary_Business/Bills_Legislation/Bills_Lists/Details_page?blsId=legislation%2fbillslst%2fbillslst_c203aa1c-1876-41a8-bc76-1de328bdb726"
new_table_lower = pd.read_html(url, header=0)[0]
old_table_lower = pd.read_csv("lower.csv")
new_table_upper = pd.read_html(url, header=0)[1]
old_table_upper = pd.read_csv("upper.csv")


async def post_new_upper_bill():
    await client.wait_until_ready()
    server = client.get_guild(id=SERVER_ID)
    channel = client.get_channel(UPPER_BILLS_CHANNEL_ID)
    await post_new_bill(channel, old_table_upper, new_table_upper)


async def post_new_lower_bill():
    await client.wait_until_ready()
    server = client.get_guild(id=SERVER_ID)
    channel = client.get_channel(LOWER_BILLS_CHANNEL_ID)
    await post_new_bill(channel, old_table_lower, new_table_lower)


async def post_new_bill(channel, old_table, new_table):
    for i in range(len(list(new_table["Short Title"]))):
        tit = list(new_table["Short Title"])[i]
        date = list(new_table["Intro House"])[i]
        if tit not in list(old_table["Short Title"]):
            print(tit, date)
            Embed = discord.Embed(title=tit,
                                  description="Introduced on {}".format(date),
                                  colour=discord.Colour.purple())
            Embed.add_field(
                name="Bill details:", value="[Click here](https://www.aph.gov.au/Parliamentary_Business/Bills_Legislation/Bills_Lists/Details_page?blsId=legislation%2fbillslst%2fbillslst_c203aa1c-1876-41a8-bc76-1de328bdb726)")
            await channel.send(embed=Embed)


new_table_lower.to_csv("lower.csv")
new_table_upper.to_csv("upper.csv")


try:
    client.run(TOKEN)
finally:
    asyncio.new_event_loop().run_until_complete(client.close())
