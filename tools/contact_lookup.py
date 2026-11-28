#!/usr/bin/env python3 -I
# usage: contact_lookup.py "<name>" ["<company>" ["<email>"]]  -> prints prior non-LinkedIn contact lines, exit 0 always
import json,sys,unicodedata
def n(s): return unicodedata.normalize("NFKD",s.lower()).encode("ascii","ignore").decode()
q=[n(a) for a in sys.argv[1:] if a.strip()]
d=json.load(open("/mnt/project-files/linkedin-stats/contacts/contact_history.json"))
hit=0
for c in d["contacts"]:
    blob=n(" ".join([c["name"],c["company"],c["email"]]))
    for t in q:
        toks=[x for x in t.replace(","," ").split() if len(x)>2]
        if t in blob or (toks and sum(x in blob for x in toks)>=min(2,len(toks)) ) :
            print(f"TIDLIGERE KONTAKT: {c['name']} ({c['company']}), {c['first_contact']} til {c['last_contact']}, {c['channel']}: {c['topic_facts']}");hit=1;break
for o in d["one_way_or_excluded"]:
    if any(t in n(o) for t in q if len(t)>3): print("KUN UDGÅENDE/UDELADT:",o);hit=1
if not hit: print("INGEN TIDLIGERE KONTAKT I DATABASEN (database er første pas, ikke udtømmende)")
