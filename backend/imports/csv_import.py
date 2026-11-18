import io
import csv
from typing import List, Dict, Any, Tuple
import openpyxl
from core.validators import validate_crop_data, validate_farm_data, ValidationError


def validate_dict_rows(
    rows: List[Dict[str, Any]],
    kind: str
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Validates a list of dictionaries for 'crops', 'prices', 'economics', or 'farms'.
    Returns:
      - valid_rows: list of parsed records ready for insertion
      - errors: list of {row, column, message, suggestion}
    """
    valid_rows = []
    errors = []
    row_idx = 1

    for row in rows:
        row_idx += 1
        clean_row = {str(k).strip().lower(): str(v).strip() for k, v in row.items() if k is not None}

        try:
            if kind == "crops":
                record = parse_crop_row(clean_row, row_idx)
                valid_rows.append(record)
            elif kind == "prices":
                record = parse_price_row(clean_row, row_idx)
                valid_rows.append(record)
            elif kind == "economics":
                record = parse_economics_row(clean_row, row_idx)
                valid_rows.append(record)
            elif kind == "farms":
                record = parse_farm_row(clean_row, row_idx)
                valid_rows.append(record)
            else:
                errors.append({
                    "row": row_idx,
                    "column": "kind",
                    "message": f"Unsupported import kind '{kind}'",
                    "suggestion": "Select crops, prices, economics, or farms"
                })
        except ValidationError as ve:
            errors.append({
                "row": row_idx,
                "column": ve.field or "general",
                "message": ve.message,
                "suggestion": "Check standard ranges in sample template"
            })
        except Exception as e:
            errors.append({
                "row": row_idx,
                "column": "general",
                "message": str(e),
                "suggestion": "Verify data types and format"
            })

    return valid_rows, errors


def parse_and_validate_csv(
    content_str: str,
    kind: str
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Parses and validates CSV content.
    """
    reader = csv.DictReader(io.StringIO(content_str))
    if not reader.fieldnames:
        return [], [{"row": 0, "column": "header", "message": "CSV header is empty or missing", "suggestion": "Include headers in the first row"}]

    return validate_dict_rows(list(reader), kind)


def parse_and_validate_excel(
    content_bytes: bytes,
    kind: str
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Parses and validates Excel (.xlsx / .xls) content using openpyxl.
    """
    try:
        wb = openpyxl.load_workbook(io.BytesIO(content_bytes), data_only=True)
        sheet = wb.active
        rows = list(sheet.iter_rows(values_only=True))
    except Exception as e:
        return [], [{"row": 0, "column": "file", "message": f"Could not read Excel file: {e}", "suggestion": "Ensure the file is a valid .xlsx workbook"}]

    if not rows or len(rows) < 1:
        return [], [{"row": 0, "column": "header", "message": "Excel workbook is empty", "suggestion": "Include headers in the first row"}]

    raw_headers = rows[0]
    headers = [str(h).strip().lower() if h is not None else "" for h in raw_headers]
    if not any(headers):
        return [], [{"row": 0, "column": "header", "message": "Excel header row is empty", "suggestion": "Include column names in row 1"}]

    dict_rows = []
    for r in rows[1:]:
        if not any(cell is not None and str(cell).strip() != "" for cell in r):
            continue
        row_dict = {}
        for h, val in zip(headers, r):
            if h:
                if hasattr(val, "strftime"):
                    row_dict[h] = val.strftime("%Y-%m")
                else:
                    row_dict[h] = str(val).strip() if val is not None else ""
        dict_rows.append(row_dict)

    return validate_dict_rows(dict_rows, kind)


def parse_and_validate_file(
    content_bytes: bytes,
    filename: str,
    kind: str
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Unified entry point for both CSV and Excel (.xlsx) file uploads.
    """
    fname_lower = (filename or "").lower()
    if fname_lower.endswith(".xlsx") or fname_lower.endswith(".xls"):
        return parse_and_validate_excel(content_bytes, kind)
    else:
        try:
            content_str = content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            content_str = content_bytes.decode("latin-1")
        return parse_and_validate_csv(content_str, kind)



def parse_crop_row(row: Dict[str, Any], idx: int) -> Dict[str, Any]:
    name = row.get("name") or row.get("crop_name")
    if not name:
        raise ValidationError("Crop name is required", field="name")

    seasons_str = row.get("seasons", "kharif,rabi")
    seasons = [s.strip().lower() for s in seasons_str.split(",") if s.strip()]

    try:
        water_req = float(row.get("water_req_mm", 500))
        duration = int(row.get("duration_days", 120))
        yield_t = float(row.get("typical_yield_t_ha", 3.0))
        labour = float(row.get("labour_person_days_ha", 45))
    except ValueError as ve:
        raise ValidationError(f"Invalid numeric value in row: {ve}", field="numeric")

    # Soil specs
    ph_amin = float(row.get("ph_abs_min", 5.0))
    ph_omin = float(row.get("ph_opt_min", 6.0))
    ph_omax = float(row.get("ph_opt_max", 7.5))
    ph_amax = float(row.get("ph_abs_max", 8.5))

    crop_data = {
        "name": name,
        "category": row.get("category", "Cereals"),
        "seasons": seasons,
        "duration_days": duration,
        "water_req_mm": water_req,
        "labour_person_days_ha": labour,
        "typical_yield_t_ha": yield_t,
        "active": True,
        "soil": {
            "ph": {"abs_min": ph_amin, "opt_min": ph_omin, "opt_max": ph_omax, "abs_max": ph_amax},
            "ec": {"abs_min": float(row.get("ec_abs_min", 0.0)), "opt_min": float(row.get("ec_opt_min", 0.0)), "opt_max": float(row.get("ec_opt_max", 2.0)), "abs_max": float(row.get("ec_abs_max", 4.0))},
            "oc": {"abs_min": float(row.get("oc_abs_min", 0.2)), "opt_min": float(row.get("oc_opt_min", 0.5)), "opt_max": float(row.get("oc_opt_max", 1.5)), "abs_max": float(row.get("oc_abs_max", 3.0))},
            "texture_suitability": {
                "loam": float(row.get("texture_loam", 1.0)),
                "sandy_loam": float(row.get("texture_sandy_loam", 0.9)),
                "clay_loam": float(row.get("texture_clay_loam", 0.85)),
                "clay": float(row.get("texture_clay", 0.7)),
                "sandy": float(row.get("texture_sandy", 0.5))
            },
            "drainage_suitability": {
                "good": float(row.get("drainage_good", 1.0)),
                "moderate": float(row.get("drainage_moderate", 0.85)),
                "poor": float(row.get("drainage_poor", 0.4))
            }
        }
    }
    validate_crop_data(crop_data)
    return crop_data


def parse_price_row(row: Dict[str, Any], idx: int) -> Dict[str, Any]:
    crop_name = row.get("crop_name") or row.get("crop")
    if not crop_name:
        raise ValidationError("Crop name is required", field="crop_name")

    month = row.get("month")  # Format YYYY-MM
    if not month or len(month.split("-")) != 2:
        raise ValidationError("Month must be in YYYY-MM format (e.g., 2024-03)", field="month")

    try:
        price = float(row.get("modal_price_per_quintal") or row.get("price", 0))
    except ValueError:
        raise ValidationError("Price must be a valid number", field="modal_price_per_quintal")

    if price <= 0:
        raise ValidationError("Price must be greater than zero", field="modal_price_per_quintal")

    return {
        "crop_name": crop_name,
        "market": row.get("market", "APMC Central"),
        "month": month,
        "modal_price_per_quintal": price,
        "source": row.get("source", "Mandi CSV Upload")
    }


def parse_economics_row(row: Dict[str, Any], idx: int) -> Dict[str, Any]:
    crop_name = row.get("crop_name") or row.get("crop")
    if not crop_name:
        raise ValidationError("Crop name is required", field="crop_name")

    try:
        cost = float(row.get("cost_per_ha", 30000))
        expected_yield = float(row.get("expected_yield_t_ha", 3.0))
        msp = float(row.get("msp_per_quintal", 0))
        year = int(row.get("year", 2025))
    except ValueError as ve:
        raise ValidationError(f"Invalid numeric value in economics row: {ve}", field="numeric")

    return {
        "crop_name": crop_name,
        "region": row.get("region", "Default"),
        "season": row.get("season", "kharif").lower(),
        "cost_per_ha": cost,
        "expected_yield_t_ha": expected_yield,
        "msp_per_quintal": msp,
        "year": year,
        "notes": row.get("notes", "CSV Upload")
    }


def parse_farm_row(row: Dict[str, Any], idx: int) -> Dict[str, Any]:
    name = row.get("name") or row.get("farm_name")
    if not name:
        raise ValidationError("Farm name is required", field="name")

    try:
        land_ha = float(row.get("land_ha", 5.0))
        ph = float(row.get("ph", 6.8))
        ec = float(row.get("ec", 0.6))
        oc = float(row.get("oc", 0.75))
        n = float(row.get("n", 280))
        p = float(row.get("p", 22))
        k = float(row.get("k", 310))
        rainfall_mm = float(row.get("rainfall_mm", 650))
        irrigation_m3 = float(row.get("irrigation_m3", 18000))
        budget_inr = float(row.get("budget_inr", 350000))
        labour = float(row.get("labour_person_days", 300))
    except ValueError as ve:
        raise ValidationError(f"Invalid numeric input in farm row: {ve}", field="numeric")

    farm_data = {
        "name": name,
        "land_ha": land_ha,
        "season": row.get("season", "kharif").lower(),
        "soil": {
            "ph": ph, "ec": ec, "oc": oc, "n": n, "p": p, "k": k,
            "texture": row.get("texture", "loam"),
            "drainage": row.get("drainage", "good")
        },
        "water": {
            "rainfall_mm": rainfall_mm,
            "effective_rainfall_pct": float(row.get("effective_rainfall_pct", 70)),
            "irrigation_m3": irrigation_m3
        },
        "budget_inr": budget_inr,
        "labour_person_days": labour
    }
    validate_farm_data(farm_data)
    return farm_data
