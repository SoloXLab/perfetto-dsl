# workflows references

Workflow docs are organized by subdirectory with a fixed entry filename:

- `.agents/workflows/<workflow-name>/WORKFLOW.md`

## Workflow index

- `feature-delivery/WORKFLOW.md`: Epic -> Feature -> User Story delivery workflow.
- `bugfix/WORKFLOW.md`: bug reproduction, root-cause, fix, regression-proof workflow.
- `refactor/WORKFLOW.md`: refactor slicing and equivalence validation workflow.
- `exploration/WORKFLOW.md`: research/spike logging and decision workflow.
- `digital-user-research/WORKFLOW.md`: passive user research workflow from public reviews.
- `issue-tracked-execution/WORKFLOW.md`: create issue, execute, backfill result, then close workflow.
- `market-discovery/WORKFLOW.md`: market opportunity analysis with issue tracking and closure.

## Selection guide

- User-facing capability change -> `feature-delivery`
- Defect/regression fix -> `bugfix`
- Structural/maintainability change -> `refactor`
- Technical investigation/spike -> `exploration`
- User reviews analysis / journey reconstruction -> `digital-user-research`
- Generic issue-tracked execution loop -> `issue-tracked-execution`
- Market analysis / opportunity discovery -> `market-discovery`

## Required gate

Before implementation/exploration/market-discovery actions:

- workflow selected
- issue id available
- branch naming compliant

## Standard subdirectories

- `scripts/`: executable code that agents can run.
- `references/`: supplemental documents loaded on demand.
- `assets/`: static resources such as templates, images, or data files.

## Asset locations (distributed)

- Feature delivery:
  - `.agents/workflows/feature-delivery/assets/issue-feature.md`
- Bugfix:
  - `.agents/workflows/bugfix/assets/issue-bugfix.md`
- Refactor:
  - `.agents/workflows/refactor/assets/issue-refactor.md`
- Exploration:
  - `.agents/workflows/exploration/assets/issue-exploration.md`
- Issue-tracked execution:
  - `.agents/workflows/issue-tracked-execution/assets/issue-backfill.md`
- Market discovery:
  - `.agents/workflows/market-discovery/assets/issue-market-discovery.md`
- Digital user research:
  - `.agents/workflows/digital-user-research/assets/issue-digital-user-research.md`
- PR writing:
  - `.agents/skills/pr-writer/assets/pr-body.md`
