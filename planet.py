#!/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file
from enum import IntEnum, unique
from typing import Optional, List, Tuple, Dict


@unique
class Direction(IntEnum):
    """ Directions in shortcut """
    NORTH = 0
    EAST = 90
    SOUTH = 180
    WEST = 270


Weight = int
"""
Weight of a given path (received from the server)

Value:  -1 if blocked path
        >0 for all other paths
        never 0
"""


class Planet:
    """
    Contains the representation of the map and provides certain functions to manipulate or extend
    it according to the specifications
    """
    infinity = 1000000000000000000

    def __init__(self):
        """ Initializes the data structure """
        self.paths = {}
        self.visited = {}  # key: coordinates, values: [Direction.*, ...]
        self.unvisited = []  # Coordinates that we get from unveiledPaths (if they are not in visited dictionary)

    def add_path(self, start: Tuple[Tuple[int, int], Direction], target: Tuple[Tuple[int, int], Direction],
                 weight: int):
        """
         Adds a bidirectional path defined between the start and end coordinates to the map and assigns the weight to it

        Example:
            add_path(((0, 3), Direction.NORTH), ((0, 3), Direction.WEST), 1)
        :param start: 2-Tuple
        :param target:  2-Tuple
        :param weight: Integer
        :return: void
        """

        # If statement to avoid overwriting
        if start[0] not in self.paths.keys():
            self.paths[start[0]] = {}
        self.paths[start[0]][start[1]] = (target[0], target[1], weight)
        if target[0] not in self.paths.keys():
            self.paths[target[0]] = {}
        self.paths[target[0]][target[1]] = (start[0], start[1], weight)

    def get_paths(self) -> Dict[Tuple[int, int], Dict[Direction, Tuple[Tuple[int, int], Direction, Weight]]]:
        """
        Returns all paths

        Example:
            {
                (0, 3): {
                    Direction.NORTH: ((0, 3), Direction.WEST, 1),
                    Direction.EAST: ((1, 3), Direction.WEST, 2),
                    Direction.WEST: ((0, 3), Direction.NORTH, 1)
                },
                (1, 3): {
                    Direction.WEST: ((0, 3), Direction.EAST, 2),
                    ...
                },
                ...
            }
        :return: Dict
        """

        return self.paths

    def shortest_path(self, start: Tuple[int, int], target: Tuple[int, int]) -> Optional[List[Tuple[Tuple[int, int], Direction]]]:
        """
        Returns the shortest path between two nodes

        Examples:
            shortest_path((0,0), (2,2)) returns: [((0, 0), Direction.EAST), ((1, 0), Direction.NORTH)]
            shortest_path((0,0), (1,2)) returns: None
        :param start: 2-Tuple
        :param target: 2-Tuple
        :return: None, List[] or List[Tuple[Tuple[int, int], Direction]]
        """

        # Input to the function - all the nodes that the robot has gone through
        nodes = self.get_paths()
        road_to_the_node = list()

        # Check if it's an empty planet / target not in nodes / start is the target -> return None
        if len(nodes) == 0 or (target not in nodes):
            return None
        elif start == target:
            return road_to_the_node
            # Dictionary with unvisited nodes
        else:
            unvisited_nodes = nodes

            # Current node = start node at the beginning, is later updated to the node with the smallest weight
            current_node = start

            # Dictionary with the distances from the start node
            # Each node has an infinity value at the beginning, except for start node
            distances = {}
            for node in unvisited_nodes.keys():
                if node == start:
                    distances[node] = 0
                else:
                    distances[node] = self.infinity

            # Keeps track of the road which leads to the target
            nodes_to_target = {}

            # As long as target is in distances -> iterate over current_neighbour and replace the distance to the
            # current node if it's smaller than the current known distance
            while target in distances:

                # get access of the neighbours of the current node
                current_neighbour = unvisited_nodes[current_node].items()

                # key is the direction
                # value contains
                for key, value in current_neighbour:
                    goal = value[0]  # Goal coordinates e.g. (0, 3)
                    distance_to_the_neighbour = value[2]  # Weight of the path
                    # 2 if statements below
                    # check if goal is in distances.keys() and check if distance of current_node (it's the distance from
                    # the start to our current node) + the distance to the current neighbour is smaller than
                    # the smallest know weight to this goal and if so:
                    if goal in distances.keys() and value[2] != -1:
                        if distances[current_node] + distance_to_the_neighbour < distances[goal]:
                            current_distance = distances[current_node] + distance_to_the_neighbour
                            distances[goal] = current_distance
                            nodes_to_target[goal] = (current_node, key)

                distances.pop(current_node)

                # Step4.  Loop through the dictionary of distances and find the node with the smallest weight
                # Assign it as a current node
                for new_node, weight in distances.items():
                    if weight == min(distances.values()):
                        current_node = new_node

            current_node = target
            while current_node != start:
                if current_node not in nodes_to_target:
                    return None
                # key -> coordinates; value -> e.g. ((1, 1), <Direction.NORTH: 0>)
                for key, value in nodes_to_target.items():
                    if key == current_node:
                        road_to_the_node.append(value)
                        current_node = value[0]
            if len(road_to_the_node) > 1:
                road_to_the_node.reverse()
            return road_to_the_node

    def intelligent_explore(self, coordinates):
        """
        Returns the direction which the robot should take.
        If there are any outgoing paths from the current vertex, it chooses the first one scanned.
        Otherwise, it goes through visited and unvisited to find the node to which the path cost is the smallest.
        """

        # Check if our current vertex has any outgoing paths, if it doesn't, then it goes inside this if statement
        # in order to find the most optimal way to choose a path.
        if len(self.visited[coordinates]) == 0:

            # List with tuples (node, total weight to the node)
            known_paths_to_coord = []

            # Looks for all known nodes (in visited or in unvisited) and if there is a known road to them, appends them
            # to known_paths_to_coord.
            for coord in self.visited.keys():
                if len(self.visited[coord]):
                    path = self.shortest_path(coordinates, coord)
                    if path is None:
                        continue
                    if len(path) == 0:
                        break
                    else:
                        total = 0
                        for vertex in path:  # path -> [((0, 0), Direction.EAST), ((1, 0), Direction.NORTH)]
                            direction = vertex[1]
                            weight = self.paths[vertex[0]][direction][2]
                            total += weight
                        known_paths_to_coord.append((coord, total))

            for coord in self.unvisited:
                path = self.shortest_path(coordinates, coord)
                # if path == []:
                #     return 'empty'
                if path:
                    total = 0
                    for vertex in path:
                        direction = vertex[1]
                        weight = self.paths[vertex[0]][direction][2]
                        total += weight
                    known_paths_to_coord.append((coord, total))

            # Loops through known_paths_to_coord and chooses the one with the smallest weight
            shortest_path_weight = self.infinity
            coord_smallest_weight = None
            for vertex in known_paths_to_coord:
                if vertex[1] < shortest_path_weight:
                    coord_smallest_weight = vertex[0]
                    shortest_path_weight = vertex[1]

            # Returns the direction to the node, which has the smallest weight relative to our current coordinates
            road_to_the_node = self.shortest_path(coordinates, coord_smallest_weight)
            # if road_to_the_node == []:
            #     return 'empty'
            if not road_to_the_node:
                return road_to_the_node
            else:
                return road_to_the_node[0][1]  # Returns direction
            # --------------------------------------------------------#
        else:
            # If there are any outgoing paths from the current vertex, choose the first one scanned by the robot.
            direction_to_take = self.visited[coordinates][0]
            return direction_to_take

    # def remove_current_coord_unvisited(self, coordinates, unvisited: list):
    #     """
    #         takes current coordinates and the unvisited list
    #         removes current_coord from list if it's in
    #         returns unvisited list
    #
    #     """
    #     temp = [x for x in unvisited if x != coordinates]
    #     unvisited = temp
    #     return unvisited

    def next_direction(self, target_message, coordinates):
        """
            takes target message and current coordinates
            checks if there is target and if target is reachable
            otherwise intelligent exploration
            returns a direction the robot should choose
        """
        if target_message is not None:
            # print("es gibt ein Target!")
            road_to_target = self.shortest_path(coordinates, target_message)  # (StartX, StartY), (TargetX, TargetY)
            if road_to_target:
                direction = road_to_target[0][1]
            else:
                direction = self.intelligent_explore(coordinates)
        else:
            direction = self.intelligent_explore(coordinates)
        return direction

    def handle_unveiled_paths(self, unveiled_paths):
        """
        Adds paths unveiled by the mothership to dict "paths" and if the vertex
        was not yet visited by the robot, to dict "unvisited".
        """
        if len(unveiled_paths):
            for path in unveiled_paths:
                first_vertex, last_vertex, path_weight, path_status = path
                if first_vertex[0] not in self.visited.keys() and first_vertex[0] not in self.unvisited:
                    self.unvisited.append(first_vertex[0])  # (StartX, StartY)
                # elif path_weight != -1 and (first_vertex[0] in self.visited.keys() and first_vertex[1] not in self.visited[first_vertex[0]]):
                    # self.visited[first_vertex[0]].append(first_vertex[1])
                    # pass

                if last_vertex[0] not in self.visited.keys() and last_vertex[0] not in self.unvisited:
                    self.unvisited.append(last_vertex[0])  # (EndX, EndY)
                # elif path_weight != -1 and (last_vertex[0] in self.visited.keys() and last_vertex[1] not in self.visited[last_vertex[0]]):
                #     pass
                    # self.visited[last_vertex[0]].append(last_vertex[1])
                self.add_path(first_vertex, last_vertex, path_weight)

        for path in unveiled_paths:
            start_vertex, end_vertex, path_weight, path_status = path
            if start_vertex[0] in self.visited.keys():
                for direction in self.visited[start_vertex[0]]:
                    if direction in self.paths[start_vertex[0]].keys():
                        self.visited[start_vertex[0]].remove(direction)
            if end_vertex[0] in self.visited.keys():
                print("in if statement, end_vertex:", end_vertex)
                for direction in self.visited[end_vertex[0]]:
                    print("in for loop, direction:", direction)
                    if direction in self.paths[end_vertex[0]].keys():
                        self.visited[end_vertex[0]].remove(direction)

    def remove_if_blocked(self, current_coord: tuple[int, int], outgoing_paths: list) -> None:
        """
        Permanently removes a blocked path (path with weight -1) from dict "visited" put adds every
        other available direction on the current coordinate.
        """
        for direction, value in self.paths[current_coord].items():
            if value[2] == -1:
                outgoing_paths.remove(direction)
        self.unvisited.remove(current_coord)
        self.visited[current_coord] = outgoing_paths

    # def remove_unveiled_paths(self, unveiled_paths) -> None:
    #     """Removes unveiled paths by the server from the current vertex"""
    #     for path in unveiled_paths:
    #         start_vertex, end_vertex, path_weight, path_status = path
    #         if start_vertex[0] in self.visited.keys():
    #             for direction in self.visited[start_vertex[0]]:
    #                 if direction in self.paths[start_vertex[0]].keys():
    #                     self.visited[start_vertex[0]].remove(direction)
    #         if end_vertex[0] in self.visited.keys():
    #             print("in if statement, end_vertex:", end_vertex)
    #             for direction in self.visited[end_vertex[0]]:
    #                 print("in for loop, direction:", direction)
    #                 if direction in self.paths[end_vertex[0]].keys():
    #                     self.visited[end_vertex[0]].remove(direction)

    def remove_driven_paths(self, start_vertex: tuple[tuple[int, int], Direction], last_vertex: tuple[tuple[int, int], Direction]):
        """
        Deletes the start direction from the last node which robot took and the end direction of the node to which the
        robot came.
        """
        start_in_visited, end_in_visited = False, False
        if start_vertex[1] in self.visited[start_vertex[0]]:
            start_in_visited = True
        if last_vertex[1] in self.visited[last_vertex[0]]:
            end_in_visited = True
        if start_in_visited:
            self.visited[start_vertex[0]].remove(start_vertex[1])
        if end_in_visited and (start_vertex[0] != last_vertex[0] or (start_vertex[0] == last_vertex[0] and start_vertex[1] != last_vertex[1])):
            self.visited[last_vertex[0]].remove(last_vertex[1])
