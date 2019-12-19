from dataclasses import dataclass, field
from enum import Enum
from input_utils import get_input
from log_utils import log
from pathfinder import *
from typing import Callable, List, Set


@dataclass
class Tile:
    value: str

    def is_corridor(self):
        return self.value == '.'

    def is_wall(self):
        return self.value == '#'


@dataclass(frozen=True)
class Door:
    symbol: str
    position: Position


@dataclass(frozen=True)
class Key:
    symbol: str
    position: Position


@dataclass
class Labyrinth:
    tile_map: List[List[Tile]]
    entrance: Position
    doors: Set[Door]
    keys: Set[Key]
    collected_keys: Set[Key] = field(default_factory=set)

    @staticmethod
    def process_map(labyrinth_map: str) -> 'Labyrinth':
        lines = labyrinth_map.split('\n')
        tile_map = [
            [0 for _ in range(len(list(lines[0])))] for _ in range(len(lines))
        ]
        entrance = None
        doors = []
        keys = []
        for y, line in enumerate(lines):
            for x, tile in enumerate(list(line)):
                tile_map[y][x] = Tile(tile)
                if tile == '@':
                    entrance = Position(x, y)
                elif tile.islower():
                    keys.append(Key(tile, Position(x, y)))
                elif tile.isupper():
                    doors.append(Door(tile, Position(x, y)))

        return Labyrinth(tile_map, entrance, doors, keys)

    def print_map(self, with_path: Path = None) -> None:

        def render(x: int, y: int) -> str:
            tile = self.tile_map[y][x]
            if tile.is_corridor() and with_path:
                if Position(x, y) in with_path:
                    return '-'

            return tile.value


        for y, line in enumerate(self.tile_map):
            print(''.join(list(map(lambda x: render(x, y), range(len(line))))))


def authorized_tile_for_labyrinth(labyrinth: Labyrinth) -> Callable[[Position], bool]:

    def authorized_tile(pos: Position) -> bool:

        if pos == Position(2, 19):
            import ipdb; ipdb.set_trace()

        tile = labyrinth.tile_map[pos.y][pos.x]
        if tile.is_wall():
            return False
        if Door(tile.value, pos) in labyrinth.doors:
            return False

        return True

    return authorized_tile

if __name__ == '__main__':
    input_str = get_input('18')
    labyrinth = Labyrinth.process_map(input_str)
    log(labyrinth, 'LABYRINTH')

    for key in labyrinth.keys:
        path = shortest_path(
            labyrinth.tile_map,
            labyrinth.entrance,
            key.position,
            authorized_tile_for_labyrinth(labyrinth),
        )
        if path:
            print(key)
            print(path)
            labyrinth.print_map(with_path=path)
