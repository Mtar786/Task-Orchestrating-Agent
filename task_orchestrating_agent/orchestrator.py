"""Orchestrator implementation for the Task Orchestrating Agent system.

The :class:`Orchestrator` is responsible for breaking down a high‑level goal
into manageable subtasks and delegating those tasks to specialized worker
agents. It uses the OpenAI API to plan the decomposition and assign tasks,
then coordinates the execution of each subtask by invoking the appropriate
agent. The orchestrator aggregates the results and returns them to the caller.

Example usage::

    from task_orchestrating_agent.agents import get_default_agents
    from task_orchestrating_agent.orchestrator import Orchestrator
    orchestrator = Orchestrator(get_default_agents())
    results = orchestrator.run("Plan a marketing campaign")
    print(results)

"""

from __future__ import annotations

import json
import os
from typing import Dict, List, Tuple, Optional

try:
    import openai  # type: ignore
except ImportError:  # pragma: no cover
    openai = None

from .agents import BaseAgent


class Orchestrator:
    """Central coordinator for a multi‑agent system.

    An orchestrator receives a goal, plans the tasks required to achieve that
    goal and delegates those tasks to appropriate worker agents. The planning
    and delegation logic leverages the OpenAI ChatCompletion API. A
    configuration of agents must be provided when constructing the orchestrator.
    """

    def __init__(self, agents: List[BaseAgent], *, model: str = "gpt-4") -> None:
        """Initialise the orchestrator.

        Args:
            agents: A list of agent instances available for delegation. Each
                agent should have a unique name.
            model: The OpenAI model used for planning (default: "gpt-4").
        """
        # Map agents by lowercase name for case-insensitive lookup
        self.agents: Dict[str, BaseAgent] = {agent.name.lower(): agent for agent in agents}
        self.model: str = model

    def _ensure_openai(self, api_key: Optional[str]) -> None:
        """Ensure the OpenAI client is available and API key is configured."""
        if openai is None:
            raise RuntimeError(
                "The openai package is not installed. Install it with `pip install openai`."
            )
        key = api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            raise RuntimeError(
                "No OpenAI API key provided for the orchestrator. Set the OPENAI_API_KEY environment variable or pass api_key."
            )
        openai.api_key = key

    def _plan(self, goal: str, *, api_key: Optional[str], temperature: float = 0.3) -> List[Tuple[str, str]]:
        """Generate a plan by decomposing the goal into subtasks.

        The OpenAI model is prompted to produce a JSON list where each element
        contains ``agent`` and ``task`` keys. The orchestrator then parses
        this JSON and returns a list of (agent_name, subtask_description)
        tuples.

        Args:
            goal: The high‑level objective to accomplish.
            api_key: Explicit OpenAI API key. If not provided, uses the
                ``OPENAI_API_KEY`` environment variable.
            temperature: Sampling temperature for the planning model.

        Returns:
            A list of (agent_name, subtask_description) tuples.

        Raises:
            RuntimeError: If planning fails or the response cannot be parsed.
        """
        self._ensure_openai(api_key)
        # Build the description of available agents for the prompt
        available_agents_desc = "\n".join(
            f"- {agent.name}: {agent.role_prompt.split('.')[0]}..." for agent in self.agents.values()
        )
        system_message = {
            "role": "system",
            "content": (
                "You are a Task Orchestrator Agent. Your job is to break complex goals into "
                "manageable subtasks and assign them to appropriate specialized agents. "
                "Return your plan as a JSON array. Each entry must have two keys: "
                "'agent' (the name of the agent to perform the task) and 'task' (a short description of the subtask)."
            ),
        }
        user_message = {
            "role": "user",
            "content": (
                f"Goal: {goal}\n\n"
                f"Available agents:\n{available_agents_desc}\n\n"
                "Please propose a decomposition of the goal into subtasks. "
                "Use only the provided agent names when assigning tasks. Format your response as JSON."
            ),
        }
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[system_message, user_message],
                temperature=temperature,
            )
        except Exception as exc:
            raise RuntimeError(f"Orchestrator planning failed: {exc}") from exc
        try:
            plan_text: str = response["choices"][0]["message"]["content"].strip()
            # Ensure JSON is enclosed properly; if not, try to extract from code block
            plan_json_text = plan_text
            # Remove Markdown code fences if present
            if plan_json_text.startswith("```"):
                # Remove the first line and last line that contain code fencing
                parts = plan_json_text.split("\n")
                if parts[0].startswith("```"):
                    parts = parts[1:]
                if parts and parts[-1].startswith("```"):
                    parts = parts[:-1]
                plan_json_text = "\n".join(parts)
            plan: List[dict] = json.loads(plan_json_text)
            result: List[Tuple[str, str]] = []
            for item in plan:
                agent_name = str(item.get("agent", "")).strip()
                task_description = str(item.get("task", "")).strip()
                if agent_name and task_description:
                    result.append((agent_name, task_description))
            return result
        except Exception as exc:
            raise RuntimeError(
                f"Failed to parse orchestration plan as JSON: {exc}. Raw response: {plan_text}"
            ) from exc

    def run(self, goal: str, *, api_key: Optional[str] = None) -> Dict[str, str]:
        """Execute a full orchestration loop for the given goal.

        This method plans the goal, delegates subtasks to the configured
        worker agents and aggregates their outputs. The final output is a
        dictionary mapping agent names to their respective results.

        Args:
            goal: The high‑level objective to accomplish.
            api_key: Explicit OpenAI API key. If omitted, the ``OPENAI_API_KEY``
                environment variable is used.

        Returns:
            A dictionary where keys are agent names and values are their outputs.

        Raises:
            RuntimeError: If planning or agent execution fails.
        """
        plan = self._plan(goal, api_key=api_key)
        results: Dict[str, str] = {}
        for agent_name, task_description in plan:
            # Normalize name to lower case for lookup
            name_key = agent_name.lower()
            if name_key not in self.agents:
                raise RuntimeError(
                    f"Unknown agent '{agent_name}' in plan. Available agents: {list(self.agents.keys())}"
                )
            agent = self.agents[name_key]
            # Compose a prompt for the agent that includes the task description
            agent_prompt = (
                f"Subtask: {task_description}\n\n"
                f"Context: The overall goal is '{goal}'. Perform your role on this specific subtask."
            )
            results[agent.name] = agent.run(agent_prompt, api_key=api_key)
        return results