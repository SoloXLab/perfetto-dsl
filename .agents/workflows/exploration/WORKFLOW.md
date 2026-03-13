# Workflow: 探索思路（Research / Spike）

## Trigger
- 方案调研、技术选型、风险验证、PoC

## Entry Gate（Hard Stop）
在执行探索动作前，必须先满足：
1. 已选择本 workflow；
2. 已创建并确认 Exploration issue `#id`；
3. 分支命名满足 `exploration-<issue id>`（允许 `cursor/exploration-<issue id>`，若无需分支则至少记录预期分支名）。
若任一条件不满足，先回到 Create Issue 步骤，禁止进入探索执行。
默认由 Cloud Agent 创建 exploration issue，非用户手动创建。

## Issue rules
1. 只创建一个 Exploration issue。
   - 模板路径：`.agents/workflows/exploration/assets/issue-exploration.md`
2. 在 issue 中持续记录：假设、实验设计、过程日志、结果、结论、下一步建议。
3. 若后续转开发，再从结论拆出 Epic/Feature/User Story。

## Steps
1. Define question
   - 明确探索问题与成功标准。
2. Explore
   - 按实验项记录过程与证据。
3. Conclude
   - 形成可执行建议（采纳/不采纳/待验证）。
4. Optional PR
   - 若需要 PR，分支名使用 `exploration-<issue id>`（或 `other-<issue id>`）。
   - 仅在需要提交 PoC 或文档时创建 PR，且应包含 `Refs #<exploration-id>`。
5. Transition gate（转开发门禁）
   - 若探索结论转为 feature/bugfix/refactor，必须先创建对应 delivery issue 并拿到 `#id`，再进入实现。
6. Close issue
   - 探索结论沉淀后由 Cloud Agent 关闭 exploration issue，并回填结论与后续建议。

## Outputs
- 探索 issue 完整日志
- 结论与决策建议
- （可选）PoC PR
