"""CSC111 Project 1: Text Adventure Game - Event Logger

Instructions (READ THIS FIRST!)
===============================

This Python module contains the code for Project 1. Please consult
the project handout for instructions and details.

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
from dataclasses import dataclass
from typing import Optional


@dataclass
class Event:
    """
    A node representing one event in an adventure game.

    Instance Attributes:
    - id_num: Integer id of the location associated with this event.
    - description: Description of the location associated with this event.
    - next_command: The command that led from this event to the next event. None if this is the last event.
    - next: The next event in the game sequence, or None if this is the last event.
    - prev: The previous event in the game sequence, or None if this is the first event.

    Representation Invariants:
    - self.id_num >= -1
    - self.description != ""
    """
    id_num: int
    description: str
    next_command: Optional[str] = None
    next: Optional[Event] = None
    prev: Optional[Event] = None


class EventList:
    """
    A linked list of game events.

    Instance Attributes:
    - first: The first event in the list.
    - last: The last event in the list.

    Representation Invariants:
    - (self.first is None) == (self.last is None)
    - (self.first is not None) or (self.last is not None) or (self.first is None and self.last is None)
    """
    first: Optional[Event]
    last: Optional[Event]

    # Note: You may ADD parameters/attributes/methods to this class as you see fit.
    # But do not rename or remove any existing methods/attributes in this class

    def __init__(self) -> None:
        """Initialize a new empty event list."""

        self.first = None
        self.last = None

    def display_events(self) -> None:
        """Display all events in chronological order."""
        curr = self.first
        while curr:
            print(f"Location: {curr.id_num}, Command: {curr.next_command}")
            curr = curr.next

    def is_empty(self) -> bool:
        """
        Return whether this event list is empty.
        >>> EventList().is_empty()
        True

        >>> non_empty_list = EventList()
        >>> non_empty_list.add_event(Event(id_num=1, description=""))
        >>> non_empty_list.is_empty()
        False
        """
        return self.first is None

    def add_event(self, event: Event, command: str = None) -> None:
        """
        Add the given new event to the end of this event list.
        The given command is the command which was used to reach this new event, or None if this is the first
        event in the game.
        """
        # Hint: You should update the previous node's <next_command> as needed
        if self.is_empty():
            self.first = event
            self.last = event
            return

        if command is not None:
            self.last.next_command = command

        event.prev = self.last
        self.last.next = event
        self.last = event

    def remove_last_event(self) -> None:
        """
        Remove the last event from this event list.
        If the list is empty, do nothing.

        >>> test_list = EventList()
        >>> test_list.add_event(Event(id_num=1, description=""))
        >>> test_list.remove_last_event()
        >>> test_list.is_empty()
        True
        """
        # Hint: The <next_command> and <next> attributes for the new last event should be updated as needed
        if self.is_empty():
            return
        self.last = self.last.prev
        if self.last is not None:
            self.last.next_command = None
            self.last.next = None
        else:
            self.first = None

    def get_id_log(self) -> list[int]:
        """Return a list of all location IDs visited for each event in this list, in sequence."""
        node = self.first
        list_so_far = []
        while node is not None:
            list_so_far.append(node.id_num)
            node = node.next

        return list_so_far

    def to_data(self) -> list[dict]:
        """Return a list of dictionaries representing the events in this list."""
        data = []
        curr = self.first
        while curr:
            data.append({
                'id_num': curr.id_num,
                'description': curr.description,
                'next_command': curr.next_command
            })
            curr = curr.next
        return data

    def from_data(self, data: list[dict]) -> None:
        """Populate this event list from a list of dictionaries."""
        self.first = None
        self.last = None
        for event_data in data:
            event = Event(id_num=event_data['id_num'], description=event_data['description'])
            self.add_event(event, event_data['next_command'])


if __name__ == "__main__":
    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (Delete the "#" and space before each line.)
    # IMPORTANT: keep this code indented inside the "if __name__ == '__main__'" block
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999', 'static_type_checker']
    })
