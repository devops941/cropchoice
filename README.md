# 🌱 CropChoice 2026 — Intelligent Crop Decision Support & Portfolio Optimization

> **Enterprise-Grade Agricultural Decision Support System** combining FAO ECOCROP soil suitability modeling, Analytic Hierarchy Process (AHP), TOPSIS multi-criteria ranking, and SciPy HiGHS Mixed-Integer Linear Programming (MILP) portfolio optimization with SLSQP Mean-Variance Efficient Frontier and 5,000-trial Monte Carlo VaR simulations.

---

## 📁 Clean Repository Structure

The project code is organized strictly into **two clean, self-contained directories**:

```
cropchoice/
├── backend/                  # Complete Python FastAPI backend & decision engines
│   ├── core/                 # Mathematical engines (AHP, TOPSIS, MILP, VaR, Soil Fit)
│   ├── db/                   # MongoDB Atlas connection & 11 PyMongo repositories
│   ├── routers/              # 13 REST API endpoints (/api/...)
│   ├── imports/              # CSV/Excel parsing and validator
│   ├── config/               # Presets & criteria YAML definitions
│   ├── data/                 # Sample CSV templates (soil, crops, prices, farms)
│   ├── outputs/              # Exported audit reports & logs
│   ├── scripts/              # Database seed script (seed.py)
│   ├── tests/                # PyTest test suite (9 test suites)
│   ├── config.py             # Fail-fast pydantic-settings configuration
│   ├── main.py               # FastAPI application entry point
│   ├── requirements.txt      # Python dependencies
│   └── .env                  # MongoDB Atlas URI & secrets
│
├── frontend/                 # Complete React 18 + Vite + Tailwind CSS frontend
│   ├── src/
│   │   ├── components/       # 2026 Trend Design UI components (Strictly NO Blue)
│   │   ├── context/          # AuthContext & FarmContext state managers
│   │   ├── pages/            # 16 complete application views
│   │   ├── services/         # Axios API client (/api/...)
│   │   └── types/            # TypeScript domain interfaces
│   ├── package.json          # Dependencies (Lucide-React, Recharts, Tailwind)
│   └── vite.config.ts        # Vite configuration with /api proxy to 8000
│
├── README.md                 # Project documentation & run guide
└── PROJECT_SPEC_CROPCHOICE.md# Detailed project engineering specification
```

---

## 🚀 How to Run the Project

### 1. Start the Backend

Open a terminal and navigate to the `backend/` folder:

```bash
cd backend

# 1. Install dependencies (if not already installed)
pip install -r requirements.txt

# 2. (Optional) Re-seed MongoDB Atlas with 16 crops, 10-yr mandi prices, and demo farms
python scripts/seed.py

# 3. Start the FastAPI backend server
uvicorn main:app --reload --port 8000
```

- **API Documentation (Swagger UI)**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/api/health`

---

### 2. Start the Frontend

Open a second terminal and navigate to the `frontend/` folder:

```bash
cd frontend

# 1. Install frontend packages (if not already done)
npm install

# 2. Start the Vite development server
npm run dev
```

- **Web Application URL**: `http://localhost:5173`

---

## 🔑 Demo Login Credentials

The application includes convenient **1-Click Demo Login** buttons on the login screen, or you can log in manually:

| Role | Email | Password |
|---|---|---|
| **Administrator** | `admin@cropchoice.local` | `Admin@CropChoice2026!` |
| **Demo Planner** | `planner@cropchoice.local` | `Planner@CropChoice2026!` |

---

## 🎨 2026 Organic Agriculture Theme (Strictly NO Blue)

The design system adheres strictly to 2026 agricultural ergonomics with warm organic tones:
- **Forest & Emerald Green** (`#047857`, `#059669`): Primary growth, sustainability, high viability.
- **Warm Amber** (`#D97706`): Yields, moderate soil suitability, advisory highlights.
- **Terracotta Clay** (`#C2763F`): Soil health, organic carbon, land metrics.
- **Fresh Deep Mint / Teal** (`#0D9488`): Water allocation, irrigation demand (replaces blue).
- **Coral Rose** (`#E11D48`): Risk warnings, price volatility, water stress.

---

## 🧪 Running Automated Tests

Run the test suite directly inside the `backend/` directory:

```bash
cd backend
python -m pytest tests
```
*All 9 test suites cover trapezoidal soil membership, Saaty AHP consistency, TOPSIS rank validation, and HiGHS MILP portfolio optimization.*
