import discord
import asyncio
import json
import datetime
from scraper.init_driver import init_driver
from scraper.scrape import scrape
from scraper.items_filter import item_filter
from scraper.item_enumerator import enumerate_items
from scraper.log_data import log_data

with open('bot_settings.json', 'r', encoding='utf-8') as f:
    bot_settings = json.load(f)
    TOKEN = bot_settings["discord_token"].strip()
    CHANNEL_ID = int(bot_settings["channel_id"])

with open('settings.json', 'r', encoding='utf-8') as f:
    settings = json.load(f)

intents = discord.Intents.default()
client = discord.Client(intents=intents)

driver = init_driver()#BEWARE runs constantly (-300MB of RAM)!!!

async def send_to_discord(car):
    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        print("Could not find the channel.")
        return

    manufacturer = car["title"].split()[0]
    if car["data"]["oldtimer"]:
        embed = discord.Embed(
            title=car["title"],
            url=car["link"],
            color=discord.Color.gold()
        )
    elif (car["price"] <= 1000 and manufacturer in settings["whitelist"]) or (car["price"] <= 500 and manufacturer not in settings["blacklist"]):
        embed = discord.Embed(
            title=car["title"],
            url=car["link"],
            color=discord.Color.green()
        )
    else:
        embed = discord.Embed(
            title=car["title"],
            url=car["link"],
            color=discord.Color.blue()
        )

    embed.set_image(url=car["img_link"])
    if car["data"]["oldtimer"]:
        embed.description = (
            f'**{car["price"]} €, {car["data"]["mileage"]} km**\n'
            f'_{car["data"]["1.reg"]}, {car["data"]["engine"]}_\n**OLDTIMER**'
        )
    else:
        embed.description = (
            f'**{car["price"]} €, {car["data"]["mileage"]} km**\n'
            f'_{car["data"]["1.reg"]}, {car["data"]["engine"]}_'
        )

    await channel.send(embed=embed)


async def run_every_5_minutes():
    await client.wait_until_ready()
    while not client.is_closed():
        now = datetime.datetime.now()
        #print(f"curr time: {now} (hour: {now.hour}, minute: {now.minute})")

        if bot_settings["start_hour"] <= now.hour < bot_settings["end_hour"]:
            seconds_until_next_run = (5 - (now.minute % 3)) * 60 - now.second
            if seconds_until_next_run <= 0:
                seconds_until_next_run += 5 * 60

            print(f"sleeping for {seconds_until_next_run} seconds")
            await asyncio.sleep(seconds_until_next_run)

            try:
                print(f"[{datetime.datetime.now()}] Scraping started.")
                scraped = await asyncio.to_thread(scrape, driver)
                data = enumerate_items(item_filter(scraped))
                log_data(data)
                for car in data:
                    await send_to_discord(car)
                print(f"[{datetime.datetime.now()}] Cycle complete.")
            except Exception as e:
                print("Error in scraping cycle:", e)
        else:
            #sleep at off hours
            await asyncio.sleep(60)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    client.loop.create_task(run_every_5_minutes())

client.run(TOKEN)
