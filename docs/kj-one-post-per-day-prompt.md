# Prompt til KJ-projektet: maks ét LinkedIn-opslag pr. dag pr. profil

Indsæt som fast regel i KJ-projektets instruktioner og i alle KJ-opgaver, der planlægger eller udgiver opslag.

```
REGEL: MAKS ÉT OPSLAG PR. DAG PR. LINKEDIN-PROFIL (hård, ingen undtagelser uden mit udtrykkelige Ja).
Gælder Køge Jernmand-siden og Michaels personlige profil hver for sig: aldrig to opslag på samme profil samme kalenderdag (Europe/Copenhagen).
Baggrund 26/11-2026: to opslag gik ud samme dag, fordi to systemer planlagde uafhængigt (LinkedIn-connectorens kø og Postproxy), og Postproxy-jobs oprettes uger i forvejen. KJ-siden fik også to opslag kl. 06:45 samme dag.

Før du planlægger, flytter, bytter eller udgiver et opslag (create_linkedin_post, Postproxy post_publish/post_update, kalenderevent "KJ LinkedIn opslag (planlagt i Postproxy)"):
1. Hent LIVE, aldrig cache:
   a) Postproxy history_list med limit 400 (standardgrænsen skjuler jobs oprettet for uger siden), gem som fil.
   b) Kalenderevents "KJ LinkedIn opslag (planlagt i Postproxy)" for de næste 21 dage; Postproxy-id'er står i beskrivelsen ("Postproxy-id: X"). Det er KJ-sidens id'er.
   c) Personlig profil: get_linkedin_scheduled_posts og egne publicerede opslag (enrich_linkedin_person_posts public_identifier michaelmarkdk).
2. Kør python3 -I tools/post_day_guard.py (repo michaelmarkdnk75/linkedin-assistant):
   - KJ-siden: check <YYYY-MM-DD> --scope kj --postproxy <fil> --kj-ids <id'er fra kalenderen>
   - Personlig: check <YYYY-MM-DD> --connector <fil> --postproxy <fil> --own <fil> --kj-ids <id'er fra kalenderen> [--ignore <id på det opslag, du selv flytter>]
   Kun exit 0 må planlægge eller udgive. Exit 2 = HOLD: nævn konflikten (id, tid, tekststart) og foreslå en anden dag. Exit 3 = kunne ikke afgøres, tæl som HOLD.
3. Alle Postproxy LinkedIn-jobs, der ikke er på KJ-listen, tæller som personlige. Er du i tvivl om et id, tæl det som personligt.
4. Tjek igen lige før selve udgivelsen (frisk hentning, ikke filen fra planlægningen). Et godkendt Ja ophæver ikke reglen: hold og spørg, hvilket opslag der flyttes.
5. Hver uge og før hver ny batch af planlagte opslag: kør `audit --from <i dag> --days 21` for hver profil. Ved en dag med 2+ opslag: skriv det øverst i mailen/svaret og foreslå, hvilket der flyttes. Slet eller ret aldrig et planlagt opslag uden mit Ja.
6. Samme minut, to opslag, eller to profiler samme tidspunkt tæller som fejl: forskyd minutterne og undgå :00/:45, hvis en anden opgave bruger dem.
7. Skriv i hver plan-mail én linje: "opslagstjek: <profil> <dato> exit <kode>".
```
