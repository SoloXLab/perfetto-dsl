# GitHub Cloud Agent Rules

## Universal lifecycle
- 所有任务类型都必须以 Create Issue(s) 开始，再进入后续流程。
- 增加强制门禁：所有任务在进入实际工作前，必须先完成 Issue First Gate（workflow 已选定 + issue id 已存在）。
- Issue 内容允许“滚动展开”：先详细记录当前阶段，后续阶段在推进时逐步补全。
- PR 仅实现一个最小可交付单元（一个 user story、一个 bugfix 单元、或一个 refactor 切片）。

## Issue First Gate（Hard Stop）
- Gate 适用：`feature / bugfix / refactor / exploration`。
- Gate 通过条件（全部满足）：
  1) 已选择 workflow；
  2) 已创建 issue 并获得 `#id`；
  3) 分支名满足 `<type>-<issue id>`（允许 `cursor/<type>-<issue id>`）。
- Gate 未通过时，禁止执行：代码实现、提交、PR、实现相关验证命令。
- 默认由 Cloud Agent 直接创建 issue（优先使用 `GITHUB_TOKEN` 调 GitHub API），不得将创建动作转交用户。
- 仅在环境故障导致创建失败时，允许输出 issue 草稿 + 错误信息 + 重试命令，且保持阻断直到拿到 `#id`。

## GitHub authentication (Token source)
- 任何需要 GitHub 鉴权的操作（API 调用、脚本、CLI 增强流程），统一从环境变量 `GITHUB_TOKEN` 读取 token。
- 禁止在代码、脚本、命令、文档中硬编码 token；禁止将 token 写入仓库文件。
- 认证头示例：`Authorization: Bearer $GITHUB_TOKEN`。
- 若 `GITHUB_TOKEN` 不存在或为空：流程状态应标记为 BLOCKED，仅允许进入“补齐环境变量/切换无鉴权路径”动作。
- 调试日志中不得打印 token 原文（包括完整请求头、完整 URL query 等）。

## Workflow types
- 新需求开发：必须按 Epic -> Feature -> User Story 建立层级 issue。
- 缺陷修复：按 bugfix 最佳实践记录复现、根因、修复与回归验证。
- 重构代码：按重构最佳实践记录动机、边界、风险、等价性验证。
- 探索思路：仍必须先创建一个 exploration issue，记录过程、结论、候选方案；PR 可选。

## Requirement quality (OpenSpec)
- 需求开发类 issue 使用 OpenSpec 风格：Context / Scope / Constraints / Acceptance / Non-goals。
- Epic/Feature/User Story 都要可追踪验收标准，且 Story 可直接映射到 PR。

## Branch & commit
- 不直接在 `main/master` 开发；每个任务使用独立分支。
- 分支命名强约束：`<type>-<issue id>`。
- type 仅允许：`feature` / `bugfix` / `refactor` / `exploration` / `other`。
- 示例：`feature-123`、`bugfix-456`、`refactor-789`。
- 注意：部分工具（如 Cursor）创建 PR 时可能使用 `cursor/<type>-<issue id>`，Actions 的 branch filters / regex 需同时覆盖有无 `cursor/` 前缀两种情况。
- 小步提交，单次提交只做一个逻辑变更。
- Commit message: `type(scope): summary`，常见 type: feat/fix/refactor/docs/chore/test.

## PR & review
- PR 必须关联**当前任务对应的 Issue**（正文必须包含 `Closes #<current-issue-id>`，必要时补 `Refs #parent`），并说明所属层级/类型。
- 无 issue id、关联错误 issue、或仅在评论区提到 issue 的 PR，均视为违规并阻断合并。
- PR 描述必须包含：背景、改动点、验证方式、风险与回滚。
- 评审未通过或门禁失败时，不允许合并。
- 除非用户明确要求，Cloud Agent 不得将“创建 issue / 关联 PR / 关闭 issue”转交给用户。

## CI gates & release
- 至少有一个门禁 workflow：lint / test / build。
- CI 失败必须先修复并重新跑绿，再继续流程。
- 发布动作（release/deploy）由 tag 或 workflow_dispatch 触发，并在 issue 中回填版本与结果。

## Safety & closure
- 不提交密钥、token、私有凭据。
- 破坏性操作（删除、迁移）必须在 PR 中写明影响范围和回滚。
- 交付类型：仅当 PR 合并且 CI 通过后关闭 issue。
- 探索类型：结论沉淀完成后关闭 issue，并回填结论与后续建议。
- 关闭 issue 时回填：实现摘要、验证结果、发布结果、后续待办（如有）。
- 合并后必须执行关闭校验：若未被 `Closes #id` 自动关闭，Cloud Agent 需用 API 显式关闭并补充总结评论。
