import os
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import math
import random
from datetime import datetime, timezone
import bcrypt
import numpy as np
from config import get_settings
from db.mongo import get_db, ensure_indexes
from db.repositories.user_repo import UserRepository
from db.repositories.crop_repo import CropRepository
from db.repositories.price_repo import PriceRepository
from db.repositories.farm_repo import FarmRepository
from db.repositories.criteria_repo import CriteriaRepository
from db.repositories.ranking_repo import RankingRepository
from db.repositories.optimizer_repo import OptimizerRepository
from db.repositories.scenario_repo import ScenarioRepository
from core.scoring import compute_crop_criteria
from core.topsis import run_topsis
from core.optimizer import solve_portfolio_optimization
from core.sensitivity import run_sensitivity_analysis

SEED_DISCLAIMER = "illustrative demo values: verify with official sources before real use"


def hash_pwd(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


CROPS_SEED_DATA = [
    {
        "name": "Rice",
        "category": "Cereals",
        "seasons": ["kharif", "rabi"],
        "duration_days": 125,
        "water_req_mm": 1200,
        "labour_person_days_ha": 65,
        "typical_yield_t_ha": 4.5,
        "cost_per_ha": 42000,
        "base_price": 2350,
        "msp": 2300,
        "price_volatility": 0.12,
        "soil": {
            "ph": {"abs_min": 5.0, "opt_min": 5.5, "opt_max": 7.0, "abs_max": 8.5},
            "ec": {"abs_min": 0.0, "opt_min": 0.0, "opt_max": 2.0, "abs_max": 4.0},
            "oc": {"abs_min": 0.3, "opt_min": 0.6, "opt_max": 1.8, "abs_max": 3.5},
            "texture_suitability": {"clay": 0.95, "clay_loam": 1.0, "loam": 0.9, "sandy_loam": 0.6, "sandy": 0.3},
            "drainage_suitability": {"poor": 0.85, "moderate": 0.95, "good": 0.8, "excessive": 0.4}
        }
    },
    {
        "name": "Wheat",
        "category": "Cereals",
        "seasons": ["rabi"],
        "duration_days": 120,
        "water_req_mm": 450,
        "labour_person_days_ha": 40,
        "typical_yield_t_ha": 4.2,
        "cost_per_ha": 35000,
        "base_price": 2400,
        "msp": 2275,
        "price_volatility": 0.10,
        "soil": {
            "ph": {"abs_min": 5.5, "opt_min": 6.2, "opt_max": 7.5, "abs_max": 8.5},
            "ec": {"abs_min": 0.0, "opt_min": 0.0, "opt_max": 1.8, "abs_max": 3.5},
            "oc": {"abs_min": 0.3, "opt_min": 0.5, "opt_max": 1.5, "abs_max": 3.0},
            "texture_suitability": {"loam": 1.0, "clay_loam": 0.95, "sandy_loam": 0.85, "clay": 0.7, "sandy": 0.4},
            "drainage_suitability": {"good": 1.0, "moderate": 0.85, "poor": 0.3, "excessive": 0.6}
        }
    },
    {
        "name": "Maize",
        "category": "Cereals",
        "seasons": ["kharif", "rabi"],
        "duration_days": 105,
        "water_req_mm": 500,
        "labour_person_days_ha": 38,
        "typical_yield_t_ha": 5.0,
        "cost_per_ha": 32000,
        "base_price": 2200,
        "msp": 2090,
        "price_volatility": 0.14,
        "soil": {
            "ph": {"abs_min": 5.2, "opt_min": 6.0, "opt_max": 7.2, "abs_max": 8.2},
            "ec": {"abs_min": 0.0, "opt_min": 0.0, "opt_max": 1.5, "abs_max": 3.0},
            "oc": {"abs_min": 0.25, "opt_min": 0.5, "opt_max": 1.5, "abs_max": 3.0},
            "texture_suitability": {"loam": 1.0, "sandy_loam": 0.95, "clay_loam": 0.85, "sandy": 0.5, "clay": 0.6},
            "drainage_suitability": {"good": 1.0, "moderate": 0.85, "poor": 0.2, "excessive": 0.7}
        }
    },
    {
        "name": "Groundnut",
        "category": "Oilseeds",
        "seasons": ["kharif", "rabi"],
        "duration_days": 115,
        "water_req_mm": 450,
        "labour_person_days_ha": 45,
        "typical_yield_t_ha": 2.2,
        "cost_per_ha": 38000,
        "base_price": 6400,
        "msp": 6783,
        "price_volatility": 0.16,
        "soil": {
            "ph": {"abs_min": 5.3, "opt_min": 6.0, "opt_max": 7.0, "abs_max": 8.0},
            "ec": {"abs_min": 0.0, "opt_min": 0.0, "opt_max": 1.2, "abs_max": 2.5},
            "oc": {"abs_min": 0.2, "opt_min": 0.45, "opt_max": 1.2, "abs_max": 2.5},
            "texture_suitability": {"sandy_loam": 1.0, "loam": 0.9, "sandy": 0.8, "clay_loam": 0.7, "clay": 0.4},
            "drainage_suitability": {"good": 1.0, "moderate": 0.8, "excessive": 0.75, "poor": 0.2}
        }
    },
    {
        "name": "Cotton",
        "category": "Commercial",
        "seasons": ["kharif"],
        "duration_days": 160,
        "water_req_mm": 700,
        "labour_person_days_ha": 55,
        "typical_yield_t_ha": 2.0,
        "cost_per_ha": 48000,
        "base_price": 7200,
        "msp": 7121,
        "price_volatility": 0.22,
        "soil": {
            "ph": {"abs_min": 5.8, "opt_min": 6.5, "opt_max": 8.0, "abs_max": 8.8},
            "ec": {"abs_min": 0.0, "opt_min": 0.0, "opt_max": 2.5, "abs_max": 4.5},
            "oc": {"abs_min": 0.3, "opt_min": 0.5, "opt_max": 1.5, "abs_max": 3.0},
            "texture_suitability": {"clay": 0.95, "clay_loam": 1.0, "loam": 0.9, "sandy_loam": 0.7, "sandy": 0.4},
            "drainage_suitability": {"good": 1.0, "moderate": 0.9, "poor": 0.3, "excessive": 0.6}
        }
    },
    {
        "name": "Sugarcane",
        "category": "Commercial",
        "seasons": ["kharif"],
        "duration_days": 330,
        "water_req_mm": 1800,
        "labour_person_days_ha": 95,
        "typical_yield_t_ha": 95.0,
        "cost_per_ha": 115000,
        "base_price": 340,
        "msp": 315,
        "price_volatility": 0.08,
        "soil": {
            "ph": {"abs_min": 5.5, "opt_min": 6.5, "opt_max": 7.5, "abs_max": 8.5},
            "ec": {"abs_min": 0.0, "opt_min": 0.0, "opt_max": 2.0, "abs_max": 4.0},
            "oc": {"abs_min": 0.4, "opt_min": 0.7, "opt_max": 2.0, "abs_max": 3.5},
            "texture_suitability": {"loam": 1.0, "clay_loam": 0.95, "clay": 0.85, "sandy_loam": 0.75, "sandy": 0.4},
            "drainage_suitability": {"good": 1.0, "moderate": 0.9, "poor": 0.4, "excessive": 0.5}
        }
    },
    {
        "name": "Banana",
        "category": "Horticulture",
        "seasons": ["kharif"],
        "duration_days": 320,
        "water_req_mm": 1600,
        "labour_person_days_ha": 90,
        "typical_yield_t_ha": 45.0,
        "cost_per_ha": 140000,
        "base_price": 1800,
        "msp": 0,
        "price_volatility": 0.24,
        "soil": {
            "ph": {"abs_min": 5.5, "opt_min": 6.5, "opt_max": 7.5, "abs_max": 8.2},
            "ec": {"abs_min": 0.0, "opt_min": 0.0, "opt_max": 1.5, "abs_max": 3.0},
            "oc": {"abs_min": 0.4, "opt_min": 0.8, "opt_max": 2.2, "abs_max": 4.0},
            "texture_suitability": {"clay_loam": 1.0, "loam": 0.95, "sandy_loam": 0.8, "clay": 0.7, "sandy": 0.4},
            "drainage_suitability": {"good": 1.0, "moderate": 0.85, "poor": 0.2, "excessive": 0.6}
        }
    },
    {
        "name": "Tomato",
        "category": "Horticulture",
        "seasons": ["kharif", "rabi"],
        "duration_days": 110,
        "water_req_mm": 600,
        "labour_person_days_ha": 80,
        "typical_yield_t_ha": 25.0,
        "cost_per_ha": 58000,
        "base_price": 1800,
        "msp": 0,
        "price_volatility": 0.35,
        "soil": {
            "ph": {"abs_min": 5.5, "opt_min": 6.2, "opt_max": 7.2, "abs_max": 8.0},
            "ec": {"abs_min": 0.0, "opt_min": 0.0, "opt_max": 1.8, "abs_max": 3.2},
            "oc": {"abs_min": 0.3, "opt_min": 0.6, "opt_max": 1.8, "abs_max": 3.0},
            "texture_suitability": {"loam": 1.0, "sandy_loam": 0.95, "clay_loam": 0.85, "sandy": 0.6, "clay": 0.5},
            "drainage_suitability": {"good": 1.0, "moderate": 0.85, "poor": 0.2, "excessive": 0.7}
        }
    },
    {
        "name": "Onion",
        "category": "Horticulture",
        "seasons": ["kharif", "rabi"],
        "duration_days": 130,
        "water_req_mm": 550,
        "labour_person_days_ha": 75,
        "typical_yield_t_ha": 18.0,
        "cost_per_ha": 52000,
        "base_price": 2200,
        "msp": 0,
        "price_volatility": 0.38,
        "soil": {
            "ph": {"abs_min": 5.8, "opt_min": 6.5, "opt_max": 7.5, "abs_max": 8.2},
            "ec": {"abs_min": 0.0, "opt_min": 0.0, "opt_max": 1.2, "abs_max": 2.5},
            "oc": {"abs_min": 0.3, "opt_min": 0.6, "opt_max": 1.5, "abs_max": 3.0},
            "texture_suitability": {"sandy_loam": 1.0, "loam": 0.95, "clay_loam": 0.75, "sandy": 0.65, "clay": 0.4},
            "drainage_suitability": {"good": 1.0, "moderate": 0.8, "poor": 0.2, "excessive": 0.7}
        }
    },
    {
        "name": "Chilli",
        "category": "Spices",
        "seasons": ["kharif", "rabi"],
        "duration_days": 150,
        "water_req_mm": 650,
        "labour_person_days_ha": 85,
        "typical_yield_t_ha": 2.5,
        "cost_per_ha": 65000,
        "base_price": 16500,
        "msp": 0,
        "price_volatility": 0.28,
        "soil": {
            "ph": {"abs_min": 5.5, "opt_min": 6.2, "opt_max": 7.2, "abs_max": 8.0},
            "ec": {"abs_min": 0.0, "opt_min": 0.0, "opt_max": 1.5, "abs_max": 3.0},
            "oc": {"abs_min": 0.3, "opt_min": 0.6, "opt_max": 1.6, "abs_max": 3.0},
            "texture_suitability": {"loam": 1.0, "sandy_loam": 0.95, "clay_loam": 0.85, "clay": 0.6, "sandy": 0.5},
            "drainage_suitability": {"good": 1.0, "moderate": 0.85, "poor": 0.2, "excessive": 0.7}
        }
    },
    {
        "name": "Turmeric",
        "category": "Spices",
        "seasons": ["kharif"],
        "duration_days": 240,
        "water_req_mm": 1100,
        "labour_person_days_ha": 95,
        "typical_yield_t_ha": 5.5,
        "cost_per_ha": 98000,
        "base_price": 11200,
        "msp": 0,
        "price_volatility": 0.26,
        "soil": {
            "ph": {"abs_min": 5.5, "opt_min": 6.0, "opt_max": 7.2, "abs_max": 8.0},
            "ec": {"abs_min": 0.0, "opt_min": 0.0, "opt_max": 1.5, "abs_max": 3.0},
            "oc": {"abs_min": 0.4, "opt_min": 0.75, "opt_max": 2.0, "abs_max": 3.5},
            "texture_suitability": {"loam": 1.0, "clay_loam": 0.95, "sandy_loam": 0.85, "clay": 0.7, "sandy": 0.4},
            "drainage_suitability": {"good": 1.0, "moderate": 0.85, "poor": 0.2, "excessive": 0.65}
        }
    },
    {
        "name": "Ragi (Finger Millet)",
        "category": "Millets",
        "seasons": ["kharif", "rabi"],
        "duration_days": 105,
        "water_req_mm": 350,
        "labour_person_days_ha": 35,
        "typical_yield_t_ha": 2.8,
        "cost_per_ha": 24000,
        "base_price": 3800,
        "msp": 4290,
        "price_volatility": 0.11,
        "soil": {
            "ph": {"abs_min": 5.0, "opt_min": 5.8, "opt_max": 7.5, "abs_max": 8.5},
            "ec": {"abs_min": 0.0, "opt_min": 0.0, "opt_max": 2.2, "abs_max": 4.5},
            "oc": {"abs_min": 0.15, "opt_min": 0.4, "opt_max": 1.2, "abs_max": 2.5},
            "texture_suitability": {"sandy_loam": 1.0, "loam": 0.95, "clay_loam": 0.8, "sandy": 0.75, "clay": 0.6},
            "drainage_suitability": {"good": 1.0, "moderate": 0.9, "excessive": 0.85, "poor": 0.3}
        }
    },
    {
        "name": "Sorghum",
        "category": "Millets",
        "seasons": ["kharif", "rabi"],
        "duration_days": 110,
        "water_req_mm": 400,
        "labour_person_days_ha": 35,
        "typical_yield_t_ha": 2.6,
        "cost_per_ha": 22000,
        "base_price": 3200,
        "msp": 3371,
        "price_volatility": 0.12,
        "soil": {
            "ph": {"abs_min": 5.2, "opt_min": 6.0, "opt_max": 7.8, "abs_max": 8.5},
            "ec": {"abs_min": 0.0, "opt_min": 0.0, "opt_max": 2.0, "abs_max": 4.0},
            "oc": {"abs_min": 0.2, "opt_min": 0.45, "opt_max": 1.4, "abs_max": 2.8},
            "texture_suitability": {"clay": 0.9, "clay_loam": 1.0, "loam": 0.95, "sandy_loam": 0.8, "sandy": 0.5},
            "drainage_suitability": {"good": 1.0, "moderate": 0.9, "poor": 0.4, "excessive": 0.7}
        }
    },
    {
        "name": "Blackgram",
        "category": "Pulses",
        "seasons": ["kharif", "rabi"],
        "duration_days": 75,
        "water_req_mm": 300,
        "labour_person_days_ha": 28,
        "typical_yield_t_ha": 1.1,
        "cost_per_ha": 21000,
        "base_price": 7600,
        "msp": 7400,
        "price_volatility": 0.15,
        "soil": {
            "ph": {"abs_min": 5.5, "opt_min": 6.2, "opt_max": 7.5, "abs_max": 8.2},
            "ec": {"abs_min": 0.0, "opt_min": 0.0, "opt_max": 1.5, "abs_max": 3.0},
            "oc": {"abs_min": 0.25, "opt_min": 0.5, "opt_max": 1.4, "abs_max": 2.8},
            "texture_suitability": {"loam": 1.0, "clay_loam": 0.95, "sandy_loam": 0.85, "clay": 0.7, "sandy": 0.5},
            "drainage_suitability": {"good": 1.0, "moderate": 0.85, "poor": 0.25, "excessive": 0.7}
        }
    },
    {
        "name": "Greengram",
        "category": "Pulses",
        "seasons": ["kharif", "zaid"],
        "duration_days": 70,
        "water_req_mm": 280,
        "labour_person_days_ha": 26,
        "typical_yield_t_ha": 1.0,
        "cost_per_ha": 19500,
        "base_price": 8200,
        "msp": 8682,
        "price_volatility": 0.14,
        "soil": {
            "ph": {"abs_min": 5.5, "opt_min": 6.2, "opt_max": 7.5, "abs_max": 8.2},
            "ec": {"abs_min": 0.0, "opt_min": 0.0, "opt_max": 1.5, "abs_max": 2.8},
            "oc": {"abs_min": 0.25, "opt_min": 0.5, "opt_max": 1.4, "abs_max": 2.8},
            "texture_suitability": {"loam": 1.0, "sandy_loam": 0.95, "clay_loam": 0.85, "sandy": 0.55, "clay": 0.6},
            "drainage_suitability": {"good": 1.0, "moderate": 0.85, "poor": 0.25, "excessive": 0.75}
        }
    },
    {
        "name": "Sunflower",
        "category": "Oilseeds",
        "seasons": ["kharif", "rabi"],
        "duration_days": 95,
        "water_req_mm": 400,
        "labour_person_days_ha": 35,
        "typical_yield_t_ha": 1.8,
        "cost_per_ha": 28000,
        "base_price": 5400,
        "msp": 7280,
        "price_volatility": 0.18,
        "soil": {
            "ph": {"abs_min": 5.5, "opt_min": 6.2, "opt_max": 7.8, "abs_max": 8.5},
            "ec": {"abs_min": 0.0, "opt_min": 0.0, "opt_max": 1.8, "abs_max": 3.5},
            "oc": {"abs_min": 0.25, "opt_min": 0.5, "opt_max": 1.5, "abs_max": 3.0},
            "texture_suitability": {"loam": 1.0, "sandy_loam": 0.9, "clay_loam": 0.9, "clay": 0.75, "sandy": 0.5},
            "drainage_suitability": {"good": 1.0, "moderate": 0.9, "poor": 0.3, "excessive": 0.7}
        }
    }
]


def generate_synthetic_prices(base_price: float, volatility: float, years: int = 10) -> list:
    """Generates 120 monthly price observations with trend, seasonality and random walk."""
    prices = []
    current_price = base_price * 0.75  # 10 years ago was lower
    months = []
    for y in range(2015, 2015 + years):
        for m in range(1, 13):
            months.append(f"{y}-{m:02d}")

    for idx, m in enumerate(months):
        month_num = int(m.split("-")[1])
        # Seasonal swing +/- 8%
        seasonal = math.sin((month_num - 3) * math.pi / 6) * 0.08
        # Long-term inflation drift ~4% per year
        drift = 0.003
        # Stochastic shock
        shock = np.random.normal(0, volatility * 0.25)
        current_price = current_price * (1.0 + drift + shock)
        modal_price = round(max(50.0, current_price * (1.0 + seasonal)), 0)

        prices.append({
            "month": m,
            "modal_price_per_quintal": modal_price,
            "market": "APMC Central",
            "source": f"Synthetic Agmarknet Series ({SEED_DISCLAIMER})"
        })
    return prices


def seed_database():
    settings = get_settings()
    db = get_db()
    ensure_indexes(db)

    print("--- Seeding CropChoice Database ---")
    user_repo = UserRepository(db)
    crop_repo = CropRepository(db)
    price_repo = PriceRepository(db)
    farm_repo = FarmRepository(db)
    criteria_repo = CriteriaRepository(db)
    ranking_repo = RankingRepository(db)
    optimizer_repo = OptimizerRepository(db)
    scenario_repo = ScenarioRepository(db)

    # 1. Admin and Planner Users
    admin_user = user_repo.find_by_email(settings.ADMIN_EMAIL)
    if not admin_user:
        admin_pwd_hash = hash_pwd(settings.ADMIN_PASSWORD)
        admin_user = user_repo.create_user(
            name="CropChoice Admin",
            email=settings.ADMIN_EMAIL,
            password_hash=admin_pwd_hash,
            role="admin"
        )
        print(f"Created Admin: {settings.ADMIN_EMAIL}")
    else:
        print(f"Admin already exists: {settings.ADMIN_EMAIL}")

    admin_id = str(admin_user["_id"])

    planner_email = "planner@cropchoice.local"
    planner_user = user_repo.find_by_email(planner_email)
    if not planner_user:
        planner_pwd_hash = hash_pwd("Planner@2026!")
        planner_user = user_repo.create_user(
            name="Kavitha Raman (Agronomist)",
            email=planner_email,
            password_hash=planner_pwd_hash,
            role="planner"
        )
        print(f"Created Demo Planner: {planner_email}")
    planner_id = str(planner_user["_id"])

    # 2. Crops, Economics & 10 Years Prices
    crop_id_map = {}
    price_records_to_insert = []
    print(f"Seeding {len(CROPS_SEED_DATA)} crop profiles and 10-year monthly prices...")

    for cdata in CROPS_SEED_DATA:
        existing = crop_repo.get_by_name(cdata["name"])
        if not existing:
            created = crop_repo.create_crop({
                "name": cdata["name"],
                "category": cdata["category"],
                "seasons": cdata["seasons"],
                "duration_days": cdata["duration_days"],
                "water_req_mm": cdata["water_req_mm"],
                "labour_person_days_ha": cdata["labour_person_days_ha"],
                "typical_yield_t_ha": cdata["typical_yield_t_ha"],
                "soil": cdata["soil"],
                "active": True,
                "source_note": f"ICAR Package of Practices ({SEED_DISCLAIMER})"
            }, user_id=admin_id)
            cid = created["id"]
        else:
            cid = existing["id"]

        crop_id_map[cdata["name"]] = cid

        # Economics
        crop_repo.upsert_economics({
            "crop_id": cid,
            "crop_name": cdata["name"],
            "region": "South India",
            "season": "kharif",
            "cost_per_ha": cdata["cost_per_ha"],
            "expected_yield_t_ha": cdata["typical_yield_t_ha"],
            "msp_per_quintal": cdata["msp"],
            "year": 2025,
            "notes": f"CACP benchmark ({SEED_DISCLAIMER})"
        })

        # Synthetic 10-year monthly prices
        prices = generate_synthetic_prices(cdata["base_price"], cdata["price_volatility"])
        for p in prices:
            p["crop_id"] = cid
            p["crop_name"] = cdata["name"]
            price_records_to_insert.append(p)

    price_repo.bulk_upsert(price_records_to_insert)
    print(f"Seeded {len(price_records_to_insert)} price points across 10 years.")

    # 3. Demo Farms
    farms_data = [
        {
            "name": "Green Valley Integrated Farm",
            "location": {"state": "Tamil Nadu", "district": "Coimbatore", "lat": 11.0168, "lon": 76.9558},
            "land_ha": 6.0,
            "season": "kharif",
            "soil": {"ph": 6.8, "ec": 0.5, "oc": 0.85, "n": 290, "p": 24, "k": 320, "texture": "loam", "drainage": "good"},
            "water": {"rainfall_mm": 680, "effective_rainfall_pct": 70, "irrigation_m3": 22000},
            "budget_inr": 420000,
            "labour_person_days": 380
        },
        {
            "name": "Cauvery Delta Agri-Zone",
            "location": {"state": "Tamil Nadu", "district": "Thanjavur", "lat": 10.7870, "lon": 79.1378},
            "land_ha": 10.0,
            "season": "kharif",
            "soil": {"ph": 7.4, "ec": 0.9, "oc": 0.70, "n": 260, "p": 18, "k": 290, "texture": "clay_loam", "drainage": "moderate"},
            "water": {"rainfall_mm": 750, "effective_rainfall_pct": 75, "irrigation_m3": 35000},
            "budget_inr": 650000,
            "labour_person_days": 550
        },
        {
            "name": "Deccan Semi-Arid Holding",
            "location": {"state": "Karnataka", "district": "Raichur", "lat": 16.2120, "lon": 77.3439},
            "land_ha": 5.0,
            "season": "kharif",
            "soil": {"ph": 7.8, "ec": 0.8, "oc": 0.40, "n": 180, "p": 12, "k": 210, "texture": "sandy_loam", "drainage": "good"},
            "water": {"rainfall_mm": 420, "effective_rainfall_pct": 60, "irrigation_m3": 12000},
            "budget_inr": 250000,
            "labour_person_days": 240
        }
    ]

    farm_ids = []
    for f in farms_data:
        existing_farms = farm_repo.list_farms(planner_id)
        match = next((x for x in existing_farms if x["name"] == f["name"]), None)
        if not match:
            created = farm_repo.create_farm(f, owner_id=planner_id)
            farm_ids.append(created["id"])
        else:
            farm_ids.append(match["id"])

    main_farm_id = farm_ids[0]
    print(f"Demo farms created: {len(farm_ids)}")

    # 4. Criteria Profiles
    criteria_presets = [
        {"name": "Balanced Decision Profile", "weights": {"water": 0.25, "soil": 0.25, "return": 0.25, "variability": 0.25}},
        {"name": "Water-Saving & Conservation", "weights": {"water": 0.50, "soil": 0.20, "return": 0.20, "variability": 0.10}},
        {"name": "Profit-First Strategy", "weights": {"water": 0.10, "soil": 0.20, "return": 0.60, "variability": 0.10}},
        {"name": "Low Market Risk", "weights": {"water": 0.20, "soil": 0.20, "return": 0.20, "variability": 0.40}}
    ]

    profile_id = None
    for cp in criteria_presets:
        created = criteria_repo.create_profile(cp, owner_id=planner_id)
        if not profile_id:
            profile_id = created["id"]

    # 5. Execute initial Ranking, Sensitivity & Portfolio Optimization
    main_farm = farm_repo.get_by_id(main_farm_id)
    all_crops = crop_repo.list_crops()
    all_econ = {e["crop_id"]: e for e in crop_repo.list_all_economics()}
    price_stats_map = {c["id"]: price_repo.get_crop_stats(c["id"]) for c in all_crops}

    # Evaluate
    evaluations = []
    for crop in all_crops:
        cid = crop["id"]
        econ = all_econ.get(cid)
        p_stats = price_stats_map.get(cid)
        eval_item = compute_crop_criteria(crop, main_farm, econ, p_stats)
        evaluations.append(eval_item)

    default_weights = {"water": 0.25, "soil": 0.25, "return": 0.25, "variability": 0.25}
    ranking_res = run_topsis(evaluations, default_weights)

    saved_ranking = ranking_repo.save_ranking({
        "farm_id": main_farm_id,
        "farm_name": main_farm["name"],
        "profile_id": profile_id,
        "profile_name": "Balanced Decision Profile",
        "inputs_snapshot": {"weights": default_weights},
        "results": ranking_res["results"],
        "rank_correlation": ranking_res["rank_correlation"],
        "weights": default_weights
    }, owner_id=planner_id)

    ranking_id = saved_ranking["id"]
    print("Initial TOPSIS ranking seeded.")

    # Sensitivity
    sens_res = run_sensitivity_analysis(evaluations, default_weights)
    ranking_repo.save_sensitivity(ranking_id, sens_res)
    print("Sensitivity analysis & Dirichlet Monte Carlo seeded.")

    # 6. Portfolio Optimization
    closeness_map = {r["crop_id"]: r["closeness"] for r in ranking_res["results"]}
    eligible_crops = [e for e in evaluations if not e.get("is_excluded", False)]

    limits = {
        "land_ha": main_farm["land_ha"],
        "water_m3": main_farm["water"]["irrigation_m3"],
        "budget_inr": main_farm["budget_inr"],
        "labour": main_farm["labour_person_days"]
    }
    opt_params = {
        "objective": "max_return",
        "max_share": 0.40,
        "min_crops": 3,
        "min_area": 0.5,
        "use_all_land": True
    }

    opt_result = solve_portfolio_optimization(eligible_crops, closeness_map, limits, opt_params)

    saved_opt = optimizer_repo.save_optimization({
        "farm_id": main_farm_id,
        "farm_name": main_farm["name"],
        "ranking_id": ranking_id,
        "objective": "max_return",
        "status": opt_result["status"],
        "allocation": opt_result["allocation"],
        "totals": opt_result["totals"],
        "utilisation": opt_result["utilisation"],
        "diversification": opt_result["diversification"],
        "risk": opt_result["risk"],
        "shadow_prices": opt_result["shadow_prices"],
        "feasibility_report": opt_result["feasibility_report"],
        "baselines": opt_result["baselines"],
        "efficient_frontier": opt_result["efficient_frontier"]
    }, owner_id=planner_id)
    opt_id = saved_opt["id"]
    print(f"Initial Portfolio Optimization seeded (Allocations: {len(opt_result['allocation'])} crops).")

    # 7. Scenarios
    scenarios_templates = [
        {
            "name": "Severe Drought Shock (-35% Water)",
            "description": "Simulates 35% decline in irrigation and rainfall during dry spell.",
            "modifications": {"irrigation_pct": -35.0, "rainfall_pct": -30.0},
            "summary": {"net_return": 185000, "water_m3": 14300, "effective_crops": 2.8, "top_crops": ["Maize", "Ragi", "Groundnut"], "feasible": True}
        },
        {
            "name": "Vegetable & Mandi Price Slump (-25% Prices)",
            "description": "Examines vulnerability against a 25% drop in market modal prices.",
            "modifications": {"price_pct": -25.0},
            "summary": {"net_return": 162000, "water_m3": 19500, "effective_crops": 3.1, "top_crops": ["Groundnut", "Rice", "Turmeric"], "feasible": True}
        },
        {
            "name": "Enhanced Working Capital (+25% Budget)",
            "description": "Assesses return upside with ₹5.25L expanded credit line.",
            "modifications": {"budget_pct": 25.0},
            "summary": {"net_return": 268000, "water_m3": 21800, "effective_crops": 3.4, "top_crops": ["Turmeric", "Tomato", "Chilli"], "feasible": True}
        }
    ]

    for sc in scenarios_templates:
        scenario_repo.save_scenario({
            "farm_id": main_farm_id,
            "farm_name": main_farm["name"],
            "name": sc["name"],
            "description": sc["description"],
            "base_optimization_id": opt_id,
            "modifications": sc["modifications"],
            "result_optimization_id": opt_id,
            "summary": sc["summary"]
        }, owner_id=planner_id)

    print("Scenarios seeded.")
    print("Database seeding complete!")


if __name__ == "__main__":
    seed_database()
