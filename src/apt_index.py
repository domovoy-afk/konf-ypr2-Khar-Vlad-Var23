"""Чтение индекса Ubuntu Packages без обращения к менеджеру пакетов."""

import gzip
import io
import lzma
import re
from http.client import HTTPException
from urllib.parse import urlsplit
from urllib.request import urlopen

DEFAULT_INDEX = "dists/noble/main/binary-amd64/Packages.xz"
INDEX_NAMES = {"Packages", "Packages.gz", "Packages.xz"}
FIELDS = {"Package", "Pre-Depends", "Depends"}
DEPENDENCY_NAME = re.compile(r"[a-z0-9][a-z0-9+.-]+")
TIMEOUT_SECONDS = 30


def index_url(repository):
    """Принимает прямой URL Packages или корень зеркала Ubuntu."""
    url = urlsplit(repository)
    if url.path.rsplit("/", 1)[-1] in INDEX_NAMES:
        return repository
    path = f"{url.path.rstrip('/')}/{DEFAULT_INDEX}"
    return url._replace(path=path).geturl()


def control_records(lines):
    """Разбирает абзацы deb822 и продолжения нужных полей."""
    fields = {}
    current = ""
    for line in lines:
        if not line.strip():
            if fields:
                yield fields
            fields = {}
            current = ""
            continue
        if line[0].isspace():
            if current in fields:
                fields[current] += " " + line.strip()
            continue
        current, _, value = line.partition(":")
        if current in FIELDS:
            fields[current] = value.strip()
    if fields:
        yield fields


def dependency_names(record):
    """Извлекает имена всех альтернатив обязательных зависимостей."""
    names = {}
    for field in ("Pre-Depends", "Depends"):
        for alternative in re.split(r"[,|]", record.get(field, "")):
            match = DEPENDENCY_NAME.match(alternative.strip())
            if match:
                names[match.group()] = None
    return tuple(names)


def parse_index(lines):
    """Возвращает отображение пакет → прямые зависимости."""
    packages = {}
    for record in control_records(lines):
        name = record.get("Package")
        if name:
            packages.setdefault(name, dependency_names(record))
    if not packages:
        raise ValueError("индекс Packages не содержит записей о пакетах")
    return packages


def unpack(response, url):
    """Открывает текстовый индекс с учетом формата сжатия."""
    path = urlsplit(url).path
    if path.endswith(".xz"):
        return lzma.LZMAFile(response)
    if path.endswith(".gz"):
        return gzip.GzipFile(fileobj=response)
    return response


def fetch_index(repository):
    """Загружает и разбирает индекс пакетов по HTTP(S)."""
    url = index_url(repository)
    try:
        with urlopen(url, timeout=TIMEOUT_SECONDS) as response:
            with io.TextIOWrapper(unpack(response, url), "utf-8") as lines:
                return parse_index(lines)
    except (OSError, EOFError, HTTPException, lzma.LZMAError) as error:
        message = f"не удалось прочитать индекс {url}: {error}"
        raise ValueError(message) from error
