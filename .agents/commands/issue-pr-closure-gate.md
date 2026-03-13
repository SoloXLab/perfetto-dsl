# Command: Issue-PR-Closure Gate

用于保证 GitHub 交付闭环三件事不遗漏：
1) Cloud Agent 创建 issue  
2) PR 正文关联 issue  
3) PR 合并后 issue 关闭并回填总结

## 适用
- `feature`
- `bugfix`
- `refactor`
- `exploration`（PR 可选，但 issue 创建与关闭仍适用）

## 执行口令（可直接贴给 Agent）
在任务结束前执行 Issue-PR-Closure Gate 并输出：
1) Issue Created By  
2) PR Link Status  
3) Merge Status  
4) Issue Close Status  
5) Gate  
6) Next Action

规则：
- Issue Created By 必须是 `cloud-agent`（默认），不是 `user`；
- PR 必须包含 `Closes #<current-issue-id>`（exploration 可用 `Refs #<current-issue-id>`）；
- 合并后必须验证 issue 状态为 closed；
- 若未自动关闭，Cloud Agent 必须用 API 显式关闭并回填总结；
- 任一项失败，Gate=BLOCKED。

输出模板：
Issue Created By: <cloud-agent | user | unknown>
PR Link Status: <closes-linked | refs-linked | missing>
Merge Status: <merged | open | unknown>
Issue Close Status: <closed | open | unknown>
Gate: <PASS | BLOCKED>
Next Action: <close issue / patch PR body / retry API / done>

## 最小检查建议
- 检查 PR 关联语句：PR 正文包含 `Closes #<id>`（或 exploration 场景 `Refs #<id>`）
- 检查 issue 状态：`open/closed`
- 关闭 issue 后补充总结：实现摘要 + 验证结果 + 发布结果（如适用）

## 常见误用
- 误用 1：issue 内容写好了但让用户去创建。→ 违规，应由 Cloud Agent 创建。
- 误用 2：PR 没写 `Closes #id`。→ 违规，无法保证自动关闭。
- 误用 2.1：PR 链接了不相关 issue。→ 违规，必须链接当前任务 issue。
- 误用 3：PR 合并后不检查 issue 状态。→ 违规，必须校验并补齐关闭动作。
