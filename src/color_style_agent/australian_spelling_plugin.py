"""Provides an ADK plugin which ensures the use of Australian spelling."""

from __future__ import annotations

from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.adk.plugins import BasePlugin
from google.genai import types
from openai import AsyncOpenAI, OpenAIError
from pydantic import BaseModel, Field, ValidationError

from color_style_agent.tokenizer import (
    MarkdownToken,
    markdown_to_tokens,
    replace_text_tokens,
    tokens_to_markdown,
)

VERBOSE_LOGGING = False


class CorrectedTextSegments(BaseModel):
    """Structured response from the spelling correction model."""
    segments: list[str] = Field(
        description=(
            "Corrected text segments. Must contain exactly one item for each "
            "input segment, in the same order"
        )
    )


class AustralianSpellingPlugin(BasePlugin):
    """Processes the final response to ensure Australian spelling."""

    def __init__(self) -> None:
        super().__init__(name="austalian_spelling")
        self._openai_client = AsyncOpenAI()

    async def on_event_callback(
        self, *, invocation_context: InvocationContext, event: Event
    ) -> Event | None:
        """Modify the final response event."""
        if not event.is_final_response():
            return None

        if event.content is None or event.content.parts is None:
            return None

        original_markdown = "".join(
            part.text for part in event.content.parts if part.text is not None
        )

        tokens = markdown_to_tokens(original_markdown)
        corrections: list[str] = await self._get_corrections(tokens)
        replace_text_tokens(tokens, corrections)
        corrected_markdown = tokens_to_markdown(tokens)
        corrected_markdown += "\n(corrected by plugin)"

        corrected_content = types.Content(
            role=event.content.role, parts=[types.Part(text=corrected_markdown)]
        )

        return event.model_copy(update={"content": corrected_content})
    
    async def _get_corrections(self, tokens: list[MarkdownToken]) -> list[str]:
        text_segments: list[str] = [
            token.value
            for token in tokens
            if token.kind == "text"
        ]
        
        if not text_segments:
            return []
        
        self._print_segments(text_segments, "ORIGINAL")
        
        try:
            response = await self._openai_client.responses.parse(
                model="gpt-4o",
                instructions= "\n".join([
                    "You convert American spelling to Australian spelling",
                    (
                        "You have been given a list of text segments, "
                        "some of which contain Americal spelling of words."
                    ),
                    (
                        "You are required to return an updated list of text segments, "
                        "replacing any Americal spelling with Australian spelling."
                    ),
                    (
                        "Only change spelling variants, such as 'color' to 'colour', "
                        "'behavior' to 'behaviour', 'organize' to 'organise', "
                        "and similar."
                    ),
                    (
                        "Do not add explanations, Markdown fences, commentary, labels, "
                        "or extra text."
                    ),
                    "If a segment needs no correction, return it unchanged."
                    "Return the same number of segments in the same order.",
                ]),
                input=(
                    "Correct these text segments to use Australian spelling. "
                    "Return only the structured response.\n\n"
                    f"{text_segments}"
                ),
                text_format=CorrectedTextSegments
            )
            parsed = response.output_parsed
            if parsed is None:
                print("ERROR 01")
                return []
            
            corrected_segments = parsed.segments
            if corrected_segments is None:
                print("ERROR 02")
                return []
            
            self._print_segments(corrected_segments, "CORRECTED")

            if len(corrected_segments) != len(text_segments):
                print("ERROR 03")
                return []
            
            if any(not segment.strip() for segment in corrected_segments):
                print("ERROR 04")
                return []
            
            return corrected_segments

        except (OpenAIError, ValidationError, ValueError):
            return []
        

    def _print_segments(self, segments:list[str], title:str | None = None) -> None:
        if not VERBOSE_LOGGING:
            return
        print("-----------------------")
        if title:
            print(title)
            print("-------")
        for segment in segments:
            print(f'  "{segment}"')
        print("-----------------------")

