from dataclasses import dataclass
from enum import Enum
from functools import total_ordering
from typing import Any, List, Tuple


class Hemisphere(Enum):
    Left = 0
    Right = 1


@dataclass
# @total_ordering
class MyRational:
    numerator: int
    denominator: int
    #
    # @property
    # def value(self):
    #     if denominator == 0:
    #         return 'inf'
    #
    #     return self.numerator / self.denominator
    #
    # def __eq__(self, other):
    #     return self.numerator * other.denominator == other.numerator * self.denominator
    #
    # def __lt__(self, other):
    #     if self.value == 'inf' and other.value != 'inf':
    #         return False
    #     if self.value != 'inf' and other.value == 'inf':
    #         return True
    #
    #     return self.value < other.value


@dataclass
class Asteroid:
    angle: MyRational
    distance: float
    hemisphere: Hemisphere


def get_input():
    with open('input.csv') as f:
        return f.read().strip('\n')


def str_to_map(input_str: str) -> List[List[str]]:
    return list(
        map(
            list,
            input_str.split('\n')
        )
    )


def visible_asteroid_count(from_point: Tuple[int, int], asteroid_map: List[List[str]]) -> int:
    asteroid_angles = set()
    for line in range(len(asteroid_map)):
        for column in range(len(asteroid_map[0])):
            if line == from_point[0] and column == from_point[1]:
                continue

            if asteroid_map[line][column] == '#':
                if from_point[0] == line:
                    if from_point[1] - column > 0:
                        asteroid_angles.add('a')
                    else:
                        asteroid_angles.add('b')
                else:
                    slope = (from_point[1] - column) / (from_point[0] - line)
                    if from_point[0] - line > 0:
                        asteroid_angles.add(f'+{slope}')
                    else:
                        asteroid_angles.add(f'-{slope}')

    return len(asteroid_angles)


def visibility_map(asteroid_map: List[List[str]]) -> List[List[int]]:
    visib_map = [
        [0 for _ in range(len(asteroid_map[0]))] for _ in range(len(asteroid_map))
    ]
    for line in range(len(asteroid_map)):
        for column in range(len(asteroid_map[0])):
            if asteroid_map[line][column] == '#':
                visib_map[line][column] = visible_asteroid_count((line,column), asteroid_map)
            else:
                visib_map[line][column] = '.'

    return visib_map


def find_best_spot(visibility_map: List[List[int]]) -> Tuple[int, Tuple[int, int]]:
    max_vis = 0
    best_spot = None
    for line in range(len(visibility_map)):
        for column in range(len(visibility_map[0])):
            if visibility_map[line][column] == '.':
                continue

            if int(visibility_map[line][column]) > max_vis:
                max_vis = int(visibility_map[line][column])
                best_spot = (line, column)

    return max_vis, best_spot


def angle_map(asteroid_map: List[List[str]], station_coords: Tuple[int, int]) -> List[List[float]]:
    angular_map = [
        [0 for _ in range(len(asteroid_map[0]))] for _ in range(len(asteroid_map))
    ]

    for line in range(len(asteroid_map)):
        for column in range(len(asteroid_map[0])):
            if asteroid_map[line][column] == '.':
                continue


def display_line(line: List[Any]) -> None:
    print(''.join(list(map(str, line))))


if __name__ == '__main__':
    input_str = get_input()
#     input_str = """.#..#
# .....
# #####
# ....#
# ...##"""
    asteroid_map = str_to_map(input_str)
    visib_map = visibility_map(asteroid_map)
    max_vis, best_spot = find_best_spot(visib_map)

    print(max_vis)

# 3,4
# 1,0
# 2,2
#
# (4 - 0) / (3 - 1)  == (4 - 2) / (3 - 2)
#
# y = ax + b
#
# 4 = 3a + b
# 0 = a + b
#
# 4 - 0 = (3 - 1)a
# 4 - 2 = (3 - 2)a
#
#
