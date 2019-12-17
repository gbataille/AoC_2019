from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from input_utils import get_input
from intcode import Program, read_memory, run_program
from log_utils import log
from pathfinder import Position
from typing import Dict, List, Optional, Set, Tuple

SIZE = 50


class Direction(Enum):
    LEFT = 'L'
    RIGHT = 'R'
    FORWARD = 'F'


class RobotFacing(Enum):
    UP = '^'
    DOWN = 'v'
    LEFT = '<'
    RIGHT = '>'


@dataclass
class Camera:
    read_data: str = ''


@dataclass
class Robot:
    camera: Camera = Camera()
    planned_path: str = ''
    position: Position = None
    facing: RobotFacing = RobotFacing.UP



@dataclass
class Ship:
    robot: Robot = Robot()
    scaffold_map: List[List[str]] = field(default_factory=list)
    intersections: Set[Position] = field(default_factory=set)
    n_grams_with_count: Dict[int, Tuple[int, Set[str]]] = field(default_factory=dict)

    def make_scaffold_map(self) -> None:
        self.scaffold_map = list(map(list, self.robot.camera.read_data.strip('\n').split('\n')))

    def display_scaffold_map(self, with_intersection=False) -> None:
        for idx, line in enumerate(self.scaffold_map):
            to_display = deepcopy(line)

            if with_intersection:
                for intersection in self.intersections:
                    if intersection.y == idx:
                        to_display[intersection.x] = 'O'

            print(''.join(to_display))

        print("\n\n\n")

    def is_scaffold(self, position: Position) -> bool:
        if position.x < 0 or position.y < 0:
            return False
        try:
            return self.scaffold_map[position.y][position.x] == '#'
        except IndexError:
            return False

    def compute_intersections(self):
        for y in range(1, len(self.scaffold_map) - 1):
            for x in range(1, len(self.scaffold_map[0]) - 1):
                if (
                    self.is_scaffold(Position(x, y))
                    and self.is_scaffold(Position(x + 1, y))
                    and self.is_scaffold(Position(x - 1, y))
                    and self.is_scaffold(Position(x, y + 1))
                    and self.is_scaffold(Position(x, y - 1))
                ):
                    self.intersections.add(Position(x, y))

    def add_instruction(self, direction: Direction):
        if direction == Direction.FORWARD:
            path_prefix, last_num = self.robot.planned_path.rsplit(',', 1)
            self.robot.planned_path = path_prefix + ',' + str(int(last_num) + 1)
        else:
            self.robot.planned_path += f',{direction.value},1'

    def set_start_position(self):
        for y, line in enumerate(self.robot.camera.read_data.split('\n')):
            for x, value in enumerate(line):
                if value == '^':
                    self.robot.position = Position(x, y)
                    return

    def _in_map(self, position: Position) -> bool:
        return (
            position.x >= 0 and
            position.x < len(self.scaffold_map[0]) and
            position.y >= 0 and
            position.y < len(self.scaffold_map)
        )

    def set_next_state(self) -> Optional[Direction]:
        if self.robot.facing == RobotFacing.UP:
            pos = Position(self.robot.position.x, self.robot.position.y - 1)
            if self.is_scaffold(pos):
                self.add_instruction(Direction.FORWARD)
                self.robot.position = pos
                return

            pos = Position(self.robot.position.x + 1, self.robot.position.y)
            if self.is_scaffold(pos):
                self.add_instruction(Direction.RIGHT)
                self.robot.facing = RobotFacing.RIGHT
                self.robot.position = pos
                return

            pos = Position(self.robot.position.x - 1, self.robot.position.y)
            if self.is_scaffold(pos):
                self.add_instruction(Direction.LEFT)
                self.robot.facing = RobotFacing.LEFT
                self.robot.position = pos
                return

        elif self.robot.facing == RobotFacing.RIGHT:
            pos = Position(self.robot.position.x + 1, self.robot.position.y)
            if self.is_scaffold(pos):
                self.add_instruction(Direction.FORWARD)
                self.robot.position = pos
                return

            pos = Position(self.robot.position.x, self.robot.position.y + 1)
            if self.is_scaffold(pos):
                self.add_instruction(Direction.RIGHT)
                self.robot.facing = RobotFacing.DOWN
                self.robot.position = pos
                return

            pos = Position(self.robot.position.x, self.robot.position.y - 1)
            if self.is_scaffold(pos):
                self.add_instruction(Direction.LEFT)
                self.robot.facing = RobotFacing.UP
                self.robot.position = pos
                return

        elif self.robot.facing == RobotFacing.DOWN:
            pos = Position(self.robot.position.x, self.robot.position.y + 1)
            if self.is_scaffold(pos):
                self.add_instruction(Direction.FORWARD)
                self.robot.position = pos
                return

            pos = Position(self.robot.position.x - 1, self.robot.position.y)
            if self.is_scaffold(pos):
                self.add_instruction(Direction.RIGHT)
                self.robot.facing = RobotFacing.LEFT
                self.robot.position = pos
                return

            pos = Position(self.robot.position.x + 1, self.robot.position.y)
            if self.is_scaffold(pos):
                self.add_instruction(Direction.LEFT)
                self.robot.facing = RobotFacing.RIGHT
                self.robot.position = pos
                return

        elif self.robot.facing == RobotFacing.LEFT:
            pos = Position(self.robot.position.x - 1, self.robot.position.y)
            if self.is_scaffold(pos):
                self.add_instruction(Direction.FORWARD)
                self.robot.position = pos
                return

            pos = Position(self.robot.position.x, self.robot.position.y - 1)
            if self.is_scaffold(pos):
                self.add_instruction(Direction.RIGHT)
                self.robot.facing = RobotFacing.UP
                self.robot.position = pos
                return

            pos = Position(self.robot.position.x, self.robot.position.y + 1)
            if self.is_scaffold(pos):
                self.add_instruction(Direction.LEFT)
                self.robot.facing = RobotFacing.DOWN
                self.robot.position = pos
                return

        raise IndexError('')

    def compute_robot_path(self):
        try:
            while True:
                self.set_next_state()
        except IndexError:
            self.robot.planned_path = self.robot.planned_path[1:]
            return

    def compute_n_grams(self):
        l = self.robot.planned_path.split(',')
        for size in range(1, 21):
            if len(l) % size != 0:
                continue

            nb_words = int(len(l) / size)

            cur_pos = 0
            words = set()
            for idx in range(nb_words):
                word = l[idx * size:((idx + 1) * size)]
                words.add(','.join(word))

            self.n_grams_with_count[size] = (len(words), words)


def get_camera_value(ship: Ship):

    def output_function(program: Program, value: int) -> Program:
        ship.robot.camera.read_data += chr(value)
        return program

    return output_function


main_movement_routine = 'A,B,B,A,B,C,A,C,B,C\n'
# a = ['L', ',', 4, ',', 'L', ',', 6, ',', 'L', ',', 8, ',', 'L', ',', 12, '\n']
# b = ['L', ',', 8, ',', 'R', ',', 12, ',', 'L', ',', 12, '\n']
# c = ['R', ',', 12, ',', 'L', ',', 6, ',', 'L', ',', 6, ',', 'L', ',', 8, '\n']
a = 'L,4,L,6,L,8,L,12\n'
b = 'L,8,R,12,L,12\n'
c = 'R,12,L,6,L,6,L,8\n'
end = 'n\n'
def solution_in():

    def input_function(program: Program, position: int) -> Program:
        global main_movement_routine
        global a
        global b
        global c
        global end

        if main_movement_routine:
            next_char = main_movement_routine[0]
            main_movement_routine = main_movement_routine[1:]
        elif a:
            next_char = a[0]
            a = a[1:]
        elif b:
            next_char = b[0]
            b = b[1:]
        elif c:
            next_char = c[0]
            c = c[1:]
        elif end:
            next_char = end[0]
            end = end[1:]
        else:
            raise ValueError('')

        # if type(next_char) == int:
        #     instr = next_char
        # else:
        #     instr = ord(next_char)
        # print(f'Sending {next_char}: {instr}')
        print(f'Sending {next_char}: {ord(next_char)}')

        program.set_memory(position, ord(next_char))
        return program

    return input_function


def solution_out():
    def output_function(program: Program, value: int) -> Program:
        print(f'Solution: {value}')
        return program

    return output_function



if __name__ == '__main__':
    input_str = get_input('17')
    ship = Ship()
    program = Program(
        read_memory(input_str),
        0,
        solution_in(),
        get_camera_value(ship)
    )
    program = run_program(program)
    ship.make_scaffold_map()
    ship.display_scaffold_map()
    # ship.compute_intersections()
    # ship.display_scaffold_map(with_intersection=True)

    ship.set_start_position()
    log(f'robot start position: {ship.robot.position}', 'ROBOT_START')
    ship.compute_robot_path()
    log(f'robot path: {ship.robot.planned_path}', 'ROBOT_PATH')
    ship.compute_n_grams()
    log(f'n-grams: {ship.n_grams_with_count}', 'N_GRAM')

    print(input_str)
    new_input = '2' + input_str[1:]
    print(new_input)
    program = Program(
        read_memory(new_input),
        0,
        solution_in(),
        solution_out()
    )
    run_program(program)
