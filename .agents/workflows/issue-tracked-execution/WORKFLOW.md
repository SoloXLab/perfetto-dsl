# Workflow: Issue 跟踪执行闭环（Create -> Execute -> Backfill -> Close）

## Trigger
- 需要用一个 issue 跟踪任务全过程（从启动到收尾）
- 任务重点是执行闭环与结果沉淀，而非复杂研发流程编排
- 适合文档改造、配置调整、轻量交付、一次性运营/技术任务

## Entry Gate（Hard Stop）
在执行任务前，必须先满足：
1. 已选择本 workflow；
2. 已创建并确认当前执行 issue `#id`；
3. 分支命名满足 `other-<issue id>`（允许 `cursor/other-<issue id>`）。

若任一条件不满足，先回到 Create Issue 步骤，禁止进入执行。  
默认由 Cloud Agent 创建 issue，非用户手动创建。
若任务已明确属于其他专用 workflow（如 `feature-delivery`、`bugfix`、`refactor`、`exploration`、`digital-user-research`、`market-discovery`），应切换到对应 workflow，并遵循该 workflow 的分支命名规则。

## Issue rules
1. 一个 issue 对应一个最小可交付单元，避免混杂多个目标。
2. issue 必填：
   - 背景与目标（为什么做）
   - 范围与非目标（做什么/不做什么）
   - 验收标准（可观察）
   - 最小验证命令（如 lint/test/build 或等价检查）
   - 跟踪字段：当前状态（todo/doing/blocked/done）、关联分支、关联 PR（如有）
3. 执行期间持续回填：
   - 进度清单（完成/进行中/阻塞）
   - 风险与处理
   - 关键决策与依据
4. 关闭前必须完成结果回填；若存在关联 PR，PR 正文必须包含 `Closes #<issue-id>`（必要时补 `Refs #<related-id>`）。

## Delivery steps
1. Create Issue
   - 按当前任务类型选择对应模板并写入完整初始信息（不要固定使用某两个模板）。
   - 模板来源以对应 workflow 为准，集中索引见：`.agents/workflows/references/README.md`。
   - 若该任务类型没有专用模板，至少确保 issue 满足本页 `Issue rules` 的必填字段。
   - 若无 issue id，Cloud Agent 立即创建并返回 `#id`。
2. Execute
   - 按最小切片执行任务，必要时小步提交。
   - 过程中将里程碑进度回填 issue（checklist 或注释）。
3. Validate
   - 执行最小可行验证并记录命令与结果。
   - 若验证失败，修复并重试，直到满足验收标准。
4. Backfill Result
   - 使用模板：`.agents/workflows/issue-tracked-execution/assets/issue-backfill.md`
   - 在 issue 中回填交付摘要：改动、验证、风险、后续建议。
   - 若存在关联 PR，必须写明 `Closes #<issue-id>`（必要时补 `Refs #<related-id>`）。
5. Close Issue
   - 确认结果已回填且验收达成后关闭 issue。
   - 若自动关闭失败，Cloud Agent 使用 API 显式关闭。

## Outputs
- 全程可追溯的 issue 日志（创建、执行、回填、关闭）
- 可复现的最小验证记录
- 关闭 issue 时的交付总结
