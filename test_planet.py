#!/usr/bin/env python3

import unittest
from RobolabCode.planet import Direction, Planet


class ExampleTestPlanet(unittest.TestCase):
    def setUp(self):
        """
        Instantiates the planet data structure and fills it with paths

        +--+
        |  |
        +-0,3------+
           |       |
          0,2-----2,2 (target)
           |      /
        +-0,1    /
        |  |    /
        +-0,0-1,0
           |
        (start)

        """
        # Initialize your data structure here
        self.planet = Planet()
        self.planet.add_path(((0, 0), Direction.NORTH), ((0, 1), Direction.SOUTH), 1)
        self.planet.add_path(((0, 1), Direction.WEST), ((0, 0), Direction.WEST), 1)

    @unittest.skip('Example test, should not count in final test results')
    def test_target_not_reachable_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target not reachable nearby

        Result: Target is not reachable
        """
        self.assertIsNone(self.planet.shortest_path((0, 0), (1, 2)))


class TestRoboLabPlanet(unittest.TestCase):
    def setUp(self):
        """
        Instantiates the planet data structure and fills it with paths

        MODEL YOUR TEST PLANET HERE (if you'd like):
        MY PLANET
                          2,3 --- 3,3
                           |
          0,2 --- 1,2 --- 2,2
           |       |       |
          0,1 --- 1,1 --- 2,1 --- 3,1
           |       |       |
          0,0 --- 1,0 --- 2,0
           |
        (start)

        """
        # Initialize your data structure here
        self.planet = Planet()
        self.planet.add_path(((0, 0), Direction.EAST), ((1, 0), Direction.WEST), 3)
        self.planet.add_path(((1, 0), Direction.EAST), ((2, 0), Direction.WEST), 3)
        self.planet.add_path(((0, 0), Direction.NORTH), ((0, 1), Direction.SOUTH), 1)
        self.planet.add_path(((0, 1), Direction.NORTH), ((0, 2), Direction.SOUTH), 1)
        self.planet.add_path(((0, 1), Direction.EAST), ((1, 1), Direction.WEST), 3)
        self.planet.add_path(((1, 0), Direction.NORTH), ((1, 1), Direction.SOUTH), 1)
        self.planet.add_path(((1, 1), Direction.EAST), ((2, 1), Direction.WEST), 3)
        self.planet.add_path(((1, 1), Direction.NORTH), ((1, 2), Direction.SOUTH), 1)
        self.planet.add_path(((0, 2), Direction.EAST), ((1, 2), Direction.WEST), 3)
        self.planet.add_path(((1, 2), Direction.EAST), ((2, 2), Direction.WEST), 3)
        self.planet.add_path(((2, 1), Direction.NORTH), ((2, 2), Direction.SOUTH), 1)
        self.planet.add_path(((2, 2), Direction.NORTH), ((2, 3), Direction.SOUTH), 1)
        self.planet.add_path(((2, 1), Direction.EAST), ((3, 1), Direction.WEST), 3)
        self.planet.add_path(((2, 3), Direction.EAST), ((3, 3), Direction.WEST), 3)
        self.planet.add_path(((2, 1), Direction.SOUTH), ((2, 0), Direction.NORTH), 1)

    def test_integrity(self):
        """
        This test should check that the dictionary returned by "planet.get_paths()" matches the expected structure
        """
        # self.fail('implement me!')

        structure = {
            (0, 0): {
                Direction.EAST: ((1, 0), Direction.WEST, 3),
                Direction.NORTH: ((0, 1), Direction.SOUTH, 1),
            },
            (0, 1): {
                Direction.SOUTH: ((0, 0), Direction.NORTH, 1),
                Direction.NORTH: ((0, 2), Direction.SOUTH, 1),
                Direction.EAST: ((1, 1), Direction.WEST, 3),
            },
            (1, 0): {
                Direction.WEST: ((0, 0), Direction.EAST, 3),
                Direction.EAST: ((2, 0), Direction.WEST, 3),
                Direction.NORTH: ((1, 1), Direction.SOUTH, 1),
            },
            (1, 1): {
                Direction.WEST: ((0, 1), Direction.EAST, 3),
                Direction.EAST: ((2, 1), Direction.WEST, 3),
                Direction.SOUTH: ((1, 0), Direction.NORTH, 1),
                Direction.NORTH: ((1, 2), Direction.SOUTH, 1),
            },
            (2, 0): {
                Direction.WEST: ((1, 0), Direction.EAST, 3),
                Direction.NORTH: ((2, 1), Direction.SOUTH, 1),
            },
            (0, 2): {
                Direction.EAST: ((1, 2), Direction.WEST, 3),
                Direction.SOUTH: ((0, 1), Direction.NORTH, 1),
            },
            (1, 2): {
                Direction.WEST: ((0, 2), Direction.EAST, 3),
                Direction.SOUTH: ((1, 1), Direction.NORTH, 1),
                Direction.EAST: ((2, 2), Direction.WEST, 3),
            },
            (2, 1): {
                Direction.WEST: ((1, 1), Direction.EAST, 3),
                Direction.EAST: ((3, 1), Direction.WEST, 3),
                Direction.SOUTH: ((2, 0), Direction.NORTH, 1),
                Direction.NORTH: ((2, 2), Direction.SOUTH, 1),
            },
            (3, 1): {
                Direction.WEST: ((2, 1), Direction.EAST, 3),
            },
            (2, 2): {
                Direction.SOUTH: ((2, 1), Direction.NORTH, 1),
                Direction.WEST: ((1, 2), Direction.EAST, 3),
                Direction.NORTH: ((2, 3), Direction.SOUTH, 1),
            },
            (2, 3): {
                Direction.SOUTH: ((2, 2), Direction.NORTH, 1),
                Direction.EAST: ((3, 3), Direction.WEST, 3),
            },
            (3, 3): {
                Direction.WEST: ((2, 3), Direction.EAST, 3),
            }
        }
        self.assertEqual(self.planet.get_paths(), structure)


    def test_empty_planet(self):
        """
        This test should check that an empty planet really is empty
        """
        self.new_planet = Planet()
        self.assertEqual(self.new_planet.get_paths(), {})

    def test_target(self):
        """
        This test should check that the shortest-path algorithm implemented works.

        Requirement: Minimum distance is three nodes (two paths in list returned)
        """
        result = [((0, 0), Direction.NORTH), ((0, 1), Direction.EAST), ((1, 1), Direction.EAST),
                  ((2, 1), Direction.EAST)]
        self.assertEqual(self.planet.shortest_path((0, 0), (3, 1)), result)

    def test_target_not_reachable(self):
        """
        This test should check that a target outside the map or at an unexplored node is not reachable
        """
        target = None
        self.assertEqual(self.planet.shortest_path((0, 0), (4, 4)), target)
        self.assertEqual(self.planet.shortest_path((2,2), (4,2)), target)


    def test_same_length(self):
        """
        This test should check that the shortest-path algorithm implemented returns a shortest path even if there
        are multiple shortest paths with the same length.

        Requirement: Minimum of two paths with same cost exists, only one is returned by the logic implemented
        """
        self.assertEqual(len(self.planet.shortest_path((0, 0), (1, 1))),2)
        road_one = [((0, 0), Direction.NORTH), ((0, 1), Direction.EAST)]
        road_two = [((0, 0), Direction.EAST), ((1, 0), Direction.NORTH)]

        next_node_of_road_one = road_one[1][0]
        next_node = self.planet.get_paths()[next_node_of_road_one]
        goal = next_node[Direction.EAST][0]

        next_node_of_road_two = road_two[1][0]
        next_node_two = self.planet.get_paths()[next_node_of_road_two]
        goal_two = next_node_two[Direction.NORTH][0]

        self.assertTrue(goal == goal_two)


    def test_target_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target nearby

        Result: Target is reachable
        """
        loop = [((0, 0), Direction.EAST), ((1, 0), Direction.WEST)]
        self.assertNotEqual(self.planet.shortest_path((1, 0), (0, 0)), loop)

    def test_target_not_reachable_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target not reachable nearby

        Result: Target is not reachable
        """
        target = None
        self.assertEqual(self.planet.shortest_path((0, 0), (4, 4)), target)


if __name__ == "__main__":
    unittest.main()
