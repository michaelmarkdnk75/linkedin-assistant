#!/usr/bin/env python3
"""One personal LinkedIn post per day (outreach_rules.md section 62). Run with python3 -I.

Usage:
  post_day_guard.py check <YYYY-MM-DD> [--scope personal|kj] --connector F --postproxy F --own F [--kj-ids ID,ID|@file] [--ignore ID,...]
  post_day_guard.py audit --from <YYYY-MM-DD> --days N [--scope personal|kj] --connector F --postproxy F --own F [--kj-ids ...]

Inputs are saved LIVE tool responses (never cached lists):
  --connector  get_linkedin_scheduled_posts response   (result.rows[].scheduled_at, post_urn)
  --postproxy  Postproxy history_list response, limit >= 400 (jobs[], platforms[].platform == linkedin)
  --own        enrich_linkedin_person_posts / scrape response (result.posts.elements[].created_at, post_urn)
  --kj-ids     Postproxy post ids that belong to the Koege Jernmand PAGE (calendar events
               "KJ LinkedIn opslag (planlagt i Postproxy)", description "Postproxy-id: X"). Every other
               Postproxy LinkedIn job counts as a PERSONAL post, because history_list does not show the placement.
  --scope kj   counts only the KJ-page Postproxy jobs (ids in --kj-ids); connector/own not needed.
  --ignore     ids/urns of the item being checked (so a swap does not collide with itself).

A day is a Europe/Copenhagen calendar day. Counted: connector queue, Postproxy jobs that are scheduled or published
(not deleted/failed/draft), and own published posts. Exit 0 = day is free (check) / no day has 2+ posts (audit).
Exit 2 = HOLD, conflicts printed. Exit 3 = input missing or unreadable: treat as HOLD and say so.
"""
import sys, json, re, argparse
from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo

CPH = ZoneInfo("Europe/Copenhagen")
BAD = {"deleted", "failed", "error", "cancelled", "canceled"}


def day_of(ts):
    d = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    if d.tzinfo is None:
        d = d.replace(tzinfo=ZoneInfo("UTC"))
    return d.astimezone(CPH).date()


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def connector_posts(doc):
    rows = (doc.get("result") or doc).get("rows")
    if rows is None:
        raise ValueError("connector file has no rows[]")
    return [(day_of(r["scheduled_at"]), r["post_urn"], "connector queue", r.get("scheduled_at"), (r.get("text") or "")[:50]) for r in rows]


def postproxy_posts(doc, kj_ids, scope="personal"):
    jobs = doc.get("jobs")
    if jobs is None:
        raise ValueError("postproxy file has no jobs[]")
    out = []
    for j in jobs:
        if j.get("draft") or not j.get("scheduled_at"):
            continue
        pls = [p for p in j.get("platforms", []) if p.get("platform") == "linkedin"]
        if not pls or any(p.get("status") in BAD for p in pls):
            continue
        if (j["post_id"] in kj_ids) != (scope == "kj"):  # personal: everything except KJ ids; kj: only KJ ids
            continue
        m = re.search(r"urn:li:\w+:\d+", pls[0].get("url") or "")  # published: same id as the live post, so it dedupes
        out.append((day_of(j["scheduled_at"]), m.group(0) if m else j["post_id"], "Postproxy " + pls[0].get("status", "?"), j["scheduled_at"], (j.get("content") or "")[:50]))
    return out


def own_posts(doc):
    els = ((doc.get("result") or {}).get("posts") or {}).get("elements")
    if els is None:
        raise ValueError("own-posts file has no result.posts.elements[]")
    return [(day_of(e["created_at"]), e.get("post_urn") or e.get("activity_urn"), "published (live)", e["created_at"], (e.get("text") or "")[:50]) for e in els if not e.get("is_reshare")]


def collect(a):
    kj = set()
    if a.kj_ids:
        raw = open(a.kj_ids[1:]).read() if a.kj_ids.startswith("@") else a.kj_ids
        kj = {x.strip() for x in raw.replace("\n", ",").split(",") if x.strip()}
    ign = {x.strip() for x in (a.ignore or "").split(",") if x.strip()}
    if a.scope == "kj":  # Koege Jernmand PAGE: Postproxy only (connector queue and own feed are personal)
        items = postproxy_posts(load(a.postproxy), kj, "kj")
    else:
        items = connector_posts(load(a.connector)) + postproxy_posts(load(a.postproxy), kj) + own_posts(load(a.own))
    seen, res = set(), []
    for it in items:  # a published post can appear in two sources: dedupe on URN/id
        if it[1] in ign or it[1] in seen:
            continue
        seen.add(it[1]); res.append(it)
    return res


def main(argv):
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=["check", "audit"])
    p.add_argument("day", nargs="?")
    p.add_argument("--from", dest="start")
    p.add_argument("--days", type=int, default=14)
    p.add_argument("--scope", choices=["personal", "kj"], default="personal")
    p.add_argument("--connector")
    p.add_argument("--postproxy", required=True)
    p.add_argument("--own")
    p.add_argument("--kj-ids", dest="kj_ids")
    p.add_argument("--ignore")
    a = p.parse_args(argv)
    if a.scope == "personal" and not (a.connector and a.own):
        print("CANNOT DECIDE: personal scope needs --connector and --own"); return 3
    try:
        items = collect(a)
    except Exception as e:
        print("CANNOT DECIDE: %s" % e); return 3
    by = {}
    for it in items:
        by.setdefault(it[0], []).append(it)
    if a.mode == "check":
        if not a.day:
            print("CANNOT DECIDE: no date"); return 3
        d = date.fromisoformat(a.day)
        hit = by.get(d, [])
        if hit:
            print("HOLD %s: %d personal post(s) already there" % (d, len(hit)))
            for h in hit: print("  - %s | %s | %s | %s" % (h[2], h[1], h[3], h[4].replace("\n", " ")))
            return 2
        print("OK %s: no personal post" % d); return 0
    d0 = date.fromisoformat(a.start) if a.start else datetime.now(CPH).date()
    bad = 0
    for i in range(a.days):
        d = d0 + timedelta(days=i)
        hit = by.get(d, [])
        if len(hit) >= 2:
            bad += 1
            print("CONFLICT %s: %d posts" % (d, len(hit)))
            for h in hit: print("  - %s | %s | %s | %s" % (h[2], h[1], h[3], h[4].replace("\n", " ")))
    print("audit %s +%d days: %d conflicting day(s)" % (d0, a.days, bad))
    return 2 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
