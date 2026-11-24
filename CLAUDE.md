# LinkedIn assistant

Rules: /mnt/project-files/linkedin-stats/plans/outreach_rules.md.

## Watchdog
Use the `vagthund` subagent (.claude/agents/vagthund.md) at the start and end of every LinkedIn session and whenever a scheduled task fails, is missed, uses stale data, or approval pickup looks wrong. It self-heals, logs fixes in linkedin-stats/logs, and only mails Michael when he must act.
