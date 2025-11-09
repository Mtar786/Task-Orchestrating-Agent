# Task‑Orchestrating Agent

**Break complex goals into manageable tasks using a hierarchy of specialized agents.**  
This repository implements a multi‑agent system where a central
**Orchestrator** decomposes a high‑level objective into subtasks and
delegates them to domain‑expert **worker agents**. The design follows
the pattern of hierarchical task decomposition, where higher‑level
agents break down complex goals and assign sub‑tasks to lower‑level
agents【413309057589480†L1227-L1234】.  This approach mirrors real-world
teamwork and leverages the advantages of multi‑agent systems: each
worker focuses on what it does best, while the orchestrator ensures
coherent, end‑to‑end execution【458689510885617†L329-L334】.

## Why multi‑agent systems?

Traditional AI assistants rely on a single large language model to
address arbitrary queries. While convenient, such single‑agent systems
struggle with complex workflows: they lack the ability to break
down tasks, maintain state across steps and coordinate multiple
specializations【497968394997984†L82-L85】. Multi‑agent architectures
overcome these limitations by dividing complex problems among
specialized agents and coordinating them through an orchestrator
【497968394997984†L130-L134】.  In research and enterprise settings,
multi‑agent systems allow parallel exploration of different
dimensions of a problem, separation of concerns and improved
scalability【475099020900519†L38-L56】.

In this implementation, the **Orchestrator** uses the OpenAI API to
generate a plan for the goal. It outputs a JSON array specifying which
agent should handle each subtask. By default, three worker agents are
available:

| Agent | Role |
| --- | --- |
| **ResearchAgent** | Gathers facts and summarizes information relevant to a subtask |
| **CopywritingAgent** | Writes persuasive marketing copy and communications |
| **AdDesignAgent** | Creates creative advertising concepts, slogans and campaign ideas |

You can extend the system by subclassing the base `BaseAgent` class and
registering new agents with the orchestrator.

## Installation

Python 3.8+ is required. Install dependencies via pip:

```bash
pip install openai
```

### Environment variables

The OpenAI API key can be supplied via the `--api-key` CLI option or by
setting the `OPENAI_API_KEY` environment variable.

## Usage

Run the orchestrator on a high‑level goal from the command line:

```bash
python -m task_orchestrating_agent.cli "Plan a marketing campaign" \
    --api-key sk-your-key
```

The CLI outputs a JSON object mapping each agent to its generated result.
You can also save the results to a file using the `--output` option:

```bash
python -m task_orchestrating_agent.cli "Plan a product launch" \
    --output results.json
```

## How it works

1. **Planning** – The orchestrator sends a prompt to the OpenAI
   ChatCompletion endpoint describing the goal and listing the available
   agents. The model is instructed to return a JSON array containing
   the agent name and subtask description for each step. This
   hierarchical task decomposition is inspired by the ADK "Hierarchical
   Task Decomposition" pattern, where higher‑level agents delegate
   tasks to lower‑level agents【413309057589480†L1227-L1234】.
2. **Delegation** – The orchestrator parses the JSON plan and
   sequentially calls each worker agent with its specific subtask.
   Specialized agents focus on their domain, improving quality and
   alignment【458689510885617†L349-L355】.  For instance, a research
   agent gathers background information, while a copywriting agent writes
   persuasive text.
3. **Aggregation** – The orchestrator collects the outputs of all
   agents and returns them as a dictionary. You can use these
   outputs directly or feed them into subsequent workflows.

## Research & design inspiration

* **Hierarchical task decomposition** –  The ADK documentation describes
  multi‑level trees of agents where higher‑level agents break down
  complex goals and delegate sub-tasks to lower‑level agents【413309057589480†L1227-L1234】.  This
  pattern guides the design of the orchestrator and informs the
  planning prompt.
* **Decomposition and orchestration** –  Microsoft’s AI platform
  documentation notes that multi‑agent systems enable decomposition of
  complex tasks into subtasks, delegate them to specialized agents,
  monitor progress and ensure completion【458689510885617†L329-L334】.  The
  orchestrator in this project uses these principles to plan and
  coordinate tasks.
* **Domain specialization and scalability** –  Specialized agents
  focusing on particular domains (e.g., finance, research or creative
  writing) outperform generalist agents【458689510885617†L349-L355】.  Multi‑agent
  architectures scale horizontally, allowing new agents to be
  introduced without retraining the entire system【458689510885617†L403-L416】.
* **Open-ended research** –  Anthropic’s multi‑agent research system
  explains that research tasks are dynamic and unpredictable; subagents
  explore independent directions in parallel, reducing path dependency
  and enabling thorough investigation【475099020900519†L38-L56】.  Although this
  project focuses on marketing rather than research, the same principle
  applies: each specialized agent explores its domain independently.
* **Why multiple agents?** –  V7’s overview of multi‑agent AI notes
  that dividing complex workflows among specialized agents improves
  automation and coherence, coordinated through a central orchestrator
  【497968394997984†L82-L85】, and emphasises that multi‑agent systems break
  complex problems into subtasks for specialized AIs【497968394997984†L130-L134】.

## Extending the system

To add a new agent:

1. Subclass `BaseAgent` and define a ``role_prompt`` appropriate for
   your domain.
2. Instantiate your agent and pass it into the `Orchestrator` when
   constructing the orchestrator (e.g., `Orchestrator([YourAgent(), ...])`).

You can also override the planning prompt or adjust temperature and
model to influence the decomposition strategy.

## License

This project is licensed under the MIT License. See the `LICENSE` file for
details.