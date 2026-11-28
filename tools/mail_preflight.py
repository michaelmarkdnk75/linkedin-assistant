#!/usr/bin/env python3
"""Pre-send gate for EVERY mail to Michael that carries Ja/Nej/Ret items (regressions R1-R3, R9, R10; setup/regressions.md).
Usage: mail_preflight.py email.html ID1 ID2 ...   Exit 0 = may be sent. Anything else = DO NOT SEND.
Runs check_buttons.py (visible buttons, no Make, Ret body, Apps Script links, Ja til alle) plus:
- no media promise (26/11): the mail must not promise an image/brochure/attachment that the sender will not attach;
- no background-colour <a> buttons (21/11 + 28/11: Gmail strips background; only make_button.py table pattern is allowed);
- sent through htmlBody only: the file must be a real HTML body (contains <p or <table)."""
import sys, os, re, subprocess
here = os.path.dirname(os.path.abspath(__file__))
if len(sys.argv) < 3: print(__doc__); sys.exit(2)
h = open(sys.argv[1], encoding="utf-8").read()
err = 0
r = subprocess.run([sys.executable, "-I", os.path.join(here, "check_buttons.py")] + sys.argv[1:])
if r.returncode: err += 1
for m in re.finditer(r"<a\b[^>]*>", h, re.I):
    if re.search(r"background(-color)?\s*:", m.group(0), re.I):
        print("BACKGROUND ON <a> (Gmail strips it, button invisible): use tools/make_button.py"); err += 1; break
PROMISE = r"(billede\w*|image|foto|photo|brochure\w*|karrusel\w*|carousel|vedh[æa]ft\w*|attached)\s+(f[øo]lger|will follow|comes? separately|kommer)"
for m in re.finditer(PROMISE, re.sub(r"<[^>]+>", " ", h), re.I):
    print("MEDIA PROMISE (26/11): mail promises", m.group(0), "- attach it or remove the promise"); err += 1; break
if not re.search(r"<(p|table|div)\b", h, re.I): print("NOT HTML BODY"); err += 1
print("PREFLIGHT", "FAILED" if err else "OK"); sys.exit(1 if err else 0)
