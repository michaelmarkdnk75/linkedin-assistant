#!/usr/bin/env python3
"""§37b: flag C-level/headhunter/HR viewers on EVERY delta run, independent of the watermark.
Usage: viewer_flag.py <profile_views_page.json> [more pages...]  (raw result of get_linkedin_account_my_profile_views, whole response or elements list)
Prints rows whose headline/display_name matches the title list; anonymous rows are matched on their descriptor and company/industry text (e.g. 'Telecommunications')."""
import sys, json, re
PAT=re.compile(r"\b(ceo|cto|cio|coo|cfo|chief|direkt\w*|adm\.?|administrerende|managing director|vp|vice president|svp|evp|head of|rekrutter\w*|recruit\w*|hr\b|talent|executive search|headhunt\w*|partner)\b",re.I)
def rows(o):
    if isinstance(o,list): return o
    if "elements" in o: return o["elements"]
    return rows(o.get("result",o.get("profile_views",{}))) if isinstance(o,dict) else []
for f in sys.argv[1:]:
    for r in rows(json.load(open(f))):
        t=" ".join(str(r.get(k,"")) for k in ("display_name","headline"))
        if PAT.search(t): print(r.get("position"),r.get("viewed_at_text"),r.get("network_distance","anon" if r.get("is_anonymous") else "?"),t[:140])
