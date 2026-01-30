import json
from pathlib import Path

from game.combat.Attack import Attack


# Load attack data from file

def load_attacks():
    attacks_path = Path(__file__).resolve().parents[2] / "attacks.json"
    with attacks_path.open(encoding="utf-8") as attacks_file:
        data = json.load(attacks_file)
    for key, value in data.items():
        # Turn values in the dictionary into constructor parameters of the Attack class
        data[key] = Attack(**value)
    return data


ATTACKS = load_attacks()
