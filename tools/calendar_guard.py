#!/usr/bin/env python3
"""Calendar delete guard (regression R14, 28/11-2026; outreach_rules.md section 42 + CALENDAR HOLD RULE 18/11).
Usage: calendar_guard.py <get_event_or_list_event.json> [--approved-by-michael]
Exit 0 = deleting this event is allowed: it is a HOLD created by Claude ("HOLD:" summary, description says created by Claude / HOLD-routine / 'Foreslået')
AND Michael approved the deletion (button slet*/clicks or chat), flag --approved-by-michael.
Exit 2 = refuse (not a Claude HOLD, or no approval). Never delete any other calendar event."""
import sys, json
a = [x for x in sys.argv[1:] if not x.startswith("--")]
ok = "--approved-by-michael" in sys.argv
e = json.load(open(a[0])); e = e.get("event", e)
s = str(e.get("summary", "")); d = str(e.get("description", "")).lower()
if not s.upper().startswith("HOLD"): print("REFUSED: not a HOLD event:", s); sys.exit(2)
if not any(k in d for k in ("oprettet af claude", "hold-rutine", "foreslået", "foreslaaet", "slet når", "slettes hvis")): print("REFUSED: HOLD not marked as created by Claude"); sys.exit(2)
if not ok: print("REFUSED: no approval by Michael (button/click/chat) for deleting", s); sys.exit(2)
print("OK delete allowed:", s, e.get("id", "")); sys.exit(0)
