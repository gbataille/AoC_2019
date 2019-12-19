from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from input_utils import get_input
from log_utils import log
from intcode import Program, read_memory, run_program
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

    def display_tractor_beam_field(self):
        for line in self.tractor_beam_field:
            print(''.join(list(map(render, line))))

    def set_tractor_beam_field(self, pos: Position, value: int) -> None:
        if not self.tractor_beam_field:
            self.tractor_beam_field = [
                [0 for _ in range(self.size)] for _ in range(self.size)
            ]

        self.tractor_beam_field[pos.y][pos.x] = value
        if value == 1:
            if pos.y not in self.left_line:
                self.left_line[pos.y] = pos.x

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

    world = World(50)

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

    # we can determine the "equation" of the sides of the beam because the ratio are converging
    print(world.nb_affected_points)
    print(world.left_line)
    tot = 0
    nb_elem = 0
    for y, x in world.left_line.items():
        # Remove the first lines that have bad precision
        if y < 35:
            continue

        ratio = y/x
        tot += ratio
        nb_elem += 1
        print(ratio)

    average = tot / nb_elem
    print(f'##### average: {average}')
    for y, x in world.left_line.items():
        if y < 35:
            continue

        print(f'For y={y}, I would compute x={y/average} (rounded to {round(y/average)} where the value was {x}')
