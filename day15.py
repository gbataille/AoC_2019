from dataclasses import dataclass, field
from enum import Enum
from input_utils import get_input
from intcode import Program, run_program, read_memory, EndProgram
from log_utils import log
import os
from pathfinder import closest_tile, max_distance, Position
import time
from typing import List, Set


AREA_SIZE = 50
ROBOT_START = int(AREA_SIZE/2)
DISPLAY = False
DISPLAY_SLEEP = 0.01


class DirectionInstruction(Enum):
    NORTH = 1
    SOUTH = 2
    WEST = 3
    EAST = 4

    def move(self, position: 'Position') -> 'Position':
        if self == DirectionInstruction.NORTH:
            return Position(position.x, position.y - 1)
        elif self == DirectionInstruction.EAST:
            return Position(position.x + 1, position.y)
        elif self == DirectionInstruction.SOUTH:
            return Position(position.x, position.y + 1)
        else:   # WEST
            return Position(position.x - 1, position.y)

    @staticmethod
    def direction_to(from_pos: 'Position', to_pos: 'Position') -> 'DirectionInstruction':
        if to_pos.x - from_pos.x < 0:
            return DirectionInstruction.WEST
        elif to_pos.x - from_pos.x > 0:
            return DirectionInstruction.EAST
        elif to_pos.y - from_pos.y > 0:
            return DirectionInstruction.SOUTH
        else:
            return DirectionInstruction.NORTH


class StatusNotification(Enum):
    WALL = 0
    MOVED = 1
    MOVED_AND_TANK_FOUND = 2


class Tile(Enum):
    OUT = -100
    UNEXPLORED = -1
    WALL = 0
    EMPTY = 1
    OXYGEN = 2
    ROBOT = 3


def render_tile(tile: Tile):
    if type(tile) == int:
        return str(tile)

    if tile == Tile.UNEXPLORED:
        return ' '
    elif tile == Tile.WALL:
        return '#'
    elif tile == Tile.EMPTY:
        return '.'
    elif tile == Tile.OXYGEN:
        return 'O'
    elif tile == Tile.ROBOT:
        return 'D'
    elif tile == Tile.OUT:
        return '-'


@dataclass
class Robot:
    position: Position = Position(ROBOT_START, ROBOT_START)

    def move(self, direction: DirectionInstruction) -> None:
        self.position = direction.move(self.position)


def starting_area():
    area = (
        [[Tile.OUT for _ in range(AREA_SIZE)]] +
        [[Tile.OUT] + [Tile.UNEXPLORED for _ in range(AREA_SIZE - 2)] + [Tile.OUT] for _ in range(AREA_SIZE - 2)] +
        [[Tile.OUT for _ in range(AREA_SIZE)]]
    )
    area[ROBOT_START][ROBOT_START] = Tile.EMPTY
    return area


@dataclass
class Area:
    tiles: List[List[Tile]] = field(default_factory=starting_area)
    robot: Robot = Robot()
    current_instruction: DirectionInstruction = DirectionInstruction.NORTH
    current_path: List[Position] = None
    tank_position: Position = None

    def display(self, force=False) -> None:
        if not DISPLAY and not force:
            return

        os.system('clear')
        for idx, line in enumerate(self.tiles):
            pretty_line = list(map(render_tile, line))

            if idx == self.robot.position.y:
                pretty_line[self.robot.position.x] = 'D'

            print(''.join(pretty_line))

        time.sleep(DISPLAY_SLEEP)

    def get_tile_at_position(self, position: Position) -> Tile:
        return self.tiles[position.y][position.x]

    def set_tile_under_robot(self, tile: Tile) -> None:
        self.tiles[self.robot.position.y][self.robot.position.x] = tile

    def set_tile_in_front_of_robot(self, tile: Tile) -> None:
        in_front = self.current_instruction.move(self.robot.position)
        self.tiles[in_front.y][in_front.x] = tile

    def move_robot(self):
        self.robot.move(area.current_instruction)


def send_instruction(area: Area):

    def input_function(program: Program, position: int) -> Program:
        log(f'At {area.robot.position}. Instructing {area.current_instruction}')
        program.set_memory(position, area.current_instruction.value)
        return program

    return input_function


def update_area_map(area: Area):

    def output_function(program: Program, value: int) -> Program:
        log(f'At {area.robot.position}, status in {value}')

        if value == StatusNotification.MOVED.value:
            area.move_robot()
            area.set_tile_under_robot(Tile.EMPTY)
        elif value == StatusNotification.MOVED_AND_TANK_FOUND.value:
            area.move_robot()
            area.tank_position = area.robot.position
            area.set_tile_under_robot(Tile.OXYGEN)
        else:
            area.set_tile_in_front_of_robot(Tile.WALL)

        area.display()

        if value == StatusNotification.MOVED_AND_TANK_FOUND.value:
            log(f'Found oxygen at {area.robot.position}')

        if not area.current_path:
            closest = closest_tile(
                area.tiles, area.robot.position, Tile.UNEXPLORED, {Tile.WALL, Tile.OUT}
            )
            if closest is None:
                raise EndProgram('Entire map discovered')

            next_tile_pos, path = closest
            area.current_path = path
            log(f'At {area.robot.position}. Going to {next_tile_pos}')

        next_tile = area.current_path.pop(0)
        area.current_instruction = DirectionInstruction.direction_to(
            area.robot.position, next_tile
        )
        log(f'At {area.robot.position}. Next tile is {next_tile}. Moving {area.current_instruction}')

        return program

    return output_function


if __name__ == '__main__':
    input_str = get_input('15')
    memory = read_memory(input_str)
    area = Area()
    area.display()

    program = Program(
        memory,
        0,
        send_instruction(area),
        update_area_map(area)
    )

    run_program(program)

    # At the end of the program, the robot is on the tank
    tank_pos = area.tank_position
    print(f'tank_pos {tank_pos}')
    _, shortest_path = closest_tile(
        area.tiles, Position(ROBOT_START, ROBOT_START), Tile.OXYGEN, {Tile.WALL, Tile.OUT}
    )
    print(len(shortest_path))
    area.display(force=True)
    print(f'tank_pos {tank_pos}')

    tiles_per_distance = max_distance(area.tiles, tank_pos, {Tile.WALL, Tile.OUT})
    for dist, tiles in tiles_per_distance.items():
        for tile in tiles:
            area.tiles[tile.y][tile.x] = dist % 10

    area.display(force=True)
    print(max(list(tiles_per_distance.keys())))
