from typing import Dict, Any, List, Optional


class ValidationError(Exception):
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.field = field


def validate_soil_ranges(ph: Dict[str, float], ec: Dict[str, float], oc: Dict[str, float]):
    for name, r in [("pH", ph), ("EC", ec), ("OC", oc)]:
        amin = float(r.get("abs_min", 0))
        omin = float(r.get("opt_min", 0))
        omax = float(r.get("opt_max", 0))
        amax = float(r.get("abs_max", 0))
        if not (amin <= omin <= omax <= amax):
            raise ValidationError(
                f"Range ordering violation for {name}: abs_min ({amin}) <= opt_min ({omin}) <= opt_max ({omax}) <= abs_max ({amax}) must hold.",
                field=f"soil.{name.lower()}"
            )


def validate_crop_data(data: Dict[str, Any]):
    name = data.get("name")
    if not name or not str(name).strip():
        raise ValidationError("Crop name is required", field="name")

    water = float(data.get("water_req_mm", 0))
    if water < 50 or water > 5000:
        raise ValidationError("Crop water requirement must be between 50 and 5,000 mm", field="water_req_mm")

    duration = int(data.get("duration_days", 0))
    if duration < 30 or duration > 365:
        raise ValidationError("Crop duration must be between 30 and 365 days", field="duration_days")

    typical_yield = float(data.get("typical_yield_t_ha", 0))
    if typical_yield <= 0:
        raise ValidationError("Typical yield must be positive", field="typical_yield_t_ha")

    soil = data.get("soil", {})
    if "ph" in soil and "ec" in soil and "oc" in soil:
        validate_soil_ranges(soil["ph"], soil["ec"], soil["oc"])


def validate_farm_data(data: Dict[str, Any]):
    name = data.get("name")
    if not name or not str(name).strip():
        raise ValidationError("Farm name is required", field="name")

    land = float(data.get("land_ha", 0))
    if land <= 0 or land > 10000:
        raise ValidationError("Farm land area must be greater than 0 ha", field="land_ha")

    soil = data.get("soil", {})
    ph = float(soil.get("ph", 7.0))
    if ph < 3.0 or ph > 10.0:
        raise ValidationError("Soil pH must be between 3.0 and 10.0", field="soil.ph")

    ec = float(soil.get("ec", 0.0))
    if ec < 0.0 or ec > 20.0:
        raise ValidationError("Soil EC must be non-negative (0 - 20 dS/m)", field="soil.ec")

    oc = float(soil.get("oc", 0.0))
    if oc < 0.0 or oc > 10.0:
        raise ValidationError("Soil Organic Carbon must be between 0% and 10%", field="soil.oc")

    water = data.get("water", {})
    rainfall = float(water.get("rainfall_mm", 0))
    if rainfall < 0 or rainfall > 10000:
        raise ValidationError("Rainfall must be between 0 and 10,000 mm", field="water.rainfall_mm")

    irrigation = float(water.get("irrigation_m3", 0))
    if irrigation < 0:
        raise ValidationError("Irrigation volume must be non-negative", field="water.irrigation_m3")

    budget = float(data.get("budget_inr", 0))
    if budget < 0:
        raise ValidationError("Farm budget cannot be negative", field="budget_inr")


def validate_weights(weights: Dict[str, float]) -> Dict[str, float]:
    for k, v in weights.items():
        if v < 0:
            raise ValidationError(f"Weight for '{k}' cannot be negative", field=f"weights.{k}")
    tot = sum(weights.values())
    if tot <= 0:
        raise ValidationError("Total weights must sum to a positive value", field="weights")
    return {k: round(v / tot, 4) for k, v in weights.items()}
