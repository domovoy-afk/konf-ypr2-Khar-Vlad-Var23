"""Преобразование графа зависимостей в диаграмму D2."""

import json


def format_d2(graph):
    """Создает диаграмму с отдельными идентификаторами и подписями узлов."""
    ids = {package: f"p{index}" for index, package in enumerate(graph)}
    lines = ["direction: right", ""]
    for package, node_id in ids.items():
        lines.append(f"{node_id}: {json.dumps(package, ensure_ascii=False)}")
    root = next(iter(ids))
    lines.extend([f'{ids[root]}.style.fill: "#DBEAFE"', ""])
    for package, dependencies in graph.items():
        for dependency in dependencies:
            lines.append(f"{ids[package]} -> {ids[dependency]}")
    return "\n".join(lines).rstrip()
