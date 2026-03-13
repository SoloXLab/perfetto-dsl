# Workflow: 新需求开发（Issue-driven + OpenSpec）

## Trigger
- 新需求开发
- 新模块/新接口/新页面建设

## Entry Gate（Hard Stop）
在执行 Implement + PR 前，必须先满足：
1. 已选择本 workflow；
2. 已创建并确认当前 Story issue `#id`；
3. 分支命名满足 `feature-<issue id>`（允许 `cursor/feature-<issue id>`）。
若任一条件不满足，先回到 Create Issue 步骤，禁止进入实现。
默认由 Cloud Agent 创建 issue，非用户手动创建。

## Issue rules
1. 建立 Epic issue（业务目标与范围）。
2. Epic 下建立 Feature issue（功能切片与依赖）。
3. Feature 下建立 User Story issue（可单独进入一个 PR 的最小交付）。
4. Epic/Feature/User Story 均按 OpenSpec 模板记录：Context / Scope / Constraints / Acceptance / Non-goals。
   - 模板路径：
     - `.agents/workflows/feature-delivery/assets/issue-feature.md`
5. 使用“滚动展开”：先细化当前要做的 Story，其余后续逐步细化。

## Delivery steps
1. Select Story
   - 选择一个 User Story 作为当前开发目标。
   - 若缺少 issue，Cloud Agent 需先创建并完善内容。
2. Implement + PR
   - 分支名使用 `feature-<issue id>`。
   - 基于 story issue 建分支、实现、提交并发起 PR。
   - PR 正文必须写明 `Closes #<story-id>`，必要时 `Refs #<feature-id>`。
3. CI gates
   - 触发 lint/test/build。
   - CI 失败则修复并重跑，直至通过。
4. Merge + release
   - 合并后触发发布流程（tag 或 workflow_dispatch）。
5. Close issues
   - 先验证 Story issue 是否已自动关闭；若未关闭，Cloud Agent 显式关闭。
   - 在 Feature/Epic 回填进展、版本、剩余项。

## Outputs
- Epic/Feature/User Story 层级 issue 链路
- 关联 PR、CI、release 记录
- 关闭 issue 的交付总结
