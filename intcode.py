from dataclasses import dataclass
from enum import Enum
import os
from typing import Callable, List


class EndProgram(Exception):
    pass


class ParamMode(Enum):
    Position = 0
    Value = 1
    Relative = 2


OPCODE_PARAM_COUNT = {
    1: 3,
    2: 3,
    3: 1,
    4: 1,
    5: 2,
    6: 2,
    7: 3,
    8: 3,
    9: 1,
    99: 0,
}


@dataclass
class Program:
    memory: List[int]
    instr_pointer: int
    input_function: Callable[['Program', int], 'Program']
    output_function: Callable[['Program', int], 'Program']
    _instr_pointer_modified: bool = False
    relative_base: int = 0

    def set_instr_pointer(self, value: int) -> 'Program':
        self.instr_pointer = value
        self._instr_pointer_modified = True
        return self

    def set_memory(self, pos: int, value: int) -> 'Program':
        if pos >= len(self.memory):
            self.memory.extend([0] * (pos - len(self.memory) + 1))

        self.memory[pos] = value
        return self

    def get_memory(self, pos: int) -> int:
        if pos >= len(self.memory):
            return 0
        else:
            return self.memory[pos]

    def move_instr_pointer(self, instr_params_count: int) -> 'Program':
        if self._instr_pointer_modified:
            self._instr_pointer_modified = False
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


def get_input():
    with open('input.csv') as f:
        return f.read()


def read_memory(mem_str: str) -> List[int]:
    return list(map(int, mem_str.split(',')))


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
            mode = ParamMode.Position
        else:
            mode = param_modes[idx]

        params.append(
            Param(
                program.get_memory(program.instr_pointer + idx + 1),
                mode
            )
        )

    return params


def param_value(program: Program, param: Param, as_position: bool = False) -> int:
    if param.mode == ParamMode.Value:
        return param.value
    elif param.mode == ParamMode.Position:
        if as_position:
            return param.value
        else:
            return program.get_memory(param.value)
    elif param.mode == ParamMode.Relative:
        if as_position:
            return program.relative_base + param.value
        else:
            return program.get_memory(program.relative_base + param.value)


def run_program(program: Program) -> Program:
    try:
        while True:
            program = handle_operation(program)
    except EndProgram:
        print("\n-- Program ended --\n")

    return program


def handle_operation(program: Program) -> Program:
    int_instr = program.get_memory(program.instr_pointer)
    instr = read_instr(int_instr)

    params = get_params(program, instr.opcode, instr.parameter_modes)

    method_name = f'handle_{str(instr.opcode)}'
    method = globals()[method_name]
    if os.environ.get('INTCODE_DEBUG'):
        print('-------')
        print(f'Calling {method_name}')
        print(f'with params: {params} of value {[param_value(program, param) for param in params]}')
        print(f'with instr_pointer: {program.instr_pointer}')
        print(f'with relative_base: {program.relative_base}')
        print(f'with memory: {program.memory}')
    program = method(program, params)
    if os.environ.get('INTCODE_DEBUG'):
        print('#######')
        print(f'outputs memory: {program.memory}')
        print(f'with relative_base: {program.relative_base}')

    # Move program to next instruction
    program.move_instr_pointer(OPCODE_PARAM_COUNT[instr.opcode] + 1)

    return program


def handle_1(program: Program, params: List[int]):
    if os.environ.get('INTCODE_DEBUG'):
        print('Summing')
        print(f'  {param_value(program, params[0])}')
        print(f'  {param_value(program, params[1])}')
        print(f'  and storing at {params[2].value}')
    program.set_memory(
        param_value(program, params[2], as_position=True),
        param_value(program, params[0]) + param_value(program, params[1])
    )

    return program


def handle_2(program: Program, params: List[int]):
    if os.environ.get('MULTIPLYING'):
        print('Summing')
        print(f'  {param_value(program, params[0])}')
        print(f'  {param_value(program, params[1])}')
        print(f'  and storing at {program.get_memory(params[2].value)}')
    program.set_memory(
        param_value(program, params[2], as_position=True),
        param_value(program, params[0]) * param_value(program, params[1])
    )

    return program


def handle_3(program: Program, params: List[int]):
    position = param_value(program, params[0], as_position=True)
    program = program.input_function(program, position)
    return program


def handle_4(program: Program, params: List[int]):
    value = param_value(program, params[0])
    program = program.output_function(program, value)
    return program


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
    pos = param_value(program, params[2], as_position=True)
    if param1 < param2:
        program.set_memory(pos, 1)
    else:
        program.set_memory(pos, 0)

    return program


def handle_8(program: Program, params: List[int]):
    param1 = param_value(program, params[0])
    param2 = param_value(program, params[1])
    pos = param_value(program, params[2], as_position=True)
    if param1 == param2:
        program.set_memory(pos, 1)
    else:
        program.set_memory(pos, 0)

    return program


def handle_9(program: Program, params: List[int]):
    param = param_value(program, params[0])
    program.relative_base += param
    return program


def handle_99(program: Program, params: List[int]):
    raise EndProgram('Over')
