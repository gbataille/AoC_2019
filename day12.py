from dataclasses import dataclass, field
from enum import Enum
from input_utils import get_input
from log_utils import log
import re
from typing import List, Set


@dataclass
class Position:
    x: int
    y: int
    z: int


@dataclass
class Vector:
    dx: int
    dy: int
    dz: int


@dataclass
class Moon:
    position: Position
    velocity: Vector = field(default_factory=lambda: Vector(0, 0, 0))

    @property
    def energy(self):
        return self.kinetic_energy * self.potential_energy

    @property
    def kinetic_energy(self):
        return abs(self.velocity.dx) + abs(self.velocity.dy) + abs(self.velocity.dz)

    @property
    def potential_energy(self):
        return abs(self.position.x) + abs(self.position.y) + abs(self.position.z)


@dataclass
class Space:
    moons: List[Moon]

    @property
    def total_energy(self):
        energy = 0
        for moon in self.moons:
            energy += moon.energy

        return energy


@dataclass
class SpaceTime:
    state: List[Space]


def time_step(space_time: SpaceTime) -> SpaceTime:
    apply_gravity_force(space_time)
    move_moons(space_time)

    return space_time


def apply_gravity_force(space_time: SpaceTime) -> SpaceTime:
    last_state = space_time.state[-1]
    for moon in last_state.moons:
        for other in last_state.moons:
            if other == moon:
                continue

            for coord in ['x', 'y', 'z']:
                delta = getattr(other.position, coord) - getattr(moon.position, coord)
                if delta != 0:
                    setattr(moon.velocity, f'd{coord}', getattr(moon.velocity, f'd{coord}') + int(delta / abs(delta)))

    return space_time


def move_moons(space_time: SpaceTime) -> SpaceTime:
    last_state = space_time.state[-1]
    new_moons = []
    for moon in last_state.moons:
        new_moons.append(
            Moon(
                Position(
                    moon.position.x + moon.velocity.dx,
                    moon.position.y + moon.velocity.dy,
                    moon.position.z + moon.velocity.dz
                ),
                moon.velocity
            )
        )

    space_time.state.append(Space(new_moons))
    return space_time


def parse_input(input_str: str) -> SpaceTime:
    moons = []
    for moon_str in input_str.split('\n'):
        m = re.match(r'<x=(.*), y=(.*), z=(.*)>', moon_str)
        moons.append(Moon(Position(int(m.group(1)), int(m.group(2)), int(m.group(3)))))

    space = Space(moons)
    return SpaceTime([space])


if __name__ == '__main__':
    input_str = get_input('12')
#     input_str = """<x=-1, y=0, z=2>
# <x=2, y=-10, z=-7>
# <x=4, y=-8, z=8>
# <x=3, y=5, z=-1>"""
    log(input_str)

    space_time = parse_input(input_str)
    log(space_time)

    nb_steps = 1000

    for _ in range(nb_steps):
        space_time = time_step(space_time)

    log("---------")
    for state in space_time.state:
        log(state.moons[0])

    print(space_time.state[-1].total_energy)
