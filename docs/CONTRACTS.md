# CivicFlow: Shared Contracts

This file lists **the interfaces both Claude lanes depend on**. Lane A (backend) implements them, and Lane B (frontend + data tooling) consumes them.

**Change rule:** nobody changes anything in this file alone. To change a contract:
1. Open a PR titled `contract: <what>` that edits this file **and** the code together.
2. The other lane's driver approves it.
3. Lane B regenerates its types (`npm run gen:api`) right after the merge.

Adding a **new optional field** or a **new endpoint** is a "minor" change: post it in team chat, then merge. Renaming or removing anything is a "major" change and needs the PR above.

Status: **DRAFT v1**. It is frozen at gate G0 (see TASKS.md).

---

## 1. General conventions

- Base path `/api/v1`. All JSON uses `snake_case`. Times are ISO-8601 with an offset (stored as UTC, shown as Asia/Kolkata).
- **IDs:** complaints `SR-2026-000123`, work orders `WO-2026-000040`, assets `STREETLIGHT-W12-00871`, wards `W12`, crews `W12-A`, users and agent runs are UUIDs.
- **Errors** (always this shape, with the correct HTTP status):
  ```json
  { "error": { "code": "INVALID_TRANSITION", "message": "Human-readable text", "details": {} } }
  ```
  Codes: `VALIDATION_ERROR` 422, `UNAUTHENTICATED` 401, `FORBIDDEN` 403, `NOT_FOUND` 404, `INVALID_TRANSITION` 409, `CONFLICT` 409, `CAPTCHA_FAILED` 400, `RATE_LIMITED` 429, `INTERNAL` 500.
- **Pagination:** query `page` (1-based), `page_size` (default 10, max 100). Response:
  ```json
  { "items": [], "total": 245, "page": 1, "page_size": 10 }
  ```
- **CSV export:** every list endpoint marked ⬇ also accepts `format=csv`. It uses the same filters and returns `text/csv` with a `Content-Disposition` header.
- **Media:** responses never contain file paths. They contain `url` values that are short-lived signed links (`/api/v1/media/{token}`, valid for 15 min).
- The source of truth for request/response shapes is FastAPI's OpenAPI (`/openapi.json`). Lane B generates `web/src/api/types.ts` from it. **Nobody hand-edits `types.ts`.**

## 2. Enums (`backend/app/core/enums.py`, mirrored by the generated types)

```
Role:            CITIZEN | WARD_OFFICER | FIELD_TEAM | CONTROL_ROOM | AGENCY
SRStatus:        SUBMITTED | ASSIGNED | IN_PROGRESS | ON_HOLD | WORK_COMPLETED | VERIFIED
                 | RESOLVED | CLOSED | MERGED | REJECTED | REOPENED
WOStatus:        ASSIGNED | IN_PROGRESS | ON_HOLD | COMPLETED | REWORK | VERIFIED
Priority:        P1 | P2 | P3 | P4
Category:        POTHOLE | ROAD_DAMAGE | STREETLIGHT | GARBAGE | WATER_LEAK | SEWAGE_OVERFLOW
                 | BLOCKED_DRAIN | WATERLOGGING | TREE_FALL | OPEN_MANHOLE | OTHER
Source:          CITIZEN_WEB | VEHICLE_FEED | HELPDESK | CSV_IMPORT
SLAState:        ON_TRACK | AT_RISK | BREACHED | PAUSED
HoldReason:      MATERIAL | AGENCY | WEATHER | ACCESS | CITIZEN
RejectReason:    NOT_CIVIC_ISSUE | OUTSIDE_JURISDICTION | INSUFFICIENT_INFO | DUPLICATE_SPAM
AssetOwner:      MUNICIPAL | BESCOM | BWSSB
Agency:          BESCOM | BWSSB
AttachmentKind:  CITIZEN | BEFORE | AFTER
ActorType:       HUMAN | AGENT | SYSTEM
ClosureType:     CITIZEN | AUTO
AgentName:       case_investigator | followup_escalation | road_hazard_sensing
                 | evidence_auditor | surge_commander
RunStatus:       RUNNING | SUCCEEDED | FALLBACK | FAILED
Verdict:         PASS | FLAG | FAIL
ClusterDecision: CREATE | CORROBORATE | REPAIR_FAILURE | DISMISS | REVIEW
ProposalStatus:  PENDING | APPROVED | REJECTED
Language:        en | kn
```

## 3. Authentication

- `POST /auth/register` `{name, mobile, password, language}` → `User` (role CITIZEN). The mobile number is a 10-digit Indian number; the password has at least 8 characters.
- `POST /auth/login` `{mobile, password}` → `User`, plus an httpOnly cookie `cf_session` (JWT, 8 h, SameSite=Lax). Repeated failures → `RATE_LIMITED`.
- `POST /auth/logout` → 204. `GET /auth/me` → `User` or 401.
- `User` = `{id, name, mobile_masked, role, designation?, ward_id?, department_id?, crew_id?, agency?, language}`
- **Scoping rules** (enforced in the backend, never only in the UI):
  - A CITIZEN sees only their own complaints, or one complaint by `sr_id` + `tracking_code`.
  - A WARD_OFFICER sees only their ward.
  - FIELD_TEAM sees only their crew's work orders and **never** a reporter's phone number. They cannot approve or verify work.
  - AGENCY sees only referrals to their agency.
  - CONTROL_ROOM sees everything.

## 4. Endpoints

`[role]` = who may call it. ⬇ = also supports CSV export.

### Public (no login)
| Method & path | Purpose |
|---|---|
| `GET /public/stats` | `{total, resolved, within_sla_pct, avg_resolution_days, unique_issues}` for the home page strip |
| `GET /public/ticker` | published advisories `[{id, text_en, text_kn, published_at}]` |
| `GET /public/wards` | ward directory `[{id, name, zone, officer_name, officer_designation, office_phone}]` |
| `GET /public/search?q=` | `{grievances:[{sr_id, category, status}], pages:[{title, path}], wards:[...]}`. Grievance search matches an exact SR id only |
| `POST /public/visit` / `GET /public/visits` | real visitor counter (one hit per browser session) |
| `GET /captcha` | `{captcha_id, question}` (math question, single use, expires in 10 min) |
| `GET /meta/categories` `GET /meta/departments` `GET /meta/wards` | dropdown data (wards include GeoJSON when `?geo=1`) |

### Complaints
| Method & path | Role | Purpose |
|---|---|---|
| `POST /complaints` (multipart) | anyone | fields `category, description, lat, lon, address?, landmark?, name?, mobile?, anonymous, captcha_id, captcha_answer, consent` + optional `photo`. Returns `AckSlip` |
| `GET /complaints/track?sr_id=&tracking_code=` | anyone | `TrackView` |
| `GET /complaints/mine` | CITIZEN | `Page[ComplaintRow]` |
| `POST /complaints/{id}/confirm` `{rating 1–5, comment?}` | owner/tracking code | RESOLVED → CLOSED (CITIZEN) |
| `POST /complaints/{id}/reopen` `{reason}` | owner/tracking code | RESOLVED → REOPENED |
| `GET /complaints` ⬇ filters `status, priority, category, sla_state, ward_id, escalated, source, q` | OFFICER, CONTROL | `Page[ComplaintRow]` |
| `GET /complaints/{id}` | OFFICER, CONTROL | `ComplaintDetail` |
| `GET /complaints/{id}/analysis` | OFFICER, CONTROL | latest Case Investigator run: `{run: AgentRunDetail, brief: TriageBrief, duplicate_suggestions:[...]}` |
| `POST /complaints/{id}/accept` `{run_id}` | OFFICER | SUBMITTED/REOPENED → ASSIGNED |
| `POST /complaints/{id}/override` `{run_id, changes:{category?, priority?, department_id?, owner_id?}, reason}` | OFFICER | applies the changes, then ASSIGNED; the override is stored on the run |
| `POST /complaints/{id}/merge` `{parent_sr_id, reason}` · `/unmerge` `{reason}` | OFFICER | |
| `POST /complaints/{id}/reject` `{reason_code, explanation}` | OFFICER | |
| `POST /complaints/{id}/hold` `{reason_code, note}` · `/resume` | OFFICER | the SLA pauses for approved reasons |
| `POST /complaints/import` (multipart CSV) | CONTROL | bulk import (helpdesk/legacy). Returns `{accepted, rejected:[{row, reason}]}` |

### Work orders & verification
| Method & path | Role | Purpose |
|---|---|---|
| `POST /complaints/{id}/work-orders` `{crew_id, asset_id?, root_cause, scope, est_cost_inr}` | OFFICER | the form that merges inspection and work order |
| `GET /work-orders/mine` | FIELD | `Page[WorkOrderRow]` |
| `GET /work-orders/{id}` | FIELD (own), OFFICER, CONTROL | `WorkOrderDetail` (includes `rework_reason?`, `audit?: AuditVerdict`) |
| `POST /work-orders/{id}/start` | FIELD | |
| `POST /work-orders/{id}/photos` (multipart `kind=BEFORE\|AFTER`, `photo`) | FIELD | EXIF and pHash are extracted on upload |
| `POST /work-orders/{id}/complete` | FIELD | needs an AFTER photo; emits `work_order.completed` |
| `GET /verification-queue` ⬇ | CONTROL | completed WOs with their `AuditVerdict` |
| `POST /work-orders/{id}/approve` · `/reject` `{reason}` | CONTROL | approve → VERIFIED (cascades the SR), reject → REWORK |

### Follow-up, agencies, escalation
| Method & path | Role | Purpose |
|---|---|---|
| `GET /proposals?status=PENDING` | OFFICER, CONTROL | reassignment proposals from Agent 2 |
| `POST /proposals/{id}/approve` · `/reject` `{reason}` | OFFICER | |
| `GET /referrals` ⬇ | OFFICER, CONTROL | |
| `GET /agency/referrals` | AGENCY | referrals to their agency, plus follow-up messages |
| `POST /agency/referrals/{id}/reply` `{agency_status: ACKNOWLEDGED\|IN_PROGRESS\|RESOLVED\|NOT_OURS, message}` | AGENCY | emits `referral.replied` |
| `GET /escalations` ⬇ | OFFICER, CONTROL | |
| `GET /inventory` · `GET /material-requests` ⬇ | OFFICER, CONTROL | |

### Control room
| Method & path | Role | Purpose |
|---|---|---|
| `GET /agent-runs` ⬇ filters `agent, status, model, overridden, sr_id` | CONTROL (OFFICER: own ward) | `Page[AgentRunRow]` |
| `GET /agent-runs/{id}` | same | `AgentRunDetail` (with steps) |
| `GET /incidents` · `GET /incidents/{id}` | CONTROL | |
| `POST /incidents/{id}/advisory/publish` `{text_en, text_kn}` | CONTROL | the advisory then appears in `/public/ticker` |
| `GET /hazards/clusters?bbox=&status=` · `GET /hazards/detections?bbox=&since=` | CONTROL | for the map (GeoJSON FeatureCollection) |
| `GET /hazards/review-queue` · `POST /hazards/review/{cluster_id}` `{decision: CREATE\|DISMISS, reason}` | CONTROL | |
| `GET /data-sources` | CONTROL | `[{id, name, last_ingest_at, accepted_24h, rejected_24h}]` |
| `GET /data-sources/{id}/rejections` ⬇ | CONTROL | dead-letter rows |
| `GET /kpi` | CONTROL | `{total_reports, unique_issues, sla_compliance_pct, reopen_rate_pct, closed_citizen, closed_auto, by_category:[...], by_ward:[...]}` |
| `GET /staff` ⬇ · `POST /staff` · `PATCH /staff/{id}` | CONTROL | create, edit and deactivate staff (WARD_OFFICER, FIELD_TEAM, CONTROL_ROOM, AGENCY) |
| `GET /notifications` ⬇ | CONTROL | the full outbox |
| `GET /notifications/mine` | any logged in | own in-app notifications |

### Ingestion (machine clients, `X-API-Key` header, optional `Idempotency-Key` header)
| Method & path | Purpose |
|---|---|
| `POST /ingest/detections` | JSON batch, at most 1,000 records, record format as in the original brief §9. Returns `{accepted, rejected, duplicates, rejections:[{source_record_id, reason}]}` |
| `POST /ingest/detections/csv` | CSV with the same columns |
| `POST /ingest/weather-alerts` | `{source_alert_id, area_name, lat, lon, radius_km, severity: YELLOW\|ORANGE\|RED, kind: HEAVY_RAIN, valid_from, valid_to}` (Open-Meteo alerts are fetched by the backend itself) |

Rejection reasons: `OUT_OF_BOUNDS`, `FUTURE_TIMESTAMP`, `TOO_OLD`, `BAD_CONFIDENCE`, `UNKNOWN_HAZARD_TYPE`, `FORBIDDEN_FIELD` (VIN, phone, name), `MALFORMED`.

## 5. Key response shapes

```
AckSlip        {sr_id, tracking_code, created_at, category, ward_name, department_name,
                expected_resolution_at, language}
ComplaintRow   {sr_id, category, priority, status, ward_id, address, created_at, owner_name,
                sla_state, sla_due_at, sla_remaining_s, escalation_level, reporter_count, source}
ComplaintDetail ComplaintRow + {description, location{lat,lon}, landmark, asset_id?,
                parent_sr_id?, incident_id?, attachments:[Attachment], work_orders:[WorkOrderRow],
                referrals:[...], timeline:[TimelineEntry], reporter_contact? (never sent to FIELD_TEAM)}
TrackView      {sr_id, category, status, priority, ward_name, created_at, expected_resolution_at,
                timeline:[TimelineEntry], photos:{before?:Attachment, after?:Attachment},
                can_confirm, can_reopen, delay_reason?}
TimelineEntry  {at, stage, remarks, actor_type}   # remarks in plain words, in the citizen's language
Attachment     {id, kind, url, taken_at?, uploaded_at}
WorkOrderRow   {wo_id, sr_id, crew_id, status, scope, assigned_at, completed_at?, audit_verdict?}
AgentRunRow    {id, agent, trigger, subject_id, status, model, decision_summary, confidence,
                latency_ms, overridden, started_at}
AgentRunDetail AgentRunRow + {input_summary, output, rationale:[str], fallback_reason?,
                overridden_by?, override_reason?, steps:[AgentStep]}
AgentStep      {seq, tool, args, result_summary, ok, ms}
```

## 6. Agent output schemas (`backend/app/agents/<agent>/schema.py`)

These shapes are what the **System Analysis** panel, the **Activity Log** and the **verification queue** display, so they are a frontend contract.

```
TriageBrief      {category, category_changed: bool, priority, department_id, ward_id,
                  suggested_officer_id, asset_id?, duplicate_of?, duplicate_confidence: 0–1,
                  repeat_failure: bool, repeat_failure_note?, planned_work_conflict?: str,
                  interagency_referral?: {agency, reason}, rationale: [str] (3–5), confidence: 0–1}
FollowupDecision {case_id, sla_state, diagnosed_causes: [{type: CREW_OVERLOAD|NO_STOCK|
                  AGENCY_PENDING|UNASSIGNED|OTHER, evidence}], actions_taken: [str],
                  proposals: [proposal_id], citizen_message_reason?: str, rationale: [str], confidence}
SensingReport    {clusters: [{cluster_id, decision: ClusterDecision, reason, linked_sr?, linked_wo?}],
                  summary, confidence}
AuditVerdict     {verdict: Verdict, score: 0–100, checks: [{name: TAKEN_AFTER_ASSIGNMENT|
                  GPS_WITHIN_RADIUS|NOT_REUSED|VISION_FIXED|VISION_SAME_SCENE, passed: bool|null,
                  detail}], rationale: [str], deficiency?: str}
SurgePlan        {incidents: [{name, sr_ids, severity, suggested_resources_text}],
                  advisory_draft: {en, kn}, situation_summary, confidence}
```

## 7. Events (`backend/app/core/events.py`)

Each event is `{name, payload, at}`. The payload always includes the subject id.

```
complaint.submitted {sr_id}          complaint.reopened {sr_id, reopen_count}
complaint.status_changed {sr_id, from, to}    complaint.merged {sr_id, parent_sr_id}
work_order.created {wo_id, sr_id}    work_order.completed {wo_id}
work_order.rework {wo_id, reason}    work_order.verified {wo_id}
referral.created {referral_id, sr_id}  referral.replied {referral_id}
escalation.created {sr_id, level}    detections.ingested {source_id, count}
weather_alert.received {alert_id}    incident.created {incident_id}
advisory.published {incident_id}     agent_run.finished {run_id, agent}
```

## 8. Agent runtime & LLM interface (Lane A internal, listed here so both lanes know it)

- **Tool:** `@tool(name, description, args_model: type[BaseModel], kind: "read"|"safe_act"|"propose")`. The function has the signature `fn(ctx: ToolContext, args) -> dict` and returns at most ~2 KB of JSON. `ToolContext` = `{db, run_id, agent, actor (AGENT identity), clock}`.
- **Agent:** `name, prompt_file, tools: list[str], output_model, triggers, max_steps=8, timeout_s=30, build_input(event)->dict, fallback(ctx, input)->output_model, apply(ctx, output)`.
- **LLM client:** `LLMClient.chat(system, messages, tools, images=None) -> {text?, tool_calls:[{id,name,args}], usage}`.
- **Providers**, configured in `.env`:
  ```
  LLM_PROVIDERS=gemini,groq,ollama            # tried in order; then rules
  LLM_GEMINI_BASE_URL=...  LLM_GEMINI_API_KEY=...  LLM_GEMINI_MODEL=...  LLM_GEMINI_VISION=true
  LLM_GROQ_BASE_URL=...    LLM_GROQ_API_KEY=...    LLM_GROQ_MODEL=...    LLM_GROQ_VISION=false
  LLM_OLLAMA_BASE_URL=http://host.docker.internal:11434/v1  LLM_OLLAMA_MODEL=...
  LLM_<NAME>_KIND=openai|anthropic          # default openai (OpenAI-compatible)
  LLM_<NAME>_TOOLS=native|json              # json = prompt-based tool calls for weak models
  AGENT_MODE=live|record|replay|rules
  ```
  On a 429, timeout or 5xx error the client moves to the next provider. Each `agent_runs.model` row stores `provider:model` or `rules`.
- **`make llm-check`** calls every configured provider and prints a table: reachable / tool calling / JSON output / vision / latency.

## 9. Seed fixed IDs (Lane B seed relies on them; Lane A tests may use them)

```
Wards:   W07 Kengeri Satellite Town · W12 Kengeri · W13 Rajarajeshwari Nagar
         W14 Hemmigepura · W15 Jnanabharathi · W16 Ullal
Assets:  STREETLIGHT-W12-00871 (BESCOM, Kengeri bus stand, 2 failures in last 60 days)
Crews:   W12-A, W12-B (idle, ~1.2 km from demo job), W13-A (overloaded, 9 open WOs, capacity 4), W13-B
WOs:     WO-2026-000040 (pothole repaired 12 days ago; simulator hits this spot)
Stock:   cold_mix_asphalt = 0, led_driver_40w = 0
Places:  "Govt. Higher Primary School, Kengeri" (fictionalised name), Kengeri bus stand
Data source: oem-sim (API key from .env INGEST_KEY_OEM_SIM)
```

## 10. Environment (`.env.example`, owned by Lane A)

`DATABASE_URL`, `JWT_SECRET`, `MEDIA_DIR`, `MEDIA_URL_SECRET`, `SEED_ADMIN_MOBILE`, `SEED_ADMIN_PASSWORD`, `SEED_STAFF_PASSWORD`, `INGEST_KEY_OEM_SIM`, `INGEST_KEY_WEATHER`, `WEATHER_LAT`, `WEATHER_LON`, `TIME_SCALE` (tests only, default 1), `AGENT_MODE`, the `LLM_*` block above, `API_BASE_URL` (simulator), `VITE_API_BASE` (web).
