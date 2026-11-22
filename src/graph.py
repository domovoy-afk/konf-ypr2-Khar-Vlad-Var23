"""Чтение тестового графа и построение подграфа зависимостей."""

from collections import deque
from pathlib import Path

from config import ROOT_DEPTH, TEST_NAME


def read_test_graph(filename):
    """Читает строки `ПАКЕТ: ЗАВИСИМОСТИ` с именами A–Z."""
    graph = {}
    with Path(filename).open(encoding="utf-8-sig") as source:
        for line_number, line in enumerate(source, 1):
            line = line.partition("#")[0].strip()
            if not line:
                continue
            package, separator, tail = line.partition(":")
            names = (package.strip(), *tail.split())
            if not separator or not all(map(TEST_NAME.fullmatch, names)):
                raise ValueError(f"{filename}:{line_number}: ожидается A: B C")
            package, *dependencies = names
            if package in graph:
                raise ValueError(f"{filename}:{line_number}: повтор {package}")
            graph[package] = tuple(dict.fromkeys(dependencies))
    return graph


def dependency_graph(packages, root, max_depth, exclude_substring):
    """Обходит граф в ширину, сохраняя глубины и исходящие ребра."""
    if root not in packages:
        raise ValueError(f"пакет {root} отсутствует в репозитории")
    depths = {root: ROOT_DEPTH}
    queue = deque([root])
    graph = {}
    while queue:
        package = queue.popleft()
        depth = depths[package]
        graph[package] = []
        if depth == max_depth:
            continue
        for dependency in packages.get(package, ()):
            if exclude_substring and exclude_substring in dependency:
                continue
            graph[package].append(dependency)
            if dependency not in depths:
                depths[dependency] = depth + 1
                queue.append(dependency)
    return graph, depths


def format_graph(graph, depths):
    """Форматирует список смежности с глубиной каждого узла."""
    return "\n".join(
        f"{depths[package]} {package}: {' '.join(dependencies)}".rstrip()
        for package, dependencies in graph.items()
    )
