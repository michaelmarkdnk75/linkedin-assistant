#!/usr/bin/env python3
"""Usage: check_buttons.py email.html ID1 ID2 ... -> exit 0 only if every id has JA, NEJ and RET buttons.
Since 21/11-2026 (outreach_rules.md section 52): Ja/Nej = Apps Script links (script.google.com/macros/s/.../exec?afst=li-svar&v=ja|nej&id=..),
Ret = mailto michaelmarkdnk@gmail.com subject 'LI RET <id>' with NON-EMPTY body. Make hook links (hook.eu1.make.com) are REJECTED.
Also needs a 'Ja til alle' link (id range a-b)."""
import sys, re, urllib.parse
html = open(sys.argv[1], encoding="utf-8").read(); ids = sys.argv[2:]
APPS="https://script.google.com/macros/s/AKfycbxWXJs0qyBTyBhHeTfhgKhBSzJ_V5t723MQgc9juzZvAo8LzZlf6pcodY0CYehXHIxw/exec"
# VISIBLE-BUTTON GUARD (28/11-2026, outreach_rules.md section 65): white text on an <a> is only allowed inside a <td> with bgcolor.
_WH=r'color:\s*(#fff\b|#ffffff\b|white\b|#fefefe\b|rgb\(\s*255\s*,\s*255\s*,\s*255\s*\))'
_invis=0
for _m in re.finditer(r'<a\b[^>]*>', html, re.I):
    if re.search(_WH, _m.group(0), re.I):
        _pre=html[:_m.start()]; _td=_pre.rfind('<td'); _tdc=_pre.rfind('</td')
        if _td<0 or _tdc>_td or not re.search(r'bgcolor\s*=\s*["\']?#', _pre[_td:].split('>')[0], re.I): _invis+=1
if _invis: print(f"INVISIBLE BUTTONS: {_invis} <a> with white text outside a td bgcolor - use tools/make_button.py"); sys.exit(1)
links = [l.replace("&amp;","&") for l in re.findall(r'<a[^>]+href="((?:mailto:|https://)[^"]+)"', html, re.I)]
subs, err = set(), 0
for l in links:
    if "make.com" in l.lower(): print("MAKE LINK NOT ALLOWED:", l[:80]); err+=1; continue
    if l.lower().startswith("mailto:"):
        to,_,q = l[7:].partition("?"); qq=urllib.parse.parse_qs(q)
        if to.lower()!="michaelmarkdnk@gmail.com": print("BAD TO:",to); err+=1
        s=qq.get("subject",[""])[0].strip().upper()
        if s.startswith("LI RET") and not qq.get("body",[""])[0].strip(): print("EMPTY RET BODY",s); err+=1
        subs.add(s)
    elif l.startswith(APPS+"?"):
        q=urllib.parse.parse_qs(l.partition("?")[2])
        if q.get("afst",[""])[0]!="li-svar": print("BAD afst:",l[-60:]); err+=1
        if "@" in q.get("id",[""])[0] or "%40" in l.partition("?")[2].replace("fra=michaelmarkdnk%40gmail.com",""): print("EMAIL IN ID/TEKST"); err+=1
        v=q.get("v",[""])[0].upper(); i=q.get("id",[""])[0]
        if v not in("JA","NEJ"): print("BAD v:",v); err+=1
        subs.add(f"LI {v} {i}".upper())
    elif "linkedin.com" in l.lower(): pass
    else: print("BAD LINK:",l[:80]); err+=1
for i in ids:
    for a in ("JA","NEJ","RET"):
        if f"LI {a} {i}".upper() not in subs: print(f"MISSING {a} {i}"); err+=1
if not any(re.match(r"LI JA \S+-\S+$", s) for s in subs): print("MISSING Ja til alle"); err+=1
print(f"ids={len(ids)} links={len(links)} errors={err}"); sys.exit(1 if err else 0)
