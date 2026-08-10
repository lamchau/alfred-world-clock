# v3.0.0

## Breaking Changes
- **Keyword changed** — the `now` and `meet` keywords have been consolidated into a single `tz` keyword. Update any hotkeys or external triggers that reference the old keywords.
- **Modifier keys reassigned** — ⌘+Enter and ⌥+Enter now create calendar meetings instead of copying ISO timestamps. ISO copy has moved to ⌃+Enter and ⇧+Enter.

## Requirements
- **`gdate` (GNU date)** — required for relative date offsets with calendar units (`days`, `weeks`, `months`, `years`). Install via Homebrew:
  ```
  brew install coreutils
  ```
  This provides `/opt/homebrew/bin/gdate`. Sub-day offsets (`3h`, `30m`) do not require `gdate`.

## Features
- **Meeting creation from timezone results** — ⌘+Enter opens default calendar app, ⌥+Enter opens the other. Outlook gets a `.ics` file; Chrome/Edge open Google Calendar. Configurable via workflow settings (Default Calendar App, Other Calendar App, Meeting Duration).
- **Relative date offsets via `gdate`** — support `days`, `weeks`, `months`, `years` (e.g. `tz 3 months`, `tz 2 weeks 3 days`, `tz -1 year`). Short forms like `3d`, `2w` are expanded automatically.
- **Ctrl/Shift modifier keys** — ⌃+Enter copies ISO with microseconds, ⇧+Enter copies ISO without. Modifiers now support passing variables to downstream actions.
- **Timezone data updater** — `just update-tz` downloads latest IANA tzdata and regenerates flags and plist entries.
- **Custom timestamp format** — configurable format string in workflow settings.

## Performance
- **Pre-computed flags dict** — timezone flags are now a dict literal instead of runtime CSV parsing.

## Refactoring
- Replace `pytz` with stdlib `zoneinfo`
- Replace `pytimeparse` with inline duration parser
- Vendor `pyflow` into `src/` (no external Python dependencies)
- Consolidate `now`/`meet` keywords into single `tz` keyword

## Build
- Migrate from `poetry` to `uv`
- Drop `pytz`, `pytimeparse`, and `alfred-pyflow` dependencies
- Add justfile recipes: `dev`, `build`, `setup`, `bump`, `release`
- Normalize line endings to LF

## Tests
- Add test suites for data module, formatters, time parsing, duration handling, `.ics` generation, and pyflow Item modifiers
