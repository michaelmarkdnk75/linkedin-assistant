#!/usr/bin/env python3
"""Read Sheet clicks. Usage: klik_pickup.py <values.json> [id ...]
values.json = output of Google_Sheets get_values on 1OOFMQMzpv3DXjSWyDnxznZ-f1xzto-dfT6a9Y2482uw range klik!A:I (JSON with "values").
Prints ja/nej per id for afst=li-svar; id ranges 'A-B' expand over the ordered id args. FIRST ANSWER RULE: earliest click per id wins
(section FIRST-ANSWER) unless --latest. Ret is NOT a click: it arrives as Gmail 'LI RET <id>'. Gmail inbox AND label LI-godkendelser stay a source too."""
import sys, json, re
a=[x for x in sys.argv[1:] if x!="--latest"]; latest="--latest" in sys.argv
rows=json.load(open(a[0]))["values"][1:]; known=a[1:]
res={}
for r in rows:
    r=r+[""]*9
    t,afst,fra,v,_,i=r[0],r[1],r[2],r[3].lower(),r[4],r[5]
    if v=="ignorer" and re.match(r"^(KS|KR)\d",i): v="nej"  # Ignorer on KS/KR = Nej (stops reminders)
    if afst!="li-svar" or v not in("ja","nej"): continue
    ids=[i]
    if known and i not in known:
        for j,ch in enumerate(i):
            if ch=="-" and i[:j] in known and i[j+1:] in known:
                ids=known[known.index(i[:j]):known.index(i[j+1:])+1]; break
    for k in ids:
        if latest or k not in res: res[k]=(v,t)
for k,(v,t) in res.items(): print(k,v,t)
