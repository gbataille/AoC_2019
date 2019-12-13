from dataclasses import dataclass, field
from enum import Enum
from input_utils import get_input
from log_utils import log
import math
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


@dataclass(frozen=True)
class CoordState:
    positions: List[int]
    velocities: List[int]

    @staticmethod
    def from_space(space: 'Space', coord: str) -> 'CoordState':
        pos = []
        vel = []
        for moon in space.moons:
            pos.append(getattr(moon.position, coord))
            vel.append(getattr(moon.velocity, f'd{coord}'))

        return CoordState(pos, vel)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash(tuple(self.positions)) * hash(tuple(self.velocities))


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


def lcm(a, b):
    return abs(a*b) // math.gcd(a, b)


def time_step(space: Space) -> Space:
    space = apply_gravity_force(space)
    space = move_moons(space)

    return space


def apply_gravity_force(last_state: Space) -> Space:
    new_moons = []
    for moon in last_state.moons:
        v = Vector(moon.velocity.dx, moon.velocity.dy, moon.velocity.dz)
        for other in last_state.moons:
            if other == moon:
                continue

            for coord in ['x', 'y', 'z']:
                delta = getattr(other.position, coord) - getattr(moon.position, coord)
                if delta != 0:
                    setattr(v, f'd{coord}', getattr(v, f'd{coord}') + int(delta / abs(delta)))

        new_moons.append(
            Moon(
                Position(
                    moon.position.x,
                    moon.position.y,
                    moon.position.z
                ),
                v
            )
        )

    return Space(new_moons)


def move_moons(last_state: Space) -> Space:
    for moon in last_state.moons:
        moon.position.x = moon.position.x + moon.velocity.dx
        moon.position.y = moon.position.y + moon.velocity.dy
        moon.position.z = moon.position.z + moon.velocity.dz

    return last_state


def parse_input(input_str: str) -> Space:
    moons = []
    for moon_str in input_str.split('\n'):
        m = re.match(r'<x=(.*), y=(.*), z=(.*)>', moon_str)
        moons.append(Moon(Position(int(m.group(1)), int(m.group(2)), int(m.group(3)))))

    return Space(moons)


if __name__ == '__main__':
    input_str = get_input('12')
#     input_str = """<x=-1, y=0, z=2>
# <x=2, y=-10, z=-7>
# <x=4, y=-8, z=8>
# <x=3, y=5, z=-1>"""
#     input_str = """<x=-8, y=-10, z=0>
# <x=5, y=5, z=10>
# <x=2, y=-7, z=3>
# <x=9, y=-8, z=-3>"""
    log(input_str)

    space0 = parse_input(input_str)
    space = parse_input(input_str)

    nb_steps = 1000

    iteration = 0
    x_state = set()
    y_state = set()
    z_state = set()

    x_cycle_size = None
    y_cycle_size = None
    z_cycle_size = None

    x = CoordState.from_space(space, 'x')
    y = CoordState.from_space(space, 'y')
    z = CoordState.from_space(space, 'z')

    print('############')
    print(x)
    print(y)
    print(z)
    print('############')

    x_state.add(x)
    y_state.add(y)
    z_state.add(z)

    while True:
    # for _ in range(nb_steps):
        iteration += 1
        space = time_step(space)

        x = CoordState.from_space(space, 'x')
        y = CoordState.from_space(space, 'y')
        z = CoordState.from_space(space, 'z')


        if x in x_state and not x_cycle_size:
            x_cycle_size = iteration
            print(x)
        else:
            x_state.add(x)
        if y in y_state and not y_cycle_size:
            y_cycle_size = iteration
            print(y)
        else:
            y_state.add(y)
        if z in z_state and not z_cycle_size:
            z_cycle_size = iteration
            print(z)
        else:
            z_state.add(z)

        if x_cycle_size and y_cycle_size and z_cycle_size:
            print('found all cycles')
            print(x_cycle_size)
            print(y_cycle_size)
            print(z_cycle_size)
            print(lcm(lcm(x_cycle_size, y_cycle_size), z_cycle_size))
            break

        if space0 == space:
            break
