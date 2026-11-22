"""Загрузка и проверка конфигурации CLI."""

import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

import yaml

APT_NAME = re.compile(r"[a-z0-9][a-z0-9+.-]+")
TEST_NAME = re.compile(r"[A-Z]+")
ROOT_DEPTH = 0


@dataclass(frozen=True)
class Config:
    """Параметры работы анализатора."""

    package: str
    repository: str
    test_mode: bool
    max_depth: int
    exclude_substring: str


def read_yaml(path):
    """Читает YAML и проверяет набор параметров."""
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
    except yaml.YAMLError as error:
        raise ValueError(f"ошибка YAML в {path}: {error}") from error
    if not isinstance(data, dict):
        raise ValueError("YAML должен содержать словарь параметров")
    expected = Config.__annotations__.keys()
    missing = expected - data.keys()
    if missing:
        raise ValueError(f"отсутствуют параметры: {', '.join(sorted(missing))}")
    unknown = data.keys() - expected
    if unknown:
        names = ", ".join(sorted(map(str, unknown)))
        raise ValueError(f"неизвестные параметры: {names}")
    return Config(**data)


def validate(config):
    """Проверяет типы параметров и синтаксис имени пакета."""
    if type(config.test_mode) is not bool:
        raise ValueError("test_mode: укажите true или false")
    pattern = TEST_NAME if config.test_mode else APT_NAME
    if not isinstance(config.package, str) or not pattern.fullmatch(
        config.package
    ):
        raise ValueError("package: недопустимое имя для выбранного режима")
    if type(config.max_depth) is not int or config.max_depth < ROOT_DEPTH:
        raise ValueError("max_depth: требуется целое число от 0")
    if not isinstance(config.exclude_substring, str):
        raise ValueError('exclude_substring: требуется строка, например ""')
    if not isinstance(config.repository, str) or not config.repository.strip():
        raise ValueError("repository: требуется непустой URL или путь")


def repository_path(config, directory):
    """Проверяет путь к графу или URL индекса."""
    if config.test_mode:
        path = directory / config.repository
        if not path.is_file():
            raise ValueError(f"repository: файл не найден: {path}")
        return str(path.resolve())
    try:
        url = urlsplit(config.repository)
        url.port
    except ValueError as error:
        raise ValueError("repository: некорректный URL") from error
    if url.scheme not in {"http", "https"} or not url.hostname:
        raise ValueError("repository: требуется URL с http:// или https://")
    if any(character.isspace() for character in config.repository):
        raise ValueError("repository: URL содержит пробельные символы")
    return config.repository


def load_config(filename):
    """Загружает конфигурацию из файла и нормализует путь к репозиторию."""
    path = Path(filename)
    config = read_yaml(path)
    validate(config)
    repository = repository_path(config, path.parent)
    return Config(
        config.package,
        repository,
        config.test_mode,
        config.max_depth,
        config.exclude_substring,
    )
