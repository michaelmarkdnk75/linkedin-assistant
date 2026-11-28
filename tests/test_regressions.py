"""Regression suite (setup/regressions.md). Run: python3 -I tests/test_regressions.py  (exit 0 = all past fixes still locked)."""
from pathlib import Path
import os, sys, json, glob, re, subprocess, tempfile, shutil, unittest
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
T = os.path.join(ROOT, "tools")
def run(script, *args, cwd=None):
    return subprocess.run([sys.executable, "-I", os.path.join(T, script)] + [str(a) for a in args], capture_output=True, text=True, cwd=cwd)
def tmp(name, content):
    p = os.path.join(TD, name); open(p, "w", encoding="utf-8").write(content if isinstance(content, str) else json.dumps(content)); return p
TD = tempfile.mkdtemp()
sys.path.insert(0, T)
import make_button as mb

def good_html(ids=("X1", "X2")):
    s = f'<p>{mb.jn_button("Ja til alle","green","JA",ids[0]+"-"+ids[-1])}</p>'
    for i in ids: s += f"<p><b>{i}</b> Hvorfor: x. Grundlag: y. Dialog: z.</p>" + mb.triple(i, "Hej\nTekst")
    return s

class Buttons(unittest.TestCase):          # R1 21/11, R2 28/11
    def test_good(self): self.assertEqual(run("mail_preflight.py", tmp("g.html", good_html()), "X1", "X2").returncode, 0)
    def test_white_text_link_invisible(self):
        h = good_html() + '<p><a href="mailto:michaelmarkdnk@gmail.com?subject=LI%20JA%20X3" style="color:#fff;padding:8px">Ja</a></p>'
        r = run("check_buttons.py", tmp("w.html", h), "X1", "X2"); self.assertEqual(r.returncode, 1); self.assertIn("INVISIBLE", r.stdout)
    def test_background_link_blocked(self):
        h = good_html() + '<p><a href="https://example.com" style="background:#0a7d3b;color:#0a7d3b">x</a></p>'
        self.assertNotEqual(run("mail_preflight.py", tmp("b.html", h), "X1", "X2").returncode, 0)
    def test_make_link_blocked(self):
        h = good_html() + '<a href="https://hook.eu1.make.com/abc?x=1">Ja</a>'
        self.assertNotEqual(run("check_buttons.py", tmp("m.html", h), "X1", "X2").returncode, 0)
    def test_missing_nej(self):
        h = good_html(("X1",)).replace(mb.jn_button("Nej", "red", "NEJ", "X1"), "")
        self.assertNotEqual(run("check_buttons.py", tmp("n.html", h), "X1").returncode, 0)
    def test_empty_ret_body_blocked(self):
        h = good_html(("X1",)).replace("body=Hej%0ATekst", "body=")
        self.assertNotEqual(run("check_buttons.py", tmp("e.html", h), "X1").returncode, 0)
    def test_media_promise(self):
        h = good_html() + "<p>Billedet følger i en separat mail</p>"
        self.assertNotEqual(run("mail_preflight.py", tmp("p.html", h), "X1", "X2").returncode, 0)

class FollowsBuilder(unittest.TestCase):   # R2 follows 28/11
    def test_builder_output_passes(self):
        d = [dict(id=f"FW{i}", name=f"Test {i}", title="CIO", grp="Gruppe", relation="2. grad", loc="DK", dialog="Ingen dialog") for i in (1, 2)]
        out = os.path.join(TD, "f.html")
        r = run("build_follows_mail.py", tmp("f.json", d), out, "Intro"); self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(run("mail_preflight.py", out, "FW1", "FW2").returncode, 0)

class StaticScan(unittest.TestCase):       # R1/R2 + R4: no hand-written invisible buttons or Make anywhere in prompts/templates
    FILES = glob.glob(ROOT + "/setup/*.md") + glob.glob(ROOT + "/plans/message_templates.md") 
    def test_no_white_text_anchor_outside_td(self):
        for f in self.FILES:
            if f.endswith(("make_button.py", "check_buttons.py", "mail_preflight.py")): continue
            for m in re.finditer(r"<a\b[^>]*color:\s*(#fff|#ffffff|white)[^>]*>", Path(f).read_text(encoding="utf-8", errors="ignore"), re.I):
                self.fail(f"{f}: hand-written white-text <a> (use make_button.py): {m.group(0)[:80]}")
    def test_no_make_hooks_in_active_setup(self):
        for f in glob.glob(ROOT + "/setup/*.md"):
            t = Path(f).read_text(encoding="utf-8", errors="ignore")
            self.assertNotIn("hook.eu1.make.com/", t.replace("hook.eu1.make.com/ ", ""), f)

class CV(unittest.TestCase):               # R3 11/11 two CVs, R4 old versions, R5 27/11 generic folder
    FID = "1eca8BhjZHsxH1bq1OKvRWJRGbSfn7Cxq"; URL = "https://drive.google.com/uc?export=download&id=" + FID
    G = "Hej Anna\nTak for forbindelsen 🙌 Efter mange år som leder i IT er jeg klar til at tage næste skridt og få et bredere ansvar for, hvordan IT kan skabe endnu større værdi for forretningen.\nJeg har vedhæftet mit CV, så du har det ved hånden, hvis du sidder med en rolle, hvor det kunne passe. Jeg tager også gerne en kort snak.\nMange hilsner\nMichael"
    def args(self, name="CV_Michael_Mark_DA.pdf", url=None, size="295364", text=None, thread=None):
        meta = tmp("meta.json", {"file": {"id": self.FID, "title": "CV_Michael_Mark_DA.pdf", "mimeType": "application/pdf", "size": size}})
        return ["DA", name, url or self.URL, tmp("t.txt", text or self.G), meta, "--thread", thread or tmp("th.json", {"items": [], "pagination": {"has_more": False}})]
    def test_ok(self): self.assertEqual(run("cv_guard.py", *self.args()).returncode, 0)
    def test_wrong_file(self): self.assertEqual(run("cv_guard.py", *self.args(name="CV_Michael_Mark_CAVE_IT_DA.pdf")).returncode, 3)
    def test_generic_folder_url(self): self.assertNotEqual(run("cv_guard.py", *self.args(url="https://drive.google.com/uc?export=download&id=OTHER")).returncode, 0)
    def test_wrong_size(self): self.assertEqual(run("cv_guard.py", *self.args(size="111111")).returncode, 4)
    def test_second_cv_blocked(self):
        th = tmp("th2.json", {"items": [{"item": {"type": "outbox", "sent_at": "2026-11-11", "attachments": [{"file_name": "CV_Michael_Mark_DA.pdf"}]}}], "pagination": {"has_more": False}})
        self.assertEqual(run("cv_guard.py", *self.args(thread=th)).returncode, 6)
    def test_thread_required(self): self.assertEqual(run("cv_guard.py", *self.args()[:5]).returncode, 6)
    def test_incomplete_thread_blocked(self):
        self.assertEqual(run("cv_guard.py", *self.args(thread=tmp("th3.json", {"items": [], "pagination": {"has_more": True}}))).returncode, 6)
    def test_nontemplate_text_blocked(self): self.assertEqual(run("cv_guard.py", *self.args(text="Hej Anna\nHer er mit CV.")).returncode, 5)

class Registry(unittest.TestCase):         # R6 one proposal per person, R7 first answer wins
    def setUp(self):
        self.d = tempfile.mkdtemp(); os.makedirs(self.d + "/tools"); os.makedirs(self.d + "/plans")
        shutil.copy(T + "/proposal_registry.py", self.d + "/tools/"); shutil.copy(T + "/send_gate.py", self.d + "/tools/")
    def reg(self, *a): return subprocess.run([sys.executable, "-I", self.d + "/tools/proposal_registry.py", *a], capture_output=True, text=True)
    def gate(self, i): return subprocess.run([sys.executable, "-I", self.d + "/tools/send_gate.py", i], capture_output=True, text=True).returncode
    def test_duplicate_blocked_and_first_answer_wins(self):
        self.assertEqual(self.reg("add", "A1", "p", "P", "message", "t").returncode, 0)
        self.assertEqual(self.reg("add", "A2", "p", "P", "message", "t").returncode, 1)
    def test_gate(self):
        self.reg("add", "A1", "p", "P", "message", "t")
        self.assertEqual(self.gate("A1"), 1)              # open: no Ja
        self.assertEqual(self.gate("NOPE"), 1)            # unknown
        self.reg("set", "A1", "approved"); self.assertEqual(self.gate("A1"), 0)
        self.reg("set", "A1", "sent"); self.assertEqual(self.gate("A1"), 4)   # never twice
    def test_superseded_not_sendable(self):
        self.reg("add", "A1", "p", "P", "message", "t"); self.reg("set", "A1", "cancelled"); self.assertEqual(self.gate("A1"), 1)

class PostPerDay(unittest.TestCase):       # R8 26/11 two posts
    def test_conflict(self):
        con = tmp("c.json", {"result": {"rows": [{"scheduled_at": "2026-12-01T06:30:00Z", "post_urn": "u1", "text": "a"}]}})
        pp = tmp("p.json", {"jobs": [{"post_id": "J1", "scheduled_at": "2026-12-01T07:00:00Z", "platforms": [{"platform": "linkedin", "status": "scheduled"}], "content": "b"}]})
        own = tmp("o.json", {"result": {"posts": {"elements": []}}})
        self.assertEqual(run("post_day_guard.py", "check", "2026-12-01", "--connector", con, "--postproxy", pp, "--own", own).returncode, 2)
        self.assertEqual(run("post_day_guard.py", "check", "2026-12-02", "--connector", con, "--postproxy", pp, "--own", own).returncode, 0)
    def test_missing_input_is_hold(self): self.assertEqual(run("post_day_guard.py", "check", "2026-12-01", "--postproxy", tmp("x.json", {"jobs": []})).returncode, 3)

class Comments(unittest.TestCase):         # R9 24/11 language
    def test_language_mismatch(self):
        post = tmp("post.txt", "Vi har haft en rigtig god uge med mange nye kolleger og de er alle til for at hjælpe os med det her."); en = tmp("en.txt", "Thanks for sharing this, the team will have a great week and we are with you on this one.")
        self.assertEqual(run("comment_guard.py", "lang", post, en).returncode, 2)
        da = tmp("da.txt", "Tak fordi du deler det her, det er jeg helt enig i, og det har vi også set hos os.")
        self.assertEqual(run("comment_guard.py", "lang", post, da).returncode, 0)

class Calendar(unittest.TestCase):         # R14 28/11 calendar delete
    def ev(self, s, d): return tmp("ev.json", {"summary": s, "description": d, "id": "e1"})
    def test_claude_hold_approved(self): self.assertEqual(run("calendar_guard.py", self.ev("HOLD: x (foreslået)", "Oprettet af Claude (HOLD-rutine)"), "--approved-by-michael").returncode, 0)
    def test_no_approval(self): self.assertEqual(run("calendar_guard.py", self.ev("HOLD: x", "Oprettet af Claude (HOLD-rutine)")).returncode, 2)
    def test_not_hold(self): self.assertEqual(run("calendar_guard.py", self.ev("Interview Telenor", "Oprettet af Claude"), "--approved-by-michael").returncode, 2)

class SendQueue(unittest.TestCase):       # sender work list is read-only and lists only approved items
    def test_lists_only_approved(self):
        d = tempfile.mkdtemp(); os.makedirs(d + "/tools"); os.makedirs(d + "/plans"); shutil.copy(T + "/send_queue.py", d + "/tools/")
        json.dump({"items": [{"id": "A", "person_key": "a", "channel": "follow", "status": "approved"}, {"id": "B", "person_key": "b", "channel": "cv", "status": "open"}]}, open(d + "/plans/pending_proposals.json", "w"))
        r = subprocess.run([sys.executable, "-I", d + "/tools/send_queue.py"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0); self.assertIn("A a", r.stdout); self.assertNotIn("B b", r.stdout)

class SelfMail(unittest.TestCase):         # R12 26/11
    def test_ok(self): self.assertEqual(run("selfmail_check.py", tmp("s1.json", {"labelIds": ["SENT", "INBOX", "UNREAD"]})).returncode, 0)
    def test_sent_only(self): self.assertEqual(run("selfmail_check.py", tmp("s2.json", {"labelIds": ["SENT"]})).returncode, 1)

class RegisteredBeforeMail(unittest.TestCase):   # R28 28/11 follows FW220-FW245 mailed unregistered
    def test_missing_id_blocks(self):
        reg = tmp("reg.json", {"items": [{"id": "A1", "person_key": "p", "person": "P", "channel": "follow", "status": "open"}]})
        env = dict(os.environ, LI_REGISTRY=reg)
        ok = subprocess.run([sys.executable, "-I", T + "/registry_check.py", "A1"], capture_output=True, text=True, env=env)
        bad = subprocess.run([sys.executable, "-I", T + "/registry_check.py", "A1", "A2"], capture_output=True, text=True, env=env)
        self.assertEqual(ok.returncode, 0); self.assertEqual(bad.returncode, 3); self.assertIn("A2", bad.stdout)
    def test_wrapper_calls_registry_check(self):
        self.assertIn("registry_check.py", Path(T + "/run_checked_send.sh").read_text())

class OutreachV2(unittest.TestCase):        # R29-R32 28/11 outreach v2 (rules 67, setup/outreach_v2.md)
    RULES = Path(ROOT + "/plans/outreach_rules.md").read_text(encoding="utf-8")
    S58 = "05ba1ad866f48b3d74b83c0a80968df1093201afbf84e64729de26ae892c9e7f"
    def test_s58_locked(self):
        import hashlib
        m = re.search(r"^## 58\..*?(?=^## 59\.)", self.RULES, re.S | re.M)
        self.assertTrue(m); self.assertEqual(hashlib.sha256(m.group(0).encode()).hexdigest(), self.S58, "section 58 changed: needs Michael's approval of the text, then update S58 hash")
    def test_rules_67_markers(self):
        m = re.search(r"^## 67\..*", self.RULES, re.S | re.M); self.assertTrue(m)
        for k in ("67a", "67b", "67c", "67d", "67e", "67f", "25 om ugen", "7-10 hverdage", "Ugemåling", "setup/outreach_v2.md"): self.assertIn(k, m.group(0))
    def test_v2_list_has_trig_ids_and_status(self):
        t = Path(ROOT + "/setup/outreach_v2.md").read_text(encoding="utf-8")
        self.assertRegex(t, r"STATUS: (FORESLÅET|GODKENDT|UDFØRT)")
        ids = set(re.findall(r"trig_[A-Za-z0-9]{24}", t)); self.assertGreaterEqual(len(ids), 8)
    def test_draft_message_not_in_templates_before_approval(self):
        tpl = Path(ROOT + "/plans/message_templates.md").read_text(encoding="utf-8")
        self.assertNotIn("15 min til sparring om NIS2", tpl, "sparring text is a draft until Michael approves (then move to templates and delete this test)")
    def test_invites_not_a_fill_target(self):   # static check: quota_tracker must not run in tests (it appends to the real quota_log.csv)
        self.assertIn("if b!='send_connection_requests'", Path(T + "/quota_tracker.py").read_text())

if __name__ == "__main__":
    try: unittest.main(verbosity=1)
    finally: shutil.rmtree(TD, ignore_errors=True)
