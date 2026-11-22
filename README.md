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

Режим `--direct` печатает имена прямых обязательных зависимостей
из полей `Pre-Depends` и `Depends`. Синтаксис этих полей описан
в [Debian Policy](https://www.debian.org/doc/debian-policy/ch-relationships.html).
В список входят все имена из альтернатив, разделенных `|`.

Принимается прямой URL `Packages`, `Packages.gz`, `Packages.xz` либо
корневой URL зеркала. Для корневого URL используется индекс
`dists/noble/main/binary-amd64/Packages.xz` (Ubuntu 24.04, main, amd64).
Если пакет описан в индексе несколько раз, берется первая запись.

## Тестовый репозиторий и обход в ширину

Формат файла: одна строка `A: B C` на пакет. Имена состоят из заглавных
латинских букв. `E:` задает пакет без зависимостей. Ссылки на имена без
собственной строки считаются листьями. Комментарии начинаются с `#`.

```sh
python src/main.py examples/test.yaml --graph
python src/main.py examples/ubuntu.yaml --direct
```

Для `examples/test.yaml` вывод имеет вид:

```text
0 A: B C
1 B: D
1 C: D
2 D: E
3 E:
```

В первой колонке кратчайшее расстояние от исходного пакета. Пакеты на
предельной глубине включаются без исходящих ребер. Фильтр учитывает
регистр и применяется к зависимостям. При `exclude_substring: D` в
примере останутся `A`, `B`, `C`. При `max_depth: 1` результат имеет
тот же набор узлов. Для `package: F` и глубины 3 будут показаны обе
дуги `F → G` и `G → F`. Очередь BFS обрабатывает каждый узел один раз.

## Порядок загрузки

```sh
python src/main.py examples/test.yaml --order
```

Программа топологически сортирует полученный подграф, ставя зависимости
перед пакетами, которым они нужны. Исходный пакет входит в список.
Для `A` результат `E, D, B, C, A`. При фильтре `D` результат
`B, C, A`. Для изолированного `H` в списке один пакет. Для цикла
`F ↔ G` программа сообщает об ошибке и завершает работу с кодом 1.

Для сравнения с APT на Ubuntu 24.04:

```sh
python src/main.py examples/ubuntu.yaml --order
apt-get --print-uris --download-only --yes --no-install-recommends install hello
```

Сравнение выполнено в Ubuntu Base 24.04.4, APT 2.8.3, amd64, на индексе
`noble/main`. При глубине 2 анализатор выдал `libgcc-s1, libc6, hello`.
С базовым состоянием системы APT вывел URI только для `hello`: обе
библиотеки уже установлены.

Чтобы повторить проверку с пустым списком установленных пакетов:

```sh
empty_status=$(mktemp)
apt-get -o "Dir::State::status=$empty_status" --print-uris --download-only \
  --yes --no-install-recommends install hello
rm "$empty_status"
```

С пустым списком APT выдал URI в порядке `gcc-14-base, libgcc-s1, libc6,
hello`. `gcc-14-base` находится на глубине 3 и не вошел в граф глубины 2.
При глубине 3 виден цикл `libc6 ↔ libgcc-s1`, и топологической сортировки
для этого графа нет. APT может подготовить список загрузок для такого
набора, так как скачивание архивов и их установка выполняются отдельно.
APT также разрешает версии, альтернативы и виртуальные пакеты.

## Диаграммы D2

В обычном режиме CLI печатает описание диаграммы D2. Стрелка идет от
пакета к его зависимости. Исходный пакет выделен голубым. В трех
примерах используется глубина 2 и отключен фильтр.

| Пакет | Конфигурация | Исходник D2 | Граф |
| --- | --- | --- | --- |
| `hello` | [YAML](examples/ubuntu.yaml) | [D2](examples/diagrams/hello.d2) | [Просмотр][hello-d2] |
| `xz-utils` | [YAML](examples/xz-utils.yaml) | [D2](examples/diagrams/xz-utils.d2) | [Просмотр][xz-d2] |
| `zstd` | [YAML](examples/zstd.yaml) | [D2](examples/diagrams/zstd.d2) | [Просмотр][zstd-d2] |

Для повторной генерации и отрисовки с установленным D2:

```sh
python src/main.py examples/ubuntu.yaml > hello.d2
d2 hello.d2 hello.svg
d2 examples/diagrams/xz-utils.d2 xz-utils.svg
d2 examples/diagrams/zstd.d2 zstd.svg
```

### Сравнение с графами APT

В той же среде Ubuntu Base команда `apt-cache dotty` строит граф в DOT.
Параметр `GivenOnly` ограничивает развертывание заданным пакетом, чтобы
сопоставить его прямые связи с первым уровнем D2.

```sh
for package in hello xz-utils zstd; do
  apt-cache -o APT::Cache::GivenOnly=true dotty "$package"
done
```

| Пакет | Общие прямые зависимости D2 и DOT | Дополнительные связи в DOT |
| --- | --- | --- |
| `hello` | `libc6` | `hello-traditional`, `hello-debhelper` |
| `xz-utils` | `libc6`, `liblzma5` | `lzma`, `xz-lzma`, `lzip`, `manpages-de`, `manpages-fr` |
| `zstd` | `libc6`, `libgcc-s1`, `liblz4-1`, `liblzma5`, `libstdc++6`, `zlib1g` | — |

Штатный DOT показывает конфликты зелеными стрелками. В D2 попадают
связи из `Depends` и `Pre-Depends`. На втором уровне D2 у `hello`
видна связь `libc6 → libgcc-s1`, которая не раскрывается при
`GivenOnly=true`. У `zstd` обе библиотеки достигаются на первом
уровне, поэтому D2 показывает обе дуги цикла между ними.
Команды описаны в справке Ubuntu
[`apt-cache`](https://manpages.ubuntu.com/manpages/noble/man8/apt-cache.8.html)
и [`apt-get`](https://manpages.ubuntu.com/manpages/noble/man8/apt-get.8.html).

[hello-d2]: https://play.d2lang.com/?script=SsksSk0uyczPs1IoykzPKOHl4uUqMLBSUMpIzcnJV-LlKjC0UlDKyUxKNgNxjCCc9ORk3WJDkICBXnFJZU6qXlpmTo6VgpKyi5Oro5urEsQYBV07hQJDkBlglhEvF2AA&sketch=0&theme=0
[xz-d2]: https://play.d2lang.com/?script=SsksSk0uyczPs1IoykzPKOHl4uUqMLBSUKqo0i0tycwpVuLlKjC0UlDKyUxKNgNxjCCcnKrcRFMQ3xjCT09O1i02BAkY6BWXVOak6qVl5uRYKSgpuzi5Orq5KkFMVtC1UygwhLOMQKaDWcYgo2GygAEA&sketch=0&theme=0
[zstd-d2]: https://play.d2lang.com/?script=XI9BC4MgGIbvQf_hwx3DyFIDD4ONtf9R1prgtkgv69ePL-k77PY8L_qgo1snG93nbWB18zPmWZ4tlQG2hTiyPFuEAebdYDVKnWS2lgeBQ5MGv0m-uzz81St0lTzE0RbFntDY9m4QM1prgGFNSD70YcKpKkP8-ql8OO8NsNPt2l3uHUsPA36GRRDVRA2RJFJEGj9CN-qdWiLsNUSSSNE59bdhRR_bbwA=&sketch=0&theme=0
