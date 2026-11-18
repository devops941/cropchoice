import io
import csv
from pathlib import Path
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from fastapi.responses import StreamingResponse, PlainTextResponse
import openpyxl
from deps import get_current_user
from db.repositories.crop_repo import CropRepository
from db.repositories.price_repo import PriceRepository
from db.repositories.farm_repo import FarmRepository
from db.repositories.ranking_repo import RankingRepository
from db.repositories.optimizer_repo import OptimizerRepository
from db.repositories.import_repo import ImportRepository
from imports.csv_import import parse_and_validate_csv, parse_and_validate_file

router = APIRouter(prefix="/import-export", tags=["Import & Export Center"])
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@router.get("/sample/{kind}.csv")
def download_sample_csv(kind: str):
    filepath = DATA_DIR / "sample" / f"{kind}_sample.csv"
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return PlainTextResponse(
            content=content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={kind}_sample.csv"}
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Sample template for '{kind}' not found.")


@router.get("/sample/{kind}.xlsx")
def download_sample_excel(kind: str):
    filepath = DATA_DIR / "sample" / f"{kind}_sample.csv"
    try:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = kind.capitalize()

        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                ws.append(row)

        stream = io.BytesIO()
        wb.save(stream)
        stream.seek(0)

        return StreamingResponse(
            stream,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={kind}_sample.xlsx"}
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Sample template for '{kind}' not found.")


@router.post("/upload/{kind}")
async def upload_file(
    kind: str,
    file: UploadFile = File(...),
    auto_commit: bool = Form(False),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    uid = str(current_user["_id"])
    import_repo = ImportRepository()

    content_bytes = await file.read()
    valid_rows, errors = parse_and_validate_file(content_bytes, file.filename or "uploaded.csv", kind=kind)

    job = import_repo.create_job(kind=kind, filename=file.filename or "uploaded.csv", uploaded_by=uid)
    job_id = job["id"]

    committed_count = 0
    if auto_commit and valid_rows:
        committed_count = commit_imported_records(kind, valid_rows, uid)

    import_repo.update_job(job_id, {
        "status": "completed" if auto_commit else "validated",
        "n_rows": len(valid_rows) + len(errors),
        "n_valid": len(valid_rows),
        "n_errors": len(errors),
        "errors": errors[:50],
        "preview_data": valid_rows[:15],
        "committed_count": committed_count
    })

    return {
        "job_id": job_id,
        "filename": file.filename,
        "kind": kind,
        "total_rows": len(valid_rows) + len(errors),
        "valid_rows_count": len(valid_rows),
        "error_count": len(errors),
        "errors": errors,
        "preview_data": valid_rows[:10],
        "committed": auto_commit,
        "committed_count": committed_count
    }


def commit_imported_records(kind: str, records: List[Dict[str, Any]], user_id: str) -> int:
    crop_repo = CropRepository()
    price_repo = PriceRepository()
    farm_repo = FarmRepository()

    count = 0
    if kind == "crops":
        for r in records:
            existing = crop_repo.get_by_name(r["name"])
            if not existing:
                crop_repo.create_crop(r, user_id=user_id)
                count += 1
            else:
                crop_repo.update_crop(existing["id"], r)
                count += 1

    elif kind == "prices":
        # Resolve crop names to ids
        resolved = []
        for p in records:
            c = crop_repo.get_by_name(p["crop_name"])
            if c:
                p["crop_id"] = c["id"]
                resolved.append(p)
        count = price_repo.bulk_upsert(resolved)

    elif kind == "economics":
        for e in records:
            c = crop_repo.get_by_name(e["crop_name"])
            if c:
                e["crop_id"] = c["id"]
                crop_repo.upsert_economics(e)
                count += 1

    elif kind == "farms":
        for f in records:
            farm_repo.create_farm(f, owner_id=user_id)
            count += 1

    return count


@router.get("/export/ranking/{ranking_id}.csv")
def export_ranking_csv(ranking_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    repo = RankingRepository()
    ranking = repo.get_by_id(ranking_id, owner_id=str(current_user["_id"]))
    if not ranking:
        raise HTTPException(status_code=404, detail="Ranking not found")

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Rank", "Crop Name", "Closeness (C_i)", "WSM Score", "Water Demand (mm)", "Soil Score", "Net Return (INR/ha)", "Price CV", "Explanation"])

    for r in ranking.get("results", []):
        cv = r.get("criteria_values", {})
        writer.writerow([
            r.get("rank"),
            r.get("crop_name"),
            r.get("closeness"),
            r.get("wsm_score"),
            cv.get("water"),
            cv.get("soil"),
            cv.get("return"),
            cv.get("variability"),
            r.get("explanation")
        ])

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=crop_ranking_{ranking_id}.csv"}
    )


@router.get("/export/optimization/{opt_id}.xlsx")
def export_optimization_excel(opt_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    repo = OptimizerRepository()
    opt = repo.get_optimization(opt_id, owner_id=str(current_user["_id"]))
    if not opt:
        raise HTTPException(status_code=404, detail="Optimization not found")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Allocation & Portfolio"

    ws.append(["CropChoice Portfolio Optimization Summary"])
    ws.append(["Farm Name", opt.get("farm_name", "N/A")])
    ws.append(["Objective", opt.get("objective", "max_return")])
    ws.append([])

    ws.append(["Allocated Crop", "Category", "Area (ha)", "Land Share (%)", "Expected Net Return (INR)", "Water Needed (m3)", "Cost (INR)", "Labour (Days)"])
    for a in opt.get("allocation", []):
        ws.append([
            a.get("crop_name"),
            a.get("category"),
            a.get("area_ha"),
            f"{a.get('share', 0) * 100:.1f}%",
            a.get("expected_return"),
            a.get("water_m3"),
            a.get("cost_inr"),
            a.get("labour_days")
        ])

    ws.append([])
    totals = opt.get("totals", {})
    ws.append(["TOTALS", "", totals.get("total_land_ha"), "100%", totals.get("net_return"), totals.get("water_m3"), totals.get("cost_inr"), totals.get("labour_days")])

    ws.append([])
    div = opt.get("diversification", {})
    ws.append(["Diversification Metrics"])
    ws.append(["Effective Crops (1/HHI)", div.get("effective_crops")])
    ws.append(["HHI Index", div.get("hhi")])
    ws.append(["Shannon Entropy", div.get("entropy")])
    ws.append(["Rating", div.get("diversification_rating")])

    out = io.BytesIO()
    wb.save(out)
    out.seek(0)

    return StreamingResponse(
        out,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=portfolio_allocation_{opt_id}.xlsx"}
    )
