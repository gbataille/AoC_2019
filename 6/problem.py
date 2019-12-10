from dataclasses import dataclass, field
import os
from typing import Dict, List


@dataclass
class Body:
    orbited_body: str = None
    satellites: List[str] = field(default_factory=list)

    def add_satellite(self, sat: str) -> 'Body':
        self.satellites.append(sat)
        return self

    def add_center(self, center: str) -> 'Body':
        self.orbited_body = center
        return self

    @property
    def connected_bodies(self) -> List[str]:
        return self.satellites + [self.orbited_body]


@dataclass
class Universe:
    bodies_idx: Dict[str, Body] = field(default_factory=dict)
    my_location: str = None
    santa_location: str = None

    def add_orbit(self, center: str, sat: str) -> 'Universe':
        center_body = self.bodies_idx.get(center)
        sat_body = self.bodies_idx.get(sat)

        if center_body is None:
            center_body = Body()
            self.bodies_idx[center] = center_body

        center_body.add_satellite(sat)

        if sat_body is None:
            sat_body = Body()
            self.bodies_idx[sat] = sat_body

        sat_body.orbited_body = center

        return self

    def get_body(self, body: str) -> Body:
        return self.bodies_idx.get(body)


def get_input():
    with open('input.csv') as f:
        return f.read()


def check_corruption():
    pass


def parse_orbits(in_str: str) -> Universe:
    universe = Universe()
    for line in in_str.split('\n'):
        if line == "":
            continue

        center, satellite = line.split(')')

        if satellite == 'YOU':
            universe.my_location = center
        elif satellite == 'SAN':
            universe.santa_location = center
        else:
            universe.add_orbit(center, satellite)

    return universe

def count_orbits(universe: Universe) -> int:
    return rec_count_orbits(universe, 'COM', 0)


def rec_count_orbits(universe: Universe, from_body: str, dst_from_com: int) -> int:
    body = universe.get_body(from_body)

    nb_orbits = 0
    for sat in body.satellites:
        # one direct orbit between from_body and sat
        # sat to COM has dst_from_com indirect orbits
        # And then we had the orbits of anything orbiting sat
        nb_orbits += 1 + dst_from_com + rec_count_orbits(universe, sat, dst_from_com + 1)

    return nb_orbits


def path_length_finder(from_body: str, to_body: str, universe: Universe) -> int:
    shortest_routes = {from_body: 0}
    return rec_path_length_finder(from_body, to_body, universe, shortest_routes)

def rec_path_length_finder(
    from_body: str,
    to_body: str,
    universe: Universe,
    shortest_routes: Dict[str, int]
) -> int:
    if os.environ.get('DEBUG'):
        print('-----')
        print(from_body)
        print(shortest_routes)
    distance_to_body = shortest_routes[from_body]
    bodies_to_traverse = []

    body_details = universe.get_body(from_body)
    for connected_body in body_details.connected_bodies:
        if connected_body == to_body:
            return distance_to_body + 1

        if connected_body not in shortest_routes:
            shortest_routes[connected_body] = distance_to_body + 1
            bodies_to_traverse.append(connected_body)

    for body in bodies_to_traverse:
        solution = rec_path_length_finder(body, to_body, universe, shortest_routes)
        if solution:
            return solution


if __name__ == '__main__':
    in_str = get_input()
    if os.environ.get('TEST'):
        in_str = """COM)B
B)C
C)D
D)E
E)F
B)G
G)H
D)I
E)J
J)K
K)L
K)YOU
I)SAN
"""
    universe = parse_orbits(in_str)
    # nb_orbits = count_orbits(universe)
    # print(nb_orbits)
    path_length = path_length_finder(universe.my_location, universe.santa_location, universe)
    print(path_length)
