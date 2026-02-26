# UofT Campus Adventure

A text-based adventure game set on the University of Toronto campus, featuring interactive gameplay, entity management, and event logging.

## Overview

UofT Campus Adventure is an interactive game simulation that takes players on an adventure through the University of Toronto campus. The project combines a game engine with entity management and event tracking to create an immersive text-based experience.

## Features

- **Interactive Adventure Gameplay** - Navigate through UofT campus locations and interact with various entities
- **Game Entities** - Comprehensive system for managing characters, items, and locations
- **Event Logging** - Track and log all events that occur during gameplay
- **Configurable Game Data** - Easy-to-modify JSON-based game configuration
- **Simulation Engine** - Advanced simulation capabilities for game scenarios

## Project Structure

- `adventure.py` - Main game engine and gameplay logic
- `game_entities.py` - Entity classes and management system for game objects
- `game_data.json` - Configuration file containing game data, locations, and entities
- `event_logger.py` - Event tracking and logging system
- `simulation.py` - Game simulation and scenario management
- `report.tex` - Technical project report

## Getting Started

### Requirements

- Python 3.x
- Standard library dependencies only

### Installation

```bash
git clone https://github.com/Caleb-Gawthroupe/UofT-Campus-Adventure.git
cd UofT-Campus-Adventure
```

### Running the Game

```bash
python adventure.py
```

## How It Works

1. **Game Initialization** - The game loads configuration from `game_data.json`
2. **Entity Management** - Game entities (characters, items, locations) are created and managed through `game_entities.py`
3. **Adventure Loop** - Players interact with the game through the adventure engine in `adventure.py`
4. **Event Tracking** - All player actions and events are logged via `event_logger.py`
5. **Simulation** - Complex game scenarios can be run through `simulation.py`

## Configuration

Customize your game experience by editing `game_data.json`. This file contains:
- Location definitions
- Entity information
- Game parameters
- Dialogue and story elements

## Project Documentation

For detailed information about the project, see `report.tex`.

## Team

Created by [Caleb-Gawthroupe](https://github.com/Caleb-Gawthroupe) and Arush Gupta

## License

Please see the repository for license information.
