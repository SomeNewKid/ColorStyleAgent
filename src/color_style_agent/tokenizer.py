"""Markdown tokenization helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

TokenKind = Literal["text", "inline_code", "fenced_code"]


@dataclass(frozen=True)
class MarkdownToken:
    """A token from a Markdown document."""

    kind: TokenKind
    value: str


def markdown_to_tokens(markdown: str) -> list[MarkdownToken]:
    """Tokenize Markdown into editable text and protected code regions."""
    tokens: list[MarkdownToken] = []
    text_start = 0
    index = 0

    while index < len(markdown):
        fenced_code_end = _find_fenced_code_end(markdown, index)
        if fenced_code_end is not None:
            _append_text_token(tokens, markdown[text_start:index])
            tokens.append(
                MarkdownToken(
                    kind="fenced_code",
                    value=markdown[index:fenced_code_end],
                )
            )
            index = fenced_code_end
            text_start = index
            continue

        inline_code_end = _find_inline_code_end(markdown, index)
        if inline_code_end is not None:
            _append_text_token(tokens, markdown[text_start:index])
            tokens.append(
                MarkdownToken(
                    kind="inline_code",
                    value=markdown[index:inline_code_end],
                )
            )
            index = inline_code_end
            text_start = index
            continue

        index += 1

    _append_text_token(tokens, markdown[text_start:])
    return tokens


def tokens_to_markdown(tokens: list[MarkdownToken]) -> str:
    """Reconstruct Markdown from tokens."""
    return "".join(token.value for token in tokens)


def replace_text_tokens(tokens: list[MarkdownToken], text_segments: list[str]) -> None:
    """Replace text tokens with corrected text segments."""
    text_token_indexes = [
        index for index, token in enumerate(tokens) if token.kind == "text"
    ]

    if len(text_token_indexes) != len(text_segments):
        return

    if any(not segment.strip() for segment in text_segments):
        return

    for token_index, text_segment in zip(
        text_token_indexes,
        text_segments,
        strict=True,
    ):
        tokens[token_index] = MarkdownToken(kind="text", value=text_segment)


def _append_text_token(tokens: list[MarkdownToken], value: str) -> None:
    if not value:
        return

    tokens.append(MarkdownToken(kind="text", value=value))


def _find_fenced_code_end(markdown: str, index: int) -> int | None:
    fence_width = _get_opening_fence_width(markdown, index)
    if fence_width is None:
        return None

    search_index = _find_line_end(markdown, index)
    while search_index < len(markdown):
        if markdown[search_index] == "\n":
            line_start = search_index + 1
        else:
            line_start = search_index

        closing_fence_end = _get_closing_fence_end(
            markdown,
            line_start,
            fence_width,
        )
        if closing_fence_end is not None:
            return closing_fence_end

        search_index = _find_line_end(markdown, line_start)

    return len(markdown)


def _get_opening_fence_width(markdown: str, index: int) -> int | None:
    if not _is_line_start(markdown, index):
        return None

    fence_start = _skip_optional_leading_spaces(markdown, index)
    if fence_start != index:
        return None

    return _count_backticks(markdown, index, minimum=3)


def _get_closing_fence_end(
    markdown: str,
    line_start: int,
    opening_fence_width: int,
) -> int | None:
    fence_start = _skip_optional_leading_spaces(markdown, line_start)
    fence_width = _count_backticks(markdown, fence_start, minimum=opening_fence_width)
    if fence_width is None:
        return None

    suffix_start = fence_start + fence_width
    suffix_end = _find_line_end(markdown, suffix_start)
    suffix = markdown[suffix_start:suffix_end]
    if suffix.strip():
        return None

    return suffix_end


def _find_inline_code_end(markdown: str, index: int) -> int | None:
    delimiter_width = _count_backticks(markdown, index, minimum=1)
    if delimiter_width is None:
        return None

    delimiter = "`" * delimiter_width
    closing_index = markdown.find(delimiter, index + delimiter_width)
    if closing_index == -1:
        return None

    return closing_index + delimiter_width


def _count_backticks(markdown: str, index: int, *, minimum: int) -> int | None:
    count = 0
    while index + count < len(markdown) and markdown[index + count] == "`":
        count += 1

    if count < minimum:
        return None

    return count


def _is_line_start(markdown: str, index: int) -> bool:
    return index == 0 or markdown[index - 1] == "\n"


def _skip_optional_leading_spaces(markdown: str, line_start: int) -> int:
    index = line_start
    spaces = 0

    while index < len(markdown) and markdown[index] == " " and spaces < 3:
        index += 1
        spaces += 1

    return index


def _find_line_end(markdown: str, index: int) -> int:
    line_end = markdown.find("\n", index)
    if line_end == -1:
        return len(markdown)

    return line_end
