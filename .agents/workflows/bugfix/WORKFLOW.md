# Workflow: 修复缺陷（Issue-driven）

## Trigger
- 线上故障、测试缺陷、回归问题

## Entry Gate（Hard Stop）
在执行 Implement + PR 前，必须先满足：
1. 已选择本 workflow；
2. 已创建并确认 Bug issue `#id`；
3. 分支命名满足 `bugfix-<issue id>`（允许 `cursor/bugfix-<issue id>`）。
若任一条件不满足，先回到 Create Issue 步骤，禁止进入实现。
默认由 Cloud Agent 创建 bug issue，非用户手动创建。

## Issue rules
1. 创建 Bug issue，记录：现象、影响范围、严重级别、环境信息。
   - 模板路径：`.agents/workflows/bugfix/assets/issue-bugfix.md`
2. Bug issue 必填：复现步骤、预期/实际、根因分析、修复方案、回归验证计划。
3. 复杂故障可建立父级 incident issue，并拆分多个 bugfix sub-issues。
4. 允许滚动展开：先完整记录已确认信息，再补充新发现。

## Delivery steps
1. Reproduce & isolate
   - 最小复现并确认根因。
   - 若缺少 bug issue，Cloud Agent 需先创建并补齐复现信息。
2. Implement + PR
   - 分支名使用 `bugfix-<issue id>`。
   - 按 bug issue 建分支，修复根因并补防回归。
   - PR 正文必须标注 `Closes #<bug-id>`。
3. CI gates
   - 运行并通过相关测试/构建门禁。
   - 失败即修复并重跑。
4. Merge + release
   - 合并后触发发布。
5. Close issues
   - 先验证 bug issue 是否已自动关闭；若未关闭，Cloud Agent 显式关闭。
   - 记录发布版本、监控观察项、遗留风险。

## Outputs
- 缺陷完整证据链（复现、根因、修复、验证）
- 关联 PR / CI / release 结果
