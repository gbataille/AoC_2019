from dataclasses import dataclass, field
from enum import Enum
from input_utils import get_input
from log_utils import log
import math
from typing import Dict, List, Optional, Set


@dataclass
class Element:
    name: str
    qty: int

    @staticmethod
    def from_string(elem_str: str) -> 'Element':
        elem_data = elem_str.split(' ')
        elem = Element(elem_data[1], int(elem_data[0]))
        return elem


@dataclass
class Reaction:
    reactants: List[Element]
    product: Element


@dataclass
class Lab:
    know_reactions: Dict[str, Reaction] = field(default_factory=dict)
    available_reactants: Dict[str, Element] = field(default_factory=dict)
    fuel_produced: int = 0

    def add_reaction(self, reaction: Reaction) -> 'Lab':
        self.know_reactions[reaction.product.name] = reaction
        return self

    def get_reaction_for_product(self, product: str) -> Reaction:
        return self.know_reactions[product]

    def get_reactant(self, reactant_name: str) -> Element:
        elem = self.available_reactants.get(reactant_name)
        if elem is None:
            elem = Element(reactant_name, 0)
            self.available_reactants[reactant_name] = elem

        return elem

    @property
    def first_missing_reactant(self) -> Optional[Element]:
        for elem_name, elem in self.available_reactants.items():
            if elem.qty < 0 and elem.name != 'ORE':
                return elem

    def produce_missing_reactant(self, elem: Element) -> None:
        log(f'Producing {elem.qty} units of {elem.name}')
        log(self.available_reactants)
        reaction = self.know_reactions[elem.name]
        nb_reactions = math.ceil(abs(elem.qty) / reaction.product.qty)
        self.available_reactants[elem.name].qty += nb_reactions * reaction.product.qty
        log(self.available_reactants)
        for reactant in reaction.reactants:
            reactant_needed_qty = reactant.qty * nb_reactions
            lab_reactant = self.get_reactant(reactant.name)
            lab_reactant.qty -= reactant_needed_qty
        log(self.available_reactants)

    def run_lab(self) -> None:
        missing_reactant = self.first_missing_reactant
        while missing_reactant:
            self.produce_missing_reactant(missing_reactant)
            missing_reactant = self.first_missing_reactant

    def compute_ore(self, product: str) -> int:
        self.available_reactants[product] = Element(product, -1)
        self.run_lab()
        return abs(self.available_reactants['ORE'].qty)

    def produce_max_fuel(self) -> int:
        while self.available_reactants['ORE'].qty > 0:
            self.available_reactants['FUEL'] = Element('FUEL', -1)
            self.run_lab()
            self.fuel_produced += 1
            log(f'Produced {self.fuel_produced} fuel', 'FUEL')
            if self.nothing_left():
                log(f'Cycle of product {self.fuel_produced} : remaining_ore {self.available_reactants["ORE"].qty}', 'LEFT')

        return self.fuel_produced - 1       # we produced one too many

    def nothing_left(self):
        result = True
        for _, element in self.available_reactants.items():
            if element.name in ['ORE', 'FUEL']:
                continue

            if element.qty != 0:
                return False


def parse_input(input_str: str) -> Lab:
    lab = Lab()
    for line in input_str.split('\n'):
        from_elem, to_elem = line.split(' => ')
        product = Element.from_string(to_elem)

        reactants_data = from_elem.split(', ')
        reactants = []
        for reactant_data in reactants_data:
            reactants.append(Element.from_string(reactant_data))

        lab.add_reaction(Reaction(reactants, product))

    return lab


if __name__ == '__main__':
    input_str = get_input('14')
    input_str = """157 ORE => 5 NZVS
165 ORE => 6 DCFZ
44 XJWVT, 5 KHKGT, 1 QDVJ, 29 NZVS, 9 GPVTF, 48 HKGWZ => 1 FUEL
12 HKGWZ, 1 GPVTF, 8 PSHF => 9 QDVJ
179 ORE => 7 PSHF
177 ORE => 5 HKGWZ
7 DCFZ, 7 PSHF => 2 XJWVT
165 ORE => 2 GPVTF
3 DCFZ, 7 NZVS, 5 HKGWZ, 10 PSHF => 8 KHKGT"""
#     input_str = """9 ORE => 2 A
# 8 ORE => 3 B
# 7 ORE => 5 C
# 3 A, 4 B => 1 AB
# 5 B, 7 C => 1 BC
# 4 C, 1 A => 1 CA
# 2 AB, 3 BC, 4 CA => 1 FUEL"""
#     input_str = """171 ORE => 8 CNZTR
# 7 ZLQW, 3 BMBT, 9 XCVML, 26 XMNCP, 1 WPTQ, 2 MZWV, 1 RJRHP => 4 PLWSL
# 114 ORE => 4 BHXH
# 14 VRPVC => 6 BMBT
# 6 BHXH, 18 KTJDG, 12 WPTQ, 7 PLWSL, 31 FHTLT, 37 ZDVW => 1 FUEL
# 6 WPTQ, 2 BMBT, 8 ZLQW, 18 KTJDG, 1 XMNCP, 6 MZWV, 1 RJRHP => 6 FHTLT
# 15 XDBXC, 2 LTCX, 1 VRPVC => 6 ZLQW
# 13 WPTQ, 10 LTCX, 3 RJRHP, 14 XMNCP, 2 MZWV, 1 ZLQW => 1 ZDVW
# 5 BMBT => 4 WPTQ
# 189 ORE => 9 KTJDG
# 1 MZWV, 17 XDBXC, 3 XCVML => 2 XMNCP
# 12 VRPVC, 27 CNZTR => 2 XDBXC
# 15 KTJDG, 12 BHXH => 5 XCVML
# 3 BHXH, 2 VRPVC => 7 MZWV
# 121 ORE => 7 VRPVC
# 7 XCVML => 6 RJRHP
# 5 BHXH, 4 VRPVC => 5 LTCX"""

    lab = parse_input(input_str)
    log(lab)
    log('-----\n')

    lab.available_reactants['ORE'] = Element('ORE', 1000000000000)

    # print(lab.compute_ore('FUEL'))
    print(lab.produce_max_fuel())
