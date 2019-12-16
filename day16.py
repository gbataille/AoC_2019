from dataclasses import dataclass, field
from enum import Enum
from input_utils import get_input
from log_utils import log
import math
from typing import List, Set


BASE_PATTERN = [0, 1, 0, -1]
NB_PHASES = 100
NB_INPUT_REPETITION = 10000

@dataclass
class Signal:
    data: List[int]


def repeat_pattern(idx: int) -> List[int]:
    pattern = []
    for i in BASE_PATTERN:
        pattern.extend([i] * idx)

    return pattern


def apply_transformation(signal: Signal, pattern: List[int]) -> int:
    nb_pattern = math.ceil(len(signal.data) / len(pattern))
    repeating_pattern = nb_pattern * pattern
    repeating_pattern.pop(0)
    pairs = zip(signal.data, repeating_pattern)
    mult = map(lambda x: x[0] * x[1], pairs)
    tot = sum(mult)
    return abs(tot) % 10


def run_phase(signal: Signal) -> Signal:
    new_signal = Signal([0 for _ in range(len(signal.data))])
    for idx, chunk in enumerate(signal.data):
        pattern = repeat_pattern(idx + 1)
        new_signal.data[idx] = apply_transformation(signal, pattern)

    return new_signal


def signal_from_input(input_str: str) -> Signal:
    return Signal(list(map(int, list(input_str))))


if __name__ == '__main__':
    input_str = get_input('16')
    # input_str = '80871224585914546619083218645595'
    signal = signal_from_input(input_str)
    signal = Signal(signal.data * NB_INPUT_REPETITION)
    for _ in range(NB_PHASES):
        signal = run_phase(signal)

    print(''.join(list(map(str, signal.data[:8]))))
