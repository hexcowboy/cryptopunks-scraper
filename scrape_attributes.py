import asyncio
import aiohttp
import re
import json
from rich import print

url: str = "https://www.larvalabs.com/cryptopunks/details/{id}"
punks_range: range = range(1000)
with open("punks.json") as punks_json_file:
    punks: dict = json.load(punks_json_file)

id_regex = re.compile(
    '<h1 style="margin-top: 0px; margin-bottom: 5px;">CryptoPunk ([0-9].*)</h1>'
)
species_regex = re.compile(
    'One of <b>[0-9]*</b> <a href="/cryptopunks/search\?query=.*">(.*)</a> punks\.'
)
attrs_regex = re.compile('<a href="/cryptopunks/search\?query=%22.*%22">(.*)</a>')


def request_all_punks(session):
    requests = []
    for punk in punks_range:
        if str(punk) in punks:
            # Punk is already saved in the JSON file
            continue
        requests.append(
            asyncio.create_task(session.get(url.format(id=punk), ssl=False))
        )
    return requests


async def scrape_punks():
    async with aiohttp.ClientSession() as session:
        punk_request = request_all_punks(session)
        punk_requests = await asyncio.gather(*punk_request)
        for request in punk_requests:
            response_text = await request.text()

            # Get the punk ID from regex searching the page
            try:
                punk = int(id_regex.findall(response_text)[0])
            except IndexError:
                print("Too many requests... Use another connection")
                break
            punks[punk] = {}

            # Get the species from regex searching the page
            species = species_regex.findall(response_text)[0]
            punks[punk]["species"] = species

            # Get all punk attributes from regex searching the page
            punks[punk]["attributes"] = []
            attrs = attrs_regex.findall(response_text)
            for attr in attrs:
                punks[punk]["attributes"].append(attr)


asyncio.run(scrape_punks())

with open("punks.json", "w") as file:
    json.dump(punks, file)
    print(f"Saved all punks to {file.name}")
