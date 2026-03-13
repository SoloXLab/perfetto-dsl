---
name: exploration-logger
description: Use when running idea exploration, research spikes, or technical investigation that should be tracked in a single issue log without mandatory delivery PR.
---

# Exploration Logger

## Use this skill when
- 当前任务是探索思路/方案调研/技术选型
- 目标是形成结论与后续建议，而不是直接交付生产代码

## Inputs
- 探索问题与成功标准
- exploration issue `#id`
- 可用实验手段与证据来源

## Procedure
0. 先过 Issue First Gate：确认 workflow 已选、exploration issue 已创建并拿到 `#id`。
1. 建立单一 exploration issue（由 Cloud Agent 创建，不转交用户）。
2. 用 `.agents/workflows/exploration/assets/issue-exploration.md` 记录假设与实验计划。
3. 按时间顺序持续追加实验日志与证据。
4. 输出结论（采纳/不采纳/待验证）与下一步建议。
5. 探索完成后由 Cloud Agent 关闭 exploration issue，并回填总结。
6. 若要进入开发，拆分为 Epic/Feature/User Story 并转交付流程。

## Guardrails
- 结论必须可追溯到实验记录与证据。
- 记录不只写结论，还需写约束与失败尝试。
- 探索转开发时，必须重新走 delivery issue 门禁。
- 除非用户明确要求，不把 issue 创建/关闭动作交给用户。

## Outputs
- 完整探索日志（假设、实验、证据、结论）
- 决策建议（采纳/不采纳/待验证）
- 后续可执行任务拆分建议（如需）

## Output checklist
- [ ] One exploration issue created
- [ ] Hypotheses and experiment logs recorded
- [ ] Clear decision documented
- [ ] Exploration issue closed by Cloud Agent with summary
- [ ] Follow-up delivery issues proposed (if needed)

## Minimal example
- Hypothesis: 「方案 A 在高并发下优于方案 B」
- Evidence: 基准数据、失败场景、资源占用对比
- Decision: 「暂不采纳 A，转向 B + 缓存层优化」
