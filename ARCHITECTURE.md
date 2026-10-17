# Architecture

`ARCHITECTURE.md` is the technical source of truth for the current system structure. Product behavior belongs in `PRODUCT.md`.

## Fixed decisions

### Runtime and packaging

- The project is a Python CLI package targeting Python 3.10+.
- Packaging is defined in `pyproject.toml` using setuptools.
- The installed console entry point is `chat-history-to-project = chat_history_to_project.cli:main`.
- `run.py` is a thin repository launcher and must not contain business logic.
- `uv.lock` is committed to keep the development environment reproducible.
- Runtime dependencies are kept minimal; currently tiktoken is the only direct runtime dependency.

### Input contract

- The parser targets the official ChatGPT export format.
- The project does not attempt generic schema detection or repair of arbitrary malformed exports.
- Numbered conversation files are treated as one logical export and processed in numeric order.
- When numbered files exist, a legacy `conversations.json` alongside them is ignored to avoid duplicate processing.
- Input JSON files are decoded one at a time; the entire multi-file export is not materialized in memory.
- Empty placeholder objects found in official exports and non-visible internal message records are omitted.

### Output and limits

- Output is compact UTF-8 JSON.
- Each conversation contains `title` and an ordered list of `messages`. Each message contains `role` and `content` only.
- Pure single-part text is serialized as a string. Multiple parts and multimodal content are kept as ordered lists without altering nested objects.
- Raw mapping IDs and graph fields (`id`, `parent`, `children`) are needed for input traversal only; they are not included in output.
- Each invocation writes to a new timestamped directory; previous runs are immutable.
- File-count limits are hard constraints, not targets.
- Per-file token and byte limits are checked against the final serialized JSON payload.
- Large conversations may be split only at message boundaries.
- Records and fragments retain their global input order across output files. Packing optimizations cannot reorder them to satisfy a file-count limit.
- Token counting uses tiktoken with `o200k_base`; the default 1.9M-token limit intentionally leaves margin below the documented ChatGPT limit.

### Quality

- Tests use the Python standard-library `unittest`.
- Ruff owns formatting and static lint checks.
- GitHub Actions runs lint plus the test suite across the supported Python versions.

## System structure

Processing flow:

```text
CLI
 │
 ▼
processor
 │
 ├── export_reader
 ▼
parser ──> models
 │
 ▼
filters
 │
 ▼
splitter ──> tokenizer
 │
 ▼
writer
```

### `cli.py`

Responsible for:

- defining command-line arguments;
- validating CLI-level argument combinations;
- mapping plan presets to file limits;
- presenting success/error information to the user.

Important boundaries:

- Must not parse export JSON.
- Must not implement splitting or file-writing logic.

### `processor.py`

Responsible for:

- orchestrating the processing pipeline;
- passing normalized options between stages;
- returning the final `ProcessResult`.

Important boundaries:

- Contains orchestration, not stage-specific business logic.

### `export_reader.py`

Responsible for:

- accepting ZIP, directory, or JSON paths;
- discovering supported conversation files;
- combining numbered exports in numeric order;
- yielding conversations incrementally, holding at most one input JSON document in memory;
- decoding JSON input.

Important boundaries:

- Does not interpret conversation structure.
- Does not filter or transform messages.

### `parser.py`

Responsible for:

- translating raw ChatGPT export objects into typed internal models;
- reconstructing the visible branch via `current_node`;
- extracting supported message content fields;
- deriving a conversation timestamp from message timestamps when needed.

Important boundaries:

- Knows the official ChatGPT export schema.
- Does not know output file limits or CLI options.

### `models.py`

Responsible for:

- typed `Conversation` and `Message` representations;
- conversion of those models into the minimal semantic output schema, preserving message sequence;
- searchable text used by filters.

### `filters.py`

Responsible for:

- date-range filtering;
- case-insensitive include/exclude text filtering.

Important boundaries:

- Works only with parsed models.
- Does not read files or write output.

### `splitter.py`

Responsible for:

- measuring conversation/output records;
- splitting oversized conversations at message boundaries;
- packing records into files without exceeding configured limits;
- enforcing the maximum output-file count;
- performing an exact final serialized-payload limit check.

Important boundaries:

- Must fail rather than emit an invalid partial result.
- Packing strategy is an implementation detail; configured limits are invariants.

### `tokenizer.py`

Responsible for:

- token counting;
- canonical compact JSON serialization used for measurement/output.

`TokenCounter` uses `encode_ordinary` so literal text resembling tokenizer special tokens is treated as normal user content.

### `writer.py`

Responsible for:

- creating the timestamped run directory;
- writing `part_NNN.json` files.

Important boundaries:

- Must not choose how records are split.
- Must not overwrite an existing run directory.

### `config.py`

Responsible for:

- plan preset constants;
- default token and byte limits;
- tokenizer encoding name.

Constants tied to external ChatGPT behavior should include the verification source/date in nearby comments or product documentation.

## Architecture principles

- Keep CLI, parsing, filtering, packing, and I/O as separate responsibilities.
- Keep the public product narrow; do not add abstractions for hypothetical integrations.
- Prefer typed internal models over passing raw dictionaries between pipeline stages.
- Verify final serialized output when enforcing external hard limits.
- Remove structural overhead but never rewrite conversation content or drop multimodal parts purely for compression.
- Fail explicitly when constraints cannot be satisfied; do not silently truncate history.
- Keep dependencies minimal and standard-library-first where practical.
- Tests should target observable invariants and realistic official-export behavior.

## Repository layout

```text
.
├── src/chat_history_to_project/
│   ├── cli.py
│   ├── config.py
│   ├── export_reader.py
│   ├── filters.py
│   ├── models.py
│   ├── parser.py
│   ├── processor.py
│   ├── splitter.py
│   ├── tokenizer.py
│   └── writer.py
├── tests/
├── run.py
├── pyproject.toml
└── uv.lock
```

## Open questions

- Whether output should eventually offer another serialization format while retaining JSON as the V1 default.
- Whether the current packing implementation needs optimization for very large histories after measurements on real exports.
