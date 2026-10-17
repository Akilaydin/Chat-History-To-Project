# Verified 2026-09-27 against:
# https://help.openai.com/en/articles/10169521-projects-in-chatgpt
PLAN_FILE_LIMITS = {
    "free": 5,
    "go": 25,
    "plus": 25,
    "edu": 40,
    "pro": 40,
    "business": 40,
    "enterprise": 40,
}

DEFAULT_PLAN = "plus"
# ChatGPT documents a 2,000,000-token limit for text/document files. Keep a 5% buffer
# because the server-side tokenizer used for file processing is not documented.
DEFAULT_MAX_TOKENS_PER_FILE = 1_900_000
# https://help.openai.com/en/articles/8555545-file-uploads-faq
DEFAULT_MAX_FILE_BYTES = 512_000_000
TOKEN_ENCODING = "o200k_base"


def resolve_max_files(plan: str | None, max_files: int | None) -> int:
    if max_files is not None:
        return max_files
    return PLAN_FILE_LIMITS[plan or DEFAULT_PLAN]
