#!/bin/sh
project_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd) || exit 1
python=python3
if [ -x "$project_dir/.venv/bin/python" ]; then
    python=$project_dir/.venv/bin/python
fi
exec "$python" "$project_dir/src/main.py" "$@"
