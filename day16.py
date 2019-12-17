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
    # input_str = '03081770884921959731165446850517'
    signal = signal_from_input(input_str)
    signal = Signal(signal.data * NB_INPUT_REPETITION)

    # For part 2 there is a trick.
    # An element in the output at position N does not depend on anyting before position N is the
    # input list, because of the leading 0s in the repeating pattern
    # * You don't compute anything before the offset.
    # Then you realize that len(input_list) - offset < offset
    # Which means that the mask is 0 till the offset and then 1 till the end.
    # * You just have to do a sum
    # * The smart way to do it is that the last element in a phase is the last element is the phase
    # before. The penultimate element in phase P is last element in phase P + penultimate element in
    # phate P - 1

    offset = int(input_str[:7])
    input_len = len(input_str) * 10000
    log(f'Offset {offset}, input_len {input_len}')

    stripped_input = signal.data[offset:]
    for _ in range(NB_PHASES):
        new_signal = [0 for _ in range(len(stripped_input))]
        for i in range(len(stripped_input)):
            new_signal[i*-1 - 1] = (new_signal[i*-1] + stripped_input[i*-1 - 1]) % 10
        stripped_input = new_signal

    print(''.join(list(map(str, stripped_input[:8]))))
