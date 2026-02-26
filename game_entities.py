"""CSC111 Project 1: Text Adventure Game - Game Entities

Instructions (READ THIS FIRST!)
===============================

This Python module contains the entity classes for Project 1, to be imported and used by
the `adventure` module.
Please consult the project handout for instructions and details.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2026 CSC111 Teaching Team
"""
from __future__ import annotations
from dataclasses import dataclass
from math import ceil


@dataclass
class Location:
    """A location in our text adventure game world.

    Instance Attributes:
        - id_num: An integer representing the location's unique ID.
        - brief_description: A short description of the location.
        - long_description: A detailed description of the location.
        - available_commands: A dictionary mapping valid command strings (e.g., "go north") to the ID of the destination location.
        - items: A list of names of items present in this location.
        - enemies: A list of names of enemies present in this location.
        - visited: A boolean indicating whether the player has visited this location.

    Representation Invariants:
        - self.id_num >= -1
        - self.brief_description != ""
        - self.long_description != ""
    """

    # This is just a suggested starter class for Location.
    # You may change/add parameters and the data available for each Location object as you see fit.
    #
    # The only thing you must NOT change is the name of this class: Location.
    # All locations in your game MUST be represented as an instance of this class.

    id_num: int
    brief_description: str
    long_description: str
    available_commands: dict[str, int]
    items: list[str]
    enemies: list[str]
    visited: bool = False


@dataclass
class Item:
    """An item in our text adventure game world.

    Instance Attributes:
        - name: The name of the item.
        - description: The description of the item.
        - start_position: The location ID where the item is initially found.
        - target_position: The location ID where the item should be deposited.
        - target_points: The points awarded for depositing the item at the target position.
        - weight: The weight of the item.
        - combat_use: An integer representing the item's use in combat (0: unusable, 1: heal, 2: damage).
        - strength: The amount of health healed or damage dealt.

    Representation Invariants:
        - self.name != ""
        - self.weight >= 0.0
        - self.combat_use in {0, 1, 2}
        - self.strength >= 0
    """

    name: str
    description: str
    start_position: int
    target_position: int
    target_points: int
    weight: float
    combat_use: int
    strength: int


@dataclass
class Inventory:
    """A system for managing a collection of items within a restricted weight capacity.

    Instance Attributes:
        - items: A list of Item objects currently held in this inventory.
        - weight_limit: The maximum allowable total weight capacity (must be positive).
        - current_weight: The total weight of all items currently stored.

    Representation Invariants:
        - self.weight_limit > 0
        - self.current_weight >= 0.0
        - self.current_weight <= self.weight_limit
        - # Precision issues aside, current_weight should match sum of item weights
        # - self.current_weight == sum(item.weight for item in self.items)
    """
    items: list[Item]
    weight_limit: int
    current_weight: float

    def __init__(self, items: list[Item] = [], weight_limit: int = 0, current_weight: float = 0.0) -> None:
        self.items = items
        self.weight_limit = weight_limit
        self.current_weight = current_weight

    def take_item(self, item: Item, current_location: Location) -> Location:
        """Add an item to the inventory.
        Returns the updated Location object for current location
        """
        if self.current_weight + item.weight <= self.weight_limit:
            self.items.append(item)
            self.current_weight += item.weight
            print(f"Added {item.name} to inventory.")
            current_location.items.remove(item.name)
            current_location.available_commands.pop(f"take {item.name}", 0)
        else:
            print(f"Your inventory is full. Drop an item to take {item.name}.")

        return current_location

    def drop_item(self, item: Item, current_location: Location) -> Location:
        """Drops an item from inventory
        Returns the updated locaiton object for current location
        """
        self.items.remove(item)
        current_location.available_commands[f"take {item.name}"] = current_location.id_num
        self.current_weight -= item.weight
        print(f"Dropped {item.name}.")
        current_location.items.append(item.name)
        return current_location


@dataclass
class Player:
    """A representation of a player character containing their personal inventory
    and status.

    Instance Attributes:
        - inventory: An Inventory object containing the items currently carried by the player.
        - speed: The speed of the player (affects step cost).
        - attack: The attack power of the player.
        - defense: The defense power of the player.
        - max_health: The maximum health of the player.
        - current_health: The current health of the player.
        - points: Available points for stat upgrades.

    Representation Invariants:
        - self.inventory is not None
        - self.current_health >= 0
        - self.current_health <= self.max_health
        - self.speed >= 0
        - self.attack >= 0
        - self.defense >= 0
        - self.points >= 0
    """

    inventory: Inventory

    # Combat Stats
    speed: int
    attack: int
    defense: int

    max_health: int
    current_health: int

    points: int = 10

    def __init__(self, inventory: Inventory, speed: int = 0, attack: int = 0, defense: int = 0, max_health: int = 10, current_health: int = 10, skip_stats_selection: bool = False) -> None:
        self.inventory = inventory
        self.max_health = max_health
        self.current_health = current_health

        self.speed = speed
        self.attack = attack
        self.defense = defense

        # Combat Stats Tuning
        if not skip_stats_selection:
            while self.points > 0:
                print(f"You have {self.points} points to spend on combat stats. Note no stat can be more than 5 points.")
                print(f"1. Speed: {self.speed}")
                print(f"2. Attack: {self.attack}")
                print(f"3. Defense: {self.defense}")
                choice = input("Enter your choice: ")
                self.add_points(int(choice))

    def add_points(self, stat: int) -> None:
        """Update the player's combat stats by spending available points.

        The player chooses a stat (1 for speed, 2 for attack, or 3 for defense)
        and specifies how many points to add. A stat cannot exceed 5 points
        total, and the player cannot spend more points than they have available.

        Preconditions:
            - stat in {1, 2, 3}
            - self._points >= 0
        """
        if not 1 <= stat <= 3:
            print("Invalid Choice")
            return

        curr_stat = [self.speed, self.attack, self.defense][stat - 1]
        stat_string = ["Speed", "Attack", "Defense"][stat - 1]

        while True:
            try:
                to_add_input = input(f"How many points would you like to add to {stat_string}: ")
                to_add = int(to_add_input)
                break
            except ValueError:
                print("Please enter a valid integer.")

        if to_add <= 0:
            print("Points Must Be Positive Number")
            return

        if to_add > self.points:
            print(f"You only have {self.points} points left.")
            return

        if curr_stat + to_add > 5:
            print(f"{stat_string} cannot be more than 5. Current: {curr_stat}")
            return

        # Add Changes
        self.points -= to_add
        if stat == 1:
            self.speed += to_add
        elif stat == 2:
            self.attack += to_add
        elif stat == 3:
            self.defense += to_add

    def check_inventory(self) -> None:
        """
        Prints the player's inventory.

        Doctests:
        >>> inventory = Inventory([], 10, 0.0)
        >>> player = Player(inventory, 0, 0, 0, 0, 10, 10)
        >>> player.check_inventory()
        Inventory:
        >>> inventory = Inventory([Item("Potion", 0, 0, 0, 0)], 10, 0.0)
        >>> player = Player(inventory, 0, 0, 0, 0, 10, 10)
        >>> player.check_inventory()
        Inventory:
        - Potion
        """
        print("Inventory:")
        for item in self.inventory.items:
            print(f"- {item.name}")

    def check_stats(self) -> None:
        """Print the player's current status and stats."""
        print(f"Current Health: {self.current_health}/{self.max_health}")
        print(f"Speed: {self.speed}")
        print(f"Attack: {self.attack}")
        print(f"Defense: {self.defense}")


@dataclass
class Enemy:
    """ Represents Enemies
    Instance Attributes:
        - name: name of the enemy
        - max_health: maximum health of the enemy
        - current_health: current health of the enemy
        - attack: damage the enemy deals
        - attack_pattern: the order in which the enemy attacks

    Representation Invariants:
        - self.max_health > 0
        - self.current_health >= 0
        - self.current_health <= self.max_health
        - self.attack >= 0
        - len(self.attack_pattern) > 0
        - all(attack in ["small", "big"] for attack in self.attack_pattern)
    """
    name: str
    max_health: int
    current_health: int
    attack: int
    attack_pattern: list[str]
    items: list[Item]

    def __init__(self, name: str, max_health: int, current_health: int, attack: int, attack_pattern: list[str], items: list[Item]) -> None:
        self.name = name
        self.max_health = max_health
        self.current_health = current_health
        self.attack = attack
        self.attack_pattern = attack_pattern
        self.items = items

    def deal_damage(self, turn_number: int) -> int:
        """Return the damage dealt by this entity based on its attack_pattern and the current turn_number.

        The damage is equal to self.attack if the attack_type is "big", otherwise it is
        half of self.attack (rounded up). The attack_pattern cycles based on the turn_number.

        Preconditions:
            - turn_number > 0
            - self.attack_pattern != []
            - all(type in {"big", "small"} for type in self.attack_pattern)
        """
        turn_number = (turn_number % len(self.attack_pattern)) - 1
        attack_type = self.attack_pattern[turn_number]
        if attack_type == "big":
            return self.attack
        else:
            return ceil(self.attack / 2)

    def take_damage(self, damage: int) -> bool:
        """Decreases enemies health by damage amount and returns whether the enemy is dead.
        Preconditions:
            - damage > 0
        """
        self.current_health -= damage
        return self.current_health > 0


@dataclass
class Puzzle(Location):
    """ Represents a Puzzle Location
    Instance Attributes:
        - completed: Whether the puzzle has been completed.
    """
    completed: bool = False


# Note: Other entities you may want to add, depending on your game plan:
# - Puzzle class to represent special locations (could inherit from Location class if it seems suitable)
# - Player class
# etc.

if __name__ == "__main__":
    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (Delete the "#" and space before each line.)
    # IMPORTANT: keep this code indented inside the "if __name__ == '__main__'" block
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999', 'static_type_checker']
    })