#!/usr/bin/env python3
"""CV send guard (Michael 2026-11-05 CV RULE, outreach_rules.md §18). FAIL CLOSED.
Usage: cv_guard.py <lang DA|EN> <file_name> <file_url> <text_file> <drive_meta_json> [--ret]
- file must be CV_Michael_Mark_DA.pdf / CV_Michael_Mark_EN.pdf with the fixed Drive id.
- drive_meta_json = output of Google Drive get_file_metadata for that id (proves the file exists:
  matching id, name, mimeType application/pdf, not trashed). Missing/unreadable -> blocked.
- text must be template G (DA) / G-EN (EN) with only the name filled in, unless --ret
  (Michael's own edited text); old long CV texts and banned wording are always blocked.
Exit 0 = send allowed. Anything else = send NOTHING, status 'held: cv guard'."""
import sys, json, re
CV = {"DA": ("CV_Michael_Mark_DA.pdf", "1eca8BhjZHsxH1bq1OKvRWJRGbSfn7Cxq"),
      "EN": ("CV_Michael_Mark_EN.pdf", "1brrqaBXuKN5xgX4-uF13bth0SSVAqTj-")}
G = {"DA": "Tak for forbindelsen 🙌 Efter mange år som leder i IT er jeg klar til at tage næste skridt og få et bredere ansvar for, hvordan IT kan skabe endnu større værdi for forretningen.\nJeg har vedhæftet mit CV, så du har det ved hånden, hvis du sidder med en rolle, hvor det kunne passe. Jeg tager også gerne en kort snak.\nMange hilsner\nMichael",
     "EN": "Thanks for connecting 🙌 After many years as an IT leader, I'm ready to take the next step and a broader responsibility for how IT creates even more value for the business. I've attached my CV in case you have a role where it could fit. Happy to have a short chat too.\nBest regards\nMichael"}
GREET = {"DA": r"^Hej [^\n]+\n", "EN": r"^Hi [^\n]+\n"}
BANNED = ["generisk", "generic", "_v3", "_v7", "_v8", "organisationsændring", "organisational change", "organizational change", "fritstillet"]
def die(code, msg): print("BLOCKED:", msg); sys.exit(code)
a = sys.argv[1:]
ret = "--ret" in a; a = [x for x in a if x != "--ret"]
if len(a) != 5: die(2, __doc__)
lang, name, url, tf, mf = a
lang = lang.upper()
if lang not in CV: die(2, f"lang {lang}")
want, fid = CV[lang]
if name != want: die(3, f"file_name {name!r} != {want!r}")
if any(b in name.lower() or b in url.lower() for b in BANNED[:5]): die(3, "old CV version in name/url")
if not re.fullmatch(r"https://drive\.google\.com/uc\?export=download&id=" + re.escape(fid), url): die(3, f"file_url must be https://drive.google.com/uc?export=download&id={fid}")
try:
    m = json.load(open(mf)); m = m.get("file", m) if isinstance(m, dict) else {}
except Exception as e: die(4, f"Drive metadata missing/unreadable ({e}): CV file not verified")
if m.get("id") != fid: die(4, f"Drive id {m.get('id')!r} != {fid}")
if m.get("title", m.get("name")) != want: die(4, f"Drive name {m.get('title', m.get('name'))!r} != {want!r}")
if "pdf" not in str(m.get("mimeType", "")).lower(): die(4, "not a PDF")
if m.get("trashed") or m.get("labels", {}).get("trashed"): die(4, "CV file is in trash")
try: t = open(tf, encoding="utf-8").read().strip().replace("\r\n", "\n")
except Exception as e: die(5, f"text unreadable ({e})")
low = t.lower()
for b in BANNED[5:]:
    if b in low: die(5, f"banned wording: {b}")
if not ret:
    if not re.match(GREET[lang], t): die(5, "text must start with greeting line (template G/G-EN)")
    body = re.sub(GREET[lang], "", t, count=1).strip()
    norm = lambda s: re.sub(r"\s+", " ", s).strip()
    if norm(body) != norm(G[lang]): die(5, "text is not template G/G-EN verbatim")
print(f"OK {lang} {want} ({'RET text' if ret else 'template G' + ('-EN' if lang == 'EN' else '')})")
