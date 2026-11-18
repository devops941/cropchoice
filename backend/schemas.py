from typing import List, Dict, Any, Optional
import re
from pydantic import BaseModel, Field, field_validator


def _clean_email(v: str) -> str:
    v = v.strip().lower()
    if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', v):
        raise ValueError("Invalid email format.")
    return v


# Auth Schemas
class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=6, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return _clean_email(v)


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return _clean_email(v)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


class RefreshRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6)


class ForgotPasswordRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return _clean_email(v)


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6)


# Farm Schemas
class SoilData(BaseModel):
    ph: float = 6.8
    ec: float = 0.6
    oc: float = 0.75
    n: float = 280.0
    p: float = 22.0
    k: float = 310.0
    texture: str = "loam"
    drainage: str = "good"


class WaterData(BaseModel):
    rainfall_mm: float = 650.0
    effective_rainfall_pct: float = 70.0
    irrigation_m3: float = 18000.0


class FarmCreateRequest(BaseModel):
    name: str
    location: Optional[Dict[str, Any]] = None
    land_ha: float = 5.0
    season: str = "kharif"
    soil: SoilData
    water: WaterData
    budget_inr: float = 350000.0
    labour_person_days: float = 300.0


# Crop Schemas
class CropCreateRequest(BaseModel):
    name: str
    category: str = "Cereals"
    seasons: List[str] = ["kharif", "rabi"]
    duration_days: int = 120
    water_req_mm: float = 500.0
    labour_person_days_ha: float = 45.0
    typical_yield_t_ha: float = 3.5
    soil: Dict[str, Any] = {}
    active: bool = True
    source_note: Optional[str] = None


# Price Schemas
class PriceCreateRequest(BaseModel):
    crop_id: str
    crop_name: Optional[str] = None
    market: str = "APMC Central"
    month: str
    modal_price_per_quintal: float
    source: Optional[str] = None


# Criteria & AHP Schemas
class AhpComputeRequest(BaseModel):
    matrix: List[List[float]]
    criteria_names: List[str] = ["water", "soil", "return", "variability"]


class CriteriaProfileCreate(BaseModel):
    name: str
    mode: str = "direct"
    criteria: List[str] = ["water", "soil", "return", "variability"]
    weights: Dict[str, float]
    ahp_matrix: Optional[List[List[float]]] = None
    ahp_cr: Optional[float] = None


# Ranking Schemas
class RankingRunRequest(BaseModel):
    farm_id: str
    weights: Dict[str, float]
    profile_id: Optional[str] = None
    profile_name: Optional[str] = None
    use_wsr: bool = False


# Optimizer Schemas
class OptimizationRunRequest(BaseModel):
    farm_id: str
    ranking_id: Optional[str] = None
    objective: str = "max_return"
    max_share: float = 0.40
    min_crops: int = 2
    min_area: float = 0.4
    use_all_land: bool = True
    target_return: float = 150000.0
    risk_weight: float = 0.5
    forced_min_areas: Dict[str, float] = {}


# Scenario Schemas
class ScenarioCreateRequest(BaseModel):
    farm_id: str
    name: str
    description: str = ""
    base_optimization_id: Optional[str] = None
    modifications: Dict[str, Any] = {}


# Simulation Schemas
class SimulationRunRequest(BaseModel):
    optimization_id: str
    n_runs: int = 5000
    seed: int = 42
    method: str = "bootstrap"
