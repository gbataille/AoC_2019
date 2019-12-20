from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from input_utils import get_input
from intcode import Program, read_memory, run_program
from log_utils import log
import math
from pathfinder import Position
import sys
from typing import Callable, Dict, List, Set


@dataclass
class PointValueComputer:
    memory: List[int]
    _value: int = -1
    _instructions: List[int] = field(default_factory=list)

    def get_point_as_string(self, pos: Position) -> int:
        value = self.get_point_value(pos)
        if value == 1:
            return '#'
        else:
            return '.'

    def get_point_value(self, pos: Position) -> int:
        self._instructions = [pos.x, pos.y]
        program = Program(
            deepcopy(self.memory),
            0,
            self.send_robot_coordinates(),
            self.set_tractor_beam_field()
        )

        run_program(program)

        return self._value

    def send_robot_coordinates(self) -> Callable[[Program, int], Program]:
        def input_function(program: Program, position: int) -> Program:
            program.set_memory(position, self._instructions.pop(0))
            return program
        return input_function


    def set_tractor_beam_field(self) -> Callable[[Program, int], Program]:
        def output_function(program: Program, value: int) -> Program:
            self._value = value
            return program
        return output_function


@dataclass
class LineDetails:
    left_bound: int = None
    right_bound: int = None

    @property
    def is_full(self):
        return self.left_bound is not None and self.right_bound is not None

    @property
    def beam_width(self):
        return self.right_bound - self.left_bound + 1

    def display_line(self, from_column, to_column, line_nb='na', display_column_indicator=True):
        if display_column_indicator:
            print('{:>13}'.format(str(from_column)))
        data = [
            '#' if i <= self.right_bound and i >= self.left_bound else '.'
            for i in range(from_column, to_column)
        ]
        print('{:<12}'.format(f'line: {str(line_nb)}') + "".join(data))


class Mode(Enum):
    LEFT = 0
    RIGHT = 1


@dataclass
class World:
    offset: int
    next_robot_position: Position
    mode: Mode = Mode.LEFT
    tractor_beam_field: Dict[int, LineDetails] = field(default_factory=dict)
    x_coord_sent: bool = False
    _memory: List[int] = None
    _pvc: PointValueComputer = None

    def display_tractor_beam_field(self, from_line, to_line, from_column, to_column):
        print('{:>13}'.format(str(from_column)))
        for idx, line in enumerate(
            self.tractor_beam_field[from_line - self.offset:to_line - self.offset]
        ):
            data = [
                '#' if i <= line.right_bound and i >= line.left_bound else '.'
                for i in range(from_column, to_column)
            ]
            print('{:<12}'.format(str(idx + from_line)) + "".join(data))

    def init_world(self, memory: List[int]) -> None:
        self._memory = memory
        self._pvc = PointValueComputer(memory)

    def compute_tractor_beam_field(self, from_line, to_line) -> None:
        pass

    def compute_left(self, start_at: Position) -> int:
        pos = start_at
        while True:
            value = self._pvc.get_point_value(pos)
            if value == 1:
                return pos.x
            else:
                pos = Position(pos.x + 1, pos.y)

    def compute_right(self, start_at: Position) -> int:
        pos = start_at
        while True:
            value = self._pvc.get_point_value(pos)
            if value == 0:
                return pos.x - 1
            else:
                pos = Position(pos.x + 1, pos.y)

    def compute_line(self, line_idx) -> None:
        previous_line = self.tractor_beam_field.get(line_idx - 1)
        if not previous_line:
            pos = Position(int(line_idx / 10), line_idx)
        else:
            pos = Position(previous_line.left_bound, line_idx)
        log(f'for line {line_idx}, compute left starting at {pos}')
        left = self.compute_left(pos)

        if not previous_line:
            pos = Position(left, line_idx)
        else:
            pos = Position(max(left, previous_line.right_bound), line_idx)
        log(f'for line {line_idx}, compute right starting at {pos}')
        right = self.compute_right(pos)

        line_details = LineDetails(left, right)
        self.tractor_beam_field[line_idx] = line_details
        return line_details

    def set_tractor_beam_field(self, pos: Position, value: int) -> None:
        log(f'robot position {self.next_robot_position}: {value}', 'ROBOT')
        if value == 1:
            if self.mode == Mode.LEFT:
                self.mode = Mode.RIGHT
                self.tractor_beam_field.append(LineDetails(pos.x))
                # move robot to the right side of the beam (estimated)
                if len(self.tractor_beam_field) <= 1:
                    self.next_robot_position = Position(
                        int(self.next_robot_position.x + self.next_robot_position.y / 10),
                        self.next_robot_position.y
                    )
                else:
                    # move robot to the right side of the beam (based on last line)
                    self.next_robot_position = Position(
                        self.tractor_beam_field[-2].right_bound,
                        self.next_robot_position.y
                    )
            else:
                self.next_robot_position = Position(
                    self.next_robot_position.x + 1,
                    self.next_robot_position.y
                )

        else:
            if self.mode == Mode.LEFT:
                # move the robot right to look further
                self.next_robot_position = Position(
                    self.next_robot_position.x + 1,
                    self.next_robot_position.y
                )
            else:
                self.mode = Mode.LEFT
                self.tractor_beam_field[-1].right_bound = pos.x - 1
                # move the robot down one line, to the left side of the beam
                self.next_robot_position = Position(
                    self.tractor_beam_field[-1].left_bound,
                    self.next_robot_position.y + 1
                )



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

        return program

    return output_function


def get_line_details(memory, offset, nb_lines = 1):
    world = World(
        offset,
        Position(int(offset / 4), offset)
    )

    program = Program(
        deepcopy(memory),
        0,
        send_robot_coordinates(world),
        set_tractor_beam_field(world)
    )

    while True:
        program.reset(deepcopy(memory))
        program = run_program(program)

        # if world.tractor_beam_field and world.tractor_beam_field[-1].is_full:
        #     world.display_tractor_beam_field(OFFSET, OFFSET + 20, 0, 40)

        if len(world.tractor_beam_field) == nb_lines and world.tractor_beam_field[-1].is_full:
            break

    return world.tractor_beam_field[-1]


# def test(memory, width, line_nb):
#     top_line = get_line_details(memory, line_nb)
#     bottom_line = get_line_details(memory, line_nb + width - 1)
#     """ Testing a y value """
#     top_right = Position(top_line.right_bound, line_nb)
#     top_left = Position(top_line.left_bound, line_nb)
#     bottom_left = Position(top_line.right_bound - width + 1, line_nb + width - 1)
#     bottom_right = Position(top_line.right_bound, line_nb + width - 1)
#
#     print(f'Testing square between {top_right} and {bottom_left}')
#     print('\n')
#     return (
#         top_left.x >= 0 and bottom_left.x >= 0 and
#         top_right.x >= 0 and bottom_right.x >= 0 and
#         bottom_left.x >= bottom_line.left_bound and bottom_left.x <= bottom_line.right_bound
#     )
def test(world, width, line_nb):
    top_line = world.compute_line(line_nb)
    bottom_line = world.compute_line(line_nb + width - 1)
    """ Testing a y value """
    top_right = Position(top_line.right_bound, line_nb)
    top_left = Position(top_line.left_bound, line_nb)
    bottom_left = Position(top_line.right_bound - width + 1, line_nb + width - 1)
    bottom_right = Position(top_line.right_bound, line_nb + width - 1)

    log(f'Testing square between {top_right} and {bottom_left}', 'TEST')
    return (
        top_left.x >= 0 and bottom_left.x >= 0 and
        top_right.x >= 0 and bottom_right.x >= 0 and
        bottom_left.x >= bottom_line.left_bound and bottom_left.x <= bottom_line.right_bound
    )


# def dichotomy(memory, width, min_bound: int, max_bound: int) -> int:
#     log(f'Dichotomy between {min_bound} and {max_bound}', 'DICHOTOMY')
#     mid_point = math.floor((min_bound + max_bound) / 2)
#     if mid_point == min_bound:
#         if test(memory, width, mid_point):
#             return min_bound
#         elif test(memory, width, mid_point + 1):
#             return mid_point + 1
#         else:
#             raise ValueError("Dichotomy failed")
#
#     if not test(memory, width, mid_point):
#         return dichotomy(memory, width, mid_point, max_bound)
#     else:
#         return dichotomy(memory, width, min_bound, mid_point)
def dichotomy(world, width, min_bound: int, max_bound: int) -> int:
    log(f'Dichotomy between {min_bound} and {max_bound}', 'DICHOTOMY')
    mid_point = math.floor((min_bound + max_bound) / 2)
    if mid_point == min_bound:
        if test(world, width, mid_point):
            return min_bound
        elif test(world, width, mid_point + 1):
            return mid_point + 1
        else:
            raise ValueError("Dichotomy failed")

    if not test(world, width, mid_point):
        return dichotomy(world, width, mid_point, max_bound)
    else:
        return dichotomy(world, width, min_bound, mid_point)


if __name__ == '__main__':
    input_str = get_input('19')
    memory = read_memory(input_str)
    pvc = PointValueComputer(memory)

    # for y in range(40, 80):
    #     sys.stdout.write('{:<12}'.format(str(y)))
    #     for x in range(30):
    #         sys.stdout.write(pvc.get_point_as_string(Position(x, y)))
    #
    #     sys.stdout.write('\n')

    world = World(0, Position(0,0))
    world.init_world(memory)
    # for i in range(6, 13):
    #     world.compute_line(i)
    #     print(world.tractor_beam_field[i])

    WIDTH = 6
    line_solution = dichotomy(world, WIDTH, 0, 100)
    for i in range(line_solution - 30, line_solution):
        if test(world, WIDTH, i):
            line_solution = i
            break
    line_details = world.tractor_beam_field[line_solution]
    solution = Position(line_details.right_bound - WIDTH + 1, line_solution)
    print(solution)
    print(10000 * solution.x + solution.y)

    WIDTH = 100
    line_solution = dichotomy(world, WIDTH, 950, 1000)
    for i in range(line_solution - 30, line_solution):
        if test(world, WIDTH, i):
            line_solution = i
            break
    line_details = world.tractor_beam_field[line_solution]
    solution = Position(line_details.right_bound - WIDTH + 1, line_solution)
    print(solution)
    print(10000 * solution.x + solution.y)

    for y in [line_solution, line_solution + WIDTH - 1]:
        sys.stdout.write('{:<12}'.format(str(y)))
        for x in range(250, 400):
            sys.stdout.write(pvc.get_point_as_string(Position(x, y)))

        sys.stdout.write('\n')

    # line_idx = OFFSET
    # while True:
    #     line = get_line_details(memory, line_idx)
    #
    #     log(f'{line_idx} -> {line.beam_width}')
    #     if line.beam_width >= 100:
    #         break
    #
    #     line_idx += 1
    #
    # print(line_idx)
    # line.display_line(0, 500)

    # width = 100
    #
    # solution = dichotomy(memory, width, 827, 1200)
    #
    # # print(f"\n\n{solution}\n\n")
    # # for i in range(solution - 20, solution + 120):
    # #     get_line_details(memory, i).display_line(250, 400, line_nb=i, display_column_indicator=False)
    #
    # for i in range(solution - 30, solution + 1):
    #     if test(memory, width, i):
    #         print(i)
    #         solution_x = get_line_details(memory, i).right_bound - width + 1
    #         print(str(10000 * solution_x + i))
    #         break


    # width = 10
    #
    # solution = dichotomy(memory, width, 10, 1000)
    #
    # print(f"\n\n{solution}\n\n")
    # for i in range(70, 100):
    #     get_line_details(memory, i).display_line(0, 40, line_nb=i, display_column_indicator=False)
    #
    # for i in range(solution - 30, solution + 1):
    #     if test(memory, width, i):
    #         print(i)
    #         solution_x = get_line_details(memory, i).right_bound - width + 1
    #         print(str(10000 * solution_x + i))
    #         break
