"""Task Orchestrating Agent package.

This package provides a simple framework for multi‑agent task decomposition.
It includes an orchestrator agent that can break a high‑level goal into
subtasks and delegate those to specialized worker agents such as research,
copywriting or ad‑design agents. The orchestrator uses the OpenAI API to
determine how to split tasks and each worker agent uses the same API to
generate its output.

See the README for usage instructions and design details.
"""

__all__: list[str] = []