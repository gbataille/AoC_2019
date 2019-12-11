def get_input(folder: str) -> str:
    with open(f'{folder}/input.csv') as f:
        return f.read().strip('\n')
