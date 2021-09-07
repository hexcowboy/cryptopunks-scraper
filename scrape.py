import json
import os
import signal
import sys
from pathlib import Path

import click
import requests
from rich.progress import Progress

API_URL: str = "https://wrappedpunks.com:3000/api/punks/"
PUNK_IDS: range = range(10_000)


def signal_handler(signal, frame):
    sys.stdout.write("\b\b\r")
    print("Gracefully stopping")
    sys.exit(0)


@click.command()
@click.option(
    "-o",
    "--output",
    "output_file_path",
    default=None,
    help="Name of file to send output to (json)",
)
def main(output_file_path: str = None) -> dict:
    # Catch CTRL-C
    signal.signal(signal.SIGINT, signal_handler)

    punks: dict = dict()

    # Load from the output file to resume
    if output_file_path is not None:
        output_file = Path(output_file_path)
        output_file.touch(exist_ok=True)
        with open(output_file) as file:
            if os.path.getsize(output_file):
                punks = json.load(file)

    with Progress() as progress:
        task = progress.add_task("Scraping Punks", total=len(PUNK_IDS))

        # for punk_id in PUNK_IDS:
        for punk_id in PUNK_IDS:
            if str(punk_id) in punks:
                continue

            response = requests.get(API_URL + str(punk_id))
            raw_attributes = json.loads(response.text)
            punks[punk_id] = dict()
            punk_type: str = raw_attributes["data"]["attribute"]["Type"]

            if punk_type in ["Male", "Female"]:
                punk_skin = raw_attributes["data"]["attribute"]["Skin"]
                if "Albino" in punk_skin:
                    punks[punk_id]["species"] = "Lighter Human"
                if "Dark" in punk_skin:
                    punks[punk_id]["species"] = "Darker Human"
                if "Light" in punk_skin:
                    punks[punk_id]["species"] = "Light Human"
                if "Mid" in punk_skin:
                    punks[punk_id]["species"] = "Dark Human"
                if punk_type == "Male":
                    punks[punk_id]["size"] = "Large"
                elif punk_type == "Female":
                    punks[punk_id]["size"] = "Petite"
            else:
                punks[punk_id]["species"] = str(punk_type).capitalize()
                punks[punk_id]["size"] = "Large"

            punks[punk_id]["attributes"] = list()
            for attribute in range(int(raw_attributes["data"]["attribute"]["Slots"])):
                punks[punk_id]["attributes"].append(
                    str(raw_attributes["data"]["attribute"][f"Att{str(attribute + 1)}"])
                )

            if output_file_path is not None:
                with open(output_file_path, "w") as file:
                    json.dump(punks, file)

            progress.update(
                task, completed=punk_id, description=f"Scraping Punk #{punk_id}"
            )

    return punks


if __name__ == "__main__":
    all_punks = main()
    print(all_punks)
