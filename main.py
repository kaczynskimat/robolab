#!/usr/bin/env python3

import ev3dev.ev3 as ev3
import logging
import os
import paho.mqtt.client as mqtt
import uuid
import signal

from movement import Robot

from communication import *

from odometry import Odometry
from RobolabCode.planet import Planet

client = None  # DO NOT EDIT


def run():
    # DO NOT CHANGE THESE VARIABLES
    #
    # The deploy-script uses the variable "client" to stop the mqtt-client after your program stops or crashes.
    # Your script isn't able to close the client after crashing.
    global client

    client_id = '130-' + str(uuid.uuid4())  # Replace YOURGROUPID with your group ID
    client = mqtt.Client(client_id=client_id,  # Unique Client-ID to recognize our program
                         clean_session=True,  # We want a clean session after disconnect or abort/crash
                         protocol=mqtt.MQTTv311  # Define MQTT protocol version
                         )
    # Setup logging directory and file
    curr_dir = os.path.abspath(os.getcwd())
    if not os.path.exists(curr_dir + '/../logs'):
        os.makedirs(curr_dir + '/../logs')
    log_file = curr_dir + '/../logs/project.log'
    logging.basicConfig(filename=log_file,  # Define log file
                        level=logging.DEBUG,  # Define default mode
                        format='%(asctime)s: %(message)s'  # Define default logging format
                        )
    logger = logging.getLogger('RoboLab')

    # THE EXECUTION OF ALL CODE SHALL BE STARTED FROM WITHIN THIS FUNCTION.
    # ADD YOUR OWN IMPLEMENTATION HEREAFTER.

    robot = Robot()
    odo = Odometry()
    explorer = Planet()
    com = Communication(client, logger)
    com.client.loop_start()  # start listening to incoming messages

    last_color, current_status, odo_data = robot.line_following()

    # ready-message
    current_coord, current_orient = com.return_message("ready")[1]  # (x, y)  # Direction.*
    current_vertex = (current_coord, current_orient, last_color)  # ((x, y), Direction.*, "blue" | "red")

    outgoing_paths = robot.scan_outgoing_paths(current_orient)
    explorer.visited[current_coord] = outgoing_paths
    chosen_direction = explorer.intelligent_explore(current_coord)

    com.return_message("target")


    while not (com.is_target_reached() or com.is_exploration_complete(chosen_direction)):

        # pathSelect-message
        forced_path = com.return_message("pathSelect", [current_coord, chosen_direction])
        if len(forced_path):
            chosen_direction = forced_path[0]

        robot.turn_direction(current_orient, chosen_direction)
        ev3.Sound.play_song((('D4', 'e3'),))
        current_color, current_status, odo_data = robot.line_following()
        com.clear_values()
        if current_status == "blocked":
            vertex_approx = (current_vertex[0], chosen_direction)
        else:
            vertex_approx = odo.calculate_distance(current_coord, chosen_direction, odo_data, last_color, current_color)

        start_vertex, end_vertex, path_weight, path_status = com.return_message("path",
                                                                                    [(current_coord, chosen_direction),
                                                                                     vertex_approx, current_status])
        last_color = current_color

        explorer.add_path(start_vertex, end_vertex, int(path_weight))
        current_vertex = (end_vertex[0], (end_vertex[1] + 180) % 360)
        print(f"current_vertex: {current_vertex}")  # DEBUG
        current_coord = current_vertex[0]
        current_orient = current_vertex[1]

        # target-message
        target_message = com.return_message("target")
        print("target message: ", target_message)
        if target_message == "done":
            break

        if current_coord not in explorer.visited.keys():
            outgoing_paths = robot.scan_outgoing_paths(current_orient)
            if current_coord in explorer.unvisited:
                explorer.remove_if_blocked(current_coord, outgoing_paths)
            else:
                explorer.visited[current_coord] = outgoing_paths


        unveiled_paths = com.return_message("pathUnveiled")
        explorer.remove_driven_paths(start_vertex, end_vertex)
        explorer.handle_unveiled_paths(unveiled_paths)

        if current_coord in explorer.paths.keys() and current_coord in explorer.visited.keys():
            for direction in explorer.paths[current_coord].keys():
                if direction in explorer.visited[current_coord]:
                    explorer.visited[current_coord].remove(direction)



        chosen_direction = explorer.next_direction(target_message, current_coord)

    if not com.is_target_reached():
        print("explo complete:", com.is_exploration_complete(chosen_direction))
        com.return_message("explorationComplete")

    time.sleep(3)  # wait 3 seconds for messages

    com.client.loop_stop()  # stop listening to incoming messages
    client.disconnect()

    print("Disconnected, program ended! \n")


# DO NOT EDIT
def signal_handler(sig=None, frame=None, raise_interrupt=True):
    if client and client.is_connected():
        client.disconnect()
    if raise_interrupt:
        raise KeyboardInterrupt()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    try:
        run()
        signal_handler(raise_interrupt=False)
    except Exception as e:
        signal_handler(raise_interrupt=False)
        raise e
