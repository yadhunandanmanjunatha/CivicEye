# CivicFlow: Task Board (2 people, 2 Claude Code sessions)

Read `CLAUDE.md` first: it has the file-ownership table and the rules. Interfaces are in `docs/CONTRACTS.md`.

## Who does what

| Person | Lane | Owns |
|---|---|---|
| **Person A** (lead, merges PRs; laptop 1) | **A: Backend & Agents** | `backend/` (not seed), compose, Makefile, `.env.example` |
| **Person B** (laptop 2) | **B: Frontend & Data** | `web/`, `simulator/`, `e2e/`, `backend/app/seed/**` (loader + data), `fixtures/photos/`, `docs/DEMO_SCRIPT.md` |

**Why there are no conflicts:** the two Claude sessions never edit the same folder, and they talk only through `docs/CONTRACTS.md`. If one lane needs something in the other's files, it writes it under **Requests** in `PROGRESS.md`, and the person tells the other person (call or chat).

---

## One-time setup (before any coding)

1. **Person A:** create a separate repo **inside `lakshya/`** (right now git is rooted at the home folder, so don't commit from there) and push it to GitHub:
   ```bash
   cd ~/lakshya && git init -b main && git add . && git commit -m "docs: plan, contracts, tasks"
   ```
   ```bash
   gh repo create civicflow --private --source=. --push
   ```
   Then add Person B: GitHub → the repo → Settings → Collaborators → Add people.
2. **Person B** installs Git, Node 20+, Python 3.11, Docker Desktop and Claude Code, accepts the GitHub invite, then clones:
   ```bash
   git clone https://github.com/<owner>/civicflow.git && cd civicflow
   ```
3. **Both:** create a free Gemini key (aistudio.google.com → Get API key) and a free Groq key (console.groq.com). Each person uses **their own** keys, which doubles the free quota. Keys go only in your local `.env`, never in git.
4. **Both, on a call (~30 min):** read `docs/CONTRACTS.md` together and fix anything that's wrong *now*. After gate G0, changes need a `contract:` PR.

## Daily Git routine (both drivers)

Start a task:
```bash
git switch main && git pull --ff-only && git switch -c a/A07-complaints-api
```
Stay current while working (at least every 2 hours, and right after the other lane merges):
```bash
git fetch origin && git rebase origin/main
```
Finish:
```bash
git push -u origin HEAD
```
```bash
gh pr create --fill
```
- Branch names: `a/<task-id>-<slug>` for Lane A, `b/<task-id>-<slug>` for Lane B, `fix/<slug>` for small fixes.
- **PR rule:**
  - the other person skims it (5 min) and confirms it doesn't touch their files;
  - `make test` passes;
  - **Person A merges** (squash).
- If a rebase conflicts in a file you don't own, **stop**: it means someone broke the ownership rule. Talk before resolving.

## Gates (everyone stops and checks together)

Target hours assume a 24 h build with a freeze at hour 20.

| Gate | ~Hour | Must be true | Checked by |
|---|---|---|---|
| **G0 Contracts frozen** | 2 | A01–A03 and B01 merged; on **both laptops** `make db` + `make api` + `make web` show API `/docs` and the web frame; `npm run gen:api` works | both |
| **G1 Platform** | 8 | Register/login works; Lodge → Ack slip → Track works against the real API; officer queue shows seeded aged cases; field user sees their jobs | Person A tests B's screens |
| **G2 Vertical slice** ★ | 12 | Citizen lodges → Agent 1 brief in System Analysis → officer Accept → work order → field uploads after-photo → Agent 4 verdict → control room Approve → citizen sees before/after → Confirm → CLOSED. Works with `AGENT_MODE=rules` **and** with an LLM. Playwright test green | both, together |
| **G3 All agents** | 17 | Agents 2, 3 and 5 trigger and appear in the Activity Log; agency portal reply works; hazard map; incidents + advisory publish → ticker | both |
| **G4 Demo story** | 19.5 | Whole demo story (BUILD_PLAN §11) runs twice in a row without fixes; replay cache recorded | both |
| **Freeze** | 20 | Bug fixes only. Anything unfinished is **removed from the UI** | Person A decides |

★ **G2 is the most important gate.** Until G2 passes, nobody starts G3 work.

---

## Lane A: Backend & Agents (Person A)

Each task lists: priority, dependencies, branch; files; what to do; done when; tests.

**A01 · Repo bootstrap**
- P0 · deps: setup · branch `a/A01-bootstrap`
- **Files:** `backend/{pyproject.toml,Dockerfile,app/main.py,app/config.py,app/db.py}`, `docker-compose.yml`, `Makefile`, `.env.example`, `.gitignore`
- **Do:**
  - FastAPI app with `/api/v1/health`.
  - **Dev mode, Docker only for the database:** compose service `db` (PostGIS, arm64-compatible image; test it on the Mac) on port 5432 with a named volume. The backend runs locally in a Python 3.11 venv.
  - Also add compose services `api`, `web` and `simulator` under `profiles: [full]` for the final "everything in Docker" run (B creates the web/simulator Dockerfiles in B01).
  - Makefile targets: `setup` (venv + pip install + `npm install`), `db`, `api`, `web`, `seed`, `demo`, `test`, `llm-check`, `reset`. They must work on macOS and Windows/WSL.
  - Error handler producing the CONTRACTS §1 error shape.
  - A `README.md` "Getting started" section written for someone who has never used Docker.
- **Done when:** on a clean clone, `make setup && make db && make api` → health returns 200.
- **Tests:** health check, error-shape test.

**A02 · Models + initial migration**
- P0 · deps: A01 · branch `a/A02-models`
- **Files:** `backend/app/core/enums.py`, `backend/app/modules/*/models.py`, `backend/alembic/`
- **Do:**
  - All tables from the original brief §7, plus `users.role` including `AGENCY`, `users.designation`, `users.password_hash`, `users.mobile` (unique), `material_requests`, `reassignment_proposals`, `review_queue`, `weather_alerts`, `visits`, `captchas`.
  - **One** initial migration with PostGIS + `pg_trgm` extensions and the append-only triggers on `audit_log` and `status_events`.
- **Done when:** `alembic upgrade head` runs on an empty DB.
- **Tests:** migration up; the triggers block UPDATE/DELETE.

**A03 · Contract stubs** (unblocks Lane B)
- P0 · deps: A02 · branch `a/A03-contract-stubs`
- **Files:** `backend/app/modules/*/{schemas,router,service}.py`, `backend/app/agents/*/schema.py`, `backend/app/core/events.py`
- **Do:**
  - Every endpoint in CONTRACTS §4 exists with **real Pydantic request/response models**. Each returns a correctly shaped fixture, marked by an `X-Stub: true` response header, until it's implemented. Stubs are a development aid only and get replaced task by task.
  - Agent output schemas (CONTRACTS §6). Event names (§7).
  - Service function signatures for the agents (`transition`, `create_work_order`, `create_referral`, `escalate`, `create_proposal`, `create_incident`, `create_system_complaint`, `send_to_rework`), with docstrings.
- **Done when:** `/openapi.json` covers CONTRACTS §4 and Person B has approved it. **This is G0.**
- **Tests:** an OpenAPI snapshot test.

**A04 · Clock + SLA engine**
- P0 · deps: A02 · branch `a/A04-sla`
- **Do:** `clock.now()` (TIME_SCALE for tests only); SLA states; pause/resume with an approved-reason list; `sla_remaining_s`; verification window; auto-close job.
- **Tests:** freezegun: ON_TRACK / AT_RISK at 75% / BREACHED / PAUSED; escalation doesn't change the due time; paused time is excluded.

**A05 · Workflow + audit + event bus**
- P0 · deps: A02 · branch `a/A05-workflow`
- **Do:**
  - The transition table exactly as BUILD_PLAN §5; `transition()` is the only place that writes `status`; it writes `status_events`, `audit_log` and the event.
  - Allow-list for AGENT actors (no REJECTED/CLOSED).
  - Async in-process pub/sub + `events` table.
  - SR cascades: the first WO started → IN_PROGRESS; all WOs completed → WORK_COMPLETED; REWORK → back to IN_PROGRESS; all verified → VERIFIED → RESOLVED.
- **Tests:** parametrised over every allowed and forbidden move; an agent can't close a case; a second reopen → L2.

**A06 · Auth, scoping, staff, captcha**
- P0 · deps: A03 · branch `a/A06-auth`
- **Do:** CONTRACTS §3: register/login/logout/me, bcrypt, JWT cookie, login rate limit; role and ward-scope dependencies; `/staff` CRUD; `/captcha`.
- **Tests:**
  - a W12 officer gets 404 on a W07 complaint;
  - a field user never gets `reporter_contact`;
  - a field user can't approve;
  - wrong password ×5 → RATE_LIMITED.

**A07 · Complaints API**
- P0 · deps: A05, A06 · branch `a/A07-complaints`
- **Do:**
  - Lodge (multipart, captcha, consent; EXIF GPS/time + sha256 + pHash on upload; anonymous complaints get a tracking code).
  - Ack slip, track, mine, confirm/reopen, list with filters + pagination + CSV export, detail, hold/resume, reject, merge/unmerge.
  - `POST /complaints/import` CSV.
  - Signed media URLs.
  - Public stats, ticker, wards, search, visits.
- **Done when:** these endpoints no longer return `X-Stub`.
- **Tests:** lodge → track; CSV export columns; import rejects bad rows with reasons.

**A08 · Work orders + verification + proposals**
- P0 · deps: A07 · branch `a/A08-workorders`
- **Do:** create WO (inspection fields), mine, start, photos, complete (needs an AFTER photo), verification queue, approve/reject, accept/override of the brief (override stored on the agent run), proposals approve/reject.
- **Tests:** a full SR + WO lifecycle through the API with no agents.

**A09 · Agent runtime**
- P0 · deps: A03 · can run in parallel with A04–A08 · branch `a/A09-runtime`
- **Files:** `backend/app/agents/runtime/*`
- **Do:** BUILD_PLAN §7: registry, `Agent` base, run loop with `submit_result`, validation retry, step limit, timeout, fallback through the same tool registry, `agent_runs`/`agent_steps` logging, a dispatcher queue with 3 workers (idempotent per event), and the **FakeLLM** test fixture.
- **Tests:** happy path; invalid output → retry → fallback; tool raises; timeout; step limit; the same event twice → one run.

**A10 · LLM adapter (any provider)**
- P0 · deps: A09 · branch `a/A10-llm`
- **Files:** `backend/app/adapters/llm.py`, `backend/app/agents/runtime/cache.py`, `backend/scripts/llm_check.py`
- **Do:** CONTRACTS §8:
  - OpenAI-compatible client + Anthropic client;
  - provider chain with failover on 429/timeout/5xx;
  - `native` vs `json` tool mode;
  - images for vision providers;
  - record/replay cache with normalised keys (a miss → next provider → rules);
  - `make llm-check`.
- **Tests:** failover order with mocked HTTP; JSON-mode parsing (including a malformed reply → retry); a replay hit/miss.

**A11 · `notify_citizen` + notifications**
- P0 · deps: A09 · branch `a/A11-notify`
- **Do:** EN/KN templates per event (Lane B supplies the Kannada, task B20); one message per reporter, merged reporters included; in-app + outbox; optional LLM polish with a template fallback; the `/notifications` endpoints; timeline remarks in plain words.
- **Tests:** a merged reporter gets the update; the language is honoured.

**A12 · Agent 1: Case Investigator**
- P0 · deps: A07, A10, B12 seed · branch `a/A12-investigator`
- **Do:**
  - The 11 read tools from BUILD_PLAN §6.
  - `merge_duplicate` (refuses below 0.9), `raise_p1_alert`, a referral draft.
  - Rules fallback (routing table, priority rules, duplicate score: 0.4 distance + 0.3 time + 0.3 max(text trigram, pHash)).
  - The prompt.
- **Done when:** the streetlight and school-pothole scenarios produce the briefs described in BUILD_PLAN §6.
- **Tests:** duplicate score cases; EN/KN emergency keywords → P1; FakeLLM streetlight scenario; fallback when the LLM errors.

**A13 · Agent 4: Evidence Auditor**
- P0 · deps: A08, A10 · branch `a/A13-auditor`
- **Do:** the 5 checks; missing EXIF → FLAG; `send_to_rework` only when a hard check fails; crew audit history.
- **Tests:** old photo, 2 km GPS, reused hash, missing EXIF, vision skipped. **→ G2**

**A14 · Referrals, agency portal API, escalations, stock**
- P1 · deps: A08 · branch `a/A14-referrals`
- **Do:** referral on Accept when the brief proposes one; `/agency/*`; escalation levels with authority staff; inventory and material requests.
- **Tests:** an agency user sees only their referrals; reply → event.

**A15 · Agent 2: Follow-up & Escalation**
- P1 · deps: A14, A04 · branch `a/A15-followup`
- **Do:** a scheduler tick (15 s) with a deterministic scanner (newly AT_RISK, newly BREACHED, follow-up due); one agent run per case-state; the 4 causes; reassignment proposal; material request; agency follow-up every 24 h, and after 2 unanswered → L2; the breach rule escalates one level and the agent writes the reason; honest citizen message.
- **Tests:** the seeded W13 job proposes W12-B; the seeded BESCOM referral → follow-up → L2 with a reason; no re-run on an unchanged state.

**A16 · Ingestion + weather**
- P1 · deps: A03 · can run in parallel · branch `a/A16-ingest`
- **Do:** `/ingest/detections` (+ CSV) with API key, idempotency, validation, dead-letter; `/ingest/weather-alerts`; Open-Meteo poller (every 30 min, heavy-rain → `weather_alerts`); `/data-sources`.
- **Tests:** every rejection reason, using Lane B's `seed/data/ingest_cases.json` (B19).

**A17 · Agent 3: Road Hazard Sensing**
- P1 · deps: A16 · branch `a/A17-sensing`
- **Do:** the DBSCAN helper (UTM 43N, eps 12 m); stats; filters; the create/corroborate/repair-failure/dismiss/review tools with guards; `/hazards/*` endpoints; one run per clustering pass (every 2 min).
- **Tests:** speed-breaker cluster dismissed; a single vehicle is ignored; corroboration within 25 m; repair failure at WO-040.

**A18 · Agent 5: Surge Commander + incidents**
- P2 · deps: A17 · branch `a/A18-surge`
- **Do:** the trigger rule (≥15 in 2 km / 60 min, or a weather alert + ≥8); reuse the clustering helper (eps 600 m); incidents, links, EN/KN advisory draft, situation summary; publish → ticker.
- **Tests:** the rain fixture → 2 incidents; fallback.

**A19 · KPIs**
- P2 · deps: A08 · branch `a/A19-kpi`
- **Do:** `/kpi` with AUTO closures counted separately.

**A20 · Record the replay cache + `docs/AGENTS.md`**
- P1 · deps: G3 · branch `a/A20-record`
- **Do:** run the demo story with `AGENT_MODE=record`; commit the cache; write AGENTS.md with a Mermaid diagram.

## Lane B: Frontend & Data tooling (Person B)

**B01 · Web scaffold + tokens**
- P0 · deps: setup · in parallel with A01 · branch `b/B01-scaffold`
- **Files:** `web/**`, `simulator/Dockerfile` (empty skeleton)
- **Do:** Vite React TS, React Router with route files per area (`routes/{public,citizen,officer,field,control,agency}.tsx`), `styles/tokens.css` + `base.css`, react-i18next (en/kn), `npm run gen:api` (openapi-typescript), Dockerfile. Tell Person A if anything differs from A01.

**B02 · Page frame**
- P0 · deps: B01 · branch `b/B02-frame`
- **Do:**
  - Top strip: skip link, A-/A/A+ (working), high contrast (working), EN/ಕನ್ನಡ.
  - Header: an original SVG crest (no emblem), the bilingual corporation name, a working search box (`/public/search`).
  - Navy nav; a "What's New" ticker from `/public/ticker` (hidden when empty); the prototype banner.
  - Footer with real content pages (Website Policy, Privacy, Terms, Accessibility Statement, Help, Sitemap). The Feedback link opens Lodge Grievance with category OTHER, so it really reaches the officers. Last Updated date and the real visitor count.
- **Done when:** every link goes to a real page.

**B03 · Shared components**
- P0 · deps: B01 · branch `b/B03-components`
- **Do:** `DataTable` (S.No., zebra rows, navy header, server pagination "Showing 1–10 of 245", CSV export via `format=csv`, filters), `Fieldset`, `Captcha`, `Breadcrumbs`, `SlaBadge` ("2d 4h left" / "Breached by 6h"), `StatusPill`, `EscalationBadge`, `Timeline`, `MapPicker` (Leaflet, auto-GPS + drag), `PhotoPair`, `StarRating`, `FileUpload`.
- **Tests:** component tests for DataTable pagination and SlaBadge formatting.

**B04 · API client + auth context**
- P0 · deps: A03 (G0) · branch `b/B04-api`
- **Do:** a typed fetch wrapper (cookies, the CONTRACTS error shape → a form/notice message), `AuthProvider` using `/auth/me`, role-guarded routes, a 401 → login redirect.

**B05 · Register / Login / My Profile**
- P0 · deps: B04 · branch `b/B05-auth`
- **Do:** mobile + password, validation messages, language preference; staff users land on their console.

**B06 · Home + Lodge Grievance + Acknowledgement**
- P0 · deps: B03, B04 · branch `b/B06-lodge`
- **Do:**
  - Home: quick-service tiles, the stats strip from `/public/stats`, notices from the ticker.
  - Lodge: fieldsets (Grievance / Location / Contact), photo upload (the original file is sent so EXIF is kept), map pin, anonymous option, captcha, declaration, Submit/Reset.
  - Ack slip with a **Print** button (print CSS).

**B07 · Track + My Grievances + My Notifications**
- P0 · deps: B06 · branch `b/B07-track`
- **Do:** track by SR + tracking code, the status table, a vertical timeline, before/after photos, the delay reason, Confirm + star rating, Reopen with a reason; a My Grievances table; My Notifications.

**B08 · Officer console**
- P0 · deps: B03, B04 · branch `b/B08-officer`
- **Do:**
  - Left menu, top bar (name, designation, ward, Logout).
  - Queue `DataTable` with SLA countdown, escalation badge and filters.
  - Complaint detail with the **System Analysis** panel (brief fields, rationale bullets, expandable "Steps taken" from `AgentStep[]`, Accept / Override form with a required reason), duplicate suggestions with Merge.
  - The create-work-order form, hold/resume, reject.
  - Pending reassignment proposals with Approve/Reject.
  - Referrals list.

**B09 · Field team app (mobile-first)**
- P0 · deps: B03, B04 · branch `b/B09-field`
- **Do:** My Jobs, job detail (no reporter phone), Start, before/after upload with large touch targets, Mark Completed, the rework reason banner + the auto-check result.

**B10 · Control room**
- P0 for the verification queue + Activity Log, P1 for the rest · deps: B08 · branch `b/B10-control`
- **Do:**
  - **Verification queue** (AuditVerdict, check list, before/after, Approve/Reject).
  - **Agent Activity Log** (table + drill-down to steps and rationale, auto-refresh every 5 s).
  - P1 queue, SLA breaches, escalations.
  - Staff Management (create/edit/deactivate).
  - CSV import page (complaints) showing per-row results.
  - Notifications outbox.

**B11 · Partner Agency Portal**
- P1 · deps: B04, A14 · branch `b/B11-agency`
- **Do:** referrals table, detail with the follow-up history, reply form.

**B12 · Seed loader** (Agent 1 needs this data)
- P0 · deps: A02 · branch `b/B12-seed`
- **Files:** `backend/app/seed/*.py`, `backend/app/seed/data/README.md`, `backend/tests/seed/`
- **Do:**
  - **First (hour 2–3):** write `seed/data/README.md` with the exact YAML/GeoJSON format and one example per file, so B18/B19 can fill them.
  - Then the loader: idempotent, fixed IDs from CONTRACTS §9, **timestamps relative to now** (aged cases), ~240 historical SRs generated from rules in YAML, staff accounts with passwords from `.env`, and photo EXIF rewritten from `fixtures/photos/` (piexif).
  - `make seed` calls it (Person A adds the Makefile target if it's missing).
- **Tests:** seeding twice gives identical IDs; the W13 job is at about 74% SLA right after the seed.

**B13 · Simulator**
- P1 · deps: A16 contract (it can be written against the contract before A16 lands) · branch `b/B13-simulator`
- **Do:** `simulator/sim.py` with `--once`, `--stream --rate 5`, `--scenario rain|duplicates`; 15 potholes, 5 speed breakers, noise, the corroboration pothole, hits at WO-040; it posts only to public APIs with `X-API-Key`; scenarios in YAML.
- **Tests:** a dry-run prints the expected counts.

**B14 · Road Hazard Map + Data Sources**
- P1 · deps: B03, A17 · branch `b/B14-hazard`
- **Do:** Leaflet layers (raw dots toggle, clusters sized by vehicles, dismissed speed breakers in grey, system-created complaints), the review queue with decide buttons, the Data Sources table + rejections drill-down.

**B15 · Incidents + KPIs**
- P2 · deps: A18, A19 · branch `b/B15-incidents`
- **Do:** incident list/detail with linked complaints, the advisory editor (EN/KN) + Publish, the situation summary; KPI panel with Chart.js.

**B16 · Kannada + accessibility pass**
- P2 · deps: B20 · branch `b/B16-a11y`
- **Do:** all citizen-page strings through i18n; keyboard navigation, alt text, aria labels, contrast check.

**B17 · Playwright end-to-end test**
- P0 · deps: G2 features · branch `b/B17-e2e`
- **Do:** citizen registers + lodges → officer accepts → WO → field after-photo → audit PASS → control approves → citizen confirms → CLOSED (`AGENT_MODE=rules`).

## Lane B data tasks (Claude B drafts them, Person B checks them)

**B18 · Seed geography**
- P0 · right after B12's README · branch `b/B18-geo`
- **Do:** ward polygons for the 6 wards, Mysuru Road / ORR / main roads as lines, 5 speed breakers + 1 rail crossing, ~25 sensitive places, as GeoJSON in `backend/app/seed/data/geo/`. Claude drafts them from known coordinates around Kengeri / RR Nagar; Person B checks them visually at geojson.io and fixes anything clearly misplaced. Use fictionalised names for schools and hospitals.

**B19 · Seed content**
- P0 · deps: B12 README · branch `b/B19-seed-data`
- **Do:** the YAML files: departments, SLA grid, crews, inventory, staff list (names + designations, no passwords), assets (incl. `STREETLIGHT-W12-00871` and its history), planned works, the aged demo cases, the rules for the historical complaint mix, and `ingest_cases.json` (15–20 good and bad detection records with expected results, used by A16's tests).

**B20 · Kannada**
- P2 · branch `b/B20-kn`
- **Do:** `web/src/i18n/kn.json`, the Kannada versions of the notification templates (Lane A puts the English list in PROGRESS.md Requests), and the Kannada emergency keywords. **A Kannada speaker must read it once.**

## Tasks for the people themselves (no Claude needed)

- **P-1 (Person B, hour 0–4)** · real photos near SJBIT, each taken with phone location ON:
  - pothole before;
  - pothole after (repaired, or a filled patch nearby);
  - an "after" photo taken about 2 km away;
  - a streetlight;
  - 2 extra potholes;
  - 2 waterlogging/drain photos.

  Put them in `fixtures/photos/` with a `photos.yaml` listing what each one is. Send them from the phone to the laptop as **files** (AirDrop, USB or Google Drive "original quality"), not through WhatsApp, which strips location.
- **P-2 (both)** · run `make llm-check` once A10 merges and note which providers work.
- **P-3 (both, at each gate)** · test the **other** person's lane as a real user. File every bug as a GitHub issue (steps, expected, actual, screenshot, label `lane-a`/`lane-b`).
- **P-4 (Person B, after G4)** · `docs/DEMO_SCRIPT.md` (who clicks what, which account, what to say), pitch slides, backup video.

---

## Critical path (what blocks what)

```
A01 → A02 → A03 (G0) ─┬→ A06 → A07 → A08 → A13 ─┐
                      ├→ A09 → A10 → A12 ────────┼→ G2 → A14 → A15 / A16 → A17 → A18 → G3
B01 → B04 ────────────┴→ B05..B10 ───────────────┘
B12 → B18/B19 seed data ──→ A12 (Agent 1 needs real assets/places)
```

- **A03 slipping blocks Lane B.** Person A does A03 before anything else after A02.
- **Seed data slipping makes Agent 1 look dumb.** Lane B's order is: B01 → B12 README → B18/B19 → B04 → screens.
- Lane A is the heavier lane. If Lane B runs ahead after G2, it may take **A19 KPI**, but only by agreeing it at a gate, because that's backend code.

## Ready-to-paste Claude Code prompts

### Session opener: Lane A (Person A, laptop 1)
```
You are the Lane A (Backend & Agents) developer on CivicFlow.
Read CLAUDE.md, docs/BUILD_PLAN.md §0, and docs/CONTRACTS.md. Read other BUILD_PLAN
sections only when the task points to them.
You may edit only Lane A files listed in CLAUDE.md. Do not touch web/, simulator/,
e2e/, or backend/app/seed/. Do not change docs/CONTRACTS.md; if a contract seems
wrong, stop and tell me.
Your task: <paste the task block, e.g. "A07 · Complaints API" from TASKS.md>.
Before coding, list the files you will touch and the tests you will write, then wait
for my OK. Write tests with the code, run `make test`, and report: what changed, how
to verify, what's left. Don't commit or push.
```

### Session opener: Lane B (Person B, laptop 2)
```
You are the Lane B (Frontend & Data) developer on CivicFlow.
Read CLAUDE.md, docs/BUILD_PLAN.md §0, and docs/CONTRACTS.md. For UI style, follow
CLAUDE.md "Non-negotiable product rules" (plain public-portal look, nothing for show).
You may edit only Lane B files listed in CLAUDE.md: web/, simulator/, e2e/,
backend/app/seed/**, backend/tests/seed/, fixtures/photos/, docs/DEMO_SCRIPT.md.
Do not touch any other backend file,
docker-compose.yml or the Makefile; write requests for those in PROGRESS.md.
Never hand-edit web/src/api/types.ts; run `npm run gen:api`.
Your task: <paste the task block, e.g. "B08 · Officer console" from TASKS.md>.
If an endpoint still returns the X-Stub header, build against its contract shape and
note it in PROGRESS.md. Every element you render must work; if it can't, don't render it.
Before coding, list the files you will touch, then wait for my OK. Run tests and
`npm run build`, then report: what changed, how to verify (click path), what's left.
Don't commit or push.
```

### Bug-fix prompt (either lane)
```
Bug from GitHub issue #<n>: <paste steps / expected / actual>.
Find the cause inside your lane's files only. If the cause is in the other lane,
say so and stop. Fix it, add a test that would have caught it, run tests, report.
```

## Usage tips for the two Claude accounts
- One session at a time per account. Run `/clear` between tasks and paste the opener again; it's cheaper than one endless session.
- Use Sonnet by default. Switch to Opus only for A09/A10 (runtime) or a cross-cutting bug.
- When an account hits its limit, that person reviews the other lane's PR, tests the other lane's screens, or takes photos / checks seed data until the limit resets.
- Plan big tasks (A07, A09, A12, B08, B10) for the start of a fresh usage window.
