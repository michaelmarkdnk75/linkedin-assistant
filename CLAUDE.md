# LinkedIn assistant

Rules: /mnt/project-files/linkedin-stats/plans/outreach_rules.md.

## Watchdog
Use the `vagthund` subagent (.claude/agents/vagthund.md) at the start and end of every LinkedIn session and whenever a scheduled task fails, is missed, uses stale data, or approval pickup looks wrong. It self-heals, logs fixes in linkedin-stats/logs, and only mails Michael when he must act.

## Mail to Michael must reach the inbox
Self-sent mails only get the SENT label. After every Gmail `send_message` to michaelmarkdnk@gmail.com, call `update_message_labels` on the returned id with addLabelIds ["INBOX","UNREAD"]. Add only; never remove or change other labels, and leave pickup/archive/trash rules unchanged. Full rule: §63 in outreach_rules.md.
