#!/usr/bin/env python3
"""Follows approval mail template (locked 28/11-2026, outreach_rules.md §65): buttons ONLY via make_button.py table pattern
(coloured td bgcolor + white text inside it = visible in Gmail). Never hand-written <a style=background/color:#fff>.
Usage: build_follows_mail.py follows_<date>.json out.html "<intro sentence>"  -> then run_checked_send.sh out.html "<subject>" <ids>."""
import sys, json, html, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_button import jn_button, ret_button
d = json.load(open(sys.argv[1], encoding="utf-8"))
intro = sys.argv[3] if len(sys.argv) > 3 else f"Follows: {len(d)} forslag."
e = html.escape
out = [f'<p>{e(intro)} {jn_button("Ja til alle","green","JA",d[0]["id"]+"-"+d[-1]["id"])}</p>']
for x in d:
    dial = x["dialog"]
    out.append(f'<p><b>{e(x["id"])} {e(x["name"])}</b> - {e(x["title"])}<br><small>Hvorfor: {e(x["grp"])}. Grundlag: {e(x["relation"])}, {e(x["loc"])}. {e(dial)}</small><br>'
               + jn_button("Ja","green","JA",x["id"]) + jn_button("Nej","red","NEJ",x["id"]) + ret_button(x["id"], f'Følg {x["name"]}') + '</p>')
open(sys.argv[2], "w", encoding="utf-8").write("\n".join(out) + "\n")
