# Конфигурационное управление. Практическая работа № 2

Вариант 23, группа ИКБО-32-25. CLI для анализа зависимостей пакетов Ubuntu.

## Установка и запуск

Требуется Python 3.10 или новее. Компиляция не нужна.

```sh
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

Запуск под Windows: `run.bat examples/ubuntu.yaml`. Под Linux:
`sh run.sh examples/ubuntu.yaml`. Можно запускать напрямую:
`python src/main.py examples/ubuntu.yaml`.

## Конфигурация YAML

| Поле | Значение |
| --- | --- |
| `package` | Имя пакета Ubuntu или имя из заглавных латинских букв в тестовом режиме. |
| `repository` | URL зеркала / индекса или путь к тестовому графу относительно YAML. |
| `test_mode` | `true` для файла тестового графа, `false` для Ubuntu. |
| `max_depth` | Целое число от 0. Глубина исходного пакета равна 0. |
| `exclude_substring` | Подстрока для фильтрации зависимостей. `""` отключает фильтр. |

Режим `--config-only` печатает параметры как `ключ=значение`.
Примеры ошибок всех параметров есть в `tests/test_config.py`.

## Индекс Ubuntu

По умолчанию программа печатает имена прямых обязательных зависимостей
из полей `Pre-Depends` и `Depends`. Синтаксис этих полей описан
в [Debian Policy](https://www.debian.org/doc/debian-policy/ch-relationships.html).
В список входят все имена из альтернатив, разделенных `|`.

Принимается прямой URL `Packages`, `Packages.gz`, `Packages.xz` либо
корневой URL зеркала. Для корневого URL используется индекс
`dists/noble/main/binary-amd64/Packages.xz` (Ubuntu 24.04, main, amd64).
Если пакет описан в индексе несколько раз, берется первая запись.
