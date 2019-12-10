import os
import requests
import sys

CURDIR = os.path.dirname(__file__)


def setup_day(day: int):
    day_folder = os.path.join(CURDIR, str(day))
    if not os.path.isdir(day_folder):
        print(f"Creating {day_folder}")
        os.mkdir(day_folder)

    day_input = os.path.join(day_folder, 'input.csv')
    if os.path.isfile(day_input):
        print(f"Input file {day_input} already exists")
    else:
        resp = requests.get(
            f"https://adventofcode.com/2019/day/{day}/input",
            cookies={
                'session': "53616c7465645f5fdad1274fa35662cf446990a1b76c0c17ea5a4ce4c6ac34840f7a42b2c7d94a0b88c6711da2a43a88"
            }
        )
        with open(day_input, 'wb') as input_file:
            input_file.write(resp.content)


if __name__ == '__main__':
    day = int(sys.argv[1])
    setup_day(day)
