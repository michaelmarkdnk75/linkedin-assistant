#!/usr/bin/env python3
"""Self-mail visibility check (regression R12, outreach_rules.md section 63, 26/11-2026).
Usage: selfmail_check.py <update_message_labels_response.json>  Exit 0 only if labelIds contain INBOX and UNREAD.
Run right after Gmail update_message_labels on every mail sent to michaelmarkdnk@gmail.com. Exit 1 = retry once, then report."""
import sys, json
r = json.load(open(sys.argv[1])); r = r.get("message", r)
l = set(r.get("labelIds", []))
if {"INBOX", "UNREAD"} <= l: print("OK in inbox + unread"); sys.exit(0)
print("NOT VISIBLE: labels", sorted(l)); sys.exit(1)
