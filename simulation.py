"""CSC111 Project 1: Text Adventure Game - Simulator

Instructions (READ THIS FIRST!)
===============================

This Python module contains code for Project 1 that allows a user to simulate
an entire playthrough of the game. Please consult the project handout for
instructions and details.

You can copy/paste your code from Assignment 1 into this file, and modify it as
needed to work with your game.

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
from unittest.mock import patch
import os
from event_logger import Event, EventList
from adventure import AdventureGame, combat, update_game_log
from game_entities import Location, Player, Inventory


class AdventureGameSimulation:
    """
    A simulation of an adventure game playthrough.

    Instance Attributes:
    - _game: The AdventureGame instance that this simulation uses.
    - _events: A collection of the events to process during the simulation.
    - player: The player character in the simulation.
    """

    def __init__(self, game_data_file: str, initial_location_id: int, commands: list[str]) -> None:
        """
        Initialize a new game simulation based on the given game data, that runs through the given commands.

        Preconditions:
        - len(commands) > 0
        - all commands in the given list are valid commands when starting from the location at initial_location_id
        """
        self._events = EventList()
        self._game = AdventureGame(game_data_file, initial_location_id)

        # Initialize player manually to simulate consistent stats without user input
        start_inventory = Inventory(items=[], weight_limit=10, current_weight=0)
        # Skip stats selection and manually set high stats to ensure deterministic combat
        self.player = Player(start_inventory, skip_stats_selection=True)
        self.player.attack = 5
        self.player.defense = 0
        self.player.speed = 5  # MAX SPEED to minimize step cost (1 per move)
        self.player.points = 0

        # Log initial location
        first_event = Event(id_num=self._game.get_location().id_num,
                            description=self._game.get_location().long_description)
        self._events.add_event(first_event)

        if commands:
            self.generate_events(commands, self._game.get_location())

    def generate_events(self, commands: list[str], current_location: Location) -> None:
        """
        Generate events in this simulation, based on current_location and commands.
        Executes the game logic similar to the main block in adventure.py.

        Simulates user input by consuming commands from the provided list.
        """
        command_iter = iter(commands)

        # We need to simulate the game loop consuming commands
        # Because combat might consume commands, we use the iterator
        # Also need to handle 'menu' commands if present in the walkthrough

        menu = ["look", "inventory", "stats", "score", "log", "quit", "save", "drop"]

        # We patch 'input' to return the next command from our iterator
        # allowing any function (like combat) that calls input() to work
        def mock_input(prompt: str = "") -> str:
            try:
                cmd = next(command_iter)
                # print(f"Mock Input [{prompt}]: {cmd}") # Debug print
                return cmd
            except StopIteration:
                return "quit"  # Default to quitting if out of commands

        with patch('builtins.input', side_effect=mock_input):
            while self._game.ongoing:
                location = self._game.get_location()

                # Trigger Combat logic from adventure.py
                if location.enemies:
                    enemy_to_fight = self._game.get_enemy(location.enemies[-1])
                    # combat function calls input(), which consumes commands from our list
                    self._game = combat(self.player, enemy_to_fight, self._game, self._events)

                    # After combat, location might change (flee) or enemy might be dead
                    # If game ended in combat, break
                    if not self._game.ongoing:
                        break

                # The 'main loop' part: get next command
                # We need to peek or consume. Since we are simulating strict steps, we consume.
                try:
                    choice = mock_input()
                except StopIteration:
                    break

                # Update log for movement/action
                # Note: adventure.py calls update_game_log inside the loop
                update_game_log(self._events, location, choice)

                # Process choice
                if choice == "quit":
                    self._game.ongoing = False
                    break
                elif choice in menu:
                    # Simulate menu choice (simple versions)
                    if choice == "look":
                        pass  # Logging handles description? No, description printed at start of loop in real game
                    elif choice == "inventory":
                        self.player.check_inventory()
                    elif choice == "score":
                        print(self._game.get_score(self.player))
                    elif choice == "stats":
                        self.player.check_stats()

                else:
                    if choice.startswith("go"):
                        if choice in location.available_commands:
                            result = location.available_commands[choice]
                            self._game.current_location_id = result
                            self._game.increment_steps(self.player)

                            # Log new location description as per simulation requirement
                            next_loc = self._game.get_location()
                            event = Event(id_num=next_loc.id_num, description=next_loc.long_description)
                            self._events.add_event(event, choice)

                        else:
                            print(f"Invalid direction: {choice}")

                    elif choice.startswith("take "):
                        requested_item_str = choice.replace("take ", "").strip()
                        if requested_item_str in location.items:
                            requested_item = self._game.get_item(requested_item_str)
                            loc = self.player.inventory.take_item(item=requested_item, current_location=location)
                            self._game.update_location(loc)
                        else:
                            print("Item not found")

                    elif choice.startswith("drop "):
                        requested_item_str = choice.replace("drop ", "").strip()
                        # Need to find item in inventory
                        found = False
                        for it in self.player.inventory.items:
                            if it.name == requested_item_str:
                                loc = self.player.inventory.drop_item(item=it, current_location=location)
                                self._game.update_location(loc)
                                found = True

                                # PUZZLE LOGIC (Copied from adventure.py)
                                if location.id_num == 8 and it.name == "t-card":
                                    print("You swipe the T-Card. System Access Granted.")
                                    if self._game.get_item("usb stick"):
                                        usb_stick = self._game.get_item("usb stick")
                                        exam_center = self._game.get_location(12)
                                        # Split long line
                                        if "usb stick" not in exam_center.items and \
                                                usb_stick not in self.player.inventory.items:
                                            exam_center.items.append("usb stick")
                                            exam_center.available_commands["take usb stick"] = exam_center.id_num
                                break
                        if not found:
                            print("Item not in inventory")

                # Check Win
                self._game.check_win(self.player)
                self._game.check_steps()

    def get_id_log(self) -> list[int]:
        """
        Return a list of all location IDs visited during the simulation.
        The list preserves the order of visitation.
        """
        return self._events.get_id_log()

    def run(self) -> None:
        """
        Run the game simulation and print location descriptions to the console.
        Iterates through the event log populated by generate_events.
        """
        current_event = self._events.first  # Start from the first event in the list

        while current_event:
            print(current_event.description)
            if current_event is not self._events.last:
                print("You choose:", current_event.next_command)

            # Move to the next event in the linked list
            current_event = current_event.next


if __name__ == "__main__":

    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999', 'static_type_checker']
    })

    # Resolve absolute path to game_data.json relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    game_data_path = os.path.join(script_dir, "game_data.json")

    # --- Win Walkthrough ---
    win_walkthrough = [
        "go east",  # to ROM (2)
        "go east",  # to Vic (3) - Trigger TA Combat
        # Combat Commands (TA 10HP vs 5 Atk)
        "attack",
        "attack",
        # End Combat
        "take stale bread",
        "go south",  # to Hart House (6)
        "go south",  # to King's Circle (11) - Trigger Goose Combat
        # Combat Commands:
        "inventory",  # Verify inventory usable
        "stale bread",  # Use bread to defeat Goose instantly
        # End Combat
        "take t-card",
        "go west",  # to UC (10)
        "go west",  # to Sid's (9) - Trigger Barista Combat
        # Combat Commands: (Barista has 8HP, Player 5 Atk)
        "attack",  # Deal 5. Barista 3HP.
        "attack",  # Deal 5. Barista Dead.
        # End Combat
        "take lucky mug",
        "go west",  # to Bahen (8)
        "drop t-card",  # Puzzle Trigger
        "go east",  # to Sid's (9)
        "go east",  # to UC (10)
        "go east",  # to King's Circle (11)
        "go south",  # to Exam Center (12)
        "take usb stick",
        "go north",  # to King's Circle (11)
        "go north",  # to Hart House (6)
        "go west",  # to Trinity (5)
        "go west",  # to Robarts (4) - Trigger Student Combat
        # Combat Commands: (Student 5HP)
        "attack",  # Deal 5. Student Dead.
        # End Combat
        "take laptop charger",
        "go north",  # to OISE (1)
        # Win Condition: Check happens at end of loop.
        # Wait, check_win checks if items are IN OISE (loc 1).
        # We need to DROP them.
        "drop usb stick",
        "drop lucky mug",
        "drop laptop charger",
        "quit"  # End simulation
    ]

    print("\n--- Win Walkthrough ---")
    sim = AdventureGameSimulation(game_data_path, 1, win_walkthrough)
    print("Win Walkthrough Log:", sim.get_id_log())

    # --- Lose Demo (Death) ---
    lose_demo = [
        "go south",  # to Robarts (4)
        "inventory",  # In combat
        "inventory",  # In combat
        "inventory"   # In combat -> Die
    ]
    print("\n--- Lose Demo (Death) ---")
    sim = AdventureGameSimulation(game_data_path, 1, lose_demo)
    print("Lose Demo Log:", sim.get_id_log())

    # --- Lose Demo (Steps) ---
    # Each move costs 1 step due to max speed (5). Max steps = 50.
    # We will step 51 times.
    lose_steps_demo = ["go east", "go west"] * 30
    print("\n--- Lose Demo (Steps) ---")
    # This should print "Took too long!..."
    sim = AdventureGameSimulation(game_data_path, 1, lose_steps_demo)
    print("Lose Steps Log:", sim.get_id_log())

    # --- Combat Demo ---
    combat_demo = [
        "go east",  # to ROM (2)
        "go east",  # to Vic (3) - Trigger TA Combat
        # Combat Commands
        "attack",
        "attack",
        # End Combat
        "quit"
    ]
    print("\n--- Combat Demo ---")
    sim = AdventureGameSimulation(game_data_path, 1, combat_demo)
    # Note: get_id_log captures locations.
    print("Combat Demo Log:", sim.get_id_log())

    # --- Puzzle Demo ---
    # Need to get Bread -> Kill Goose -> Get T-Card -> Drop at Bahen -> Get USB
    puzzle_demo = [
        "go east",  # to ROM (2)
        "go east",  # to Vic (3) - Combat
        "attack", "attack",
        "take stale bread",
        "go south",
        "go south",  # to King's Circle (11) - Combat
        "inventory",
        "stale bread",
        "take t-card",
        "go west",  # to UC (10)
        "go west",  # to Sid's (9) - Combat Barista
        "attack", "attack",
        "go west",  # to Bahen (8)
        "drop t-card",  # Puzzle
        "go east",  # to Sid's (9)
        "go east",  # to UC (10)
        "go east",  # to King's Circle (11)
        "go south",  # to Exam Center (12)
        "take usb stick",
        "quit"
    ]
    print("\n--- Puzzle Demo ---")
    sim = AdventureGameSimulation(game_data_path, 1, puzzle_demo)
    print("Puzzle Demo Log:", sim.get_id_log())
