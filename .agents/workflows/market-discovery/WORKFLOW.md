# Workflow: 市场机会发现（Market Discovery）

## Trigger
- 用户要做市场分析、赛道判断、竞品洞察、机会发现
- 典型表达：  
  - “帮我分析这个市场”  
  - “这个赛道值不值得做”  
  - “帮我做市场洞察 / 分析竞品 / 找市场空白”

## Required skill
- `market-discovery`（必选）
- 可叠加：`task-planner`（当范围过大或目标不清晰时）

## Entry Gate（Hard Stop）
在执行任何市场分析动作前，必须先满足：
1. 已选择本 workflow；
2. 已创建并确认 Market Discovery issue `#id`；
3. 分支命名满足 `exploration-<issue id>`（允许 `cursor/exploration-<issue id>`，若无需分支则至少记录预期分支名）。

若任一条件不满足，先回到 Create Issue 步骤，禁止进入分析执行。  
默认由 Cloud Agent 创建 issue，禁止转交用户手动创建。

## Issue rules（强制）
1. 只创建一个当前分析对应的 market-discovery issue。
2. issue 须包含：分析对象、范围、数据口径、完成标准、预期输出格式。
3. 每完成一节（节一~节五）都要回填 issue 进度（可评论追加）。
4. 分析完成后，必须将“决策门禁结论”贴回 issue（正文或评论），包含：
   - 结论：`✅ 立即进入 / ⚠️ 进入但先解障碍 / 🕐 等待 / ❌ 放弃`
   - 关键依据（需求真实性、时机窗口、竞品空白、执行风险）
   - 下一步建议（A/B）
5. 结论回填后，由 Cloud Agent 关闭该 issue；若自动关闭失败，显式关闭并记录关闭证据。

## Steps
1. Create issue
   - 使用市场分析 issue 模板（`.agents/workflows/market-discovery/assets/issue-market-discovery.md`）创建 market discovery 追踪 issue。
   - 在 issue 中写明分析对象、范围边界、假设与待验证项。
2. Run market-discovery skill
   - 按技能五节流程执行，确保事实与推断分离。
3. Section checkpoint updates
   - 每节结束后在 issue 追加：
     - 节点结论
     - 证据来源
     - 未决问题
4. Final decision log
   - 将“发现机会 · 决策门禁”完整结论贴入 issue。
5. Close issue
   - 关闭 issue 并回填最终摘要（结论 + 下一步动作）。
6. Transition gate（转开发）
   - 若结论为“进入”，再创建对应 delivery issue（Epic/Feature/User Story）并切换到 `feature-delivery` workflow。

## Outputs
- 单一 issue 的完整市场分析追踪记录（含分节进度）
- 决策门禁结论（go/no-go）
- issue 关闭证据与后续执行建议
