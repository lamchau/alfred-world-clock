# list available recipes
default:
    @just --list

# format and fix lint issues
format:
    @echo "formatting..."
    uv run ruff format src tests
    uv run ruff check --fix src tests
    @echo "format: done"

# sync dependencies
sync:
    uv sync

# run tests
test:
    @echo "running tests..."
    uv run pytest
    @echo "test: done"

# run all checks (format + test)
check: format test

# download latest IANA tzdata, regenerate flags and update info.plist
update-tz:
    @echo "updating timezone data..."
    uv run python3 tzdata/update.py
    @echo "update-tz: done"
