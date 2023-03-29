from dataclasses import dataclass
from enum import Enum
import json
from fantasynames import dwarf

known_enemies = json.load(open("enemies.json", "r"))

class Advantage(Enum):
    NONE = 0
    ADVANTAGE = 1
    DISADVANTAGE = -1

# dnd_battle_sim.py
@dataclass
class Enemy:
    max_hp: int
    health: int
    advantage: Advantage
    name: str
    race: str
    initiative: int
    armor_class: int

    @staticmethod
    def from_existing(race: str, initiative: int, name=None):
        enemy_data = next(filter(lambda x: x["name"].lower() == race.lower(), known_enemies))
        return Enemy(
            race=race,
            health=int(enemy_data["Hit Points"].split(" ")[0]),
            armor_class=int(enemy_data["Armor Class"].split(" ")[0]),
            initiative=initiative,
            name=name
        )


    def __init__(self, health: int, armor_class: int, initiative: int, race: str, name: str=None):
        self.health = health
        self.max_hp = health
        self.race = race
        self.initiative = initiative
        self.armor_class = armor_class
        self.name = name or dwarf().split(" ")[0]

    def __repr__(self):
        return f"{self.name} ({self.race})"
    
    @property
    def fuzzy_health(self):
        "Returns health out of 5 as a string of hearts."
        if self.health <= 0:
            return "💀"
        return "❤️" * (self.health // (self.max_hp // 5)) + "🖤" * (5 - (self.health // (self.max_hp // 5)))

@dataclass
class Player:
    name: str
    initiative: int
    # only exists to keep track of initiative
    def __init__(self, name: str, initiative: int):
        self.name = name
        self.initiative = initiative
    

if __name__ == "__main__":
    bob = Enemy.from_existing("Orc", 10)
    print(bob)
    bob.health = 8
    print(bob)
    print(bob.fuzzy_health())
    bob.health = 0
    print(bob.fuzzy_health())
