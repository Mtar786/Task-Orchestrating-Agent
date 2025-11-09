"""Definitions of specialized agents for the Task Orchestrating Agent system.

Each agent encapsulates a specific domain expertise and uses the OpenAI
ChatCompletion API to fulfil its assigned subtask. Agents derive from
``BaseAgent``, which manages API calls and error handling. The three
concrete agents shipped with this package are:

* :class:`ResearchAgent` – responsible for gathering facts and summarizing
  information relevant to a problem.
* :class:`CopywritingAgent` – tasked with writing persuasive text such as
  marketing copy, product descriptions or taglines.
* :class:`AdDesignAgent` – generates creative advertising concepts,
  slogans and headlines.

Additional agents can be implemented by subclassing :class:`BaseAgent`
and overriding the ``role_prompt`` attribute.
"""

from __future__ import annotations

import os
from typing import Optional

try:
    import openai  # type: ignore
except ImportError:  # pragma: no cover
    openai = None


class BaseAgent:
    """Base class for all agents.

    Subclasses should provide a ``role_prompt`` attribute that defines the
    system message used to instruct the language model about the agent's role.
    """

    name: str = "base"
    role_prompt: str = ""
    model: str = "gpt-4"

    def __init__(self, *, name: Optional[str] = None, role_prompt: Optional[str] = None, model: Optional[str] = None) -> None:
        if name is not None:
            self.name = name
        if role_prompt is not None:
            self.role_prompt = role_prompt
        if model is not None:
            self.model = model

    def _ensure_openai(self, api_key: Optional[str]) -> None:
        """Ensure the OpenAI package is installed and the API key is set."""
        if openai is None:
            raise RuntimeError(
                "The openai package is not installed. Install it with `pip install openai`."
            )
        key = api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            raise RuntimeError(
                "No OpenAI API key provided. Set the OPENAI_API_KEY environment variable or pass the api_key parameter."
            )
        openai.api_key = key

    def run(self, task: str, *, api_key: Optional[str] = None, temperature: float = 0.7) -> str:
        """Execute this agent on the given task.

        Args:
            task: Description of the subtask for the agent to perform.
            api_key: Explicit OpenAI API key. If not provided, the
                environment variable ``OPENAI_API_KEY`` is used.
            temperature: Sampling temperature for the language model.

        Returns:
            The text output produced by the agent.

        Raises:
            RuntimeError: If the OpenAI API is unavailable or fails.
        """
        self._ensure_openai(api_key)
        system_msg = {"role": "system", "content": self.role_prompt}
        user_msg = {"role": "user", "content": task}
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[system_msg, user_msg],
                temperature=temperature,
            )
        except Exception as exc:
            raise RuntimeError(f"{self.name} failed to call OpenAI API: {exc}") from exc
        try:
            return response["choices"][0]["message"]["content"].strip()
        except Exception as exc:
            raise RuntimeError(
                f"Unexpected response format from OpenAI API in {self.name}: {exc}"
            ) from exc


class ResearchAgent(BaseAgent):
    """Agent specialized in gathering facts and summarizing research."""

    name = "ResearchAgent"
    role_prompt = (
        "You are a Research Agent. Your job is to gather relevant facts, data, and "
        "context about the subject or question you are assigned. For the given "
        "task, search for information from general knowledge (no web access) and "
        "provide a concise summary with references to any important considerations."
    )


class CopywritingAgent(BaseAgent):
    """Agent specialized in writing persuasive marketing copy."""

    name = "CopywritingAgent"
    role_prompt = (
        "You are a Copywriting Agent. You write engaging and persuasive text for "
        "marketing and communications. When given a task, produce high‑quality "
        "copy tailored to the specified audience and objective. Emphasize clarity, "
        "benefits, and calls to action where appropriate."
    )


class AdDesignAgent(BaseAgent):
    """Agent specialized in creating creative advertising concepts."""

    name = "AdDesignAgent"
    role_prompt = (
        "You are an Ad Design Agent. You create creative advertising concepts, "
        "slogans, headlines, and campaign ideas. For the assigned task, deliver "
        "concise and imaginative advertising ideas that align with the brand and "
        "target audience."
    )


def get_default_agents(model: Optional[str] = None) -> list[BaseAgent]:
    """Return a list of default agents used by the orchestrator.

    Args:
        model: Optional model override for all agents (default "gpt-4").

    Returns:
        A list containing instances of ResearchAgent, CopywritingAgent and
        AdDesignAgent.
    """
    return [
        ResearchAgent(model=model) if model else ResearchAgent(),
        CopywritingAgent(model=model) if model else CopywritingAgent(),
        AdDesignAgent(model=model) if model else AdDesignAgent(),
    ]