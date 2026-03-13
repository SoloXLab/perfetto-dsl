# Workflow: 重构代码（Issue-driven）

## Trigger
- 结构性重构、可维护性改进、技术债清理

## Entry Gate（Hard Stop）
在执行 Implement + PR 前，必须先满足：
1. 已选择本 workflow；
2. 已创建并确认 Refactor issue（或 sub-issue）`#id`；
3. 分支命名满足 `refactor-<issue id>`（允许 `cursor/refactor-<issue id>`）。
若任一条件不满足，先回到 Create Issue 步骤，禁止进入实现。
默认由 Cloud Agent 创建 refactor issue，非用户手动创建。

## Issue rules
1. 创建 Refactor issue，明确动机、范围边界与非目标。
   - 模板路径：`.agents/workflows/refactor/assets/issue-refactor.md`
2. 必填内容：当前问题、目标架构/设计、风险清单、等价性验证策略。
3. 大重构拆分 sub-issues（按模块或阶段），每个子项能单独 PR。
4. 采用滚动展开：先细化当前切片，后续切片迭代细化。

## Delivery steps
1. Baseline
   - 建立当前行为基线（测试/快照/关键指标）。
   - 若缺少 refactor issue，Cloud Agent 需先创建并补齐边界与风险。
2. Implement + PR
   - 分支名使用 `refactor-<issue id>`。
   - 每次只做一个重构切片，避免混入功能变更。
   - PR 正文必须标注 `Closes #<refactor-subissue-id>`。
3. CI gates
   - 通过 lint/test/build；失败则修复重跑。
4. Merge + release
   - 合并后触发发布（若项目要求）。
5. Close issues
   - 先验证子 issue 是否已自动关闭；若未关闭，Cloud Agent 显式关闭。
   - 在父 issue 回填改进收益与剩余债务。

## Outputs
- 重构前后对照与等价性验证记录
- 关联 PR / CI / release 记录
