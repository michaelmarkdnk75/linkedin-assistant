#!/usr/bin/env python3
"""Work list for the sender run (read-only; section 66). Usage: send_queue.py [--ids FW221,C28-1]
Prints every registry item with status 'approved' grouped by channel, with the guards that channel needs BEFORE sending, so the sender
spends no calls finding them. It never relaxes a guard: follows need only send_gate (live connection check by the connector),
comments need comment_guard lang+dupe on LIVE saved tool output, cv needs cv_guard with --thread and Drive metadata files, messages need the full-thread read."""
import json, os, sys
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "plans", "pending_proposals.json")
items = [i for i in json.load(open(F))["items"] if i["status"] == "approved"]
if "--ids" in sys.argv:
    w = set(sys.argv[sys.argv.index("--ids") + 1].split(",")); items = [i for i in items if i["id"] in w]
GUARDS = {"follow": "send_gate (done by this list) + live connection check; no file guards needed -> batch them first, they are cheap",
          "comment": "like first; save live scrape_linkedin_get_post_comments output (harness saves large results to a file: pass THAT path), comment_guard.py lang + dupe, send_gate",
          "cv": "Drive get_file_metadata saved output -> cv_guard.py ... --thread <full thread output path>, one CV per person ever, send_gate",
          "message": "full thread read, recent-dialogue check, send_gate", "inmail": "full thread read, send_gate", "invite": "live connection check, send_gate"}
by = {}
for i in items: by.setdefault(i["channel"], []).append(i)
for ch, l in sorted(by.items(), key=lambda x: {"follow": 0}.get(x[0], 1)):
    print(f"== {ch} ({len(l)}): {GUARDS.get(ch, 'send_gate')}")
    for i in l: print(f"  {i['id']} {i['person_key']} target={i.get('target')} note={str(i.get('note', ''))[:50]}")
print(f"total approved: {len(items)}")
