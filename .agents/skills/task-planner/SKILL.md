---
name: task-planner
description: Use when starting a development task in a GitHub repo and you need to break requirements into executable, low-risk implementation steps with validation checkpoints.
---

# Task Planner

## Use this skill when
- 需求不完整或较复杂
- 任务需要多步提交

## Inputs
- 用户目标与期望产物
- 约束条件（时间、风险、兼容性、工具）
- 当前仓库状态（分支、issue、已有改动）

## Procedure
1. 将需求整理成：目标、非目标、约束、验收标准。
2. 输出 2-5 个执行步骤，每一步都包含验证方式。
3. 标记风险点（兼容性、数据、性能）。
4. 生成执行顺序与预期产出清单。

## Guardrails
- 计划必须可执行，避免抽象口号式步骤。
- 每个步骤都需有可观察的完成信号。
- 风险与验证必须成对出现。

## Output format
- Context
- Plan (numbered)
- Risks
- Validation commands

## Minimal example
- Context: 规范化 `.agents` 目录结构并提升可导航性。
- Plan:
  1. 新增目录索引 README；
  2. 统一 skill 文档字段；
  3. 运行结构检查并提交。
