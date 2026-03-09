# list available recipes
default:
    @just --list

# format and fix lint issues
format:
    @echo "formatting..."
    uv run ruff format src tests
    uv run ruff check --fix src tests
    @echo "format: done"

# run tests
test:
    @echo "running tests..."
    uv run pytest
    @echo "test: done"

# run all checks (format + test)
check: format test

# sync dependencies
sync:
    uv sync

# download latest IANA tzdata, regenerate flags and update info.plist
update-tz:
    @echo "updating timezone data..."
    uv run python3 tzdata/update.py
    @echo "update-tz: done"

# copy src into dist for live alfred testing
dev:
    #!/usr/bin/env bash
    set -euo pipefail
    if [[ ! -d ./dist ]]; then
        echo "no dist/ found, running full build first..." >&2
        just build
    fi
    cp -R ./src/* ./dist/
    echo "dev: copied src → dist"

# build dist from src
build:
    #!/usr/bin/env bash
    set -euo pipefail
    just update-tz
    uv sync
    echo "building dist..."

    # guard: only remove dist/ if it's inside the repo
    if [[ -e ./dist && "$(pwd)/dist" != "$(cd ./dist 2>/dev/null && pwd)" && ! -d ./dist ]]; then
        echo "[error] ./dist is not a directory, refusing to remove" >&2
        exit 1
    fi
    [[ -d ./dist ]] && rm -rf ./dist/

    cp -R ./src ./dist
    find ./dist -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    echo "build: done"

# symlink repo into alfred's workflow directory for development
setup:
    #!/usr/bin/env bash
    set -euo pipefail
    workflows_dir="$HOME/Library/Application Support/Alfred/Alfred.alfredpreferences/workflows"
    if [[ ! -d "$workflows_dir" ]]; then
        echo "[error] alfred workflows directory not found" >&2
        exit 1
    fi

    # resolve absolute path and verify info.plist exists here
    repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
    if [[ ! -f "$repo_dir/info.plist" ]]; then
        echo "[error] info.plist not found in $repo_dir — are you in the repo root?" >&2
        exit 1
    fi

    uuid=$(uuidgen | tr '[:lower:]' '[:upper:]')
    link_path="$workflows_dir/user.workflow.$uuid"

    # create symlink and verify it points back to us
    ln -s "$repo_dir" "$link_path"
    actual_target="$(readlink "$link_path")"
    if [[ "$actual_target" != "$repo_dir" ]]; then
        rm "$link_path"
        echo "[error] symlink target mismatch: expected $repo_dir, got $actual_target" >&2
        exit 1
    fi

    echo "linked → $link_path"
