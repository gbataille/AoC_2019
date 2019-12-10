from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
import itertools
import os
from typing import List

in_value = [-1]
out_value = 0


class EndProgram(Exception):
    pass


class HaltedProgram(Exception):
    pass


class ParamMode(Enum):
    Position = 0
    Value = 1


OPCODE_PARAM_COUNT = {
    1: 3,
    2: 3,
    3: 1,
    4: 1,
    5: 2,
    6: 2,
    7: 3,
    8: 3,
    99: 0,
}


@dataclass
class Program:
    memory: List[int]
    instr_pointer: int
    inputs: List[int]
    instr_pointer_modified: bool = False
    latest_output: int = None
    done: bool = False

    def set_instr_pointer(self, value: int) -> 'Program':
        self.instr_pointer = value
        self.instr_pointer_modified = True
        return self

    def set_memory(self, pos: int, value: int) -> 'Program':
        self.memory[pos] = value
        return self

    def move_instr_pointer(self, instr_params_count: int) -> 'Program':
        if self.instr_pointer_modified:
            self.instr_pointer_modified = False
        else:
            self.instr_pointer += instr_params_count

        return self


@dataclass
class Param:
    value: int
    mode: ParamMode


@dataclass
class Instruction:
    opcode: int
    parameter_modes: List[ParamMode]

    def __len__(self):
        return 1 + len(self.parameter_modes)


@dataclass
class Amplifier:
    phase_setting: int
    program: Program

    def set_input(self, value: int):
        self.program.inputs.append(value)

    def get_output(self):
        if self.program.latest_output is None:
            raise ValueError("No available output value")

        value = self.program.latest_output
        self.program.latest_output = None
        return value


def get_input():
    with open('input.csv') as f:
        return f.read()


def read_instr(int_instr: int) -> Instruction:
    param_modes = list(map(lambda x: ParamMode(int(x)), str(int_instr)[:-2]))
    param_modes.reverse()
    return Instruction(
        int(str(int_instr)[-2:]),
        param_modes
    )


def get_params(program: Program, opcode: int, param_modes: List[ParamMode]) -> List[Param]:
    params = []
    for idx in range(OPCODE_PARAM_COUNT[opcode]):
        if idx >= len(param_modes):
            mode = 0
        else:
            mode = param_modes[idx]

        params.append(
            Param(
                program.memory[program.instr_pointer + idx + 1],
                mode
            )
        )

    return params


def param_value(program: Program, param: Param) -> int:
    if param.mode == ParamMode.Value:
        return param.value
    else:
        return program.memory[param.value]


def handle_operation(program: Program) -> Program:
    int_instr = program.memory[program.instr_pointer]
    instr = read_instr(int_instr)

    params = get_params(program, instr.opcode, instr.parameter_modes)

    method_name = f'handle_{str(instr.opcode)}'
    method = globals()[method_name]
    try:
        if os.environ.get('DEBUG'):
            print('-------')
            print(f'Calling {method_name}')
            print(f'with params: {params}')
            print(f'with instr_pointer: {program.instr_pointer}')
            print(f'with memory: {program.memory}')
        program = method(program, params)
        if os.environ.get('DEBUG'):
            print('#######')
            print(f'outputs memory: {program.memory}')
            print(f'outputs instr_pointer: {program.memory}')

    finally:
        # Move program to next instruction
        program.move_instr_pointer(OPCODE_PARAM_COUNT[instr.opcode] + 1)

    return program

def handle_1(program: Program, params: List[int]):
    if os.environ.get('DEBUG'):
        print('Summing')
        print(f'  {param_value(program, params[0])}')
        print(f'  {param_value(program, params[1])}')
        print(f'  and storing at {params[2].value}')
    program.set_memory(params[2].value, param_value(program, params[0]) + param_value(program, params[1]))

    return program


def handle_2(program: Program, params: List[int]):
    if os.environ.get('MULTIPLYING'):
        print('Summing')
        print(f'  {param_value(program, params[0])}')
        print(f'  {param_value(program, params[1])}')
        print(f'  and storing at {program.memory[params[2].value]}')
    program.set_memory(params[2].value, param_value(program, params[0]) * param_value(program, params[1]))

    return program

def handle_3(program: Program, params: List[int]):
    input_value = program.inputs.pop(0)
    program.set_memory(params[0].value, input_value)

    return program


def handle_4(program: Program, params: List[int]):
    program.latest_output = param_value(program, params[0])

    raise HaltedProgram()


def handle_5(program: Program, params: List[int]):
    param1 = param_value(program, params[0])
    param2 = param_value(program, params[1])
    if param1 != 0:
        program.set_instr_pointer(param2)

    return program


def handle_6(program: Program, params: List[int]):
    param1 = param_value(program, params[0])
    param2 = param_value(program, params[1])
    if param1 == 0:
        program.set_instr_pointer(param2)

    return program


def handle_7(program: Program, params: List[int]):
    param1 = param_value(program, params[0])
    param2 = param_value(program, params[1])
    pos = params[2].value
    if param1 < param2:
        program.set_memory(pos, 1)
    else:
        program.set_memory(pos, 0)

    return program


def handle_8(program: Program, params: List[int]):
    param1 = param_value(program, params[0])
    param2 = param_value(program, params[1])
    pos = params[2].value
    if param1 == param2:
        program.set_memory(pos, 1)
    else:
        program.set_memory(pos, 0)

    return program


def handle_99(program: Program, params: List[int]):
    raise EndProgram('Over')


def run_program(program: Program) -> Program:
    if program.done:
        raise ValueError("Cannot run an already finished program")

    try:
        while True:
            # Run till its halted
            program = handle_operation(program)
    except HaltedProgram:
        pass
    except EndProgram:
        print("############# END REACHED ###############")
        program.done = True
        pass


def create_amplifier(phase_setting: int, memory: List[int]) -> Amplifier:
    start_memory = deepcopy(memory)
    program = Program(start_memory, 0, [phase_setting])
    return Amplifier(phase_setting, program)


def find_output_signal(start_memory: List[int]):
    max_output = -1
    best_sequence = []
    for input_sequence in itertools.permutations(range(5, 10), 5):
        amplifiers = [create_amplifier(x, start_memory) for x in input_sequence]

        # Init of amplifier 0
        amplifiers[0].set_input(0)

        amp_idx = 0
        e_output = -1
        while True:
            # Run one amplifier, get the output, pass it as input of the next amplifier
            current_amplifier = amplifiers[amp_idx]
            next_amplifier = amplifiers[(amp_idx + 1) % len(amplifiers)]
            if os.environ.get("DEBUG_AMP"):
                print(f"running amplifier {amp_idx} with inputs {current_amplifier.program.inputs}, and program pointer {current_amplifier.program.instr_pointer}")

            run_program(current_amplifier.program)

            if current_amplifier.program.done:
                break

            output = current_amplifier.get_output()
            if os.environ.get("DEBUG_AMP"):
                print(f"output of amplifier {amp_idx}: {output}")

            if amp_idx == 4:
                e_output = output
            next_amplifier.set_input(output)

            amp_idx = (amp_idx + 1) % len(amplifiers)

        if e_output > max_output:
            max_output = e_output
            best_sequence = input_sequence

    print(best_sequence)
    print(max_output)


if __name__ == '__main__':
    input_str = get_input()
    # input_str = "3,26,1001,26,-4,26,3,27,1002,27,2,27,1,27,26,27,4,27,1001,28,-1,28,1005,28,6,99,0,0,5"
    # input_str = "3,52,1001,52,-5,52,3,53,1,52,56,54,1007,54,5,55,1005,55,26,1001,54,-5,54,1105,1,12,1,53,54,53,1008,54,0,55,1001,55,1,55,2,53,55,53,4,53,1001,56,-1,56,1005,56,6,99,0,0,0,0,10"

    start_memory = list(map(int, input_str.split(',')))
    find_output_signal(start_memory)
