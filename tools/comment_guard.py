#!/usr/bin/env python3
"""Comment guard (outreach_rules.md §59 language, §60 duplicates). Run with python3 -I.

Usage:
  comment_guard.py lang  <post_or_thread_text_file> <draft_text_file>
  comment_guard.py dupe  <post_activity_urn> <live_comments_json> <draft_text_file> [--parent <comment_urn>] [--self-id ID[,ID...]]
  --self-id: queue ids of the item being sent (and the id it replaces); skipped in the queue scan. Live own comments still hold.
Exit 0 = OK to draft/send. Exit 2 = HOLD (reason on stdout). Exit 3 = cannot decide (treat as HOLD, say so).
live_comments_json = saved response of scrape_linkedin_get_post_comments (rows[] with is_own, content, comment_ln_id)
Queue scan covers drafts/*.json, replies/drafts_*.json, quota/*.json for same urn with open/sent status.
"""
import sys, json, re, glob, os, difflib

BASE = "/mnt/project-files/linkedin-stats"
DA = set("og i er det at en til på for med som af den har de ikke jeg vi om der et men også kan vil fra så var dig mig jer hos når hvad hvordan eller fik fået være været blev bliver skal skulle bare meget mere nogle alle denne dette ud op over under efter før deres vores min mit dit din sig sin sit hvor hvem hvilken hvilke enig tak godt godt netop nogen ingen aldrig altid måske ja nej".split())
EN = set("the and of to in is that for with as on are this it be was were have has not you your we our from by at an or but can will would how what when who which their they them there more also about into over than then them just very all any some been being do does did if so such these those i my me us his her its".split())

def tokens(t):
    return re.findall(r"[a-zæøå]+", t.lower())

def lang(t):
    w = tokens(t)
    d = sum(x in DA for x in w); e = sum(x in EN for x in w)
    ch = sum(c in "æøåÆØÅ" for c in t)
    d += ch * 2
    if d + e < 4: return None
    if d >= 1.3 * e: return "da"
    if e >= 1.3 * d: return "en"
    return None

def norm(t):
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", "", t.lower())).strip()

def sim(a, b):
    return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()

def cmd_lang(post_f, draft_f):
    p, d = open(post_f, encoding="utf-8").read(), open(draft_f, encoding="utf-8").read()
    lp, ld = lang(p), lang(d)
    if lp is None or ld is None:
        print(f"UNDECIDED post={lp} draft={ld}: judge by hand, hold if unsure"); return 3
    if lp != ld:
        print(f"HOLD language: post/thread={lp} draft={ld}. Rewrite the draft in {lp}."); return 2
    print(f"OK language {lp}"); return 0

def cmd_dupe(urn, live_f, draft_f, parent=None, self_ids=()):
    draft = open(draft_f, encoding="utf-8").read()
    act = re.search(r"(\d{15,})", urn).group(1)
    hits = []
    try:
        live = json.load(open(live_f, encoding="utf-8"))
        rows = live.get("result", live).get("rows", [])
    except Exception as e:
        print(f"HOLD cannot read live comments ({e}); never send without a live read"); return 3
    for r in rows:
        if r.get("is_own"):
            if parent is None:
                hits.append(("live own comment", r.get("comment_ln_id"), r.get("content", "")[:90]))
    # queue scan: same post urn, still alive (proposed/approved/sent/posted)
    dead = ("rejected", "nej", "cancel", "ignor", "handled_by_michael", "deleted")
    for f in glob.glob(f"{BASE}/drafts/*.json") + glob.glob(f"{BASE}/replies/drafts_*.json") + glob.glob(f"{BASE}/quota/*.json"):
        try: data = json.load(open(f, encoding="utf-8"))
        except Exception: continue
        def walk(o):
            if isinstance(o, dict):
                s = json.dumps(o, ensure_ascii=False)
                if act in s and ("text" in o or "draft" in o) and str(o.get("id", "")) not in self_ids:
                    st = str(o.get("status", "")).lower()
                    txt = o.get("text") or o.get("draft") or ""
                    if txt and txt.strip() != draft.strip() and not any(x in st for x in dead):
                        hits.append(("queue " + os.path.basename(f), o.get("id"), f"{st[:40]} | {txt[:70]}"))
                    elif txt and txt.strip() == draft.strip() and ("sent" in st or "posted" in st):
                        hits.append(("same text already sent " + os.path.basename(f), o.get("id"), st[:40]))
                for v in o.values(): walk(v)
            elif isinstance(o, list):
                for v in o: walk(v)
        walk(data)
    near = [r for r in rows if sim(draft, r.get("content", "")) > 0.6]
    if hits or near:
        print("HOLD duplicate: Michael already has a comment/draft on this post:")
        for h in hits: print("  -", *h)
        for r in near: print("  - near-identical live comment by", r.get("commenter_full_name"))
        return 2
    print("OK no own comment/queue entry on this post"); return 0

if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "lang" and len(a) == 3: sys.exit(cmd_lang(a[1], a[2]))
    if a and a[0] == "dupe" and len(a) >= 4:
        parent = a[a.index("--parent") + 1] if "--parent" in a else None
        sid = tuple(x for x in a[a.index("--self-id") + 1].split(",") if x) if "--self-id" in a else ()
        sys.exit(cmd_dupe(a[1], a[2], a[3], parent, sid))
    print(__doc__); sys.exit(1)
