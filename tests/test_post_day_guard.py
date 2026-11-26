import json, os, subprocess, sys, tempfile, unittest

G = os.path.join(os.path.dirname(__file__), "..", "tools", "post_day_guard.py")


def run(tmp, conn, pp, own, *extra):
    fs = {}
    for k, v in (("c", conn), ("p", pp), ("o", own)):
        fs[k] = os.path.join(tmp, k + ".json")
        with open(fs[k], "w") as f:
            json.dump(v, f)
    return subprocess.run([sys.executable, "-I", G] + list(extra) + ["--connector", fs["c"], "--postproxy", fs["p"], "--own", fs["o"]],
                          capture_output=True, text=True)


def job(pid, sched, status="published", plat="linkedin", draft=False):
    return {"post_id": pid, "scheduled_at": sched, "draft": draft, "content": "x", "platforms": [{"platform": plat, "status": status}]}


def pub(pid, sched, urn):
    j = job(pid, sched); j["platforms"][0]["url"] = "https://www.linkedin.com/feed/update/" + urn + "/"
    return j


class T(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.mkdtemp()
        self.empty_c = {"result": {"rows": []}}
        self.empty_o = {"result": {"posts": {"elements": []}}}

    def test_26_11_two_posts_are_caught(self):
        # 26/11: connector share 06:30Z already published, Postproxy E7tjpVb personal 07:00Z, KJ page job 1RtG2Yb excluded
        own = {"result": {"posts": {"elements": [{"created_at": "2026-11-26T06:30:03+00:00", "post_urn": "urn:li:share:1", "text": "stafet"}]}}}
        pp = {"jobs": [job("E7tjpVb", "2026-11-26T07:00:00.000Z"), job("1RtG2Yb", "2026-11-26T06:45:00.000Z")]}
        r = run(self.t, self.empty_c, pp, own, "audit", "--from", "2026-11-26", "--days", "1", "--kj-ids", "1RtG2Yb")
        self.assertEqual(r.returncode, 2, r.stdout); self.assertIn("E7tjpVb", r.stdout); self.assertNotIn("1RtG2Yb", r.stdout)

    def test_published_postproxy_job_and_live_post_count_once(self):
        own = {"result": {"posts": {"elements": [{"created_at": "2026-11-26T07:00:25+00:00", "post_urn": "urn:li:ugcPost:7", "text": "m"}]}}}
        pp = {"jobs": [pub("E7tjpVb", "2026-11-26T07:00:00.000Z", "urn:li:ugcPost:7")]}
        r = run(self.t, self.empty_c, pp, own, "audit", "--from", "2026-11-26", "--days", "1")
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_check_blocks_when_postproxy_holds_the_day(self):
        pp = {"jobs": [job("E7tjpVb", "2026-11-26T07:00:00.000Z", "pending")]}
        r = run(self.t, self.empty_c, pp, self.empty_o, "check", "2026-11-26")
        self.assertEqual(r.returncode, 2)

    def test_kj_scope_counts_only_kj_ids(self):
        pp = {"jobs": [job("1RtG2Yb", "2026-11-26T06:45:00.000Z"), job("92t2jRq", "2026-11-26T06:45:00.000Z"), job("E7tjpVb", "2026-11-26T07:00:00.000Z")]}
        fs = os.path.join(self.t, "pp.json")
        with open(fs, "w") as f:
            json.dump(pp, f)
        r = subprocess.run([sys.executable, "-I", G, "check", "2026-11-26", "--scope", "kj", "--postproxy", fs, "--kj-ids", "1RtG2Yb,92t2jRq"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)
        self.assertNotIn("E7tjpVb", r.stdout)

    def test_check_free_day(self):
        r = run(self.t, self.empty_c, {"jobs": []}, self.empty_o, "check", "2026-11-27")
        self.assertEqual(r.returncode, 0)

    def test_kj_page_and_deleted_and_other_platforms_ignored(self):
        pp = {"jobs": [job("kj", "2026-11-27T10:45:00.000Z", "pending"), job("d", "2026-11-27T07:00:00.000Z", "deleted"),
                       job("f", "2026-11-27T07:00:00.000Z", "pending", "facebook"), job("dr", "2026-11-27T07:00:00.000Z", "pending", draft=True)]}
        r = run(self.t, self.empty_c, pp, self.empty_o, "check", "2026-11-27", "--kj-ids", "kj")
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_copenhagen_day_boundary(self):
        c = {"result": {"rows": [{"post_urn": "u1", "scheduled_at": "2026-11-26T23:30:00+00:00", "text": "t"}]}}  # 27/11 00:30 DK
        self.assertEqual(run(self.t, c, {"jobs": []}, self.empty_o, "check", "2026-11-27").returncode, 2)
        self.assertEqual(run(self.t, c, {"jobs": []}, self.empty_o, "check", "2026-11-26").returncode, 0)

    def test_ignore_self_and_dedupe(self):
        c = {"result": {"rows": [{"post_urn": "u1", "scheduled_at": "2026-12-01T06:30:00+00:00", "text": "t"}]}}
        r = run(self.t, c, {"jobs": []}, self.empty_o, "check", "2026-12-01", "--ignore", "u1")
        self.assertEqual(r.returncode, 0)

    def test_bad_input_is_exit_3(self):
        r = run(self.t, {"nope": 1}, {"jobs": []}, self.empty_o, "check", "2026-11-26")
        self.assertEqual(r.returncode, 3)


if __name__ == "__main__":
    unittest.main()
