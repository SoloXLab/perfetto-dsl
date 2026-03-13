# Review Rules

- 优先审查正确性与风险，再看代码风格。
- 必查项：PR 是否在正文中关联了当前任务 issue（`Closes #<current-issue-id>`）；未满足则直接阻断合并建议。
- 对每个核心改动回答三件事：
  1. 为什么要改
  2. 如何证明改对了
  3. 出问题怎么回滚
- 若新增 workflow/skill/template，必须给出一个最小示例。
- 避免“只描述现象不提供可执行建议”的 review comment。
