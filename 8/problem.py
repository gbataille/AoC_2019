from typing import List

LINES = 6
COLUMNS = 25


def str_input_to_layers(input_str) -> List[List[str]]:
    nb_layers = int(len(input_str) / (LINES * COLUMNS))

    input_list = list(input_str)
    for idx in range(nb_layers - 1):
        input_list.insert((LINES * COLUMNS) * (idx + 1) + idx, ',')

    layers = "".join(input_list).split(',')
    layer_matrix = []
    for layer in layers:
        layer_list = list(layer)
        for idx in range(LINES - 1):
            layer_list.insert(COLUMNS * (idx + 1) + idx, ',')

        layer_matrix.append("".join(layer_list).split(','))

    return layer_matrix



def get_input() -> str:
    with open('input.csv') as f:
        return f.read()

if __name__ == '__main__':
    input_str = get_input().strip('\n')
    # input_str = '123456789012'

    layers = str_input_to_layers(input_str)

    image = [
        [0 for _ in range(COLUMNS)] for _ in range(LINES)
    ]
    for i in range(LINES):
        for j in range(COLUMNS):
            pixel = "2"
            layer_idx = 0
            while pixel == "2":
                pixel = layers[layer_idx][i][j]
                layer_idx += 1

            image[i][j] = pixel

    for line in image:
        print("".join(line))
