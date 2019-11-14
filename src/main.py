# main.py

# Main function to run malmo program

import os, sys, time
import math, errno

try:
    import MalmoPython
    import malmoutils
except:
    import malmo.MalmoPython as MalmoPython
    import malmo.malmoutils as malmoutils

import create_world as farm
from shepherd_agent import Shepherd

import functools
print = functools.partial(print, flush=True)

import json
if sys.version_info[0] == 2:
    import Tkinter as tk
else:
    import tkinter as tk

CANVAS_BORDER = 20
CANVAS_WIDTH = 600
CANVAS_HEIGHT = 600
ARENA_WIDTH = 60
ARENA_HEIGHT = 60

def canvasX(x):
    return (CANVAS_BORDER/2) + (0.5+x/float(ARENA_WIDTH))*(CANVAS_WIDTH-CANVAS_BORDER)

def canvasY(y):
    return (CANVAS_BORDER/2) + (0.5+y/float(ARENA_HEIGHT))*(CANVAS_HEIGHT-CANVAS_BORDER)

def drawEntity(entities):
    canvas.delete("all")
    for e in entities:
        # draw sheep
        if e["name"] == "Sheep":
            canvas.create_oval(canvasX(e["x"])-4, canvasY(e["z"])-4, canvasX(e["x"])+4, canvasY(e["z"])+4, fill="#0000ff")
        # draw agent
        elif e["name"] == "Jesus":
            canvas.create_oval(canvasX(e["x"])-8, canvasY(e["z"])-8, canvasX(e["x"])+8, canvasY(e["z"])+8, fill="#ff0000")
    root.update()

if __name__ == "__main__":
        
    # Create default Malmo objects:

    agent_host = MalmoPython.AgentHost()
    try:
        agent_host.parse( sys.argv )
    except RuntimeError as e:
        print('ERROR:',e)
        print(agent_host.getUsage())
        exit(1)
    if agent_host.receivedArgument("help"):
        print(agent_host.getUsage())
        exit(0)

    # create tkinker window frame
    root = tk.Tk()
    root.wm_title("SheepHerd")
    canvas = tk.Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, borderwidth=0, highlightthickness=0, bg="white")
    canvas.pack()
    root.update()

    shepherd = Shepherd()
    runs = 1
    for i in range(runs):
        mission_XML = farm.getMissionXML("Sheep Apocalypse #" + str(i+1))
        my_mission = MalmoPython.MissionSpec(mission_XML, True)
        my_mission_record = MalmoPython.MissionRecordSpec()

        # Attempt to start a mission:
        max_retries = 3
        for retry in range(max_retries):
            try:
                agent_host.startMission( my_mission, my_mission_record )
                break
            except RuntimeError as e:
                if retry == max_retries - 1:
                    print("Error starting mission:",e)
                    exit(1)
                else:
                    time.sleep(2)

        # Loop until mission starts:
        print("Starting mission " + str(i+1))
        world_state = agent_host.getWorldState()
        while not world_state.has_mission_begun:
            time.sleep(0.1)
            world_state = agent_host.getWorldState()
            for error in world_state.errors:
                print("Error:",error.text)
        
        while world_state.is_mission_running:
            shepherd.run(agent_host)
            time.sleep(0.1)
            world_state = agent_host.getWorldState()

            # Add a tkinter canvas to draw
            if world_state.number_of_observations_since_last_state > 0:
                msg = world_state.observations[-1].text
                ob = json.loads(msg)
                if "entities" in ob:
                    drawEntity(ob["entities"])
        
        shepherd.get_current_state(agent_host)
        print()
        print("Shepherd location:", shepherd.agent_location())
        print("Sheep locations:", shepherd.sheep_location())
        print("Shepherd in pen:", shepherd.end_mission())
        print("Sheep in pen:", shepherd.sheep_in_pen())

        print()
        print("End of mission")
        print()
        time.sleep(1)
        # Mission has ended.
        
    print("Completed all runs.")
