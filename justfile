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

    # compile-check with the interpreter alfred actually uses (/usr/bin/python3,
    # 3.9) so build fails loudly on any syntax error the newer dev python missed.
    # runtime bytecode caching is handled separately: the script-filter command
    # sets PYTHONPYCACHEPREFIX to the workflow cache dir, which python warms on
    # the first invocation and reuses thereafter (in-tree __pycache__ is ignored
    # once a prefix is set, so there's nothing useful to ship here).
    if [[ -x /usr/bin/python3 ]]; then
        /usr/bin/python3 -m compileall -q ./dist >/dev/null
        find ./dist -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    fi
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
    # just runs recipes from a temp file, so BASH_SOURCE points at /tmp;
    # justfile_directory() reliably resolves the repo root instead
    repo_dir="{{ justfile_directory() }}"
    if [[ ! -f "$repo_dir/info.plist" ]]; then
        echo "[error] info.plist not found in $repo_dir — are you in the repo root?" >&2
        exit 1
    fi

    # a workflow's true identity is its bundleid, not its path; match on that so
    # we reuse the right install regardless of how it was added or path quirks
    # (trailing slashes, symlink vs. imported copy)
    repo_bundleid="$(/usr/bin/plutil -extract bundleid raw -o - "$repo_dir/info.plist" 2>/dev/null || true)"
    if [[ -z "$repo_bundleid" ]]; then
        echo "[error] could not read bundleid from $repo_dir/info.plist" >&2
        exit 1
    fi

    uuid=$(uuidgen | tr '[:lower:]' '[:upper:]')
    link_path="$workflows_dir/user.workflow.$uuid"

    # reuse the existing install of this workflow instead of stacking duplicates;
    # each run generates a fresh uuid, so without this guard every `just setup`
    # would add another entry and Alfred would show one row per install
    for existing in "$workflows_dir"/*; do
        [[ -e "$existing/info.plist" ]] || continue
        existing_bundleid="$(/usr/bin/plutil -extract bundleid raw -o - "$existing/info.plist" 2>/dev/null || true)"
        if [[ "$existing_bundleid" == "$repo_bundleid" ]]; then
            if [[ -L "$existing" ]]; then
                echo "already linked → $existing"
            else
                echo "[warn] $repo_bundleid already installed (not a symlink) at $existing" >&2
                echo "[warn] remove it in Alfred first if you want a dev symlink instead" >&2
            fi
            exit 0
        fi
    done

    # create symlink and verify it points back to us
    ln -s "$repo_dir" "$link_path"
    actual_target="$(readlink "$link_path")"
    if [[ "$actual_target" != "$repo_dir" ]]; then
        rm "$link_path"
        echo "[error] symlink target mismatch: expected $repo_dir, got $actual_target" >&2
        exit 1
    fi

    echo "linked → $link_path"

# bump version (e.g. just bump major, just bump minor, just bump patch)
bump level:
    #!/usr/bin/env bash
    set -euo pipefail
    current=$(grep '^version' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
    IFS='.' read -r major minor patch <<< "$current"

    case "{{ level }}" in
        major) major=$((major + 1)); minor=0; patch=0 ;;
        minor) minor=$((minor + 1)); patch=0 ;;
        patch) patch=$((patch + 1)) ;;
        *) echo "[error] expected: major, minor, or patch" >&2; exit 1 ;;
    esac

    next="$major.$minor.$patch"
    sed -i '' "s/^version = .*/version = \"$next\"/" pyproject.toml
    plutil -replace version -string "$next" info.plist
    echo "bump: $current → $next"

# create a versioned .alfredworkflow release (e.g. just release minor)
release level:
    #!/usr/bin/env bash
    set -euo pipefail

    just bump "{{ level }}"
    just check
    just build

    version=$(grep '^version' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
    bundle_id=$(plutil -extract bundleid raw -o - ./info.plist)
    name="${bundle_id##*.}"
    filename="$name.v$version.alfredworkflow"

    echo "packaging $filename..."
    mkdir -p releases
    zip -r "releases/$filename" dist img *.png info.plist

    git add pyproject.toml info.plist
    git commit -m "chore: bump version to $version"
    git tag -a "v$version" -m "v$version"

    echo ""
    echo "released $name v$version"
    echo "  releases/$filename"
    echo "  tag: v$version"
    echo ""
    echo "to publish: git push origin main --tags"
