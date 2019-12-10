# input_string = "1,0,0,3,1,1,2,3,1,3,4,3,1,5,0,3,2,1,9,19,1,13,19,23,2,23,9,27,1,6,27,31,2,10,31,35,1,6,35,39,2,9,39,43,1,5,43,47,2,47,13,51,2,51,10,55,1,55,5,59,1,59,9,63,1,63,9,67,2,6,67,71,1,5,71,75,1,75,6,79,1,6,79,83,1,83,9,87,2,87,10,91,2,91,10,95,1,95,5,99,1,99,13,103,2,103,9,107,1,6,107,111,1,111,5,115,1,115,2,119,1,5,119,0,99,2,0,14,0"
# nums = list(map(int, input_string.split(',')))
#
# for n in range(len(nums)):
#     for v in range(len(nums)):
#
#         nums = list(map(int, input_string.split(',')))
#
#         # first
#         nums[1] = n
#         nums[2] = v
#
#         instr_pointer = 0
#         while True:
#             instr = nums[instr_pointer]
#
#             if instr == 99:
#                 break
#
#             num1 = nums[instr_pointer+1]
#             num2 = nums[instr_pointer+2]
#             pos = nums[instr_pointer+3]
#
#             if instr == 1:
#                 res = nums[num1] + nums[num2]
#             elif instr == 2:
#                 res = nums[num1] * nums[num2]
#             else:
#                 raise ValueError("wrong instruction")
#
#             nums[pos] = res
#
#             instr_pointer += 4
#
#         if nums[0] == 19690720:
#             print(n)
#             print(v)
#             print(100*n + v)
#             break
from dataclasses import dataclass
from typing import List


class EndProgram(Exception):
    pass


@dataclass
class ProgramState:
    memory: List[int]
    instr_pointer: int


def get_input():
    with open('input.csv') as f:
        return f.read()


def handle_1(prog_state: ProgramState):
    arg1 = prog_state.memory[prog_state.instr_pointer + 1]
    arg2 = prog_state.memory[prog_state.instr_pointer + 2]
    target = prog_state.memory[prog_state.instr_pointer + 3]

    prog_state.memory[target] = prog_state.memory[arg1] + prog_state.memory[arg2]
    prog_state.instr_pointer += 4

    return prog_state


def handle_2(prog_state: ProgramState):
    arg1 = prog_state.memory[prog_state.instr_pointer + 1]
    arg2 = prog_state.memory[prog_state.instr_pointer + 2]
    target = prog_state.memory[prog_state.instr_pointer + 3]

    prog_state.memory[target] = prog_state.memory[arg1] * prog_state.memory[arg2]
    prog_state.instr_pointer += 4

    return prog_state


def handle_3(prog_state: ProgramState):
    return prog_state


def handle_4(prog_state: ProgramState):
    return prog_state


def handle_99(prog_state: ProgramState):
    raise EndProgram('Over')


def execute_instr(prog_state: ProgramState):
    opcode = prog_state.memory[prog_state.instr_pointer]
    method_name = f'handle_{str(opcode)}'
    method = globals()[method_name]

    prog_state = method(prog_state)

    return prog_state


input = get_input()
prog_state = ProgramState(
    list(map(int, input.split(','))),
    0
)

prog_state.memory[1] = 12
prog_state.memory[2] = 2

try:
    while True:
        prog_state = execute_instr(prog_state)
except EndProgram:
    pass

print(prog_state)
