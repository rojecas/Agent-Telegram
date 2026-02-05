---
name: architecture-manager
description: Manage and enforce project architecture and folder standards.
---

# Architecture Manager Skill

This skill defines the structured source layout and coding conventions for the Agent Telegram project.

## 1. Directory Structure

- `src/agent_telegram/`: Main source package.
  - `core/`: Core logic (agents, history management, consolidation, data models).
  - `security/`: Configuration, threat detection, and security logging.
  - `tools/`: Dynamically registered tools callable by the assistant.
- `tests/`: System tests.
  - `unit/`: Component tests without external dependencies.
  - `integration/`: Full flow and tool tests.
- `assets/`: Persistent data (users, history, cities). DO NOT move files here without updating path configurations.
- `logs/`: Execution and security log outputs.

## 2. Coding and Agent Standards

- **Imports:** Always use absolute imports from the root package.
  - Correct: `from src.agent_telegram.core.agents import run_turn`
  - Incorrect: `import agents`
- **New Files:** IT IS STRICTLY FORBIDDEN to create files in the project root directory (except for global configs like `.env`, `requirements.txt`).
- **Naming Conventions:**
  - Tools: Must be in `src/agent_telegram/tools/` and end in `_tools.py` or `_tool.py`.
  - Tests: Must start with `test_` and reside in `tests/unit/` or `tests/integration/`.
- **Security:** Any user data access must go through the unified `SecurityLogger` in `src/agent_telegram/security/logger.py`.

## 3. Tool Registration

Tools must use the `@tool` decorator for automatic registration. Do not add tools manually to global lists in `main.py`.
