# commands/

Command playbooks for repeatable workflow checks.

## Files

- `issue-first-gate.md`: hard-stop check before implementation actions.
- `github-auth-token.md`: preflight check for GitHub token source and presence.
- `issue-pr-closure-gate.md`: end-to-end check for issue creation, PR linking, and post-merge closure.

## Usage

- Run gate checks at task start.
- If gate is `BLOCKED`, Cloud Agent should create issue directly (not delegate to user).
- Do not proceed to implementation/commit/PR until gate is `PASS`.
