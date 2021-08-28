# CryptoPunks Scraper

This project will scrape the LarvaLabs website to retrieve all CryptoPunks species and attributes.

**The completed scrape is found in [`punks.json`](./punks.json)**.

The LarvaLabs site is protected by an IPS that will detect when too many requests are made. This means that async requests are not necessary since the IPS will just block your IP after about 70 simultaneous requests. Instead, this project just scrapes one punk at a time and can take **over an hour to complete**.

## Requirements

- Python 3.7+

## Running

Start a Python virtual environment or use these commands:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install the project dependencies

```bash
pip install -r requirements.txt
```

Run the script

```bash
python scrape.py
```
