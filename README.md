# Aus Bills Discord Bot

This is a _proof of concept_ for mirroring current bills in federal parliament.

Creation of a bot to scrape the [Australian Federal Parliament](https://www.aph.gov.au/Parliamentary_Business/Bills_Legislation/Bills_Lists/Details_page?blsId=legislation%2fbillslst%2fbillslst_c203aa1c-1876-41a8-bc76-1de328bdb726) website and send to separate Senate and House of Representatives Discord channels as embeds that can be called throughout Discord server.

The bot posts a new embed if the there is a new bill in either table. If the Bill has finished, the bot deletes the bill.

Bills to be displayed with _Bill Short Title_, _Date Issued_ and a link to Australian Federal Parliament Bill Summary page ![Bill Example](/images/Aus_Bills_example.png)

## Getting started

### Make a bot

Create a discord bot [here](https://discordapp.com/developers/applications/) and get a token TOKEN. _Make sure you get the bot TOKEN and not the app TOKEN_. Invite your bot to a server and let it have Admin permissions.

The save the TOKEN as `AUS_BILLS_DISCORD_BOT_TOKEN='your_secrete_token'` with your environmental variables.

### Install

```
python3 -m pip install -U discord.py
python3 -m pip install -U pandas
git clone https://github.com/KipCrossing/Aus-Bills-Discord-Bot
cd Flux-Discord-Bot
python3 main.py
```
