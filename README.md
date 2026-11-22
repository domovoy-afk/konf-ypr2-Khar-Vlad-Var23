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

Прототип печатает пять проверенных параметров как `ключ=значение`.
Примеры ошибок всех параметров есть в `tests/test_config.py`.
