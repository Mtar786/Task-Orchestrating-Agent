"""Command‑line interface for the Task Orchestrating Agent.

This module exposes a CLI entry point that accepts a high‑level goal and
returns the outputs of all agents involved in fulfilling that goal. It
leverages the :class:`task_orchestrating_agent.orchestrator.Orchestrator`
to decompose the goal and delegate work to worker agents.

Example::

    python -m task_orchestrating_agent.cli "Plan a marketing campaign" \
        --api-key sk-... --model gpt-4o

If no API key is provided, the ``OPENAI_API_KEY`` environment variable is
used. The output is printed to standard output.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .agents import get_default_agents
from .orchestrator import Orchestrator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Task Orchestrating Agent on a high-level goal and print the results."
    )
    parser.add_argument(
        "goal",
        help="The high-level goal to be decomposed and delegated.",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="Explicit OpenAI API key (defaults to environment variable OPENAI_API_KEY).",
    )
    parser.add_argument(
        "--model",
        default="gpt-4",
        help="OpenAI model to use for both planning and agents (default: gpt-4).",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional path to write the JSON results (prints to stdout if omitted).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    agents = get_default_agents(model=args.model)
    orchestrator = Orchestrator(agents, model=args.model)
    results = orchestrator.run(args.goal, api_key=args.api_key)
    # Serialize results as JSON for easy consumption
    serialized = json.dumps(results, indent=2, ensure_ascii=False)
    if args.output:
        output_path = Path(args.output).expanduser().resolve()
        output_path.write_text(serialized, encoding="utf-8")
        print(f"Results written to {output_path}")
    else:
        print(serialized)


if __name__ == "__main__":  # pragma: no cover
    main()