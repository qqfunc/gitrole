# Development Guide for AI Agents

## Setup

After cloning the repository, install dependencies with `uv sync`.

## Coding Conventions

Follow PEP 8.

## Commands

Run the following commands after changing the code.

### editorconfig-checker

- `uv run ec`

### Typos

- `uv run typos`

### Ruff

Check and format Python code with Ruff.

#### Check Only

- `uv run ruff check`
- `uv run ruff format --check`

#### Format / Fix

- `uv run ruff check --fix`
- `uv run ruff format`

### ty

Type-check Python code with ty.

- `uv run ty check`

## Commit Messages

Follow Conventional Commits.
Pull request titles should also follow Conventional Commits.
