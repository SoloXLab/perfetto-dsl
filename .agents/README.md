# .agents Navigation

This directory stores reusable agent assets for Cursor/Claude style delivery.

## Directory map

- `rules/`: Global constraints and review rules.
- `workflows/`: Task-type execution flows (`feature`, `bugfix`, `refactor`, `exploration`).
- `skills/`: Reusable capability packs invoked by task context.
- `commands/`: Lightweight command playbooks and gate checks.

### Standard subdirectories (for skills/workflows)

- `scripts/`: Executable code that agents can run.
- `references/`: Supplemental documents loaded on demand.
- `assets/`: Static resources such as templates, images, or data files.

## Recommended execution order

1. Run Issue First Gate.
2. Pick one workflow by task type.
3. Pick required skills for that workflow.
4. Fill issue/PR content from assets templates.
5. Run minimal validation commands before commit.

## Quick selection guide

- New feature: workflow `feature-delivery` + skill `github-operator`.
- Bug fix: workflow `bugfix` + skill `github-operator`.
- Refactor: workflow `refactor` + skill `github-operator`.
- Research/spike: workflow `exploration` + skill `exploration-logger`.
- Market analysis/opportunity discovery: workflow `market-discovery` + skill `market-discovery`.
- Public-review user research/journey mapping: workflow `digital-user-research` + skill `digital-user-research`.
- Generic issue-tracking execution loop: workflow `issue-tracked-execution` + skill `github-operator`.
- Complex/unclear task: add skill `task-planner` first.
- PR description writing: add skill `pr-writer`.

## Naming conventions

- Branch: `<type>-<issue id>` or `cursor/<type>-<issue id>`.
- Commit: `type(scope): summary`.

## Notes

- Keep assets lightweight and composable.
- Prefer updating existing assets over creating overlapping ones.
- If adding a new workflow or skill, include at least one minimal usage example.
- For GitHub authenticated operations, read token only from `GITHUB_TOKEN`.
- Default ownership: Cloud Agent creates issues, links PRs, and closes issues after merge.
