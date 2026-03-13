# Command: GitHub Auth Token Check

用于在执行 GitHub 鉴权操作前，统一确认 token 来源与可用性。

## 适用
- 需要访问 GitHub API（REST/GraphQL）
- 需要用脚本执行 GitHub 写操作（创建 issue、更新 issue、触发流程等）
- 需要在命令中显式传递 Authorization Header

## 执行口令（可直接贴给 Agent）
在继续之前先执行 GitHub Auth Token Check 并输出：
1) Token Source
2) Token Presence
3) Auth Gate
4) Next Action

规则：
- Token Source 必须是环境变量 `GITHUB_TOKEN`；
- 禁止使用硬编码 token；
- 若 `GITHUB_TOKEN` 缺失或为空，Auth Gate=BLOCKED；
- BLOCKED 时仅允许补齐环境变量或切换无鉴权路径。

输出模板：
Token Source: <GITHUB_TOKEN | BLOCKED>
Token Presence: <present | missing>
Auth Gate: <PASS | BLOCKED>
Next Action: <continue GitHub ops / set env / use unauth flow>

## 最小检查命令
- `test -n "$GITHUB_TOKEN" && echo "Token Presence: present" || echo "Token Presence: missing"`

## 常见误用
- 误用 1：在脚本里写死 token。→ 违规，必须从 `GITHUB_TOKEN` 读取。
- 误用 2：把 token 写入 `.env.example` 的默认值。→ 违规，示例应留空或占位符。
- 误用 3：日志打印完整 Authorization header。→ 违规，必须脱敏。
