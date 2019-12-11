import os


def log(msg: str, env_var: str = 'DEBUG') -> None:
    if os.environ.get(env_var):
        print(msg)
