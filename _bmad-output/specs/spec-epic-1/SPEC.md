---
id: SPEC-epic-1
companions: []
sources: [../../../INTENT.md]
---

> **Canonical contract.** This SPEC and the files in `companions:` are the complete, preservation-validated contract for what to build, test, and validate. Source documents listed in frontmatter are for traceability — consult them only if you need narrative rationale or prose color this contract intentionally omits.

# Epic 1: triage data and schema

## Why

The workshop needs a reliable foundation for support-ticket triage. A validated decision contract and deterministic local dataset let later epics build the agent, MCP integration, and evaluation against stable data.

## Capabilities

- **CAP-1**
  - **intent:** The system accepts a triage decision only when it contains a supported category, priority, route, and one-sentence rationale.
  - **success:** Valid decisions use category `billing`, `bug`, `access`, `performance`, or `how-to`; priority `P1`, `P2`, `P3`, or `P4`; route `billing-team`, `bug-team`, `access-team`, `performance-team`, or `how-to-team`; and a one-sentence rationale. Any other shape is rejected with a clear error.

- **CAP-2**
  - **intent:** A person can load the workshop seed data into a local SQLite database for later triage work.
  - **success:** `uv run python load_seed.py` creates `app.db` with `tickets` and `customers` tables whose columns match `seed/tickets.csv` and `seed/customers.csv`; running the command twice produces the same database state.

## Constraints

- Use Python 3.12 or newer managed with `uv`.
- Keep every file under `seed/` read-only.
- Make no network calls and require no API keys for this epic.
- Preserve the `tickets` and `customers` table and column names consumed by `mcp/triage_server.py`.

## Non-goals

- The LangChain agent.
- MCP tools or changes to `mcp/triage_server.py`.
- Evaluation harnesses.
- Any user interface.

## Success signal

The decision contract rejects malformed triage results clearly, and `uv run python load_seed.py` deterministically loads both CSV files into `app.db`. The existing MCP server can read the resulting tables using its current names and columns.
