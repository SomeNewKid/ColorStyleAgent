"""Bootstrap the command-line application."""

import asyncio

from . import agent


def main() -> None:
    """Run the command-line application."""
    exit_code: int = asyncio.run(agent.main())
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
