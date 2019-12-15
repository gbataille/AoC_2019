from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class Position:
    x: int
    y: int


@dataclass
class Path:
    positions: List[Position] = field(default_factory=list)


def tile_content(tile_map: List[List[T]], position: Position) -> T:
    if position.y >= len(tile_map) or position.x >= len(tile_map):
        return None

    return tile_map[position.y][position.x]


def closest_tile(
    tile_map: List[List[T]], from_position: Position, tile_value: T,
    unauthorized_tile_values: Optional[Set[T]] = None
) -> Optional[Tuple[Position, Path]]:

    if unauthorized_tile_values is None:
        unauthorized_tile_values = set()

    next_to_try = [(from_position, [])]
    seen = set([from_position])
    while True:
        tile_pos, cur_path = next_to_try.pop(0)
        next_tiles = [
            tile for tile in neighbors(tile_pos)
            if tile_content(tile_map, tile) not in unauthorized_tile_values
        ]
        next_to_try.extend(
            list(map(
                lambda x: (x, cur_path + [x]),
                [tile for tile in next_tiles if tile not in seen]
            ))
        )
        seen = seen | set(next_tiles)
        if tile_content(tile_map, tile_pos) == tile_value:
            return (tile_pos, cur_path)

        if not next_to_try:
            return None


def max_distance(
    tile_map: List[List[T]], from_position: Position,
    unauthorized_tile_values: Optional[Set[T]] = None
) -> Dict[int, List[Position]]:

    if unauthorized_tile_values is None:
        unauthorized_tile_values = set()

    tiles_per_distance = {0: {from_position}}
    seen = {from_position}

    while True:
        max_dist = max(list(tiles_per_distance.keys()))
        next_tiles = set()
        for tile in tiles_per_distance[max_dist]:
            tile_neighbors = neighbors(tile)
            next_tiles = next_tiles | set(
                [
                    t for t in tile_neighbors
                    if t not in seen
                    and t.x < len(tile_map) and t.y < len(tile_map) and t.x >= 0 and t.y >= 0
                    and tile_content(tile_map, t) not in unauthorized_tile_values
                ]
            )
            seen = seen | set(next_tiles)

        if not next_tiles:
            break

        tiles_per_distance[max_dist + 1] = next_tiles

    return tiles_per_distance


def neighbors(position: Position) -> List[Position]:
    return [
        Position(position.x, position.y + 1),
        Position(position.x + 1, position.y),
        Position(position.x, position.y - 1),
        Position(position.x - 1, position.y),
    ]
