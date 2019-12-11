from dataclasses import dataclass, field
from enum import Enum
from input_utils import get_input
from intcode import Program, read_memory, run_program
from log_utils import log
from typing import List, Set


class Direction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

    def turn(self, towards: int) -> 'Direction':
        if towards == 0:
            towards = -1

        new_direction = (self.value + towards) % 4
        return Direction(new_direction)


@dataclass(frozen=True)
class Position:
    x: int
    y: int


@dataclass
class Hull:
    tiles: List[List[int]]
    painted_tiles: Set[Position] = field(default_factory=set)

    def get_value(self, pos: Position) -> int:
        return self.tiles[pos.y][pos.x]

    def paint_tile(self, pos: Position, value: int) -> None:
        log(f"Painting {pos}")
        self.tiles[pos.y][pos.x] = value
        self.painted_tiles.add(pos)

    def show(self) -> None:
        def process_line(line: List[int]) -> str:
            line = list(map(str, line))
            line_str = ''.join(line)
            line_str = line_str.replace('0', ' ')
            line_str = line_str.replace('1', '8')
            return line_str

        lines = list(map(process_line, self.tiles))
        print('\n'.join(lines))


class Action(Enum):
    Paint = 0
    Move = 1


@dataclass
class Robot:
    direction: Direction
    position: Position
    action: Action = Action.Paint

    def turn(self, towards: int) -> 'Robot':
        self.direction = self.direction.turn(towards)

    def move(self) -> 'Robot':
        if self.direction == Direction.UP:
            self.position = Position(self.position.x, self.position.y - 1)
        if self.direction == Direction.DOWN:
            self.position = Position(self.position.x, self.position.y + 1)
        if self.direction == Direction.RIGHT:
            self.position = Position(self.position.x + 1, self.position.y)
        if self.direction == Direction.LEFT:
            self.position = Position(self.position.x - 1, self.position.y)

    def switch_mode(self):
        self.action = Action((self.action.value + 1) % 2)


def scan_color(robot: Robot, hull: Hull) -> int:

    def input_function(program: Program, position: int) -> Program:
        return program.set_memory(
            position,
            hull.get_value(robot.position)
        )

    return input_function


def paint_and_move(robot: Robot, hull: Hull) -> None:

    def output_function(program: Program, value: int) -> Program:
        if robot.action == Action.Paint:
            hull.paint_tile(robot.position, value)
        else:
            robot.turn(value)
            robot.move()

        robot.switch_mode()

        return program

    return output_function


if __name__ == '__main__':
    input_str = get_input('11')
    start_memory = read_memory(input_str)

    size = 100
    robot = Robot(Direction.UP, Position(int(size/2), int(size/2)))
    hull = Hull([
        [0 for _ in range(size)] for _ in range(size)
    ])
    hull.paint_tile(Position(robot.position.x, robot.position.y), 1)

    program = Program(
        start_memory,
        0,
        scan_color(robot, hull),
        paint_and_move(robot, hull),
    )

    program = run_program(program)

    print(len(list(hull.painted_tiles)))

    hull.show()
