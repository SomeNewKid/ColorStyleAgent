"""Tests for Markdown tokenization."""

from color_style_agent.tokenizer import (
    MarkdownToken,
    markdown_to_tokens,
    replace_text_tokens,
    tokens_to_markdown,
)


def test_tokenizes_plain_text_as_single_editable_token() -> None:
    """Plain Markdown text is editable prose."""
    tokens = markdown_to_tokens("Set the color with CSS.")

    assert tokens == [MarkdownToken(kind="text", value="Set the color with CSS.")]


def test_tokenizes_inline_code_as_protected_token() -> None:
    """Inline code spans are protected from spelling correction."""
    markdown = "Use `color: red` to change color."

    tokens = markdown_to_tokens(markdown)

    assert tokens == [
        MarkdownToken(kind="text", value="Use "),
        MarkdownToken(kind="inline_code", value="`color: red`"),
        MarkdownToken(kind="text", value=" to change color."),
    ]


def test_tokenizes_fenced_code_block_as_protected_token() -> None:
    """Fenced code blocks are protected from spelling correction."""
    markdown = (
        "Example:\n\n```css\n.warning {\n  color: red;\n}\n```\n\nThe color is now red."
    )

    tokens = markdown_to_tokens(markdown)

    assert tokens == [
        MarkdownToken(kind="text", value="Example:\n\n"),
        MarkdownToken(
            kind="fenced_code",
            value="```css\n.warning {\n  color: red;\n}\n```",
        ),
        MarkdownToken(kind="text", value="\n\nThe color is now red."),
    ]


def test_ignores_inline_code_delimiters_inside_fenced_code_block() -> None:
    """Backticks inside a fenced code block remain part of the block."""
    markdown = "Before\n```text\n`color`\n```\nAfter"

    tokens = markdown_to_tokens(markdown)

    assert tokens == [
        MarkdownToken(kind="text", value="Before\n"),
        MarkdownToken(kind="fenced_code", value="```text\n`color`\n```"),
        MarkdownToken(kind="text", value="\nAfter"),
    ]


def test_tokens_to_markdown_restores_original_markdown() -> None:
    """Token values are exact slices of the original Markdown."""
    markdown = "A `color` word.\n\n```css\ncolor: blue;\n```\nDone."

    tokens = markdown_to_tokens(markdown)
    reassembled = tokens_to_markdown(tokens)

    assert reassembled == markdown


def test_replace_text_tokens_replaces_only_text_tokens() -> None:
    """Corrected text segments replace text tokens in order."""
    tokens = [
        MarkdownToken(kind="text", value="Set the color with "),
        MarkdownToken(kind="inline_code", value="`color`"),
        MarkdownToken(kind="text", value=" and behavior."),
        MarkdownToken(kind="fenced_code", value="```css\ncolor: red;\n```"),
    ]

    replace_text_tokens(
        tokens,
        [
            "Set the colour with ",
            " and behaviour.",
        ],
    )

    assert tokens == [
        MarkdownToken(kind="text", value="Set the colour with "),
        MarkdownToken(kind="inline_code", value="`color`"),
        MarkdownToken(kind="text", value=" and behaviour."),
        MarkdownToken(kind="fenced_code", value="```css\ncolor: red;\n```"),
    ]


def test_replace_text_tokens_leaves_tokens_unchanged_for_too_few_segments() -> None:
    """A segment count mismatch leaves the tokens unchanged."""
    tokens = [
        MarkdownToken(kind="text", value="Color one."),
        MarkdownToken(kind="text", value="Color two."),
    ]
    original_tokens = list(tokens)

    replace_text_tokens(tokens, ["Colour one."])

    assert tokens == original_tokens


def test_replace_text_tokens_leaves_tokens_unchanged_for_too_many_segments() -> None:
    """Extra corrected segments leave the tokens unchanged."""
    tokens = [MarkdownToken(kind="text", value="Color one.")]
    original_tokens = list(tokens)

    replace_text_tokens(tokens, ["Colour one.", "Colour two."])

    assert tokens == original_tokens


def test_replace_text_tokens_leaves_tokens_unchanged_for_empty_segment() -> None:
    """An empty corrected segment leaves the tokens unchanged."""
    tokens = [MarkdownToken(kind="text", value="Color one.")]
    original_tokens = list(tokens)

    replace_text_tokens(tokens, [""])

    assert tokens == original_tokens


def test_replace_text_tokens_leaves_tokens_unchanged_for_whitespace_segment() -> None:
    """A whitespace-only corrected segment leaves the tokens unchanged."""
    tokens = [MarkdownToken(kind="text", value="Color one.")]
    original_tokens = list(tokens)

    replace_text_tokens(tokens, ["   \n"])

    assert tokens == original_tokens
