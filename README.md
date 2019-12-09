# selection_game

$$ How to Run Our Program

```
git clone https://github.com/JamaicanMoose/concurrent-natural-selection
cd concurrent-natural-selection
pip install -r requirements.txt
*python selection_game.py

# then add in user input for game configurations!
```


## File Structure
 
* defs.py
    - Set as balance constants
* gui.py
    - Holds Gui class. 
    - Handles the visualization to the audience of the simulation. 
Is used by the simulator class.
* item.py
    - Holds Item class. Parent class for members and resources.
* map.py
    - Holds the Map class. Used to add, delete, and move items and members 
    in our data representation of the simulation.
    - Lock is acquired here.
    - Game over condition is checked based on map contents.
* member.py
    - Holds the Member class. Handles the moves that a member can make 
    (reproduce, step, use_bag).
    - Each member object has a data member function member_thread 
    that will be spawned for each other member to simulate concurrent 
    actions using member moves.
* selection_game.py
    - File that holds the main function and runs simulator
* Simulator.py
    - Takes in user input
    - Holds the Simulator class. Initializes the threads for simulation, 
        initializes the map with random resources and members, 
        and get the GUI started. 
    - Spawns resource thread
* skill.py
    - Holds the Skills and Resources class. 
    - Skills class acts as a representation of a members attributes.
    - Resources acts as items that a member can obtain to upgrade their Skills. 
    - Resource is a subclass of skill because it has the same attributes.

