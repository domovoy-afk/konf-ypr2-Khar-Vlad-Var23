"""Командная строка анализатора зависимостей."""

import argparse
import json
import sys
from dataclasses import asdict

from apt_index import fetch_index
from config import load_config


def show_config(config):
    """Печатает пять параметров в формате ключ-значение."""
    for name, value in asdict(config).items():
        print(f"{name}={json.dumps(value, ensure_ascii=False)}")


def show_direct(config):
    """Печатает прямые обязательные зависимости пакета."""
    if config.test_mode:
        raise ValueError("на этом этапе доступен только индекс Ubuntu")
    packages = fetch_index(config.repository)
    if config.package not in packages:
        raise ValueError(f"пакет {config.package} отсутствует в индексе")
    for dependency in packages[config.package]:
        print(dependency)


def main():
    """Проверяет входные параметры и запускает анализ."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", help="путь к файлу YAML")
    parser.add_argument("--config-only", action="store_true")
    args = parser.parse_args()
    try:
        config = load_config(args.config)
        action = show_config if args.config_only else show_direct
        action(config)
    except (OSError, ValueError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
