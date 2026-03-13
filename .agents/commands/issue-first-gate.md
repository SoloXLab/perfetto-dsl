# Command: Issue First Gate

用于在所有任务开始时执行硬阻断检查，避免“未建 issue 就直接做后续工作”。

## 适用
- `feature`
- `bugfix`
- `refactor`
- `exploration`

## 执行口令（可直接贴给 Agent）
在继续之前先执行 Issue First Gate 并输出：
1) Workflow
2) Issue ID
3) Branch
4) Gate (PASS/BLOCKED)

规则：
- 如果没有 issue id，立即 BLOCKED；
- BLOCKED 时默认由 Cloud Agent 立即创建 issue（并写入完整内容），不得要求用户手动创建；
- 仅在创建失败且确认是环境故障时，才允许输出 issue 草稿 + 错误信息 + 重试命令；
- Gate=PASS 前禁止进入后续任务动作（实现、提交、PR、实验执行等）。

输出模板：
Workflow: <feature|bugfix|refactor|exploration>
Issue: <#123 or BLOCKED>
Branch: <type-id or BLOCKED>
Gate: <PASS|BLOCKED>
Next Action: <agent-create-issue / implement / etc.>

## 常见误用
- 误用 1：先写代码后补 issue。→ 违规，必须先 issue。
- 误用 2：只有标题没有 issue id。→ 仍然 BLOCKED。
- 误用 3：PR 未引用 issue。→ 违规，必须 `Closes #id` 或 `Refs #id`。
- 误用 4：让用户手动创建 issue。→ 违规，默认应由 Cloud Agent 完成。
