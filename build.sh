#!/usr/bin/env bash
# this_file: build.sh
# Build the package into dist/, or the docs site: ./build.sh --docs [mkdocs options]
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"

if [[ "${1:-}" == --docs ]]; then
  shift
  export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"
  exec uvx --python 3.12 --from mkdocs==1.6.1 \
    --with mkdocs-material \
    --with pymdown-extensions \
    mkdocs build --config-file mkdocs.yml "$@"
fi

rm -rf dist
uv build
ls -l dist
