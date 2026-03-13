---
name: github-operator
description: Use when an agent needs to implement, validate, commit, and prepare pull request content in a GitHub repository with safe, auditable steps.
---

# GitHub Operator

## Use this skill when
- 需要在仓库内进行完整交付（实现 + 验证 + 提交 + PR）

## Inputs
- 已确定 workflow 与 issue `#id`
- 目标变更范围与非目标
- 项目最小验证命令（lint/test/build）
- `GITHUB_TOKEN`（GitHub API 鉴权来源）

## Procedure
0. 预检 Gate：读取 AGENTS/rules/workflow 并确认任务类型。
1. 所有任务先过 Issue First Gate：
   - workflow 已选定；
   - issue id 已存在；
   - 分支命名符合规则。
   - 未通过时，Cloud Agent 直接创建 issue 并拿到 id，禁止要求用户手动创建。
2. 实施变更：保持小步、可回滚。
3. 验证：执行最小可行测试并记录命令。
4. 提交：使用规范 commit message。
5. PR：按模板填写背景、改动、验证、风险、回滚，并包含 `Closes #id`。
6. 合并后闭环：验证 issue 是否自动关闭；若未关闭，Cloud Agent 用 API 显式关闭并回填总结。

## Guardrails
- 禁止提交敏感信息。
- 失败测试需明确说明影响。
- 不将多个不相关变更合并到同一个提交/PR。
- 未完成验证前不得推进到合并阶段。
- 除非用户明确要求，不把 GitHub 操作（建 issue / 关 issue）交给用户。

## Outputs
- 可追溯的提交记录（符合提交规范）
- 可执行的验证命令与结果
- 结构化 PR 描述（Background/What changed/Validation/Risk/Rollback）
- issue 闭环证据（PR 关联与关闭状态）

## Minimal example
- Commit: `refactor(agents): add .agents navigation readmes`
- Validation: `git status && git diff --staged`
