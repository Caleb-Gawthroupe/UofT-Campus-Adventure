"""CSC111 Project 1: Text Adventure Game - Game Manager

Instructions (READ THIS FIRST!)
===============================

This Python module contains the code for Project 1. Please consult
the project handout for instructions and details.

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
import json
import os
from typing import Optional

from game_entities import Location, Item, Player, Inventory, Enemy
from event_logger import Event, EventList


# Note: You may add in other import statements here as needed

# Note: You may add helper functions, classes, etc. below as needed


class AdventureGame:
    """A text adventure game class storing all location, item and map data.

    Instance Attributes:
        - _locations: A dictionary mapping location IDs to Location objects.
        - _items: A dictionary mapping item names to Item objects.
        - _enemies: A dictionary mapping enemy names to Enemy objects.
        - current_location_id: The ID of the player's current location.
        - ongoing: Whether the game is currently active.
        - steps: The number of steps the player has taken.
        - max_steps: The maximum allowed steps before game over.

    Representation Invariants:
        - self.current_location_id in self._locations
        - self.steps >= 0
        - self.max_steps > 0
    """

    # Private Instance Attributes (do NOT remove these two attributes):
    #   - _locations: a mapping from location id to Location object.
    #                       This represents all the locations in the game.
    #   - _items: a dictionary of Item objects, representing all items in the game.
    #   - _enemies: a dicitonary of Enemy objects, representing all enemies in the game

    _locations: dict[int, Location]
    _items: dict[str, Item]
    _enemies: dict[str, Enemy]
    current_location_id: int  # Suggested attribute, can be removed
    ongoing: bool  # Suggested attribute, can be removed
    steps: int
    max_steps: int

    def __init__(self, game_data_file: str, initial_location_id: int) -> None:
        """
        Initialize a new text adventure game, based on the data in the given file.

        The game starting location is set to the given initial_location_id.

        Preconditions:
        - game_data_file is the filename of a valid game data JSON file
        - initial_location_id is a valid location ID in the game data
        """

        # NOTES:
        # You may add parameters/attributes/methods to this class as you see fit.

        # Requirements:
        # 1. Make sure the Location class is used to represent each location.
        # 2. Make sure the Item class is used to represent each item.

        # Suggested helper method (you can remove and load these differently if you wish to do so):
        self._locations, self._items, self._enemies = self._load_game_data(game_data_file)

        # Suggested attributes (you can remove and track these differently if you wish to do so):
        self.current_location_id = initial_location_id  # game begins at this location
        self.ongoing = True  # whether the game is ongoing
        self.steps = 0
        self.max_steps = 50

    @staticmethod
    def _load_game_data(filename: str) -> tuple[dict[int, Location], dict[str, Item], dict[str, Enemy]]:
        """
        Load locations, items, and enemies from a JSON file.

        Returns a tuple containing:
        1. A dictionary of locations {id: Location}.
        2. A dictionary of items {name: Item}.
        3. A dictionary of enemies {name: Enemy}.
        """

        with open(filename, 'r') as f:
            data = json.load(f)  # This loads all the data from the JSON file

        locations = {}
        for loc_data in data['locations']:  # Go through each element associated with the 'locations' key in the file
            location_obj = Location(id_num=loc_data['id'],
                                    brief_description=loc_data['brief_description'],
                                    long_description=loc_data['long_description'],
                                    available_commands=loc_data['available_commands'],
                                    items=loc_data['items'],
                                    enemies=loc_data['enemies'])
            locations[loc_data['id']] = location_obj

        items = {}
        for item_data in data['items']:  # Go through each element associated with the 'items' key in the file
            item_obj = Item(name=item_data['name'],
                            description=item_data['description'],
                            start_position=item_data['start_position'],
                            target_position=item_data['target_position'],
                            target_points=item_data['target_points'],
                            weight=item_data['weight'],
                            combat_use=item_data['combat_use'],
                            strength=item_data['strength'],)
            items[item_obj.name] = item_obj

        enemies = {}
        for enemy_data in data['enemies']:  # Go through each element associated with the 'items' key in the file
            enemy_obj = Enemy(name=enemy_data['name'],
                              max_health=enemy_data['max_health'],
                              current_health=enemy_data['current_health'],
                              attack=enemy_data['attack'],
                              items=enemy_data['items'],
                              attack_pattern=enemy_data['attack_pattern'])
            enemies[enemy_obj.name] = enemy_obj

        return locations, items, enemies

    def get_location(self, loc_id: Optional[int] = None) -> Location:
        """
        Return Location object associated with the provided location ID.

        If no ID is provided, return the Location object associated with the current location.

        Preconditions:
        - loc_id is None or loc_id in self._locations
        """
        if loc_id:
            return self._locations[loc_id]
        else:
            return self._locations[self.current_location_id]

    def get_item(self, item_name: str) -> Optional[Item]:
        """
        Return the Item object with the given name, or None if it doesn't exist.
        """
        return self._items.get(item_name)

    def get_enemy(self, enemy_name: str) -> Optional[Enemy]:
        """
        Return the Enemy object with the given name, or None if it doesn't exist.
        """
        return self._enemies.get(enemy_name)

    def update_location(self, location_to_update_: Location) -> None:
        """
        Update the stored location object with a new version.
        Useful when the state of a location (e.g., items in it) changes.
        """
        self._locations[location_to_update_.id_num] = location_to_update_

    def save_game(self, filename: str, player_: Player, game_log_: EventList) -> None:
        """
        Save the current game state to a JSON file.

        The save file includes:
        - Current location
        - Step count
        - Player stats (inventory, health, attack, defense, speed, points)
        - Visited locations
        - Items and enemies at each location
        - The event log
        """
        data = {
            'location_id': self.current_location_id,
            'steps': self.steps,
            'player': {
                'inventory': [item.name for item in player_.inventory.items],
                'speed': player_.speed,
                'attack': player_.attack,
                'defense': player_.defense,
                'max_health': player_.max_health,
                'current_health': player_.current_health,
                'points': player_.points
            },
            'visited_locations': [loc_id for loc_id, loc in self._locations.items() if loc.visited],
            'location_items': {str(loc_id): loc.items for loc_id, loc in self._locations.items()},
            'location_enemies': {str(loc_id): loc.enemies for loc_id, loc in self._locations.items()},
            'log': game_log_.to_data()
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Game saved to {filename}")

    def load_game(self, filename: str, p_load_: Player, log_load_: EventList) -> None:
        """
        Load the game state from a JSON file.

        Restores the player's stats, inventory, and location, as well as the
        state of the world (items, enemies, visited locations).
        """
        if not os.path.exists(filename):
            print("Save file not found.")
            return

        with open(filename, 'r') as f:
            data_ = json.load(f)

        # Restore player using public attribute 'points'
        p_load_.inventory.items = [self._items[n] for n in data_['player']['inventory'] if n in self._items]
        p_load_.speed = data_['player']['speed']
        p_load_.attack = data_['player']['attack']
        p_load_.defense = data_['player']['defense']
        p_load_.max_health = data_['player']['max_health']
        p_load_.current_health = data_['player']['current_health']
        p_load_.points = data_['player']['points']

        self._restore_game_state(data_, log_load_)

    def _restore_game_state(self, data_: dict, log_load_: EventList) -> None:
        """
        Helper method to restore game state variables from loaded data.
        """
        self.current_location_id = data_['location_id']
        self.steps = data_.get('steps', 0)

        for lid_, loc_ in self._locations.items():
            loc_.visited = lid_ in data_['visited_locations']
            if str(lid_) in data_['location_items']:
                loc_.items = data_['location_items'][str(lid_)]

            # Sync commands
            loc_.available_commands = {k: v for k, v in loc_.available_commands.items()
                                       if not k.startswith("take ")}
            for itm_ in loc_.items:
                loc_.available_commands[f"take {itm_}"] = loc_.id_num

        log_load_.from_data(data_['log'])

    def check_steps(self) -> None:
        """
        Check if the player has exceeded the maximum allowed steps.
        If so, ends the game and prints a failure message.
        """
        if self.steps >= self.max_steps:
            print("Took too long! The Assignment is passed due, and you no longer can make POST.")
            self.ongoing = False

    def get_score(self, player_: Player) -> int:
        """
        Calculate the player's current score.

        The score is based on:
        - Helper items found (e.g. old socks)
        - Items successfully brought to their target locations
        """
        score_val_ = 0
        for lid_, loc_ in self._locations.items():
            for item_name_ in loc_.items:
                item_obj_ = self.get_item(item_name_)
                if item_obj_ and item_obj_.target_position == lid_:
                    score_val_ += item_obj_.target_points

        for item_ in player_.inventory.items:
            if item_.name == "old socks":
                score_val_ += item_.target_points
            elif item_.target_position == self.current_location_id:
                score_val_ += item_.target_points
        return score_val_

    def check_win(self, player_: Player) -> None:
        """
        Check if the player has won the game.

        Winning requires bringing specific items (USB Stick, Lucky Mug, Laptop Charger)
        to the start location (OISE, ID 1) and ensuring they are present there.
        """
        oise_ = self.get_location(1)
        req_ = ["usb stick", "lucky mug", "laptop charger"]
        if all(i_ in oise_.items for i_ in req_):
            print("\nCONGRATULATIONS! Assignment submitted!")
            print(f"Final Score: {self.get_score(player_)}")
            self.ongoing = False

    def increment_steps(self, player_: Player) -> None:
        """
        Increment the step counter based on the player's speed.
        Higher speed results in fewer steps added per move.
        """
        self.steps += 6 - player_.speed


def flee(loc: Location) -> int:
    """
    Handle the Flee action during combat.

    Prompts the user to choose a direction to flee towards from the available exits.
    Returns the location ID of the chosen exit.
    """
    print("Which direction would you like to flee?")
    moveable_direction = [dir_ for dir_ in loc.available_commands if dir_.startswith("go")]
    for direction_ in moveable_direction:
        print("-", direction_)

    to_flee = input()
    while to_flee not in loc.available_commands:
        print("That was an invalid option; try again.")
        to_flee = input("\nEnter action: ").lower().strip()

    print("You ran away!")
    return loc.available_commands[to_flee]


def _handle_combat_defeat(game_: AdventureGame, enemy_: Enemy) -> None:
    """
    Helper function to process the defeat of an enemy.

    - Removes the enemy from the location.
    - Adds the enemy's dropped items to the location.
    - Updates available commands to allow picking up the dropped items.
    """
    print(f"{enemy_.name} has been defeated!")
    item_names_ = list(enemy_.items)
    loc_ = game_.get_location()

    # Safely remove enemy and drop items
    if loc_.enemies:
        loc_.enemies.pop()

    loc_.items.extend(item_names_)
    for item_name_ in item_names_:
        loc_.available_commands[f"take {item_name_}"] = loc_.id_num


def _combat_player_turn(player_: Player, enemy_: Enemy, game_: AdventureGame,
                        game_log_: EventList) -> bool:
    """
    Handle the player's turn in the combat loop.

    Prompts the user for an action (attack, flee, inventory) and executes it.
    Returns True if the combat encounter should end (e.g., enemy defeated or player fled),
    False otherwise.
    """
    options_ = ["attack", "flee", "inventory"]
    move_ = ""
    while move_ not in options_:
        move_ = input("What to do? Choose from Attack, Flee, or Inventory: ").lower().strip()

    # Update the log for the chosen combat action
    update_game_log(game_log_, game_.get_location(), move_)

    if move_ == "attack":
        if not enemy_.take_damage(player_.attack):
            _handle_combat_defeat(game_, enemy_)
            return True
    elif move_ == "flee":
        game_.current_location_id = flee(loc=game_.get_location())
        return True
    elif move_ == "inventory" and _handle_combat_inventory(player_, enemy_, game_):
        return True

    return False


def _handle_combat_inventory(player_: Player, enemy_: Enemy, game_: AdventureGame) -> bool:
    """
    Handle utilizing an item from the inventory during combat.

    Validates item usability (must have combat_use > 0).
    Applies item effects (heal or damage).
    Special handling for specific puzzle interactions (e.g. Stale Bread vs Giant Goose).

    Returns True if the item usage resulted in the enemy's defeat, False otherwise.
    """
    inv_items_ = player_.inventory.items
    usable_names_ = [i_.name for i_ in inv_items_ if i_.combat_use != 0]

    if not usable_names_:
        print("No Items Available!")
        return False

    player_.check_inventory()
    choice_ = input("Which item would you like to use? ").strip().lower()
    if choice_ not in usable_names_:
        print("Item not in inventory or not usable.")
        return False

    # Find the specific item object
    item_obj_ = next(i_ for i_ in inv_items_ if i_.name == choice_)

    if item_obj_.combat_use == 1:
        to_heal = min(player_.current_health + item_obj_.strength, player_.max_health)
        print(f"You healed {item_obj_.strength} health!")
        player_.current_health = to_heal
    elif item_obj_.combat_use == 2:
        if item_obj_.name == "stale bread" and enemy_.name == "Giant Goose":
            enemy_.take_damage(9999)
            _handle_combat_defeat(game_, enemy_)
            player_.inventory.items.remove(item_obj_)
            player_.inventory.current_weight -= item_obj_.weight
            return True
        print(f"You did {item_obj_.strength} damage!")
        enemy_.take_damage(item_obj_.strength)
        if enemy_.current_health <= 0:
            _handle_combat_defeat(game_, enemy_)
            return True
    return False


def combat(player_: Player, enemy_: Enemy, game_: AdventureGame, game_log_: EventList) -> AdventureGame:
    """
    Execute the main combat loop between the player and an enemy.

    Manages turns, health updates, and game over conditions.
    Returns the updated game state (though game object is mutable/shared).
    """
    print(f"You have Entered Combat with {enemy_.name}!")
    turn_num_ = 1

    while enemy_.current_health > 0 and player_.current_health > 0 and game_.ongoing:
        # Pass game_log_ into the turn handler
        if _combat_player_turn(player_, enemy_, game_, game_log_):
            break

        # Enemy Turn
        damage_taken_ = max(enemy_.deal_damage(turn_num_) - player_.defense, 1)
        player_.current_health = max(player_.current_health - damage_taken_, 0)
        print(f"Enemy Attack for {damage_taken_} Damage! HP: {player_.current_health}")

        if player_.current_health <= 0:
            print("You died! Game Over.")
            game_.ongoing = False

        turn_num_ += 1
        game_.increment_steps(player_)
        game_.check_steps()

    return game_


def update_game_log(game_log_: EventList, location_: Location, choice_: str) -> None:
    """
    Log the player's movement and action to the event history.
    Creates a new Event node and appends it to game_log_.
    """
    new_event = Event(id_num=location_.id_num,
                      description=location_.brief_description)
    game_log_.add_event(new_event, choice_)
    return


def _display_items_at_location(game_: AdventureGame, location_: Location) -> None:
    """
    Print the descriptions of all items present at the specified location.
    """
    if not location_.items:
        return

    print("\nYou see:")
    for item_name_ in location_.items:
        item_obj_ = game_.get_item(item_name_)
        if item_obj_:
            print(f"- {item_obj_.description}")


def print_description(game_: AdventureGame, game_log_: EventList, location_: Location) -> None:
    """
    Print the description of the current location.

    - If the location has been visited before, prints the brief description.
    - Otherwise, prints the long description.
    - Also lists visible items.
    """
    # Check if visited (excluding the current event just added to the log)
    if location_.id_num in game_log_.get_id_log()[:-1]:
        print(location_.brief_description)
    else:
        print(location_.long_description)
        _display_items_at_location(game_, location_)


def handle_menu_choices(choice_: str, game_: AdventureGame, player_: Player,
                        game_log_: EventList, save_file_: str) -> None:
    """
    Execute 'menu' commands that don't involve movement or direct interaction with the world.
    (e.g., look, inventory, stats, log, save, quit).
    """
    # Retrieve location inside the function instead of passing it as an argument
    current_loc_ = game_.get_location()

    if choice_ == "look":
        print(current_loc_.long_description)
        _display_items_at_location(game_, current_loc_)
    elif choice_ == "inventory":
        player_.check_inventory()
    elif choice_ == "stats":
        player_.check_stats()
    elif choice_ == "log":
        game_log_.display_events()
    elif choice_ == "save":
        game_.save_game(save_file_, player_, game_log_)
    elif choice_ == "quit":
        game_.ongoing = False


if __name__ == "__main__":
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999', 'static_type_checker']
    })
    print("\n------------------------------------------------------------------")
    print("Welcome to the UofT Adventure!")
    print("GOAL: Find the 3 required items and bring them to OISE (Start Location) to submit your assignment.")
    print("The items are: 1. USB Stick, 2. Lucky Mug, 3. Laptop Charger.")
    print("If you fail to submit on time (too many steps), you lose!")
    print("------------------------------------------------------------------\n")

    start_inventory = Inventory(items=[],
                                weight_limit=10,
                                current_weight=0)

    game_log = EventList()  # This is REQUIRED as one of the baseline requirements
    game = AdventureGame('game_data.json', 1)  # load data, setting initial location ID to 1
    menu = ["look", "inventory", "stats", "score", "log", "quit", "save", "drop"]  # Regular menu options
    save_file = 'save_game.json'
    load_save = False

    if os.path.exists(save_file):
        print("Save file detected.")
        while True:
            start_choice = input("Do you want to overwrite it or continue with it? (overwrite/continue): ")
            start_choice = start_choice.lower().strip()
            if start_choice == 'continue':
                load_save = True
                break
            elif start_choice == 'overwrite':
                break
            else:
                print("Invalid choice.")

    choice = None
    player = Player(start_inventory, skip_stats_selection=load_save)

    if load_save:
        game.load_game(save_file, player, game_log)

    # Note: You may modify the code below as needed; the following starter code is just a suggestion
    while game.ongoing:
        location = game.get_location()

        # Trigger Combat
        if location.enemies:
            enemy_to_fight = game.get_enemy(location.enemies[-1])
            game = combat(player, enemy_to_fight, game, game_log)

        update_game_log(game_log, location, choice)
        print_description(game, game_log, location)

        # Display possible actions at this location
        print("What to do? Choose from: look, inventory, stats, score, log, save, quit, drop <item>")
        print("At this location, you can also:")
        for action in location.available_commands:
            print("-", action)

        # Validate choice
        choice = input("\nEnter action: ").lower().strip()
        while choice not in location.available_commands and choice not in menu and not choice.startswith("drop"):
            print("That was an invalid option; try again.")
            choice = input("\nEnter action: ").lower().strip()

        print("========")
        print("You decided to:", choice)

        if choice in menu:
            handle_menu_choices(choice, game, player, game_log, save_file)
        else:
            if choice.startswith("go"):
                result = location.available_commands[choice]
                game.current_location_id = result
                game.increment_steps(player)
            elif choice.startswith("take "):
                requested_item_str = choice.replace("take ", "").strip()
                if requested_item_str in location.items:
                    requested_item = game.get_item(requested_item_str)  # Use getter
                    location = player.inventory.take_item(item=requested_item, current_location=location)
                    game.update_location(location)  # Use setter method
                else:
                    print("No such item here.")
            elif choice.startswith("drop "):
                requested_item_str = choice.replace("drop ", "").strip()
                requested_item = game.get_item(requested_item_str)  # Use getter
                location = player.inventory.drop_item(item=requested_item, current_location=location)
                game.update_location(location)  # Use setter method

                # Special Puzzle Logic: Drop T-Card at Bahen
                if location.id_num == 8 and requested_item.name == "t-card":
                    print("You swipe the T-Card. System Access Granted.")
                    print("A message flashes on the screen: 'USB Stick detected at Exam Center'.")
                    if game.get_item("usb stick"):
                        usb_stick = game.get_item("usb stick")
                        exam_center = game.get_location(12)
                        if "usb stick" not in exam_center.items and usb_stick not in player.inventory.items:
                            exam_center.items.append("usb stick")
                            exam_center.available_commands["take usb stick"] = exam_center.id_num
                    else:
                        print("Error: USB Stick not found in game items.")

            # Win Condition Check
            game.check_win(player)
            game.check_steps()
