# CropChoice: Intelligent Crop Portfolio Ranking & Diversification Optimizer (Dashboard Website)

**Type:** Final-year project | **Domain:** Agriculture & Food | **Level:** Intermediate
**Product style:** A real **multi-page dashboard website** with **login screens, role-based access, and data entry inside the dashboard**. Clean **light theme**, agriculture-themed colour system, advanced and clean UI components.
**Stack:** React 18 + TypeScript (Vite) + Tailwind CSS + shadcn/ui, FastAPI, Python (NumPy, SciPy, pandas, PuLP), **MongoDB Atlas (PyMongo)**, configuration through **`.env`**. **No Streamlit.**

> **Instructions for Claude Code:** Read this whole document first. Build the project phase by phase (Section 15). After each phase, run the tests and confirm the acceptance criteria before moving on. Do not skip phases. Ask me only if something is truly blocking; otherwise use the defaults stated here.
> **Hard rules:**
> 1. Do NOT use Streamlit, Dash or any Python-rendered UI. The website is a **React + Vite + TypeScript** single-page app talking to a FastAPI REST API.
> 2. The database is **MongoDB (Atlas)** via **PyMongo**. **All secrets and settings (Mongo URI, DB name, JWT secret, CORS origins, API URL) live in `.env` files only.** Never hardcode a connection string, never write a real credential into any committed file (including `.env.example`, README, tests, docs or code comments). The real URI is pasted by the developer into the local, git-ignored `.env`.
> 3. Python owns all calculations (normalization, soil suitability, AHP, TOPSIS, sensitivity, optimization, simulation, reports). The website only collects inputs, calls the API and displays results.
> 4. The theme is **light only** (Section 12). Follow the design tokens and component list exactly; the UI must look neat, clean, bright and professional.
> 5. The dashboard must open **already populated with seed data**, and every data table must support **data entry (create, edit, delete)** from the UI.
> 6. No deep learning, no computer vision.

---

## 1. Product Vision

Farmers, agronomists and planners must choose **which crops to grow** and **how much land to give each**. The decision is multi-criteria: water demand, soil suitability, expected return and price variability all matter, and different stakeholders weigh them differently. Today this is done informally or in disconnected spreadsheets.

CropChoice is a website where a user logs in, enters (or selects) a **farm profile** (land, soil, water, budget, season), maintains the **crop and price data** in the dashboard, sets **criteria weights** (direct sliders or AHP pairwise comparison), instantly gets a **transparent ranked list of crops (TOPSIS)** with sensitivity analysis, then runs a **portfolio optimizer** that allocates land across crops under constraints while maximising return or minimising risk and enforcing **diversification**. Users compare **scenarios** (drought, price crash, budget change), see **Monte Carlo risk**, and export a **decision report**.

It supports **transparent crop-planning discussions**: every number can be traced to inputs, weights and formulas shown on screen.

## 2. Objectives

1. Build a polished light-themed website with **public landing page, login/register screens, role-based dashboard** and data entry forms in the dashboard.
2. Rank crop alternatives using **water demand, soil suitability, expected return, price variability** with **adjustable weights** (direct or AHP) using **TOPSIS**, with a weighted-sum cross-check.
3. Provide **sensitivity analysis**: one-at-a-time weight sweeps, Monte Carlo weight perturbation, rank-stability matrix.
4. Provide a **Python optimization engine** (PuLP/SciPy) for land allocation with constraints (land, water, budget, labour, diversification) and clear **feasibility diagnostics**.
5. Provide **scenario comparison** and **Monte Carlo simulation** of portfolio returns (risk, probability of loss).
6. Offer reliable **data entry with validation** (clear messages, duplicates, missing/invalid values, audit trail) and CSV import.
7. Present everything through advanced UI components (leaderboards, radar charts, allocation donut/treemap, efficient-frontier scatter, tornado chart, heatmap, gauges, wizard).
8. Store all data in **MongoDB**, configured only through **`.env`**. Export results as **PDF, Excel and CSV**.

## 3. Scope

**In scope:** authentication and roles, farm profiles, crop master data, price history entry, cost/yield data, soil suitability scoring, water balance, AHP weights, TOPSIS ranking, sensitivity analysis, portfolio optimization, scenario comparison, Monte Carlo simulation, dashboard, reports, admin area, tests.
**Out of scope:** crop yield prediction ML, satellite imagery, live mandi price scraping (CSV import instead), payments, mobile native apps, multi-organisation tenancy (future work).

## 4. Users, Roles and Login Screens

| Role | Access |
|---|---|
| **Planner (default)** | Own farms, criteria profiles, rankings, optimizations, scenarios, reports; can add/edit own data; can read the shared crop library |
| **Admin** | Everything, plus manage the shared **crop library and price data**, import CSV, manage users, view audit log, system settings |

**Auth screens (all light-themed, see Section 12 for layout):**
- **Login:** email + password, show/hide password, "remember me", inline validation, error state, loading state, link to Register.
- **Register:** name, email, password (strength meter), confirm password; creates a Planner.
- **Forgot / reset password:** simple flow: request creates a one-time reset token shown to admin in the Users page (no email service required); optional SMTP via `.env` if the developer wants emails.
- **Profile / Settings:** change name, password, preferred units (hectare/acre, mm, INR) and default region.
- Session: JWT access token (short) + refresh token (httpOnly cookie or secure storage), automatic logout on expiry, protected routes, role-based route guards, **login rate limiting** (e.g. 5 failed attempts then temporary lock), bcrypt password hashing, minimum password rules.
- First admin is created by `scripts/create_admin.py` from `.env` values (`ADMIN_EMAIL`, `ADMIN_PASSWORD`).

## 5. Data Entry and Data Sources

**Everything the engine needs is editable in the dashboard** (Data pages), with inline-editable tables, modal forms, validation messages and an audit trail. CSV import is available for bulk loading.

| Dataset | Entered / sourced from | Notes |
|---|---|---|
| Crop library (shared) | Admin data entry; reference: state agricultural university package of practices, ICAR, FAO ECOCROP | Crop name, category, season(s), duration (days), water requirement (mm per season), optimal and tolerable ranges for soil pH, EC, organic carbon, texture classes, drainage, labour (person-days/ha), typical yield (t/ha) |
| Economics (per crop, per region/season) | Admin/Planner entry; reference: CACP cost of cultivation studies, state agriculture departments | Cost of cultivation per ha, expected yield, MSP (if any) |
| Price history | Admin entry or CSV; reference: Agmarknet / data.gov.in mandi prices | Monthly (or weekly) modal price per crop and market in INR per quintal, used for expected price and **price variability** |
| Farm profile (per user) | Planner entry | Name, location, total land (ha), soil test (pH, EC, organic carbon, N, P, K, texture, drainage), water availability (rainfall mm, irrigation m3 per season), budget (INR), labour (person-days), season |
| Criteria profile (per user) | Planner entry | Weights (direct) or AHP pairwise matrix with consistency ratio |
| Constraint set (per user) | Planner entry | Optimizer constraints and objective |

**Seed data (mandatory):** `scripts/seed.py` creates the admin user, a demo planner, **15-18 crops** (e.g. rice, wheat, maize, groundnut, cotton, sugarcane, banana, tomato, onion, chilli, turmeric, ragi, sorghum, blackgram, greengram, sunflower), **10 years of monthly synthetic price history** per crop (seasonality + volatility + occasional shocks), economics, 2-3 demo farms, a criteria profile, one ranking, one optimization and three scenarios. All seed values must be labelled **"illustrative demo values: verify with official sources before real use"** in the UI and README. After seeding, every dashboard widget shows data.

## 6. System Flow

```
Login (JWT) -> role-based dashboard
        |
        v
[1] Data entry / import: crop library, economics, price history, farm profile (validation + audit)
        |
        v
[2] Criteria setup: choose weights (sliders) OR AHP pairwise matrix -> weights + consistency ratio
        |
        v
[3] Scoring engine (Python): soil suitability, water demand/balance, expected return, price variability
        |
        v
[4] TOPSIS ranking (+ weighted-sum cross-check) -> leaderboard, radar profile, explanation per crop
        |
        v
[5] Sensitivity analysis: weight sweeps, Monte Carlo perturbation, rank-stability
        |
        v
[6] Portfolio optimizer: choose objective + constraints -> feasibility check -> optimal land allocation
        |
        v
[7] Scenario manager: clone and modify inputs (drought, price shock, budget) -> re-run -> compare
        |
        v
[8] Monte Carlo simulation of portfolio return -> expected value, P(loss), 5th percentile (VaR-style)
        |
        v
[9] Dashboard + Decision report (PDF / Excel / CSV)
```

## 7. Methods (precise definitions)

### 7.1 Criteria and their direction

| Criterion | Definition | Type |
|---|---|---|
| **Water demand** | Crop water requirement per hectare for the season (mm), optionally as **water stress ratio** `WSR = crop requirement / (effective rainfall + irrigation available per ha)`; use the ratio when the farm's water data exists | Cost (lower is better) |
| **Soil suitability** | 0-1 score from 7.2 | Benefit |
| **Expected return** | Net return per ha `= expected price x yield - cost of cultivation` (INR/ha); expected price = mean of last N months of modal price (default 36, configurable), or MSP if higher and the user enables "MSP floor" | Benefit |
| **Price variability** | Coefficient of variation of the price history (or standard deviation of annual log returns); optionally add yield variability if data exists | Cost (lower is better) |

Optional extra criteria (configurable, off by default): labour requirement (cost), crop duration (cost), profit-per-cubic-metre-of-water (benefit).

### 7.2 Soil suitability (FAO-style, transparent)

For each soil parameter `p` (pH, EC/salinity, organic carbon, texture, drainage) compute a **trapezoidal suitability membership** using the crop's ranges `[abs_min, opt_min, opt_max, abs_max]`: 0 outside absolute limits, 1 inside the optimum range, linear in between. Combine into one score with a selectable rule: **geometric mean** (default) or **minimum / Liebig's law**. Categorical parameters (texture, drainage) use a lookup table from crop config. Show the per-parameter breakdown in the UI so the user sees why a crop scores low. Crops with score below a **hard exclusion threshold** (default 0.3) can be excluded from the optimizer.

### 7.3 AHP weights

- User fills a pairwise comparison matrix on the **Saaty 1-9 scale** (with reciprocals) through an interactive grid or per-pair sliders.
- Weights = **principal eigenvector** of the matrix (`numpy.linalg.eig`), normalised to sum to 1.
- **Consistency:** `CI = (lambda_max - n) / (n - 1)`, `CR = CI / RI` with the Saaty random-index table; accept when **CR < 0.10**, otherwise show which pairs contribute most to the inconsistency and a suggested correction.
- Alternative: **direct weights** by sliders (auto-normalised to 100%, with a live sum indicator) and presets ("Water-saving", "Profit-first", "Low-risk", "Balanced").

### 7.4 TOPSIS ranking

1. Decision matrix `X` (crops x criteria).
2. **Vector normalisation:** `r_ij = x_ij / sqrt(sum_i x_ij^2)` (min-max available as an option).
3. Weighted matrix `v_ij = w_j * r_ij`.
4. Ideal best `A+` and ideal worst `A-` per criterion respecting benefit/cost direction.
5. Distances `S+_i = sqrt(sum_j (v_ij - A+_j)^2)` and `S-_i`.
6. **Closeness coefficient** `C_i = S-_i / (S+_i + S-_i)`; rank descending.
7. Cross-check with a **weighted sum model (WSM)** on min-max normalised values; report Spearman rho and Kendall tau between the two rankings.
8. **Explanation per crop:** contribution of each criterion to its closeness (bar breakdown) and a one-sentence plain-language reason (e.g. "Ranks 2nd: high soil suitability and return, but above-average water demand").

### 7.5 Sensitivity analysis

- **One-at-a-time:** vary each weight from 0 to 1 (others rescaled proportionally) and record rank changes; output a **tornado chart** of rank sensitivity and "weight value at which the top crop changes".
- **Monte Carlo weight perturbation:** sample weights from a **Dirichlet** distribution centred on the user's weights (concentration configurable), run TOPSIS 1,000+ times, output a **rank-probability matrix** (crop x rank), mean rank, and **top-1 stability %**.
- **Data uncertainty (optional):** perturb prices/yields by +/- x% and report rank stability.

### 7.6 Portfolio optimization

**Decision variables:** `a_c` = hectares allocated to crop `c` (continuous, >= 0); `y_c` = binary (crop selected) when minimum area or minimum crop count is used.

**Objectives (user selects one):**
1. **Maximise total expected net return:** `sum_c a_c * R_c` (LP/MILP, PuLP with CBC solver).
2. **Maximise TOPSIS-weighted benefit:** `sum_c a_c * C_c` where `C_c` is the TOPSIS closeness (rewards crops the user's weights favour).
3. **Minimise risk for a target return (mean-variance):** `min a^T Sigma a` subject to `sum a_c R_c >= target` where `Sigma` is the covariance matrix of per-hectare returns computed from price history (SciPy `minimize`, SLSQP). Output the **efficient frontier** (risk vs return for a range of targets).
4. **Balanced (weighted combination)** of normalised return and risk with a slider.

**Constraints (all editable in the UI):**
- Total land: `sum a_c <= L` (or `= L` if "use all land" is on).
- Water: `sum a_c * W_c <= Water_available` (W_c in m3/ha = mm x 10).
- Budget: `sum a_c * Cost_c <= B`.
- Labour: `sum a_c * Labour_c <= Labour_available`.
- **Diversification:** per-crop maximum share `a_c <= s_max * L` (default 40%); **minimum number of crops** `sum y_c >= k` with `a_c >= minArea * y_c` and `a_c <= L * y_c`; optional maximum number of crops; optional category balance (e.g. at least X% pulses).
- Soil: crops with suitability below the exclusion threshold have `a_c = 0`.
- Season: only crops valid for the chosen season (and optional multi-season handled as separate runs).
- Optional minimum area for specific crops chosen by the user ("must grow rice 1 ha").

**Feasibility engine:** before solving, run quick checks; when infeasible, report which constraint group conflicts (e.g. "water available supports at most 3.1 ha of the cheapest-water crop mix; required 5 ha") by **relaxing constraints one group at a time** and reporting which relaxation restores feasibility. Never return a silent failure.

**Outputs and diversification metrics:** allocation per crop, total return, water/budget/labour use and utilisation %, **HHI** `sum s_c^2` with shares `s_c`, **effective number of crops** `1/HHI`, **Shannon entropy**, risk (`sqrt(a^T Sigma a)`), shadow prices (dual values) for LP constraints ("one more m3 of water adds INR x"), and a comparison against two simple baselines (all-in on top-ranked crop; equal split among top 5).

### 7.7 Scenarios and Monte Carlo simulation

- **Scenario = named set of modifications** to a base farm/price/constraint set: e.g. **Drought** (rainfall -30%, irrigation -20%), **Price crash** (selected crop prices -25%), **MSP support**, **Budget up/down**, **Land change**. Each scenario re-runs scoring, TOPSIS and the optimizer.
- **Comparison measures:** expected net return, water use, budget use, risk, diversification (HHI / effective crops), top-3 crops, feasibility status, change vs base (delta bars).
- **Monte Carlo (default 5,000 runs, fixed seed for reproducibility):** sample price paths by **bootstrap of historical annual returns** or **lognormal** fitted to history, sample yield variation (e.g. +/- 15% normal, configurable), optional correlated shocks using the covariance matrix (Cholesky). Outputs: distribution of portfolio net return (histogram), mean, median, standard deviation, **probability of loss**, **5th percentile (VaR-style)** and expected shortfall, per-crop contribution to risk.
- All simulations are labelled as **scenario analysis, not forecasts**.

### 7.8 Validation rules for data entry (Pydantic + UI messages)

| Check | Rule |
|---|---|
| Required fields | Crop name, season, water requirement, duration, cost, yield, ranges present |
| Numeric ranges | pH 3-10, EC >= 0, organic carbon 0-10%, water requirement 50-5000 mm, yield > 0, cost >= 0, price > 0, land > 0, budget >= 0 |
| Range ordering | `abs_min <= opt_min <= opt_max <= abs_max` |
| Duplicates | Unique crop name; unique `(crop, market, month)` for prices; clear "already exists, edit instead?" message |
| Price history | Minimum 24 months required for variability; fewer shows a warning and falls back to a configured default with a visible flag |
| AHP matrix | Reciprocal symmetry, values in {1/9..9}, CR shown and flagged if above 0.10 |
| Weights | Non-negative and sum to 100% (auto-normalise with message) |
| Optimizer inputs | All limits positive; `min crops <= number of eligible crops`; `max share * crops >= 100%` when "use all land" is on |
| CSV import | Row-level error table (row, column, message, suggestion); option to import valid rows only |
| Ownership | A planner can modify only their own farms/profiles/scenarios; library edits need Admin |

Every create/update/delete writes to the **audit log** (who, what, when, old and new values).

## 8. Technology Stack

| Layer | Choice | Reason |
|---|---|---|
| Website | **React 18 + TypeScript + Vite** | Real multi-page website |
| UI components | **Tailwind CSS + shadcn/ui (Radix primitives) + lucide-react icons** | Advanced, accessible, consistent light UI |
| Charts | **Recharts** (bar, radar, scatter, area, pie/donut, treemap) + custom SVG for heatmap/tornado/gauge | Rich interactive charts |
| Tables | **TanStack Table** (sorting, filtering, column visibility, pagination, inline edit) | Data-entry-friendly grids |
| Forms | **React Hook Form + Zod** | Typed validation with clear messages |
| Data fetching / routing | **TanStack Query**, **React Router** | Caching, optimistic updates, protected routes |
| UX extras | **framer-motion** (subtle animation), **sonner** (toasts), **cmdk** (command palette), `@fontsource/inter` | Polished feel, no external CDN |
| Backend | **FastAPI** + Uvicorn, Pydantic v2, pydantic-settings | REST API, validation, `/docs` |
| Auth | PyJWT, bcrypt, slowapi (rate limiting) | Secure login |
| Database | **MongoDB Atlas** via **PyMongo** | Flexible documents, aggregation |
| Config / secrets | **`.env` + `.env.example`** (backend and frontend) | No secrets in code |
| Computation | NumPy, SciPy, pandas | Normalisation, eigenvectors, SLSQP, Monte Carlo |
| Optimization | **PuLP (CBC)**; SciPy SLSQP for quadratic risk; OR-Tools optional | LP/MILP and mean-variance |
| Reports | Jinja2 + matplotlib + weasyprint (PDF), openpyxl (Excel) | Decision report export |
| Testing | pytest + httpx TestClient, Vitest + React Testing Library, optional Playwright E2E, dedicated test DB | Quality |
| Quality | ruff, black, ESLint, Prettier, Git, pre-commit | Code quality |
| Deployment | Docker + `docker-compose.yml` (backend, frontend/nginx; Atlas as DB) optional | One-command demo |

Keep the library set minimal: no ML frameworks, no extra databases.

## 9. MongoDB Database Design

Database name from `MONGODB_DB_NAME` (default `cropchoice`). `_id` is `ObjectId` (serialized as string by the API); dates are UTC datetimes.

```text
users
{ _id, name, email, password_hash, role: "admin"|"planner", preferences: {area_unit, currency, region},
  failed_logins, locked_until, reset_token_hash, reset_expires, created_at, last_login }
  index: unique(email)

crops                                      // shared crop library (admin-managed)
{ _id, name, category, seasons: ["kharif","rabi","zaid"], duration_days,
  water_req_mm, labour_person_days_ha, typical_yield_t_ha,
  soil: { ph: {abs_min,opt_min,opt_max,abs_max}, ec: {...}, oc: {...},
          texture_suitability: {sandy,loam,clay,...: 0..1}, drainage_suitability: {poor,moderate,good: 0..1} },
  active, source_note, created_by, created_at, updated_at }
  index: unique(name)

crop_economics                             // per crop, region, season
{ _id, crop_id, region, season, cost_per_ha, expected_yield_t_ha, msp_per_quintal, year, notes }
  index: unique(crop_id, region, season, year)

price_history
{ _id, crop_id, market, month, modal_price_per_quintal, source }
  index: unique(crop_id, market, month)

farms
{ _id, owner_id, name, location: {state, district, lat, lon}, land_ha, season,
  soil: { ph, ec, oc, n, p, k, texture, drainage },
  water: { rainfall_mm, effective_rainfall_pct, irrigation_m3 },
  budget_inr, labour_person_days, created_at, updated_at }
  index: (owner_id, name)

criteria_profiles
{ _id, owner_id, name, mode: "direct"|"ahp", criteria: ["water","soil","return","variability", ...],
  weights: {...}, ahp_matrix, ahp_cr, normalization: "vector"|"minmax", created_at }

rankings
{ _id, owner_id, farm_id, profile_id, created_at, method: "topsis",
  inputs_snapshot, results: [ { crop_id, scores: {...}, closeness, rank, wsm_score, wsm_rank, explanation } ],
  rank_correlation: {spearman, kendall} }

sensitivity_runs
{ _id, ranking_id, one_at_a_time, monte_carlo: { n, concentration, rank_probability, mean_rank, top1_stability }, created_at }

constraint_sets
{ _id, owner_id, farm_id, name, objective, params: { max_share, min_crops, max_crops, min_area, use_all_land, target_return, risk_weight },
  limits: { land_ha, water_m3, budget_inr, labour }, forced_min_areas: {crop_id: ha}, excluded_crops: [] }

optimizations
{ _id, owner_id, farm_id, constraint_set_id, ranking_id, created_at, status: "optimal"|"infeasible"|"error",
  allocation: [ {crop_id, area_ha, share} ], totals: { net_return, water_m3, cost, labour },
  utilisation: {...}, diversification: { hhi, effective_crops, entropy }, risk: {...},
  shadow_prices, feasibility_report, baselines: {...}, efficient_frontier: [ {risk, return} ] }

scenarios
{ _id, owner_id, farm_id, name, description, base_optimization_id,
  modifications: { rainfall_pct, irrigation_pct, price_pct_by_crop, budget_pct, land_pct, msp_support, ... },
  result_optimization_id, summary: { net_return, water_m3, risk, effective_crops, top_crops, feasible }, created_at }

simulations
{ _id, owner_id, optimization_id, n_runs, seed, method: "bootstrap"|"lognormal",
  stats: { mean, median, std, p_loss, p5, expected_shortfall }, histogram: {bins, counts}, risk_contribution: {...}, created_at }

reports
{ _id, owner_id, created_at, title, scope: {farm_id, ranking_id, optimization_id, scenario_ids}, file_path, format }

import_jobs
{ _id, kind, filename, uploaded_by, uploaded_at, status, n_rows, n_errors, errors: [ {row, column, message} ] }

audit_log
{ _id, user_id, action: "create"|"update"|"delete"|"login"|"run", collection, document_id, old, new, at }
  index: (collection, at)
```

Implementation rules:
- `src/db/mongo.py`: single `MongoClient` built from settings (`serverSelectionTimeoutMS` from env), `get_db()`, `ping()`, `ensure_indexes()`, `$jsonSchema` validators for `users`, `crops`, `price_history`, `farms`.
- All collection access goes through repositories in `src/db/repositories/` with **owner filtering** for planner data; route handlers never touch PyMongo directly.
- Seeding and imports use `bulk_write` with upserts so they are idempotent.
- Tests use `MONGODB_TEST_DB_NAME` and drop it after the session; **never run tests against the main database**.

## 10. Environment Configuration (`.env`)

Two env files. **`.env` and `frontend/.env` are git-ignored; only the `.env.example` files are committed, with placeholder values.**

**Backend `.env.example` (project root):**
```env
# --- Application ---
APP_ENV=development
APP_HOST=127.0.0.1
APP_PORT=8000
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:5173

# --- MongoDB Atlas ---
# Paste your real Atlas connection string ONLY into your local .env (never commit it).
# URL-encode special characters in the password. Allow your IP in Atlas > Network Access.
MONGODB_URI=mongodb+srv://<db_user>:<url_encoded_password>@<cluster-host>/?retryWrites=true&w=majority
MONGODB_DB_NAME=cropchoice
MONGODB_TEST_DB_NAME=cropchoice_test
MONGODB_TIMEOUT_MS=8000

# --- Auth ---
JWT_SECRET=change-me-to-a-long-random-string
JWT_ACCESS_MINUTES=30
JWT_REFRESH_DAYS=7
MAX_FAILED_LOGINS=5
LOCKOUT_MINUTES=15
ADMIN_EMAIL=admin@cropchoice.local
ADMIN_PASSWORD=change-me-strong

# --- Optimizer / simulation defaults ---
SIM_DEFAULT_RUNS=5000
SIM_SEED=42
MAX_SHARE_DEFAULT=0.4
SOIL_EXCLUSION_THRESHOLD=0.3

# --- Files ---
REPORT_DIR=outputs/reports
UPLOAD_DIR=data/uploads
MAX_UPLOAD_MB=10
```

**Frontend `frontend/.env.example`:**
```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_NAME=CropChoice
```

Rules: `src/config.py` uses `pydantic-settings` and **fails fast with a clear message** if a required variable (e.g. `MONGODB_URI`, `JWT_SECRET`) is missing or still contains a placeholder; `/api/health` reports DB status via `ping()`; README explains "copy `.env.example` to `.env` and paste your Atlas URI"; use a **dedicated Atlas database user with `readWrite` on `cropchoice` only** (not an admin-level user); logs must never print the URI or passwords.

## 11. Backend API (FastAPI, JSON, Pydantic-validated, all under `/api`)

| Area | Endpoints |
|---|---|
| Health | `GET /health` |
| Auth | `POST /auth/register`, `POST /auth/login`, `POST /auth/refresh`, `POST /auth/logout`, `GET /auth/me`, `PUT /auth/me`, `POST /auth/change-password`, `POST /auth/forgot`, `POST /auth/reset` |
| Dashboard | `GET /dashboard/overview?farm_id=` (KPIs, top-5 ranking, allocation, scenario summary, data-completeness) |
| Crop library | `GET/POST /crops`, `GET/PUT/DELETE /crops/{id}` (write = admin), `GET /crops/{id}/soil-fit?farm_id=` |
| Economics | `GET/POST /economics`, `PUT/DELETE /economics/{id}` |
| Prices | `GET /prices?crop_id=&from=&to=`, `POST /prices`, `PUT/DELETE /prices/{id}`, `GET /prices/{crop_id}/stats` (mean, CV, volatility) |
| Farms | `GET/POST /farms`, `GET/PUT/DELETE /farms/{id}` |
| Criteria | `GET/POST /criteria-profiles`, `PUT/DELETE /criteria-profiles/{id}`, `POST /criteria/ahp` (matrix in, weights + CR out), `GET /criteria/presets` |
| Ranking | `POST /rankings` (farm, profile -> TOPSIS result), `GET /rankings`, `GET /rankings/{id}`, `POST /rankings/{id}/sensitivity` |
| Optimizer | `GET/POST /constraint-sets`, `POST /optimizations` (run), `GET /optimizations`, `GET /optimizations/{id}`, `POST /optimizations/feasibility-check` |
| Scenarios | `GET/POST /scenarios`, `PUT/DELETE /scenarios/{id}`, `POST /scenarios/{id}/run`, `POST /scenarios/compare` |
| Simulation | `POST /simulations` (optimization id, runs, method), `GET /simulations/{id}` |
| Import / export | `POST /import/{kind}` (crops, prices, economics) with validation report, `GET /export/ranking/{id}.csv`, `GET /export/optimization/{id}.xlsx` |
| Reports | `POST /reports`, `GET /reports`, `GET /reports/{id}/download` |
| Admin | `GET/POST/PUT /admin/users`, `POST /admin/users/{id}/reset-token`, `GET /admin/audit-log`, `GET /admin/system` |

Cross-cutting: central `ObjectId`/datetime serializer; consistent error format `{ "detail", "code", "fields": [...] }` so the UI can show field-level messages; pagination (`page`, `page_size`); owner scoping; role guards; CORS from `CORS_ORIGINS`; rate limiting on auth routes.

## 12. UI / UX Design System (light theme, agriculture-themed)

**Design goals:** neat, clear, calm, data-dense but not cluttered; generous spacing; strong visual hierarchy; every screen has loading skeleton, empty state (with a call to action) and error state. **Light theme only** (no dark mode needed).

### 12.1 Colour tokens (define as CSS variables and Tailwind theme colours)

| Token | Value | Use |
|---|---|---|
| `bg-base` | `#F6F8F4` | App background (warm off-white with a faint green tint) |
| `bg-surface` | `#FFFFFF` | Cards, panels, sidebar, top bar |
| `bg-subtle` | `#EEF3EC` | Table headers, hovered rows, input backgrounds, inactive tabs |
| `bg-elevated` | `#FFFFFF` + shadow | Popovers, dialogs, dropdowns |
| `border` | `#DCE5DC` | Dividers, card borders |
| `text-primary` | `#14231A` | Main text (very dark green-black) |
| `text-secondary` | `#4A5F52` | Secondary text |
| `text-muted` | `#7A8E80` | Hints, placeholders, disabled |
| `primary` | `#047857` (emerald-700, "growth") | Primary buttons, active nav item, key highlights (white text on it passes AA) |
| `primary-hover` | `#065F46` | Hover/pressed |
| `primary-soft` | `#D1FAE5` (text `#065F46`) | Selected rows, soft badges, active nav background |
| `accent-harvest` | text `#B45309`, chart `#F59E0B`, soft `#FEF3C7` | Return/profit, rank 1 badge |
| `accent-earth` | text `#9A5B2F`, chart `#C2763F`, soft `#F6E7DA` | Soil suitability |
| `accent-water` | text `#0369A1`, chart `#0EA5E9`, soft `#E0F2FE` | Water demand and usage |
| `accent-risk` | text `#BE123C`, chart `#F43F5E`, soft `#FFE4E6` | Price variability and risk |
| `success` / `warning` / `danger` / `info` | `#15803D` / `#B45309` / `#B91C1C` / `#1D4ED8` (each with a soft tinted background) | Status, validation messages, toasts |

**Criteria colour mapping (consistent everywhere):** Water = sky, Soil = clay, Return = amber, Variability/Risk = rose; crops in categorical charts use this 8-colour palette (all readable on white): emerald `#059669`, amber `#F59E0B`, sky `#0EA5E9`, clay `#C2763F`, violet `#7C3AED`, rose `#F43F5E`, lime `#65A30D`, teal `#0D9488`.

**Elevation and focus:** cards use a 1px `border` plus a soft shadow (`0 1px 2px rgba(20,35,26,.06), 0 4px 16px rgba(20,35,26,.06)`); the focus ring is `0 0 0 3px rgba(5,150,105,.25)` with a visible 2px primary outline for keyboard users. Chart gridlines use `#E5ECE5`; chart tooltips use a white card with shadow.

**Accessibility:** WCAG AA contrast everywhere (body text on `bg-base` above 12:1; use the dark `text` variants of accent colours for text and the `chart` variants only for fills); never convey meaning by colour alone (add icons or labels).

### 12.2 Typography, spacing, shape

Inter (via `@fontsource`), `tabular-nums` for all numbers in tables and KPIs; scale: 12 / 14 (body) / 16 / 20 / 24 / 32 px; 8px spacing grid; radius 12px (cards), 8px (inputs/buttons); 1px borders; consistent 24px page padding; max content width with responsive grid (12 columns desktop, stacked on mobile).

### 12.3 Advanced component library (build as reusable components)

- **Shell:** collapsible sidebar with icons and active indicator, top bar with farm selector, global search / **command palette (Ctrl+K)**, notifications popover, user menu (avatar, role badge), breadcrumbs.
- **Data display:** `KpiCard` (value, delta arrow, sparkline), `DataTable` (TanStack Table: sort, filter, column toggle, pagination, sticky header, row actions, **inline cell editing**, bulk select, CSV export), `StatusBadge`, `Stat` rows, `EmptyState`, `Skeleton`.
- **Charts:** `RankingLeaderboard` (animated horizontal bars with rank medals), `RadarProfile` (crop vs ideal on 4 criteria), `AllocationDonut` and `AllocationTreemap`, `ReturnRiskScatter` (bubble = area share, efficient frontier line), `TornadoChart` (sensitivity), `RankProbabilityHeatmap` (crop x rank), `ScenarioCompareBars` (delta vs base), `HistogramWithVaR` (Monte Carlo), `RadialGauge` (water/budget utilisation, soil fit), `PriceLineChart` with range brush.
- **Inputs:** `WeightSliders` (live sum indicator, lock icons, auto-normalise, presets), **`AhpMatrixGrid`** (pairwise Saaty sliders, reciprocal auto-fill, consistency gauge with CR colour state), constraint form with units, number inputs with steppers and unit suffix, combobox/multiselect, date and month pickers, segmented controls, switches, tooltips with formula explanations.
- **Flows:** **Stepper wizard** (Farm -> Criteria -> Ranking -> Optimize -> Scenarios -> Report), dialogs and side drawers for create/edit forms, confirm dialogs for deletes, **toast notifications** with undo, optimistic updates, unsaved-changes guard.
- **Motion:** subtle framer-motion (fade/slide 150-200 ms, bar growth on rank changes), respect `prefers-reduced-motion`.

### 12.4 Key layouts

**Login screen** (split layout): left half = brand panel with a soft light-green gradient (`#ECF6EF` to `#F6F8F4`) and a subtle topographic/field-row SVG pattern in emerald at low opacity, logo, tagline ("Choose the right crops. Defend the decision."), three short value points with icons; right half = centred white form card with soft shadow (email, password with show/hide, remember me, primary button with loading spinner, link to Register, inline error banner). Register and Forgot screens reuse the same layout. On mobile the brand panel collapses to a header.

**Dashboard (main)**
```
+---------+--------------------------------------------------------------+
| Sidebar | Top bar: [Farm selector v]   [Ctrl+K Search]  [Bell] [User]    |
|         +--------------------------------------------------------------+
| Overview| KPI: Top crop | Expected net return | Water use % | Eff. crops | P(loss) |
| Farms   +-------------------------------+------------------------------+
| Crops   | Ranking leaderboard (top 5)   | Land allocation donut/tree   |
| Prices  +-------------------------------+------------------------------+
| Criteria| Return-vs-risk scatter + frontier | Water/Budget gauges      |
| Ranking +-------------------------------+------------------------------+
| Optimize| Scenario comparison mini-bars | Data completeness + Activity |
| Scenario+-------------------------------+------------------------------+
| Reports |
| Admin   |
+---------+
```

Data-completeness card lists crops missing prices/soil ranges with "Fix now" buttons that open the data-entry drawer, so data entry is part of the dashboard flow.

## 13. Pages

| Page | Route | Content |
|---|---|---|
| Landing | `/` | Hero, product value, feature highlights, "How it works" (4 steps), screenshots, CTA to Login/Register |
| Login / Register / Forgot / Reset | `/login`, `/register`, `/forgot`, `/reset` | As in 12.4 |
| **Dashboard** | `/app` | As in 12.4 |
| Farms | `/app/farms` | Table of farms with add/edit drawer (land, soil test, water, budget, season), soil-fit preview |
| Crop Library | `/app/crops` | Editable table (admin write, planners read), detail drawer with soil range editor and radar preview |
| Economics and Prices | `/app/prices` | Price history table with inline add/edit, line chart with range brush, stats cards (mean, CV), economics editor, CSV import with validation preview |
| Criteria and Weights | `/app/criteria` | Tabs: **Sliders** (presets, live normalisation) and **AHP** (matrix grid, weights bar chart, CR gauge); save profiles |
| Ranking | `/app/ranking` | Leaderboard, TOPSIS vs WSM comparison, per-crop explanation drawer (criterion contributions, soil-fit breakdown), radar compare (select 2-3 crops), sensitivity tab (tornado, rank-probability heatmap, top-1 stability) |
| Portfolio Optimizer | `/app/optimizer` | Objective selector, constraint form (land, water, budget, labour, diversification), feasibility messages, results (allocation table + donut/treemap, utilisation gauges, shadow prices, baselines comparison, efficient frontier) |
| Scenarios | `/app/scenarios` | Scenario cards (create from templates: drought, price crash, MSP support, budget change), side-by-side comparison table and delta charts, run Monte Carlo |
| Simulation | `/app/simulation` | Histogram with VaR line, P(loss), percentile table, risk contribution per crop |
| Reports | `/app/reports` | Compose report (choose ranking, optimization, scenarios), generate PDF, Excel/CSV downloads, history |
| Data Import | `/app/import` | Upload CSV for crops/prices/economics, validation result table, commit valid rows |
| Admin | `/app/admin` | Users (roles, lock/unlock, reset token), audit log (filter), system status |
| Profile | `/app/profile` | Preferences, change password |
| About / Methodology | `/about` | Formulas for soil suitability, AHP, TOPSIS, optimizer, simulation; data sources; limitations; disclaimer ("decision support, not a guarantee") |

## 14. Project Structure

```
cropchoice/
|-- PROJECT_SPEC_CROPCHOICE.md
|-- README.md
|-- requirements.txt
|-- .env.example
|-- .gitignore                  # must include .env and frontend/.env
|-- docker-compose.yml          # optional (backend + frontend; Atlas is the DB)
|-- config/
|   |-- criteria.yaml  soil_lookup.yaml  presets.yaml  ahp_random_index.yaml
|-- data/ sample/ uploads/
|-- scripts/
|   |-- seed.py  create_admin.py
|-- src/
|   |-- config.py               # pydantic-settings, fail-fast, placeholder detection
|   |-- db/
|   |   |-- mongo.py
|   |   `-- repositories/
|   |-- core/
|   |   |-- scoring.py          # water, return, variability, assembling the decision matrix
|   |   |-- soil.py             # trapezoidal membership + combination rules
|   |   |-- ahp.py              # eigenvector weights, CI/CR, inconsistency hints
|   |   |-- topsis.py           # TOPSIS + WSM + rank correlations + explanations
|   |   |-- sensitivity.py      # one-at-a-time, Dirichlet Monte Carlo, rank-probability
|   |   |-- optimizer.py        # PuLP LP/MILP, SciPy mean-variance, efficient frontier, shadow prices
|   |   |-- feasibility.py      # pre-checks and constraint-relaxation diagnostics
|   |   |-- diversification.py  # HHI, effective crops, entropy
|   |   |-- scenarios.py        # apply modifications, run, compare
|   |   |-- simulation.py       # bootstrap/lognormal Monte Carlo, VaR, expected shortfall
|   |   `-- validators.py
|   |-- imports/csv_import.py
|   |-- report/generate.py  report/template.html.j2
|-- backend/
|   |-- main.py  deps.py  schemas.py  security.py
|   `-- routers/                # auth, dashboard, crops, economics, prices, farms, criteria, rankings, optimizer, scenarios, simulations, import_export, reports, admin
|-- frontend/
|   |-- .env.example  package.json  vite.config.ts  tailwind.config.ts  tsconfig.json  components.json
|   `-- src/
|       |-- main.tsx  App.tsx  routes.tsx
|       |-- api/ (client.ts, types.ts, hooks/)
|       |-- styles/ (globals.css with tokens, tailwind layers)
|       |-- components/ (ui/ [shadcn], layout/, charts/, forms/, tables/, wizard/, feedback/)
|       |-- pages/ (Landing, auth/*, Dashboard, Farms, Crops, Prices, Criteria, Ranking, Optimizer, Scenarios, Simulation, Reports, Import, Admin, Profile, About)
|       `-- context/ (AuthContext, FarmContext)
|-- tests/                      # backend tests
|-- notebooks/
`-- outputs/
```

Commands: `cp .env.example .env` and `cp frontend/.env.example frontend/.env` (then paste the real Atlas URI into `.env` only); `pip install -r requirements.txt`; `python -m scripts.seed`; `uvicorn backend.main:app --reload`; in `frontend/`: `npm install` then `npm run dev`; open `http://localhost:5173`.

## 15. Development Plan (12 weeks)

| Phase | Weeks | Deliverables | Acceptance criteria |
|---|---|---|---|
| 1. Setup, design, study | 1 | Repo, venv, requirements, both `.env.example`, `.gitignore`, `src/config.py`, design tokens and Tailwind theme, wireframes (Login, Dashboard, Ranking, Optimizer), notes on AHP/TOPSIS/LP | App refuses to start with clear error if `MONGODB_URI` or `JWT_SECRET` is missing/placeholder; no real credential anywhere in the repo |
| 2. MongoDB and auth backend | 2 | `mongo.py`, indexes, validators, repositories, users, JWT login/register/refresh, rate limiting, `/health`, audit log | Connects to Atlas using only `.env`; login lockout works; tests use test DB |
| 3. Seed data and data-entry APIs | 3 | `seed.py`, crop/economics/price/farm CRUD, validation (7.8), CSV import | Seed fills all collections idempotently; invalid inputs return field-level messages; audit rows created |
| 4. Scoring, AHP, TOPSIS | 4-5 | `soil.py`, `scoring.py`, `ahp.py`, `topsis.py` | AHP matches textbook example (weights and CR); TOPSIS matches hand-calculated example; cost/benefit directions correct |
| 5. Sensitivity | 6 | `sensitivity.py` | Weight sweep reproduces known rank flip; Dirichlet Monte Carlo is reproducible with a seed; probabilities sum to 1 per crop |
| 6. Optimizer and feasibility | 7-8 | `optimizer.py`, `feasibility.py`, `diversification.py` | LP matches hand-solved toy problem; constraints never violated; infeasible case returns diagnostic; HHI correct; efficient frontier monotonic |
| 7. Scenarios and simulation | 9 | `scenarios.py`, `simulation.py` | Drought scenario lowers water-hungry crop areas; Monte Carlo statistics match analytic values for a simple case; seed reproducible |
| 8. API completion | 9 | All routers in Section 11, reports, exports | API tests pass; `/docs` complete; owner scoping and role guards verified |
| 9. Frontend foundation | 10 | Vite app, theme, shell (sidebar, top bar, command palette), auth screens, route guards, typed API client, shared components | Login/register work against real API; light theme matches tokens; keyboard navigable |
| 10. Data-entry and analysis pages | 10-11 | Dashboard, Farms, Crops, Prices (inline edit + import), Criteria (sliders + AHP grid), Ranking (leaderboard, radar, sensitivity) | A planner can enter a farm, set weights, run ranking and see charts; loading/empty/error states everywhere |
| 11. Optimizer, scenarios, reports, admin | 11-12 | Optimizer, Scenarios, Simulation, Reports, Import, Admin, Profile, About, Landing | Full journey works: wizard from farm to report; PDF/Excel download correctly |
| 12. Testing, polish, deploy | 12 | Backend coverage over 70%, Vitest tests, optional Playwright journey test, accessibility and responsive pass, README, docker-compose, demo script | Demo runs from clean machine; Lighthouse accessibility above 90; no console errors |

## 16. Testing Plan

- **Config/security:** missing or placeholder env values fail fast; URI never logged; test DB isolation; password hashing (no plaintext); lockout after repeated failures; JWT expiry; planner cannot read another planner's data; non-admin cannot write the crop library.
- **Validation:** one test per rule in 7.8; CSV import error table content.
- **Soil suitability:** membership function at breakpoints (0, partial, 1); geometric mean vs minimum rule.
- **AHP:** textbook matrix gives known weights and CR; inconsistent matrix is flagged; reciprocal enforcement.
- **TOPSIS:** hand-calculated example matches to 4 decimals; benefit/cost directions; WSM correlation computed; weight changes alter ranking as expected.
- **Sensitivity:** known rank-flip threshold found; Monte Carlo reproducible; probability rows sum to 1.
- **Optimizer:** toy LP with known optimum; every constraint satisfied in output; max-share and min-crops respected; infeasible inputs give a specific diagnostic; shadow price sign sensible; mean-variance weights sum to land; frontier monotonic.
- **Simulation:** with zero variance the result equals the deterministic return; fixed seed reproducible; P(loss) between 0 and 1.
- **Scenarios:** modifications applied to a copy (base unchanged); comparison deltas correct.
- **API:** every endpoint status/schema; field-level errors; pagination; ObjectId serialization.
- **Frontend:** component tests (`KpiCard`, `DataTable` inline edit, `WeightSliders` normalisation, `AhpMatrixGrid` reciprocals, `RankingLeaderboard`); build passes with no TypeScript errors; optional Playwright test: login -> add farm -> set weights -> rank -> optimize -> download report.

## 17. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Real crop/price data incomplete | Seed data (clearly labelled illustrative), full in-dashboard data entry and CSV import, data-completeness card |
| Users misread a ranking as a guarantee | Disclaimer, transparent formulas, sensitivity and Monte Carlo shown next to results |
| AHP inconsistency confuses users | Live CR gauge, highlight offending pairs, suggestion text, fall back to sliders |
| Rank reversal and weight dependence in TOPSIS | Sensitivity module, WSM cross-check, top-1 stability metric |
| Optimizer returns unrealistic mono-crop plan | Diversification constraints (max share, min crops), HHI shown, baselines comparison |
| Infeasible constraints frustrate users | Feasibility engine with relaxation hints; never a silent failure |
| Price history too short for variability | 24-month minimum warning, flagged fallback value |
| Secrets exposed | `.env` git-ignored, `.env.example` placeholders only, least-privilege Atlas user, no credential in logs, rotate any credential that was ever shared in chat or committed |
| Atlas connection failures (IP allow-list, DNS) | Clear startup error and `/health` status; README troubleshooting steps |
| Long computations block the UI | Monte Carlo and sensitivity run in `BackgroundTasks` with status polling, or fast vectorised NumPy with progress indicator |
| Inconsistent UI | Design tokens and shared components only; no ad-hoc colours; visual QA checklist per page |

## 18. Final Deliverables Checklist

- [ ] Website with landing page, **login/register/forgot screens**, role-based dashboard
- [ ] **Data entry in the dashboard** for farms, crops, economics, prices, criteria, constraints (create/edit/delete, validation, audit trail, CSV import)
- [ ] Soil suitability, AHP weights, TOPSIS ranking (+ WSM check), sensitivity analysis
- [ ] Portfolio optimizer with diversification metrics, feasibility diagnostics, efficient frontier
- [ ] Scenario comparison and Monte Carlo risk simulation
- [ ] Light, agriculture-themed design system with advanced components as in Section 12
- [ ] FastAPI backend with Swagger docs, JWT auth, rate limiting
- [ ] MongoDB collections, indexes, validators, repositories (configured only via `.env`)
- [ ] PDF, Excel and CSV exports
- [ ] README (MongoDB Atlas + `.env` setup, seed, run), optional docker-compose, demo script
- [ ] Final project report (Introduction, Literature Review, Data and Methodology, System Design, Implementation, Results and Discussion, Conclusion and Future Work, References)
- [ ] Presentation slides
- [ ] Future work: live mandi price integration, yield-prediction models, multi-season rotation planning, multi-farm cooperative optimisation, regional language support, mobile app

## 19. Claude Code Starter Prompts

Use in order:

1. `Read PROJECT_SPEC_CROPCHOICE.md. Set up the repo structure from Section 14, requirements.txt, .gitignore (including .env and frontend/.env), both .env.example files from Section 10 with placeholder values only, src/config.py with pydantic-settings and fail-fast validation (reject missing or placeholder MONGODB_URI and JWT_SECRET), a README, and a docs/ folder with simple wireframes for Login, Dashboard, Ranking and Optimizer. Do Phase 1 only. Do not use Streamlit. Never write a real credential into any file.`
2. `Implement Phase 2: src/db/mongo.py (MongoClient from env, ping, ensure_indexes, jsonSchema validators), repositories with owner filtering, users collection, JWT register/login/refresh/logout, bcrypt, login rate limiting and lockout, audit log, and /api/health. Tests must use MONGODB_TEST_DB_NAME and clean up.`
3. `Implement Phase 3: scripts/seed.py (admin, demo planner, 15-18 crops, 10 years of monthly synthetic prices, economics, demo farms; label as illustrative) and the CRUD APIs with Pydantic validation per 7.8, audit logging and CSV import with row-level error reports.`
4. `Implement Phase 4: soil.py, scoring.py, ahp.py and topsis.py per 7.1 to 7.4 with hand-calculated unit tests (textbook AHP and TOPSIS examples).`
5. `Implement Phase 5: sensitivity.py per 7.5 (one-at-a-time sweeps, Dirichlet Monte Carlo, rank-probability matrix) with reproducible seeds and tests.`
6. `Implement Phase 6: optimizer.py (PuLP LP/MILP and SciPy mean-variance with efficient frontier and shadow prices), feasibility.py with constraint-relaxation diagnostics, diversification.py (HHI, effective crops, entropy), per 7.6 with tests.`
7. `Implement Phase 7: scenarios.py and simulation.py per 7.7 (bootstrap and lognormal Monte Carlo, VaR, expected shortfall) with tests.`
8. `Implement Phase 8: all FastAPI routers in Section 11 with field-level error format, owner scoping, role guards, exports (CSV, Excel) and PDF report generation, plus API tests.`
9. `Implement Phase 9: the frontend foundation in frontend/ with React 18, TypeScript, Vite, Tailwind, shadcn/ui, lucide-react, TanStack Query/Table, React Hook Form + Zod, framer-motion, sonner and cmdk. Apply the light design tokens from Section 12.1 exactly. Build the app shell (sidebar, top bar with farm selector, command palette, notifications, user menu), the Login, Register and Forgot/Reset screens with the split layout from 12.4, route guards and a typed API client reading VITE_API_BASE_URL.`
10. `Implement Phase 10: Dashboard, Farms, Crop Library, Economics and Prices (inline editing, CSV import preview), Criteria (WeightSliders and AhpMatrixGrid with consistency gauge) and Ranking (RankingLeaderboard, RadarProfile, explanation drawer, TornadoChart and RankProbabilityHeatmap) with loading, empty and error states.`
11. `Implement Phase 11: Portfolio Optimizer page (constraint form, feasibility messages, AllocationDonut/Treemap, gauges, efficient frontier, baselines), Scenarios, Simulation (HistogramWithVaR), Reports, Data Import, Admin (users, audit log), Profile, About and Landing pages, plus the stepper wizard that links Farm -> Criteria -> Ranking -> Optimize -> Scenarios -> Report.`
12. `Finish tests (backend coverage 70%+, Vitest component tests, optional Playwright journey), responsive and accessibility polish (contrast, keyboard, reduced motion), README with MongoDB Atlas and .env instructions and troubleshooting, optional docker-compose.yml, and a demo script.`

## 20. References (starting points)

- Saaty, T.L. (1980): The Analytic Hierarchy Process (scale, consistency ratio, random index)
- Hwang & Yoon (1981): Multiple Attribute Decision Making (TOPSIS)
- Markowitz, H. (1952): Portfolio Selection (mean-variance); Herfindahl-Hirschman index for concentration
- FAO (1976, 2007): A framework for land evaluation; FAO ECOCROP crop requirements database
- Triantaphyllou: Multi-Criteria Decision Making Methods (sensitivity analysis, rank reversal)
- Documentation: MongoDB Atlas and PyMongo, FastAPI, pydantic-settings, PuLP/CBC, SciPy optimize, React, Vite, Tailwind CSS, shadcn/ui, Radix UI, Recharts, TanStack Table/Query, Agmarknet / data.gov.in, CACP cost of cultivation reports, state agricultural university package of practices
