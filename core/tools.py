import re

_CLEANED_WORD_TO_SKIP_REGEX = re.compile(r"^([\d\-.,])+$")


def fts_raw_query_expression(term: str) -> str:
    """
    A raw PostgreSQL FTS query expression that matches any of the words in `term`.

    This removes any suspicious characters from the term.
    """
    term_without_single_quotes = term.replace("'", " ").lower()
    return " | ".join(f"'{word}'" for word in sorted(set(cleaned_words(term_without_single_quotes))))


def cleaned_words(value: str) -> set[str]:
    result = set()
    for word in value.split():
        cleaned_word = word.strip(" -+/\\*#_.,:;!?()[]{}$%&'\"")
        if _CLEANED_WORD_TO_SKIP_REGEX.match(cleaned_word) is None:
            result.add(cleaned_word)
    result = result - {""}
    return result


def shortened_text(text: str, max_length: int = 32) -> str:
    assert max_length > 3
    text_length = len(text)
    if text_length <= max_length:
        result = text
    else:
        ellipsis_index = max_length // 2
        result = text[:ellipsis_index] + "…" + text[ellipsis_index - max_length + 1 :]
    return result
