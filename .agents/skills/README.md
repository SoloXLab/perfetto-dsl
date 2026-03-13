# skills/

Reusable capability packs that can be composed per workflow.

## Standard subdirectories

- `scripts/`: 智能体可执行的代码或脚本。
- `references/`: 按需加载的补充文档。
- `assets/`: 模板、图片、数据等静态资源。

## Files

- `task-planner`: split complex tasks into low-risk executable steps.
- `github-operator`: implement, validate, commit, and prepare PR content.
- `exploration-logger`: maintain spike/research logs in a single issue.
- `pr-writer`: produce structured PR descriptions.
- `market-discovery`: run pre-product market opportunity discovery and go/no-go decision.
- `digital-user-research`: run passive user research from public reviews/discussions and output journey map + design recommendations.

## Composition examples

- feature/bugfix/refactor:
  - `github-operator`
  - add `task-planner` when requirements are unclear
- exploration:
  - `exploration-logger`
  - add `task-planner` for multi-stage investigations
- market analysis / opportunity discovery:
  - `market-discovery`
  - add `task-planner` when the market scope is too broad
- review/comment-based user research:
  - `digital-user-research`
  - add `task-planner` when scope or source coverage is unclear
- PR polishing:
  - `pr-writer`

## Maintenance rule

Avoid overlapping skills. Prefer extending an existing skill with a clear "Use this skill when" boundary.
