# AGENTS.md

## Purpose

This file tells coding agents how to work with this repository.

Use the project documents as sources of truth. Do not duplicate their full content here and do not invent product or architecture decisions that are not documented.

## Contribution workflow

- Follow `CONTRIBUTING.md` for every change. Open a PR from a separate branch; never push directly to the default branch.
- After opening the PR, wait for feedback from configured automated AI reviewers (currently Codex).
- Critically assess each finding. Fix valid issues, and explain rejected findings explicitly in the PR discussion.
- Check new reviews triggered by updates. Do not merge with unaddressed substantive findings.

## Project documents

- `README.md` — project entry point, prerequisites, installation and basic usage.
- `PRODUCT.md` — product vision, supported behavior, scope, CLI rules, limits and non-goals.
- `ARCHITECTURE.md` — technical structure, component boundaries, runtime flow, constraints and accepted technical decisions.

Before a nontrivial change, read the relevant sections of these documents and inspect the current code they describe.

If documents conflict, state the conflict explicitly instead of silently choosing one interpretation.

## Working rules

- Do not present guesses as established project decisions.
- If a required decision is missing, mark it as an assumption or open question.
- Prefer the smallest implementation that satisfies the documented requirement.
- Do not expand the current product scope with speculative or "useful later" functionality.
- Reuse existing project patterns before introducing new abstractions.
- Keep changes local to the module that owns the responsibility.
- Do not change public behavior merely to simplify implementation unless the product documentation is updated accordingly.
- When a change alters product behavior, scope, CLI semantics, limits, or user-visible output, update `PRODUCT.md`.
- When a change alters module boundaries, data flow, technical invariants, dependencies, or accepted technical decisions, update `ARCHITECTURE.md`.
- When installation, prerequisites, or basic run instructions change, update `README.md`.

## Repository-specific conventions

- Python 3.10+ is the supported runtime baseline.
- Use the `src/` package layout; business logic belongs under `src/chat_history_to_project/`.
- Keep `run.py` as a thin launcher only. Do not move implementation logic back into a root script.
- The official ChatGPT export is the supported input contract. Do not add generic malformed/arbitrary JSON recovery unless product scope changes.
- Preserve the active exported conversation branch selected by `current_node`; do not reintroduce abandoned regenerated branches.
- Output messages are an ordered list of `{role, content}` objects. IDs, parents and children belong to parsing, not output. Keep text and multimodal content intact when optimizing size.
- Output limits are hard invariants. Never solve a failing split by silently exceeding them or dropping content.
- Use compact UTF-8 JSON for V1 output.
- Keep every run in a new timestamped output directory; never reuse or clear previous run directories automatically.
- Do not add a GUI, standalone executable, API integration, database, embeddings, or multi-provider support without an explicit product decision.
- Use `unittest` for tests.
- Use Ruff for linting and formatting; do not introduce a second formatter/linter without a clear need.
- Commit `uv.lock`. Do not hand-edit it; regenerate it with uv after dependency changes.
- Keep runtime dependencies minimal. Prefer the standard library where it is sufficient.
- Before changing ChatGPT plan/file/token limits, verify the current value against official OpenAI documentation and update the verification note in `PRODUCT.md`/`config.py`.

## Automatic Code Review Rules

Report only high-confidence P0/P1 issues that:
- Cause significant functional regressions.
- Introduce security vulnerabilities or data loss.
- Can cause serious production failures.

Do not report:
- Style or formatting issues.
- Minor improvements or refactoring suggestions.
- Speculative edge cases.
- Low-impact bugs.
- Missing tests unless they expose a serious risk.

Every finding must describe a concrete failure scenario.
If no qualifying issues exist, report no findings.

## Development commands

Set up/update the development environment:

```bash
uv sync
```

Run tests:

```bash
uv run python -m unittest discover -s tests -v
```

Run lint and formatting checks:

```bash
uv run ruff check .
uv run ruff format --check .
```

Apply formatting:

```bash
uv run ruff format .
```

Run the CLI from the repository:

```bash
uv run chat-history-to-project path/to/export.zip
```

Build package artifacts:

```bash
uv build
```

## Validation expectations

For behavior changes:

- add or update focused tests for the changed invariant;
- run the full test suite;
- run Ruff checks;
- run `git diff --check`.

For packaging/CLI changes, also run a CLI smoke test or `uv build` when relevant.
