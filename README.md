# Chat History To Project

Prepare an exported ChatGPT conversation history for use as files in a ChatGPT Project.

The tool runs locally, accepts the official ChatGPT export as a ZIP, directory, or conversation JSON file, and writes upload-ready JSON parts.

## Documentation

- [`PRODUCT.md`](PRODUCT.md) — product scope, supported inputs, CLI behavior and output rules.
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — technical architecture, module boundaries and accepted technical decisions.
- [`AGENTS.md`](AGENTS.md) — instructions for coding agents working in this repository.

## Prerequisites

- Python 3.10+
- `pipx`, `pip`, or `uv`

## Installation

With `pipx`:

```bash
pipx install git+https://github.com/Akilaydin/Chat-History-To-Project.git
```

If the pipx tools directory is not yet in `PATH`:

```bash
pipx ensurepath
```

With `uv`:

```bash
uv tool install git+https://github.com/Akilaydin/Chat-History-To-Project.git
```

For a reproducible installation of a published version, select its Git tag:

```bash
uv tool install git+https://github.com/Akilaydin/Chat-History-To-Project.git@v1.0.0
```

If the uv tools directory is not yet in `PATH`:

```bash
uv tool update-shell
```

## Usage

```bash
chat-history-to-project chatgpt-export.zip
```

Run `chat-history-to-project --help` for all options.

From a clone:

```bash
uv sync
uv run chat-history-to-project path/to/export.zip
```

The thin legacy launcher can also be used:

```bash
python run.py path/to/export.zip
```

## Configuration

No secrets, API keys, or external services are required.

The default ChatGPT plan preset is `plus`. Other plan presets and explicit file limits are CLI options; see `PRODUCT.md`.

## Development and releases

GitHub Actions runs Ruff, unit tests on Python 3.10–3.14, and a package-build smoke test for PRs into `main`. Changes are reviewed and merged through pull requests.

After `main` passes CI, an explicitly pushed tag matching the version in `pyproject.toml` (for example, `v1.0.0`) triggers the release workflow. It validates the tag is reachable from `main`, repeats checks, builds the source distribution and wheel, and publishes both as a GitHub Release. Releases are not created automatically by merging PRs.

The project is installed directly from GitHub; publishing to PyPI is not configured.

