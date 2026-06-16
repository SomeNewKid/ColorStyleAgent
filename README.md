# Color Style Agent

Color Style Agent is a small Python command-line sample for exploring plugins in
Google's Agent Development Kit. It asks an ADK agent to write a short Markdown
article about CSS color properties, then applies an ADK plugin that rewrites the
final response to use Australian spelling.

> [!WARNING]
> This is an experimental project and should not be considered production-ready.

The project was created as a proof-of-concept for applying a company-wide
writing policy to agent output. The plugin tokenizes the final Markdown response
so prose can be corrected while inline code spans and fenced code blocks are
left unchanged.

## What It Does

The CLI runs a fixed sample prompt that asks for a short article explaining how
to set foreground and background colors in HTML and CSS.

The agent flow is:

1. Create an in-memory ADK session.
2. Send the article prompt to an ADK agent.
3. Receive the agent's final Markdown response.
4. Tokenize the Markdown into editable prose and protected code regions.
5. Ask OpenAI `gpt-4o` for Australian-spelling corrections for prose tokens.
6. Reconstruct the Markdown and replace the final ADK response event.

The tokenizer protects inline code and fenced code blocks so examples such as
`color: red` remain valid CSS while surrounding prose can change from American
to Australian spelling.

## Requirements

- Python 3.11.
- PowerShell on Windows.
- An `OPENAI_API_KEY` environment variable for OpenAI model calls.

## Setup

Create the virtual environment and install the project with development
dependencies:

```powershell
.\scripts\setup-dev.ps1
```

The setup script expects Python 3.11 at the path configured in
`scripts\setup-dev.ps1`.

## Running

Run the agent from the repository root:

```powershell
.\.venv\Scripts\python.exe -m color_style_agent
```

The command prints the corrected Markdown article. The current article prompt is
configured in `src/color_style_agent/agent.py`.

## Development Checks

Run formatting, linting, type checking, and tests:

```powershell
.\scripts\check.ps1
```

This runs:

- `ruff format .`
- `ruff check .`
- `pyright`
- `pytest`

## Project Structure

```text
src/color_style_agent/
  __main__.py                   Package entry point for python -m color_style_agent
  agent.py                      ADK agent setup, runner, and CLI entry point
  australian_spelling_plugin.py ADK plugin that post-processes final responses
  tokenizer.py                  Markdown tokenizer and token replacement helpers

tests/
  test_smoke.py
  test_tokenizer.py

scripts/
  setup-dev.ps1
  check.ps1
```

## Notes

This project is an ADK plugin learning exercise, not a general-purpose writing
policy engine. The tokenizer deliberately focuses on protecting Markdown inline
code spans and fenced code blocks for this proof-of-concept.

The article generation and spelling correction steps are model-driven, so final
wording can vary between runs. OpenAI API calls may incur usage costs.

## Third-Party Notices

This project has direct runtime dependencies on third-party Python packages,
including `google-adk` and `openai` (Apache-2.0). See each package's PyPI
license metadata for full license and notice terms.

## License

GNU General Public License v3.0. See the `LICENSE` file for details.
