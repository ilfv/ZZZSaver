import os
import sys


def parse_env(path: str = ".env", encoding: str = "utf-8") -> dict[str, str]:
    data = {}

    with open(path, 'r', encoding=encoding) as file:
        for line in file.read().splitlines():
            key, value = line[:line.find("=")], line[line.find("=") + 1:]
            data[key] = value

    return data


def load_env(path: str = ".env", encoding: str = "utf-8") -> bool:
    try:
        data = parse_env(path, encoding)
    except FileNotFoundError:
        sys.stderr.write("fatal: can't find .env")
        sys.exit(1)

    try:
        for key, value in data.items():
            os.environ[key] = value
    except Exception as exc:
        return False
    
    return True
