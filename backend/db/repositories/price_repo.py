import math
from typing import Optional, Dict, Any, List
from bson import ObjectId
from pymongo import UpdateOne
from db.mongo import get_db, serialize_doc


class PriceRepository:
    def __init__(self, db=None):
        self.db = db if db is not None else get_db()

    def get_prices(
        self,
        crop_id: Optional[str] = None,
        market: Optional[str] = None,
        from_month: Optional[str] = None,
        to_month: Optional[str] = None,
        limit: int = 240
    ) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {}
        if crop_id:
            query["crop_id"] = str(crop_id)
        if market:
            query["market"] = market
        if from_month or to_month:
            query["month"] = {}
            if from_month:
                query["month"]["$gte"] = from_month
            if to_month:
                query["month"]["$lte"] = to_month

        docs = list(self.db.price_history.find(query).sort("month", 1).limit(limit))
        return [serialize_doc(d) for d in docs]

    def add_price(self, data: Dict[str, Any]) -> Dict[str, Any]:
        filter_query = {
            "crop_id": str(data["crop_id"]),
            "market": data.get("market", "APMC Central"),
            "month": data["month"]  # e.g. "2024-01"
        }
        update_data = {
            "crop_id": str(data["crop_id"]),
            "crop_name": data.get("crop_name", ""),
            "market": data.get("market", "APMC Central"),
            "month": data["month"],
            "modal_price_per_quintal": float(data["modal_price_per_quintal"]),
            "source": data.get("source", "Agmarknet / Mandi Reports")
        }
        self.db.price_history.update_one(filter_query, {"$set": update_data}, upsert=True)
        return update_data

    def bulk_upsert(self, records: List[Dict[str, Any]]) -> int:
        if not records:
            return 0
        ops = []
        for r in records:
            ops.append(
                UpdateOne(
                    {
                        "crop_id": str(r["crop_id"]),
                        "market": r.get("market", "APMC Central"),
                        "month": r["month"]
                    },
                    {"$set": r},
                    upsert=True
                )
            )
        res = self.db.price_history.bulk_write(ops)
        return res.upserted_count + res.modified_count

    def get_crop_stats(self, crop_id: str, last_n_months: int = 36) -> Dict[str, Any]:
        prices = self.get_prices(crop_id=crop_id, limit=last_n_months)
        if not prices:
            return {
                "crop_id": str(crop_id),
                "count": 0,
                "mean_price": 2500.0,
                "std_dev": 500.0,
                "cv": 0.20,
                "min_price": 2000.0,
                "max_price": 3000.0,
                "is_fallback": True
            }

        values = [p["modal_price_per_quintal"] for p in prices]
        n = len(values)
        mean_val = sum(values) / n
        if n > 1:
            variance = sum((x - mean_val) ** 2 for x in values) / (n - 1)
            std_dev = math.sqrt(variance)
        else:
            std_dev = 0.0

        cv = (std_dev / mean_val) if mean_val > 0 else 0.20

        return {
            "crop_id": str(crop_id),
            "count": n,
            "mean_price": round(mean_val, 2),
            "std_dev": round(std_dev, 2),
            "cv": round(cv, 4),
            "min_price": round(min(values), 2),
            "max_price": round(max(values), 2),
            "is_fallback": n < 24
        }
