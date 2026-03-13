# Workflow: 被动式用户研究（Digital User Research）

## Trigger
- 用户评论分析（好评/差评/中性）
- 用户旅程还原（无访谈条件下）
- 从公开社区反馈中提炼痛点、诉求与设计建议
- 典型表达：
  - “帮我分析用户评论”
  - “从评论里还原用户旅程”
  - “没有访谈条件，先做用户研究”

## Required skill
- `digital-user-research`（必选）
- 可叠加：`task-planner`（当范围过大、目标不清晰时）

## Entry Gate（Hard Stop）
在执行任何研究动作前，必须先满足：
1. 已选择本 workflow；
2. 已创建并确认 Digital User Research issue `#id`；
3. 分支命名满足 `exploration-<issue id>`（允许 `cursor/exploration-<issue id>`，若无需分支则至少记录预期分支名）。

若任一条件不满足，先回到 Create Issue 步骤，禁止进入研究执行。  
默认由 Cloud Agent 创建 issue，禁止转交用户手动创建。

## Issue rules（强制）
1. 只创建一个当前研究对应的 digital-user-research issue。
2. issue 必须写明：
   - 研究对象（产品/功能/场景）
   - 研究焦点（整体体验或功能级旅程）
   - 数据来源与最小样本目标（建议 >=30 条）
   - 预期输出格式（六阶段报告）
3. 每完成一个阶段（Stage 0~6）都要回填 issue 进度（可评论追加）。
4. 报告结论必须明确区分：
   - 用户原话证据
   - 分析推断（标注“推断”）
5. 完成后由 Cloud Agent 关闭 issue；若自动关闭失败，显式关闭并记录关闭证据。

## Steps
1. Create issue
   - 使用模板：`.agents/workflows/digital-user-research/assets/issue-digital-user-research.md`。
2. Run digital-user-research skill
   - 严格按六阶段执行：
     - Stage 0：明确研究目标
     - Stage 1：数据收集与预处理
     - Stage 2：主题聚类分析
     - Stage 3：用户旅程还原
     - Stage 4：体验断点识别
     - Stage 5：设计建议
     - Stage 6：输出报告
3. Stage checkpoint updates
   - 每阶段结束后在 issue 追加：
     - 本阶段结论
     - 证据来源
     - 未决问题 / 数据不足项
4. Final decision log
   - 在 issue 中回填最终摘要：
     - Top 诉求与高频断点
     - 优先级建议（短/中/长期）
     - 后续动作（进入 feature-delivery / 继续补充数据）
5. Close issue
   - 关闭 issue 并回填最终摘要链接（报告正文或评论链接）。
6. Transition gate（转开发）
   - 若结论进入实现，必须新建 delivery issue（Epic/Feature/User Story）并切换到 `feature-delivery` workflow。

## Outputs
- 单一 issue 的完整研究轨迹（阶段进度 + 证据）
- 用户旅程地图（宏观或功能级）
- 体验断点分级（严重断点 / 摩擦点 / 满意点）
- 设计建议（按优先级）
- issue 关闭证据与后续执行建议
