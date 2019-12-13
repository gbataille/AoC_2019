from dataclasses import dataclass, field
from enum import Enum
from input_utils import get_input
from intcode import Program, read_memory, run_program
from log_utils import log
import os
import time
from typing import List, Set


def render(value: int):
    if value == 0:
        return ' '
    if value == 1:
        return '-'
    if value == 2:
        return 'X'
    if value == 3:
        return '_'
    if value == 4:
        return 'O'


@dataclass
class Scene:
    tiles: List[List[int]] = field(
        default_factory=lambda: [[0 for _ in range(100)] for _ in range(100)]
    )
    next_x: int = None
    next_y: int = None
    max_x: int = 0
    max_y: int = 0
    score: int = 0
    last_ball_x = 0
    last_paddle_x = 0

    def set_value(self, x, y, value):
        try:
            if x > self.max_x:
                self.max_x = x
            if y > self.max_y:
                self.max_y = y

            self.tiles[y][x] = value

            if value == 3:
                self.last_paddle_x = x
            elif value == 4:
                self.last_ball_x = x

        except Exception:
            print(f'failed with x = {x} and y = {y}')
            raise

    def show(self):
        os.system('clear')
        print(f'Score: {self.score}')
        for line_idx in range(self.max_y + 1):
            line = self.tiles[line_idx]
            cols = [line[i] for i in range(self.max_x + 1)]
            print(' '.join(list(map(render, cols))))

        time.sleep(0.02)

    def count_blocks(self):
        count = 0
        for line_idx in range(self.max_y + 1):
            line = self.tiles[line_idx]
            cols = [line[i] for i in range(self.max_x + 1) if line[i] == 2]
            count += len(cols)

        return count


def play(scene: Scene) -> None:

    def input_function(program: Program, position: int) -> Program:
        ball_x = scene.last_ball_x
        paddle_x = scene.last_paddle_x

        if ball_x == paddle_x:
            program.set_memory(position, 0)
        elif ball_x < paddle_x:
            program.set_memory(position, -1)
        else:
            program.set_memory(position, 1)

        return program

    return input_function


def update_scene(scene: Scene) -> None:

    def output_function(program: Program, value: int) -> Program:
        if scene.next_x is None:
            scene.next_x = value
        elif scene.next_y is None:
            scene.next_y = value
        else:
            if scene.next_x == -1 and scene.next_y == 0:
                scene.score = value
                scene.show()
            else:
                scene.set_value(scene.next_x, scene.next_y, value)
                if value == 4:
                    scene.show()

            scene.next_x = None
            scene.next_y = None

        return program

    return output_function


if __name__ == '__main__':
    input_str = get_input('13')
    scene = Scene()
    memory = read_memory(input_str)
    memory[0] = 2
    program = Program(
        memory,
        0,
        play(scene),
        update_scene(scene)
    )
    program = run_program(program)
