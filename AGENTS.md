# AGENTS Guide (Cursor/Claude Quick Control Panel)

目标：让 Cursor/Claude **只看这一页** 就能快速选择正确的 workflow、skill、command、rule 并执行。

## 0) 30 秒决策入口（先选这个）

| 任务类型 | 选用 Workflow | 必选 Skill | 推荐模板 | 分支命名 | PR 要求 |
|---|---|---|---|---|---|
| 新功能 / 新接口 / 新页面 | `.agents/workflows/feature-delivery/WORKFLOW.md` | `github-operator`（可叠加 `task-planner`） | `.agents/workflows/feature-delivery/assets/issue-feature.md` | `feature-<issue id>`（或 `cursor/feature-<issue id>`） | 必须 |
| 缺陷修复 / 回归问题 | `.agents/workflows/bugfix/WORKFLOW.md` | `github-operator`（可叠加 `task-planner`） | `.agents/workflows/bugfix/assets/issue-bugfix.md` | `bugfix-<issue id>`（或 `cursor/bugfix-<issue id>`） | 必须 |
| 重构 / 技术债治理 | `.agents/workflows/refactor/WORKFLOW.md` | `github-operator`（可叠加 `task-planner`） | `.agents/workflows/refactor/assets/issue-refactor.md` | `refactor-<issue id>`（或 `cursor/refactor-<issue id>`） | 必须 |
| 方案调研 / 技术选型 / Spike | `.agents/workflows/exploration/WORKFLOW.md` | `exploration-logger` | `.agents/workflows/exploration/assets/issue-exploration.md` | `exploration-<issue id>`（或 `cursor/exploration-<issue id>`） | 可选 |
| 市场分析 / 赛道机会判断 | `.agents/workflows/market-discovery/WORKFLOW.md` | `market-discovery`（可叠加 `task-planner`） | `.agents/workflows/market-discovery/assets/issue-market-discovery.md` + 按 `market-discovery` 五节结构输出 | `exploration-<issue id>`（或 `cursor/exploration-<issue id>`） | 可选 |
| 用户评论分析 / 用户旅程还原 / 被动式用户研究 | `.agents/workflows/digital-user-research/WORKFLOW.md` | `digital-user-research`（可叠加 `task-planner`） | `.agents/workflows/digital-user-research/assets/issue-digital-user-research.md` + 六阶段报告输出 | `exploration-<issue id>`（或 `cursor/exploration-<issue id>`） | 可选 |
| 通用任务闭环（建单跟踪→执行→回填→关单） | `.agents/workflows/issue-tracked-execution/WORKFLOW.md` | `github-operator`（可叠加 `task-planner`） | 按任务类型选择模板（参考 `.agents/workflows/references/README.md`）+ `.agents/workflows/issue-tracked-execution/assets/issue-backfill.md` | `other-<issue id>`（或 `cursor/other-<issue id>`） | 建议 |
| 任务复杂、需求不完整 | （先选上面五类之一） | `task-planner`（前置） | 按任务类型选择 | 跟随任务类型 | 跟随任务类型 |
| 需要写/改 PR 描述 | （任意） | `pr-writer` | `.agents/skills/pr-writer/assets/pr-body.md` | 不变 | 建议 |

---

## 0.5) 开工门禁（Issue First Gate，硬阻断）

> 适用范围：`feature / bugfix / refactor / exploration / market-discovery`（即所有任务）

1. 在**任何实现动作之前**（包括改代码、写提交、开 PR、跑实现相关命令），必须先满足：
   - 已创建 issue 并拿到 `#id`；
   - 已选定 workflow；
   - 已确定分支命名为 `<type>-<issue id>`（允许 `cursor/` 前缀）。
2. 若未拿到 issue id，必须立即进入“Create Issue”步骤，**禁止继续后续工作**。
3. 默认由 Cloud Agent 直接创建 issue 并写入完整内容（优先使用 `GITHUB_TOKEN` 调 GitHub API），禁止把创建动作转交给用户。
4. 仅当环境故障导致创建失败时，才允许输出“待创建 issue 草稿 + 错误信息 + 重试命令”；在拿到 `#id` 前保持阻断状态。
5. 每次任务开始时，先输出一次 Gate 状态：
   - `Workflow: ...`
   - `Issue: #...`（无则 `BLOCKED`）
   - `Branch: ...`
   - `Gate: PASS/BLOCKED`

## 0.6) PR 关联门禁（PR-Issue Link Gate，硬阻断）

1. 创建或更新 PR 时，PR 正文必须关联**当前任务的相关 issue**：
   - 必填：`Closes #<current-issue-id>`
   - 可选：`Refs #<parent-or-related-id>`
2. 若 PR 未关联 issue、关联了错误 issue，或仅在评论区提到 issue，均视为 `BLOCKED`。
3. `BLOCKED` 状态下禁止合并，必须先修正 PR 正文中的 Linked Issues。

---

## 1) 执行优先级（必须遵守）

1. 本文件 `AGENTS.md`（根级强约束）
2. `.agents/rules/*.md`（通用规则）
3. `.agents/workflows/*/WORKFLOW.md`（任务流程）
4. `.agents/skills/*/SKILL.md`（任务能力包）
5. `.agents/commands/*`（命令手册，当前仓库预留）
6. 资源按标准子目录组织：`scripts/`（可执行代码）/ `references/`（补充文档）/ `assets/`（模板、图片、数据等静态资源）。

---

## 2) 强约束（不可跳过）

1. 开始实现前，先选择匹配 workflow：`feature / bugfix / refactor / exploration / digital-user-research / market-discovery / issue-tracked-execution`。  
2. 所有任务都必须先通过 Issue First Gate；交付类任务再走完整链路：`Create Issue(s) -> PR -> CI gates -> Fix CI -> Release -> Close Issue`。
3. Issue 允许滚动展开：先细化当前阶段，后续逐步补全。  
4. 新需求类 issue 必须采用 Epic -> Feature -> User Story 层级，且使用 OpenSpec（Context / Scope / Constraints / Acceptance / Non-goals）。  
5. 每个 PR 只做一个最小交付单元，并在 PR 正文中显式关联 issue（必须包含 `Closes #id`，必要时补 `Refs #parent`）。  
6. 分支命名：`<type>-<issue id>`；允许工具前缀：`cursor/<type>-<issue id>`。  
7. 提交信息：`type(scope): summary`（例：`feat(api): add xxx endpoint`）。  
8. 必须记录最小可行验证命令；CI 未通过不得推进。  
9. 涉及 GitHub 鉴权操作时，token 只能从环境变量 `GITHUB_TOKEN` 读取，禁止硬编码或写入仓库文件。  
10. PR 合并后，Cloud Agent 必须主动确认并完成 issue 关闭（自动关闭失败时使用 API 显式关闭），并回填结果。  
11. 除非用户明确要求，否则不得把“创建 issue / 关联 PR / 关闭 issue”转交给用户。  
12. 不提交任何密钥、token、私有凭据。  

---

## 3) 资产目录总览（直接选，不必再找）

### 3.1 Rules（目录：`.agents/rules/`）

| 文件 | 用途 |
|---|---|
| `github-agent-rules.md` | GitHub 交付总规则：生命周期、分支、提交、PR、CI、Release、关闭 issue |
| `review-rules.md` | 评审规则：优先正确性/风险，要求验证证据与回滚方案 |

### 3.2 Workflows（目录：`.agents/workflows/`）

| 文件 | 触发场景 | 关键产物 |
|---|---|---|
| `feature-delivery/WORKFLOW.md` | 新需求开发 | Epic/Feature/Story issue 链路 + PR/CI/Release |
| `bugfix/WORKFLOW.md` | 缺陷修复 | 复现/根因/修复/回归证据链 |
| `refactor/WORKFLOW.md` | 重构治理 | 基线与等价性验证记录 |
| `exploration/WORKFLOW.md` | 调研探索 | 单一 exploration issue 与结论建议 |
| `digital-user-research/WORKFLOW.md` | 用户评论分析/旅程还原 | 单一 digital-user-research issue 跟踪 + 六阶段研究报告 + 结论回填 |
| `issue-tracked-execution/WORKFLOW.md` | 通用 issue 跟踪执行 | 建 issue、执行、回填结果、关闭 issue 闭环 |
| `market-discovery/WORKFLOW.md` | 市场分析/赛道判断 | 单一 market-discovery issue 跟踪 + 分节回填 + 决策结论 + issue关闭 |
| `references/README.md` | workflow 引用索引 | workflow 目录结构、选型说明与统一引用入口 |

### 3.3 Skills（目录：`.agents/skills/`）

| Skill | 何时使用 | 作用 |
|---|---|---|
| `task-planner` | 复杂任务开始前 | 把目标拆成低风险步骤并附验证点 |
| `github-operator` | 实施交付全过程 | 实现、验证、提交、PR 内容准备 |
| `exploration-logger` | 研究/Spike | 单 issue 记录探索过程与结论 |
| `pr-writer` | 需要提交高质量 PR 描述 | 输出背景、改动、验证、风险、回滚 |
| `market-discovery` | 市场洞察/赛道分析/竞品验证 | 完成发现机会五节分析并输出 go/no-go 决策 |
| `digital-user-research` | 用户评论分析/旅程还原/无访谈研究 | 基于公开评论与社区讨论产出用户旅程地图和设计建议报告 |

### 3.4 Commands（目录：`.agents/commands/`）

- 已提供门禁命令文档：`issue-first-gate.md`（建议在每个任务开头先执行）。
- 已提供鉴权检查命令文档：`github-auth-token.md`（执行 GitHub 鉴权操作前先执行）。
- 已提供交付闭环命令文档：`issue-pr-closure-gate.md`（创建 issue、PR 关联、合并后关闭的全链路检查）。
- 其他命令文档可继续放入：`.agents/commands/`。

**内建命令清单（可直接执行）**
- 查找 agent 资产：`rg --files .agents`
- 搜索规则/流程关键词：`rg "workflow|issue|CI|release" .agents`
- 最小验证（按项目实际替换）：`<lint-cmd> && <test-cmd> && <build-cmd>`
- 变更检查：`git status` / `git diff --staged`

### 3.5 Assets（模板等静态资源，按域分布）

| 模板路径 | 归属 | 用途 |
|---|---|---|
| `.agents/workflows/feature-delivery/assets/issue-feature.md` | workflow | Feature issue |
| `.agents/workflows/bugfix/assets/issue-bugfix.md` | workflow | 缺陷 issue |
| `.agents/workflows/refactor/assets/issue-refactor.md` | workflow | 重构 issue |
| `.agents/workflows/exploration/assets/issue-exploration.md` | workflow | 探索 issue |
| `.agents/workflows/market-discovery/assets/issue-market-discovery.md` | workflow | 市场分析 issue（分节进度+决策门禁） |
| `.agents/workflows/digital-user-research/assets/issue-digital-user-research.md` | workflow | 用户研究 issue（阶段进度 + 证据 + 结论） |
| `.agents/skills/pr-writer/assets/pr-body.md` | skill | PR 描述正文 |

---

## 4) 标准执行清单（Checklist）

### 实现前
- [ ] 已选择 workflow（feature/bugfix/refactor/exploration/digital-user-research/market-discovery/issue-tracked-execution）
- [ ] 已选择对应 skill（必要时先用 task-planner）
- [ ] 已确定 issue 与模板，并拿到 issue id（所有任务必填）
- [ ] 已输出 Gate 状态，且为 `Gate: PASS`（所有任务）

### 实现中
- [ ] 小步提交、单一逻辑变更
- [ ] 每次改动可验证、可回滚

### 提交/PR 前
- [ ] 运行最小可行验证并记录命令
- [ ] Commit message 符合 `type(scope): summary`
- [ ] PR 描述包含：Background / What changed / Validation / Risk / Rollback
- [ ] PR 正文包含 `Closes #<current-issue-id>`（必要时补 `Refs #<parent-id>`）

### 收尾
- [ ] CI 全绿（或失败已说明并处理）
- [ ] 发布动作已触发并记录结果（按任务类型适用）
- [ ] issue 已由 Cloud Agent 回填并关闭（所有任务）

---

## 5) 一句话执行策略

先按任务类型选 workflow，再套 skill，按模板写 issue/PR，用最小验证命令保底，最后通过 CI 与 release 完成交付闭环。
