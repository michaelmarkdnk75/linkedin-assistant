#!/usr/bin/env python3
"""Send gate (regressions R5 first-answer-wins, R6 RET is not approval, R7 never send twice; outreach_rules.md sections 51, 52, 0).
Usage: send_gate.py <proposal_id>   Exit 0 only if plans/pending_proposals.json lists the id with status 'approved'.
Exit 1 = id unknown, still open (no Ja), rejected or cancelled (superseded). Exit 4 = already sent (never send twice).
A RET reply must first be recorded as a NEW proposal (status open) and mailed again; it only becomes 'approved' after a fresh Ja."""
import sys, json, os
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "plans", "pending_proposals.json")
d = json.load(open(F)) if os.path.exists(F) else {"items": []}
it = [i for i in d["items"] if i["id"] == sys.argv[1]]
if not it: print("BLOCKED: id not in registry (no proposal on record):", sys.argv[1]); sys.exit(1)
s = it[-1]["status"]
if s == "approved": print("OK approved", sys.argv[1]); sys.exit(0)
if s == "sent": print("BLOCKED: already sent - never send twice"); sys.exit(4)
print("BLOCKED: status", s, "- needs a Ja (or was rejected/superseded)"); sys.exit(1)
