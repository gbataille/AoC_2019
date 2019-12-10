from dataclasses import dataclass
from enum import Enum
import os
from typing import List


class EndProgram(Exception):
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
class ProgramState:
    memory: List[int]
    instr_pointer: int
    instr_pointer_modified: bool = False

    def set_instr_pointer(self, value: int) -> 'ProgramState':
        self.instr_pointer = value
        self.instr_pointer_modified = True
        return self

    def set_memory(self, pos: int, value: int) -> 'ProgramState':
        self.memory[pos] = value
        return self

    def move_instr_pointer(self, instr_params_count: int) -> 'ProgramState':
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


def get_params(prog_state: ProgramState, opcode: int, param_modes: List[ParamMode]) -> List[Param]:
    params = []
    for idx in range(OPCODE_PARAM_COUNT[opcode]):
        if idx >= len(param_modes):
            mode = 0
        else:
            mode = param_modes[idx]

        params.append(
            Param(
                prog_state.memory[prog_state.instr_pointer + idx + 1],
                mode
            )
        )

    return params


def param_value(prog_state: ProgramState, param: Param) -> int:
    if param.mode == ParamMode.Value:
        return param.value
    else:
        return prog_state.memory[param.value]


def handle_operation(prog_state: ProgramState) -> ProgramState:
    int_instr = prog_state.memory[prog_state.instr_pointer]
    instr = read_instr(int_instr)

    params = get_params(prog_state, instr.opcode, instr.parameter_modes)

    method_name = f'handle_{str(instr.opcode)}'
    method = globals()[method_name]
    if os.environ.get('DEBUG'):
        print('-------')
        print(f'Calling {method_name}')
        print(f'with params: {params}')
        print(f'with instr_pointer: {prog_state.instr_pointer}')
        print(f'with memory: {prog_state.memory}')
    prog_state = method(prog_state, params)
    if os.environ.get('DEBUG'):
        print('#######')
        print(f'outputs memory: {prog_state.memory}')
        print(f'outputs instr_pointer: {prog_state.memory}')

    # Move program to next instruction
    prog_state.move_instr_pointer(OPCODE_PARAM_COUNT[instr.opcode] + 1)

    return prog_state

def handle_1(prog_state: ProgramState, params: List[int]):
    if os.environ.get('DEBUG'):
        print('Summing')
        print(f'  {param_value(prog_state, params[0])}')
        print(f'  {param_value(prog_state, params[1])}')
        print(f'  and storing at {params[2].value}')
    prog_state.set_memory(params[2].value, param_value(prog_state, params[0]) + param_value(prog_state, params[1]))

    return prog_state


def handle_2(prog_state: ProgramState, params: List[int]):
    if os.environ.get('MULTIPLYING'):
        print('Summing')
        print(f'  {param_value(prog_state, params[0])}')
        print(f'  {param_value(prog_state, params[1])}')
        print(f'  and storing at {prog_state.memory[params[2].value]}')
    prog_state.set_memory(params[2].value, param_value(prog_state, params[0]) * param_value(prog_state, params[1]))

    return prog_state

def handle_3(prog_state: ProgramState, params: List[int]):
    prog_state.set_memory(params[0].value, int(input("Program input: ")))

    return prog_state


def handle_4(prog_state: ProgramState, params: List[int]):
    print(param_value(prog_state, params[0]))

    return prog_state


def handle_5(prog_state: ProgramState, params: List[int]):
    param1 = param_value(prog_state, params[0])
    param2 = param_value(prog_state, params[1])
    if param1 != 0:
        prog_state.set_instr_pointer(param2)

    return prog_state


def handle_6(prog_state: ProgramState, params: List[int]):
    param1 = param_value(prog_state, params[0])
    param2 = param_value(prog_state, params[1])
    if param1 == 0:
        prog_state.set_instr_pointer(param2)

    return prog_state


def handle_7(prog_state: ProgramState, params: List[int]):
    param1 = param_value(prog_state, params[0])
    param2 = param_value(prog_state, params[1])
    pos = params[2].value
    if param1 < param2:
        prog_state.set_memory(pos, 1)
    else:
        prog_state.set_memory(pos, 0)

    return prog_state


def handle_8(prog_state: ProgramState, params: List[int]):
    param1 = param_value(prog_state, params[0])
    param2 = param_value(prog_state, params[1])
    pos = params[2].value
    if param1 == param2:
        prog_state.set_memory(pos, 1)
    else:
        prog_state.set_memory(pos, 0)

    return prog_state


def handle_99(prog_state: ProgramState, params: List[int]):
    raise EndProgram('Over')


if __name__ == '__main__':
    input_str = get_input()
    # input_str = "3,21,1008,21,8,20,1005,20,22,107,8,21,20,1006,20,31,1106,0,36,98,0,0,1002,21,125,20,4,20,1105,1,46,104,999,1105,1,46,1101,1000,1,20,4,20,1105,1,46,98,99"
    # input_str = "3,3,1105,-1,9,1101,0,0,12,4,12,99,1"
    prog_state = ProgramState(
        list(map(int, input_str.split(','))),
        0
    )

    try:
        while True:
            prog_state = handle_operation(prog_state)
    except EndProgram:
        pass
