from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from input_utils import get_input
from intcode import Program, read_memory, run_program
from log_utils import log
import math
from pathfinder import Position
from typing import Callable, Dict, List, Set


@dataclass
class World:
    size: int
    tractor_beam_field: List[List[int]] = field(default_factory=list)
    next_robot_position: Position = Position(0, 0)
    x_coord_sent: bool = False
    nb_affected_points: int = 0
    left_line: Dict[int, int] = field(default_factory=dict)
    right_line: Dict[int, int] = field(default_factory=dict)

    def display_tractor_beam_field(self):
        for idx, line in enumerate(self.tractor_beam_field):
            print(str(idx) + '   ' + ''.join(list(map(render, line))))

    def set_tractor_beam_field(self, pos: Position, value: int) -> None:
        if not self.tractor_beam_field:
            self.tractor_beam_field = [
                [0 for _ in range(self.size)] for _ in range(self.size)
            ]

        self.tractor_beam_field[pos.y][pos.x] = value
        if value == 1 and pos.y not in self.left_line:
            self.left_line[pos.y] = pos.x

        if value == 0 and pos.y in self.left_line and pos.y not in self.right_line:
            self.right_line[pos.y] = pos.x - 1

    def move_robot_to_next_point(self) -> None:
        if self.next_robot_position.x == self.size - 1:
            if self.next_robot_position.y == self.size - 1:
                return None
            else:
                self.next_robot_position = Position(0, self.next_robot_position.y + 1)
        else:
            self.next_robot_position = Position(
                self.next_robot_position.x + 1,
                self.next_robot_position.y
            )


def render(tile: int) -> str:
    if tile == 0:
        return '.'
    else:
        return '#'


def send_robot_coordinates(world: World) -> Callable[[Program, int], Program]:

    def input_function(program: Program, position: int) -> Program:
        if not world.x_coord_sent:
            program.set_memory(position, world.next_robot_position.x)
            world.x_coord_sent = True
        else:
            program.set_memory(position, world.next_robot_position.y)
            world.x_coord_sent = False

        return program

    return input_function


def set_tractor_beam_field(world: World) -> Callable[[Program, int], Program]:

    def output_function(program: Program, value: int) -> Program:
        world.set_tractor_beam_field(world.next_robot_position, value)

        if value == 1:
            world.nb_affected_points += 1

        return program

    return output_function


if __name__ == '__main__':
    input_str = get_input('19')
    memory = read_memory(input_str)

    world = World(100)

    program = Program(
        deepcopy(memory),
        0,
        send_robot_coordinates(world),
        set_tractor_beam_field(world)
    )

    for _ in range(world.size ** 2):
        program.reset(deepcopy(memory))
        program = run_program(program)
        world.move_robot_to_next_point()

    world.display_tractor_beam_field()

    print(world.nb_affected_points)
    # we can determine the "equation" of the sides of the beam because the ratio are converging
    ####### LEFT #########
    print("########## LEFT ###########")
    print(world.nb_affected_points)
    print(world.left_line)
    tot = 0
    nb_elem = 0
    for y, x in world.left_line.items():
        # Remove the first lines that have bad precision
        if y < 50:
            continue

        ratio = y/x
        tot += ratio
        nb_elem += 1
        print(ratio)

    left_slope = tot / nb_elem
    print(f'##### left_slope: {left_slope}')
    # for y, x in world.left_line.items():
    #     if y < 35:
    #         continue
    #
    #     print(
    #         f'For y={y}, {"OK" if round(y/left_slope) == x else "NOT OK"}. '
    #         f'I would compute x={y/left_slope} (rounded to {round(y/left_slope)} where the value was {x}'
    #     )

    ####### RIGHT #########
    print("########## RIGHT ###########")
    print(world.right_line)
    tot = 0
    nb_elem = 0
    for y, x in world.right_line.items():
        # Remove the first lines that have bad precision
        if y < 50:
            continue

        ratio = y/x
        tot += ratio
        nb_elem += 1
        print(ratio)

    right_slope = tot / nb_elem
    print(f'##### right_slope: {right_slope}')
    # for y, x in world.right_line.items():
    #     if y < 35:
    #         continue
    #
    #     print(
    #         f'For y={y}, {"OK" if round(y/right_slope) == x else "NOT OK"}. '
    #         f'I would compute x={y/right_slope} (rounded to {round(y/right_slope)} where the value was {x}'
    #     )

    SIZE_SEARCHED = 100

    def test(value):
        """ Testing a y value """
        top_right = Position(round(value/right_slope), value)
        top_left = Position(top_right.x - SIZE_SEARCHED + 1, value)
        bottom_left = Position(top_right.x - SIZE_SEARCHED + 1, top_right.y + SIZE_SEARCHED - 1)
        bottom_right = Position(top_right.x, top_right.y + SIZE_SEARCHED - 1)

        print(f'Testing square between {top_right} and {bottom_left}')
        print(f'Beam at {top_right.y} between {round(top_right.y/left_slope)} and {round(top_right.y/right_slope)}')
        print(f'Beam at {bottom_right.y} between {round(bottom_right.y/left_slope)} and {round(bottom_right.y/right_slope)}')
        print('\n')
        return (
            top_left.x >= 0 and bottom_left.x >= 0 and
            top_right.x >= 0 and bottom_right.x >= 0 and
            top_left.x >= round(top_left.y / left_slope) and
            top_left.x <= round(top_left.y / right_slope) and
            bottom_left.x >= round(bottom_left.y / left_slope) and
            bottom_left.x <= round(bottom_left.y / right_slope) and
            bottom_right.x >= round(bottom_right.y / left_slope) and
            bottom_right.x <= round(bottom_right.y / right_slope)
        )

    def dichotomy(min_bound: int, max_bound: int) -> int:
        log(f'Dichotomy between {min_bound} and {max_bound}', 'DICHOTOMY')
        mid_point = math.floor((min_bound + max_bound) / 2)
        if mid_point == min_bound:
            if test(mid_point):
                return min_bound
            elif test(mid_point + 1):
                return mid_point + 1
            else:
                raise ValueError("Dichotomy failed")

        if not test(mid_point):
            return dichotomy(mid_point, max_bound)
        else:
            return dichotomy(min_bound, mid_point)

    # find the first 5x5
    result = dichotomy(30, 100000)
    print(f'\nFor size: {SIZE_SEARCHED}, found {result}, meaning point ({round(result/right_slope) - SIZE_SEARCHED}, {result})')
    print(result)
