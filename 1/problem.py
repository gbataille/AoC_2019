import math

fuel_qty = 0
with open("input.csv") as f:
    for line in f.readlines():
        mass = int(line)
        addtl_fuel_mass = math.floor(mass / 3) - 2
        fuel_qty += addtl_fuel_mass

        while True:
            addtl_fuel = math.floor(addtl_fuel_mass / 3) - 2
            if addtl_fuel <= 0:
                break

            fuel_qty += addtl_fuel
            addtl_fuel_mass = addtl_fuel

print(fuel_qty)
