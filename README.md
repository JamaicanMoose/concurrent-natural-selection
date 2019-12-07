# selection_game

## File Structure
 
* defs.py
    * Set as balance constants
* gui.py
    * Holds Gui class. Handles the visualization to the audience of the simulation. Is used by the simulator class 
* item.py
    * Holds Item class. Subclass for members and resources. 
* map.py
    * Holds the Map class. Used to add, delete, and move items and members in our data representation of the simulation
* member.py
    * Holds the Member class. Handles the moves that a member can make.
* selection_game.py
    * File that holds the main function and runs simulator
* simulator.py
    * Holds the Simulator class. Initializes the threads for simulation, initializes the map with random resources and members, and get the GUI started. It also checks for when the game ends, when to add resources, and handle errors
* skill.py
    * Holds the Skills and Resources class. Skills class acts as a representation of a members attributes. Resources acts as items that a member can obtain to upgrade their Skills.
