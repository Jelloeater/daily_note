#!/usr/bin/env -S uv run --quiet
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "requests",
#     "typer",
# ]
# ///

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
import typer
import requests
import datetime
from pathlib import Path
import os
MOODS = {
    1:"Miserable",
    2:"Sad",
    3:"Okay",
    4:"Happy",
    5:"Joyful"
}
ENERGY = {
    1:"Exhausted",
    2:"Tired",
    3:"Okay",
    4:"Active",
    5:"Buzzing"
}


def get_wttr_json():
    return requests.get('http://wttr.in?format=j1').json()

# Mood selector
def select_mood():
    return int(typer.prompt(f"Mood choice {MOODS}"))

# Mood selector
def select_energy():
    return int(typer.prompt(f"Energy {ENERGY}: "))


def open_file(filepath):
    import platform
    import subprocess
    system = platform.system()
    if system == "Darwin":  # macOS
        subprocess.run(["open", str(filepath)])
    elif system == "Linux":
        subprocess.run(["xdg-open", str(filepath)])
    elif system == "Windows":
        subprocess.run(["start", str(filepath)], shell=True)
    else:
        logging.warning(f"Cannot auto-open file on unsupported OS: {system}")


def main(
    title: str = typer.Argument(help="Title",default=None),
    mood: int = typer.Argument(help="Mood 1-5", default=None),
    energy: int = typer.Argument(help="Energy 1-5", default=None),
    location_title: str = typer.Argument(help="Location Title", default=None)
):
    if title == None:
        title = typer.prompt("Title of the diary entry")
    if mood == None:
        mood = select_mood()
    if energy == None:
        energy = select_energy()
    if location_title == None:
        location_title = typer.prompt("Location Title")
    # title = input("Title: ")
    date = datetime.date.today().isoformat()
    filename = datetime.date.today().isoformat()
    wttr_data = get_wttr_json()
    city = wttr_data['nearest_area'][0]['areaName'][0]['value']
    long = wttr_data['nearest_area'][0]['longitude']
    lat = wttr_data['nearest_area'][0]['latitude']
    temp_c = wttr_data['current_condition'][0]['temp_C']
    location = f"{lat},{long}"
    weather = wttr_data['current_condition'][0]['weatherDesc'][0]['value']
    forecast = wttr_data['weather'][0]['hourly'][0]['weatherDesc'][0]['value']
    filename = Path.cwd() / "Daily_Notes" / f"{date}.md"
    filename.parent.mkdir(exist_ok=True)

    # Diary entry START
    entry_body = f"""
---
title: {title}
date: {date}
tags: []
mood: {mood}
mood_desc: {MOODS.get(mood)}
energy: {energy}
energy_desc: {ENERGY.get(energy)}
location: {location}
location_title: {location_title}
city: {city}
weather: {weather}
temp_c: {temp_c}
forecast: {forecast}
filename: {date}.md
---

# {title}

---------------------------------------------------------------

"""
    # Diary entry END

    # Add a check and confirmation if the file is already created
    if filename.exists():
        logging.warning(f"File {filename} already exists.")
        confirm = typer.confirm("File already exists. Do you want to overwrite it?")
        if not confirm:
            logging.info("Exiting without changes.")
            open_file(filename)
            raise typer.Abort()
        else:
            logging.info(f"Overwriting existing diary entry: {filename}")
            filename.write_text(entry_body)
    else:
        logging.info(f"Creating new diary entry: {filename}")
        filename.write_text(entry_body)

    print(f"Diary entry created: \n{filename}")
    open_file(filename)
    exit(0)

if __name__ == "__main__":
    typer.run(main)
