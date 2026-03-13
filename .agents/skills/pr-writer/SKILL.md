---
name: pr-writer
description: Use when creating or updating a GitHub pull request description so reviewers can quickly understand context, changes, validation, risk, and rollback.
---

# PR Writer

## Required sections
- Linked Issues (`Closes #id`, optional `Refs #parent`)
- Background
- What changed
- Validation
- Risk
- Rollback

## Inputs
- 提交列表与核心 diff
- 验证命令与结果
- 风险影响面与回滚路径

## Steps
1. 从提交与 diff 中提取改动点（按模块分组）。
2. 列出验证命令与结果。
3. 评估风险等级与影响面。
4. 写明回滚步骤（revert commit 或 feature flag）。
5. 套用 `.agents/skills/pr-writer/assets/pr-body.md` 输出。

## Guardrails
- 避免空泛描述（如“优化了一些代码”）。
- Validation 需可复现，命令与结果成对出现。
- Risk 与 Rollback 必须具体到影响范围和执行动作。
- 交付类 PR 必须包含 `Closes #id`，否则视为不合格描述。

## Outputs
- 结构化 PR 描述正文（可直接粘贴）
- 审阅者可快速定位改动与验证证据

## Minimal example
- Validation:
  - `npm test` ✅
  - `npm run build` ✅
