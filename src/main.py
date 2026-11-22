"""Командная строка анализатора зависимостей."""

import argparse
import json
import sys
from dataclasses import asdict

from config import load_config


def show_config(config):
    """Печатает пять параметров в формате ключ-значение."""
    for name, value in asdict(config).items():
        print(f"{name}={json.dumps(value, ensure_ascii=False)}")


def main():
    """Проверяет входные параметры и запускает анализ."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", help="путь к файлу YAML")
    args = parser.parse_args()
    try:
        show_config(load_config(args.config))
    except (OSError, ValueError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
