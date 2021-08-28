import requests
import json
import re
from rich import print
from rich.progress import Progress
from signal import signal, SIGINT
from sys import exit

url: str = "https://www.larvalabs.com/cryptopunks/details/{id}"
punks_range: range = range(10_000)
with open("punks.json") as punks_json_file:
    punks: dict = json.load(punks_json_file)

id_regex = re.compile(
    '<h1 style="margin-top: 0px; margin-bottom: 5px;">CryptoPunk ([0-9].*)</h1>'
)
species_regex = re.compile(
    'One of <b>[0-9]*</b> <a href="/cryptopunks/search\?query=.*">(.*)</a> punks\.'
)
attrs_regex = re.compile('<a href="/cryptopunks/search\?query=%22.*%22">(.*)</a>')


def handler(signal_received, frame):
    print("Exiting gracefully")
    with open("punks.json", "w") as file:
        json.dump(punks, file)
        print(f"Saved all punks to {file.name}")
    exit(0)


def scrape_punks():
    with Progress() as progress:
        task = progress.add_task("Scraping Punks", total=len(punks_range))
        for punk in punks_range:
            if str(punk) in punks:
                # Punk is already saved in the JSON file
                continue

            # Get the punk ID from regex searching the page
            try:
                response = requests.get(url.format(id=punk))
                response_text = response.text
                punk = int(id_regex.findall(response_text)[0])
            except:
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

            progress.update(task, completed=punk, description=f"Scraping Punk #{punk}")

        handler(SIGINT, scrape_punks)


if __name__ == "__main__":
    # Tell Python to run the handler() function when SIGINT is recieved
    signal(SIGINT, handler)

    print("Running. Press CTRL-C to gracefully exit.")
    scrape_punks()
