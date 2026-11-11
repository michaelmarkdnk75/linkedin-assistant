# CV rule (fail closed)

Only `CV_Michael_Mark_DA.pdf` (Drive 1eca8BhjZHsxH1bq1OKvRWJRGbSfn7Cxq) and `CV_Michael_Mark_EN.pdf` (Drive 1brrqaBXuKN5xgX4-uF13bth0SSVAqTj-) may be sent, with template G / G-EN text.

Every task runs `tools/cv_guard.py` before a CV send and sends only on exit 0.

- 2026-11-11: "LinkedIn dagligt – CV-flow + opfølgning" (trig_01ViUfnPkaXEPnekQQtrP2Yy) and "LinkedIn process approvals 17:00" (trig_01E8od8Qc7AvdapGsiw4FVen) had a hard-coded v7 CV + old long text. Both prompts were fixed. The CV-flow prompt now lives in `setup/cvflow_prompt.md` (the live copy is `/mnt/project-files/linkedin-stats/setup/cvflow_prompt.md`). The old prompt is kept in `setup/cvflow_prompt_before_2026-11-11.md`.
