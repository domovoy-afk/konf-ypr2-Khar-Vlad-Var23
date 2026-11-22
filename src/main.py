"""Командная строка анализатора зависимостей."""

import argparse
import json
import sys
from dataclasses import asdict

from apt_index import fetch_index
from config import load_config
from d2_graph import format_d2
from graph import dependency_graph, format_graph, loading_order, read_test_graph


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


def build_graph(config):
    """Загружает выбранный источник и выполняет BFS."""
    if config.test_mode:
        packages = read_test_graph(config.repository)
    else:
        packages = fetch_index(config.repository)
    return dependency_graph(
        packages, config.package, config.max_depth, config.exclude_substring
    )


def main():
    """Проверяет входные параметры и выполняет выбранный режим."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", help="путь к файлу YAML")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument(
        "--config-only", action="store_true", help="проверить YAML"
    )
    modes.add_argument(
        "--direct", action="store_true", help="прямые зависимости Ubuntu"
    )
    modes.add_argument("--order", action="store_true", help="порядок загрузки")
    modes.add_argument("--graph", action="store_true", help="список смежности")
    args = parser.parse_args()
    try:
        config = load_config(args.config)
        if args.config_only:
            show_config(config)
        elif args.direct:
            show_direct(config)
        else:
            graph, depths = build_graph(config)
            if args.order:
                print("\n".join(loading_order(graph)))
            elif args.graph:
                print(format_graph(graph, depths))
            else:
                print(format_d2(graph))
    except (OSError, ValueError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
