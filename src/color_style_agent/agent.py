"""Command-line interface for Color Style Agent."""

from __future__ import annotations

from google.adk.agents import Agent
from google.adk.labs.openai import OpenAILlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.utils.content_utils import extract_text_from_content
from google.genai import types

from color_style_agent.australian_spelling_plugin import AustralianSpellingPlugin

USE_REMOTE_OPENAI_MODEL = True
REMOTE_OPENAI_MODEL = "gpt-4o"


async def main() -> int:
    app_name = "color_style_agent"
    user_id = "cli_user"
    session_id = "cli_session"

    agent = Agent(
        name=app_name,
        description="Explains Cascading Style Sheet (CSS) uses of color.",
        instruction=(
            "You are a technical writer specializing in writing articles which help "
            "amateurs start creating simple websites using HTML, CSS, and JavaScript. "
            "You always generate content using Markdown. "
            "When presenting inline code, use a single backtick. "
            "When presenting a code block, use code fences of three backticks. "
        ),
    )
    if USE_REMOTE_OPENAI_MODEL:
        agent.model = OpenAILlm(model=REMOTE_OPENAI_MODEL)

    prompt = (
        "Write a very short article (fewer than 200 words) "
        "which provides basic instructions on setting the "
        "foreground color and background color of elements "
        "in an HTML document."
    )

    session_service = InMemorySessionService()

    await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
    )

    runner = Runner(
        agent=agent,
        app_name=app_name,
        session_service=session_service,
        plugins=[AustralianSpellingPlugin()],
    )

    message = types.Content(role="user", parts=[types.Part(text=prompt)])

    final_text = ""

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=message,
    ):
        if event.is_final_response():
            final_text = extract_text_from_content(event.content)

    print(final_text)
    return 0
