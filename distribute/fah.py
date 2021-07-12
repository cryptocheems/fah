# This is the file that should be run

import json
from math import log
from requests import get
from csv import DictWriter
from datetime import date
from constants import *
from blockchain import format_address
from drive import Drive

# Adjust points https://www.desmos.com/calculator/c9q5f46aea
def adjust(score):
    return (score, score if score < 1_000_000 else 1_800_000 * log(score + 1_000_000) - 25_115_584)


def main():
    print("Querying data...")

    with open(PREVIOUS_PATH, "r") as f:
        oldScores: dict = json.load(f)
    with open(START_PATH, "r") as f:
        start = f.read()

    scores: list = get(f"https://api.foldingathome.org/team/{TEAM_ID}/members").json()

    print("Calculating rewards...")

    validScores = {}

    # Skip the first which is ['name', 'id', 'rank', 'score', 'wus']
    for user in scores[1:]:
        address = format_address(user[0])
        # Ignore invalid names
        if address:
            validScores[address] = user[3]  # credit

    if validScores == oldScores:
        raise Exception("Valid scores identical to previous")

    with open(PREVIOUS_PATH, "w") as f:
        json.dump(validScores, f, indent=4)

    weekScores = {
        k: adjust(v - oldScores.get(k, 0))
        for (k, v) in validScores.items()
        if v > oldScores.get(k, 0)
    }
    totalPoints = sum([tup[1] for tup in weekScores.values()])
    totalMin = MIN_CHEEMS * len(weekScores)
    totalAmount = totalPoints * RATE + totalMin

    cheemsAmounts = [
        {
            "address": user[0],
            "points": user[1][0],
            "adjusted points": user[1][1],
            "cheems": (
                user[1][1] / totalPoints * (TOTAL_CHEEMS - totalMin)
                if totalAmount > TOTAL_CHEEMS
                else user[1][1] * RATE
            )
            + MIN_CHEEMS,
        }
        for user in weekScores.items()
    ]

    with open(CSV_PATH, "w", encoding="utf8", newline="") as f:
        dict_writer = DictWriter(f, cheemsAmounts[0].keys())
        dict_writer.writeheader()
        dict_writer.writerows(cheemsAmounts)

    print("Backing up...")

    today = date.today().strftime("%Y%m%d")
    drive = Drive()
    folder = drive.create_folder(start + "-" + today)
    drive.upload_file("payout.csv", DATA_PATH, folder)
    drive.upload_file("previous.json", DATA_PATH, folder)
    with open(START_PATH, "w", encoding="utf8") as f:
        f.write(today)


if __name__ == "__main__":
    main()
    print("Finished successfully")
