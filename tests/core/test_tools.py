import pytest

from core.tools import cleaned_words, fts_raw_query_expression


@pytest.mark.parametrize(
    "term,expected",
    [
        ("", set()),
        ("hello", {"hello"}),
        ("hello world", {"hello", "world"}),
        (" hello  world ", {"hello", "world"}),
        (".a.", {"a"}),
        ("'a\"", {"a"}),
        ("'a'b'", {"a'b"}),  # At this point, inside single quotes are still part of the word.
    ],
)
def test_can_clean_words(term: str, expected: set[str]):
    assert cleaned_words(term) == expected


@pytest.mark.parametrize(
    "term,expected",
    [
        ("", ""),
        ("hello", "'hello'"),
        ("hello world", "'hello' | 'world'"),
        ("Bob's house", "'bob' | 'house' | 's'"),
    ],
)
def test_can_compute_fts_raw_query_expression(term: str, expected: str):
    assert fts_raw_query_expression(term) == expected
