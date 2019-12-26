from dataclasses import dataclass
from enum import Enum
from functools import total_ordering
from input_utils import get_input
from math import gcd
import os
from pathfinder import Position
from typing import Any, Dict, List, Tuple


class Hemisphere(Enum):
    LEFT = 0
    RIGHT = 1


@dataclass
@total_ordering
class MyRational:
    numerator: int
    denominator: int

    def __init__(self, numerator: int, denominator: int) -> None:
        if denominator == 0:
            self.numerator = numerator
            self.denominator = 0
        else:
            reduction = gcd(numerator, denominator)
            self.numerator = numerator // reduction
            self.denominator = denominator // reduction

    @property
    def value(self):
        if self.denominator == 0:
            return 'inf'

        return self.numerator / self.denominator

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        if self.value == 'inf' and other.value == 'inf':
            return True

        return self.numerator == other.numerator and self.denominator == other.denominator

    def __lt__(self, other):
        if self.value == 'inf' and other.value == 'inf':
            return False
        if self.value == 'inf' and other.value != 'inf':
            return False
        if self.value != 'inf' and other.value == 'inf':
            return True

        return self.value < other.value


@dataclass(frozen=True)
@total_ordering
class AsteroidPosition:
    slope: MyRational
    hemisphere: Hemisphere

    def __hash__(self):
        return hash(self.slope) * hash(self.hemisphere)

    def __eq__(self, other):
        return self.hemisphere == other.hemisphere and self.slope == other.slope

    def __lt__(self, other):
        if self.hemisphere == other.hemisphere:
            return self.slope < other.slope if Hemisphere.LEFT else self.slope > other.slope

        elif self.hemisphere == Hemisphere.RIGHT and other.hemisphere == Hemisphere.LEFT:
            return False
        else:
            return True


@dataclass
@total_ordering
class Asteroid:
    position: AsteroidPosition
    distance: float
    abs_pos: Position

    def __hash__(self):
        return hash(self.position) * hash(self.distance)

    def __eq__(self, other):
        return self.position == other.position and self.distance == other.distance

    def __lt__(self, other):
        if self.position == other.position:
            return self.distance < other.distance
        else:
            return self.position < other.position


AsteroidMap = Dict[AsteroidPosition, List[Asteroid]]


def str_to_map(map_str: str) -> List[List[str]]:
    return list(
        map(
            list,       # type:ignore
            map_str.split('\n')
        )
    )


def build_asteroid_map_relative(
    absolute_map: List[List[str]], position: Position
) -> AsteroidMap:
    asteroid_map = {}

    for y, line in enumerate(absolute_map):
        for x, elem in enumerate(line):
            if Position(x, y) == position:
                continue

            if elem == '#':
                slope = MyRational(
                    position.y - y,
                    x - position.x,
                )
                if x == position.x:
                    hemisphere = Hemisphere.RIGHT if y < position.y else Hemisphere.LEFT
                else:
                    hemisphere = Hemisphere.RIGHT if x > position.x else Hemisphere.LEFT

                asteroid_position = AsteroidPosition(
                    slope,
                    hemisphere,
                )

                asteroids = asteroid_map.get(asteroid_position)
                if not asteroids:
                    asteroids = []
                    asteroid_map[asteroid_position] = asteroids
                asteroids.append(Asteroid(
                    asteroid_position,
                    (x - position.x) ** 2 + (y - position.y) ** 2,
                    Position(x, y),
                ))

    return asteroid_map


def build_relative_maps(absolute_map: List[List[str]]) -> Dict[Position, AsteroidMap]:
    maps = {}
    for y, line in enumerate(absolute_map):
        for x, elem in enumerate(line):
            if elem == '.':
                maps[Position(x, y)] = None
                continue

            maps[Position(x, y)] = build_asteroid_map_relative(absolute_map, Position(x, y))

    return maps


def find_best_spot(maps: Dict[Position, AsteroidMap]) -> Tuple[int, Position, AsteroidMap]:
    best_vis = 0
    best_pos = None
    best_map = None
    for pos, asteroid_map in maps.items():
        if asteroid_map is None:
            continue

        line_of_sights = len(set(asteroid_map.keys()))
        if line_of_sights > best_vis:
            best_vis = line_of_sights
            best_pos = pos
            best_map = asteroid_map

    return best_vis, best_pos, best_map


def display_line(line: List[Any]) -> None:
    print(''.join(list(map(str, line))))


if __name__ == '__main__':
    input_str = get_input('10')
#     input_str = """.#..#
# .....
# #####
# ....#
# ...##"""
#     input_str = """.#..##.###...#######
# ##.############..##.
# .#.######.########.#
# .###.#######.####.#.
# #####.##.#.##.###.##
# ..#####..#.#########
# ####################
# #.####....###.#.#.##
# ##.#################
# #####.##.###..####..
# ..######..##.#######
# ####.##.####...##..#
# .#####..#.######.###
# ##...#.##########...
# #.##########.#######
# .####.#.###.###.#.##
# ....##.##.###..#####
# .#.#.###########.###
# #.#.#.#####.####.###
# ###.##.####.##.#..##"""
    input_map = str_to_map(input_str)
    maps = build_relative_maps(input_map)
    max_vis, best_pos, best_map = find_best_spot(maps)

    line_of_sights = list(set(best_map.keys()))
    line_of_sights.sort()
    line_of_sights.reverse()
    # print('\nLine of sights:')
    # for pos in line_of_sights:
    #     print(f'  {pos}')

    for k in best_map.keys():
        best_map[k].sort()

    nb_asteroid = 0
    idx = 0
    ASTEROID_NUMBER = int(os.environ.get('ASTEROID_NUMBER', '200'))
    while True:
        pos = best_map[line_of_sights[idx]]

        if not pos:
            # remove the now empty location from line of sights
            line_of_sights.pop(idx)
            # next loop without incrementing idx (just roll over if we removed the last entry)
            idx = idx % len(line_of_sights)
            continue
        else:
            asteroid = pos.pop(0)
            nb_asteroid += 1

        if nb_asteroid == ASTEROID_NUMBER:
            break

        idx = (idx + 1) % len(line_of_sights)

    print(best_pos)
    print(asteroid)
    print(asteroid.abs_pos)
    print(asteroid.abs_pos.x * 100 + asteroid.abs_pos.y)
