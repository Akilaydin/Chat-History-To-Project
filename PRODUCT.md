# Product

`PRODUCT.md` is the source of truth for product behavior and current scope. Technical implementation details belong in `ARCHITECTURE.md`.

Chat History To Project is a local CLI utility for people who want to reuse an exported ChatGPT conversation history inside a ChatGPT Project.

The user provides the official ChatGPT data export. The tool extracts the visible conversation content, optionally filters the history, splits it into files that fit ChatGPT Project constraints, and writes the result locally. Conversation data is not uploaded by this tool.

The product is intentionally narrow: it prepares ChatGPT history for ChatGPT Projects.

## Current scope

Current milestone: V1 maintenance release.

### In scope

- Read the official ChatGPT export from a ZIP archive, extracted directory, or conversation JSON file.
- Support both `conversations.json` and numbered exports such as `conversations-000.json`, `conversations-001.json`, and so on.
- Keep the visible branch of regenerated conversations by following `current_node`.
- Preserve useful message content from the supported official export fields used by the current parser.
- Filter conversations by date and by text in titles/messages.
- Split output by ChatGPT Project file-count, token, and byte limits.
- Split a single large conversation between messages when it cannot fit in one output file.
- Write every run to a new timestamped output directory.
- Provide plan-based file-count presets and explicit CLI overrides.
- Run fully locally except for dependency/tool metadata downloads such as tiktoken's public tokenizer vocabulary.

### Out of scope

- GUI or standalone executable distribution.
- Uploading files to ChatGPT automatically.
- Calling the OpenAI API or requiring an API key.
- Importing arbitrary third-party or hand-written conversation schemas.
- Repairing malformed exports.
- Supporting Claude, Gemini, Codex, Cursor, or other providers as input/output targets.
- LLM-based summarization, semantic classification, embeddings, or project-context synthesis.
- Maintaining a database or persistent index of conversation history.

## Input

The positional `source` argument accepts:

- a ChatGPT export ZIP;
- a directory containing the extracted export;
- a conversation JSON file.

When a directory or ZIP contains numbered `conversations-NNN.json` files, they are combined in numeric order.

If numbered files are present, they are preferred over a legacy single `conversations.json` file so the same exported data is not processed twice.

The tool reads large multi-file exports incrementally and ignores empty placeholder objects within official exports.

## Conversation selection

### Visible conversation branch

ChatGPT exports represent a conversation as a mapping/tree. Regenerating or editing a response can leave multiple branches in that mapping.

When `current_node` is present, only the path from the root to that node is treated as the visible conversation. Abandoned sibling branches are not exported.

Internal records that do not contain user-visible message text or media references are omitted from the output.

The tool preserves image references in multimodal message metadata but does not copy or embed media files into the output JSON.

### Date filters

`--from YYYY-MM-DD` keeps conversations on or after the date.

`--to YYYY-MM-DD` keeps conversations on or before the date.

If the conversation-level timestamp is absent, the first available message timestamp is used.

Dates are evaluated in UTC, independently of the computer's local time zone.

### Text filters

`--include TEXT` keeps conversations whose title or message content contains the term.

`--exclude TEXT` removes conversations whose title or message content contains the term.

Both options are repeatable:

- multiple include terms use OR semantics;
- matching any exclude term removes the conversation.

Matching is case-insensitive.

If no conversation remains after filtering, the command fails instead of creating an empty run directory.

## Output

Each successful run creates a new directory under the configured output root:

```text
Output/
└── 2026-09-27_20-00-00-123456+0300/
    ├── part_001.json
    ├── part_002.json
    └── ...
```

Existing runs are never deleted or reused.

Output files contain compact UTF-8 JSON.

When one conversation must be split across output records, fragment titles are suffixed with `(part N/M)`.

Each conversation is a JSON object with a `title` and an ordered `messages` array. Each message contains only `role` and `content`:

```json
[
  {
    "title": "Example conversation",
    "messages": [
      {"role": "user", "content": "Which format should we use?"},
      {"role": "assistant", "content": "Use JSON."}
    ]
  }
]
```

The example is formatted for readability; generated files use compact JSON on one line.

- A single text part is stored as a string. Multiple parts, audio and images remain ordered arrays with their original content objects.
- The role and the exact text/multimodal part data are preserved. No messages are summarized, merged, or rewritten.
- Export-only graph metadata (`id`, `parent`, `children`) is used to find the visible conversation branch but is not needed in the output.
- Conversation and message timestamps are used for filtering but are not included in output files.

## ChatGPT Project limits

Plan presets were verified on 2026-09-27 against OpenAI's Projects documentation:

| Plan | Maximum files |
| --- | ---: |
| Free | 5 |
| Go, Plus | 25 |
| Edu, Pro, Business, Enterprise | 40 |

The default preset is `plus`.

Use another preset:

```bash
chat-history-to-project export.zip --plan free
chat-history-to-project export.zip --plan pro
```

Or set an explicit limit:

```bash
chat-history-to-project export.zip --max-files 30
```

`--plan` and `--max-files` are mutually exclusive.

The default per-file limits are:

- 1,900,000 `o200k_base` tokens, leaving a safety margin below ChatGPT's documented 2,000,000-token text/document limit;
- 512 MB.

If the selected history cannot fit within the configured maximum number of files, the command fails with an explanatory error rather than writing a partial result.

Relevant OpenAI documentation:

- <https://help.openai.com/en/articles/10169521-projects-in-chatgpt>
- <https://help.openai.com/en/articles/8555545-file-uploads-faq>

## CLI

Primary command:

```bash
chat-history-to-project SOURCE
```

Supported V1 options:

```text
--output-dir PATH
--plan {free,go,plus,edu,pro,business,enterprise}
--max-files N
--max-tokens-per-file N
--max-file-mb N
--from YYYY-MM-DD
--to YYYY-MM-DD
--include TEXT
--exclude TEXT
```

The installed `chat-history-to-project` command is the primary interface. `run.py` is only a thin launcher for running the repository directly.

## Product rules and constraints

- Processing must remain local; adding a network upload/API dependency would be a product-scope change.
- The supported input contract is the official ChatGPT export, not arbitrary JSON shaped similarly.
- A successful run must never silently exceed configured per-file limits.
- A successful run must never produce more than the configured maximum number of files.
- Optimizations must preserve message order, attribution, content text, and non-text parts. Do not deduplicate repeated statements or discard media references to save space.
- Existing output from previous runs must not be overwritten.
- Defaults tied to ChatGPT limits must be re-verified against official OpenAI documentation before they are changed.
- README should remain concise; detailed behavior belongs in this file.

## Open questions

- Whether the package should be published to PyPI instead of being installed directly from GitHub.
- Whether plan presets should remain manually maintained constants or be removed in favor of explicit `--max-files` values if OpenAI changes limits frequently.
