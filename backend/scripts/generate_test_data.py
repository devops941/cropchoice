import csv
import os
from pathlib import Path
import random
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Seed for reproducible, high quality realistic agricultural data
random.seed(2026)

BACKEND_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BACKEND_DIR.parent
DATA_SAMPLE_DIR = BACKEND_DIR / "data" / "sample"
DATA_SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

# Styles for Excel Workbooks
HEADER_FILL = PatternFill(start_color="047857", end_color="047857", fill_type="solid")
HEADER_FONT = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
ZEBRA_FILL = PatternFill(start_color="F6F8F4", end_color="F6F8F4", fill_type="solid")
BORDER_THIN = Border(
    left=Side(style='thin', color='DCE5DC'),
    right=Side(style='thin', color='DCE5DC'),
    top=Side(style='thin', color='DCE5DC'),
    bottom=Side(style='thin', color='DCE5DC')
)


def format_worksheet(ws, headers):
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.value = header
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center")

    for row_num in range(2, ws.max_row + 1):
        is_even = (row_num % 2 == 0)
        for col_num in range(1, len(headers) + 1):
            cell = ws.cell(row=row_num, column=col_num)
            cell.border = BORDER_THIN
            if is_even:
                cell.fill = ZEBRA_FILL
            # Format numbers
            if isinstance(cell.value, float):
                cell.number_format = '#,##0.00'
            elif isinstance(cell.value, int):
                cell.number_format = '#,##0'

    # Auto-adjust column widths
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            v_str = str(cell.value or "")
            if len(v_str) > max_len:
                max_len = len(v_str)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)


# ==========================================
# 1. 100 FARMS & SOIL LAB SAMPLES
# ==========================================
def generate_100_farms():
    regions = [
        ("Cauvery Delta", "Thanjavur", "Tamil Nadu", "clay_loam", "moderate"),
        ("Kongu Highland", "Coimbatore", "Tamil Nadu", "loam", "good"),
        ("Siruvani Valley", "Tiruppur", "Tamil Nadu", "sandy_loam", "good"),
        ("Vaigai Basin", "Madurai", "Tamil Nadu", "clay_loam", "moderate"),
        ("Shevaroy Foothills", "Salem", "Tamil Nadu", "loam", "good"),
        ("Tungabhadra Agri-Zone", "Raichur", "Karnataka", "clay", "poor"),
        ("Deccan Plateau", "Dharwad", "Karnataka", "clay_loam", "moderate"),
        ("Krishna Delta", "Guntur", "Andhra Pradesh", "clay", "moderate"),
        ("Godavari Belt", "Warangal", "Telangana", "loam", "good"),
        ("Godavari Black Soil", "Nashik", "Maharashtra", "clay_loam", "good"),
        ("Western Ghats Terrace", "Pune", "Maharashtra", "loam", "good"),
        ("Malwa Plateau", "Indore", "Madhya Pradesh", "clay_loam", "moderate"),
        ("Narmada Valley", "Hoshangabad", "Madhya Pradesh", "clay", "moderate"),
        ("Indo-Gangetic Plain", "Karnal", "Haryana", "loam", "good"),
        ("Sutlej Basin", "Ludhiana", "Punjab", "sandy_loam", "good")
    ]

    seasons = ["kharif", "rabi"]
    textures = ["loam", "clay_loam", "sandy_loam", "clay", "sandy"]
    drainages = ["good", "moderate", "poor"]

    farms_data = []
    for i in range(1, 101):
        reg = regions[(i - 1) % len(regions)]
        season = seasons[i % 2]
        texture = reg[3] if (i % 3 != 0) else random.choice(textures)
        drainage = reg[4] if (i % 4 != 0) else random.choice(drainages)

        land_ha = round(random.uniform(2.0, 18.0), 1)
        ph = round(random.uniform(6.1, 7.9), 2)
        ec = round(random.uniform(0.35, 1.45), 2)
        oc = round(random.uniform(0.50, 1.40), 2)
        n = round(random.uniform(230.0, 340.0), 1)
        p = round(random.uniform(16.0, 32.0), 1)
        k = round(random.uniform(220.0, 390.0), 1)

        rainfall_mm = round(random.uniform(550.0, 950.0), 0)
        effective_pct = round(random.uniform(65.0, 80.0), 0)
        # Irrigation scaled to land size: ~3,500 - 5,000 m3 per ha
        irrigation_m3 = round(land_ha * random.uniform(3200, 5200), 0)
        # Budget: ~50,000 - 80,000 INR per ha
        budget_inr = round(land_ha * random.uniform(55000, 85000), 0)
        # Labour: ~45 - 75 person days per ha
        labour = round(land_ha * random.uniform(45, 75), 0)

        farm_name = f"{reg[0]} Parcel #{i:03d} ({reg[1]})"

        farms_data.append({
            "name": farm_name,
            "land_ha": land_ha,
            "season": season,
            "ph": ph,
            "ec": ec,
            "oc": oc,
            "n": n,
            "p": p,
            "k": k,
            "texture": texture,
            "drainage": drainage,
            "rainfall_mm": rainfall_mm,
            "effective_rainfall_pct": effective_pct,
            "irrigation_m3": irrigation_m3,
            "budget_inr": budget_inr,
            "labour_person_days": labour
        })

    return farms_data


# ==========================================
# 2. 100 MANDI PRICE OBSERVATIONS
# ==========================================
def generate_100_prices():
    crops = [
        ("Rice", 2350, 200),
        ("Wheat", 2275, 180),
        ("Cotton", 7120, 500),
        ("Maize", 2090, 150),
        ("Groundnut", 6375, 450),
        ("Soybean", 4890, 350),
        ("Sugarcane", 3150, 150),
        ("Sorghum (Jowar)", 3180, 250),
        ("Pearl Millet (Bajra)", 2500, 180),
        ("Ragi (Finger Millet)", 3840, 220),
        ("Chickpea (Gram)", 5440, 380),
        ("Pigeon Pea (Tur)", 7000, 600),
        ("Black Gram (Urad)", 6950, 550),
        ("Green Gram (Moong)", 8550, 650),
        ("Tomato", 1850, 750),
        ("Onion", 2150, 600),
        ("Potato", 1650, 300)
    ]

    markets = [
        "APMC Coimbatore", "APMC Thanjavur", "APMC Madurai", "APMC Salem",
        "APMC Raichur", "APMC Nashik", "APMC Pune", "APMC Indore",
        "APMC Guntur", "APMC Karnal"
    ]

    months = [
        "2024-01", "2024-02", "2024-03", "2024-04", "2024-05", "2024-06",
        "2024-07", "2024-08", "2024-09", "2024-10", "2024-11", "2024-12",
        "2025-01", "2025-02", "2025-03", "2025-04", "2025-05", "2025-06"
    ]

    prices_data = []
    count = 0
    while count < 100:
        for crop_name, base_p, vol in crops:
            if count >= 100:
                break
            market = markets[count % len(markets)]
            month = months[count % len(months)]
            # Realistic seasonal fluctuation
            price_val = round(base_p + random.gauss(0, vol), 0)
            if price_val < 500:
                price_val = base_p

            prices_data.append({
                "crop_name": crop_name,
                "market": market,
                "month": month,
                "modal_price_per_quintal": price_val,
                "source": "Agmarknet APMC Live Feed"
            })
            count += 1

    return prices_data


# ==========================================
# 3. 100 CROP ECONOMICS RECORDS
# ==========================================
def generate_100_economics():
    base_crops = [
        ("Rice", 42000, 4.5, 2300),
        ("Wheat", 34000, 4.2, 2275),
        ("Cotton", 52000, 2.2, 7020),
        ("Maize", 31000, 5.0, 2090),
        ("Groundnut", 38000, 2.6, 6375),
        ("Soybean", 29000, 2.4, 4890),
        ("Sugarcane", 85000, 80.0, 3150),
        ("Sorghum (Jowar)", 26000, 2.8, 3180),
        ("Pearl Millet (Bajra)", 24000, 2.5, 2500),
        ("Ragi (Finger Millet)", 27000, 2.7, 3840),
        ("Chickpea (Gram)", 28000, 1.8, 5440),
        ("Pigeon Pea (Tur)", 32000, 1.5, 7000),
        ("Black Gram (Urad)", 26000, 1.2, 6950),
        ("Green Gram (Moong)", 27000, 1.1, 8550),
        ("Tomato", 72000, 24.0, 1800),
        ("Onion", 65000, 20.0, 2100),
        ("Potato", 78000, 22.0, 1600)
    ]

    regions = [
        "Tamil Nadu - Delta", "Tamil Nadu - Kongu", "Karnataka - North",
        "Karnataka - South", "Maharashtra - Vidarbha", "Maharashtra - Marathwada",
        "Andhra Pradesh - Coastal", "Telangana - Central", "Madhya Pradesh - Malwa",
        "Punjab - Central", "Haryana - Eastern"
    ]
    seasons = ["kharif", "rabi"]
    years = [2024, 2025]

    econ_data = []
    count = 0
    while count < 100:
        for cname, cost_base, yield_base, msp in base_crops:
            if count >= 100:
                break
            reg = regions[count % len(regions)]
            season = seasons[count % len(seasons)]
            year = years[count % len(years)]
            cost = round(cost_base * random.uniform(0.92, 1.12), 0)
            eyield = round(yield_base * random.uniform(0.90, 1.15), 2)

            econ_data.append({
                "crop_name": cname,
                "region": reg,
                "season": season,
                "cost_per_ha": cost,
                "expected_yield_t_ha": eyield,
                "msp_per_quintal": msp,
                "year": year,
                "notes": f"CACP Benchmark {year} - State Agro Plan"
            })
            count += 1

    return econ_data


def save_to_csv(data, filename, fieldnames):
    filepath = DATA_SAMPLE_DIR / filename
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"Saved CSV: {filepath}")

    # Also save to root directory for easy user access
    root_filepath = ROOT_DIR / filename
    with open(root_filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"Saved CSV in root: {root_filepath}")


def save_to_excel(data, filename, sheet_name, headers):
    filepath = DATA_SAMPLE_DIR / filename
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet_name

    for row_idx, item in enumerate(data, 2):
        for col_idx, h in enumerate(headers, 1):
            ws.cell(row=row_idx, column=col_idx, value=item[h])

    format_worksheet(ws, headers)
    wb.save(filepath)
    print(f"Saved Excel: {filepath}")

    # Also save in root directory
    root_filepath = ROOT_DIR / filename
    wb.save(root_filepath)
    print(f"Saved Excel in root: {root_filepath}")


def save_master_excel(farms, prices, economics):
    filepath = DATA_SAMPLE_DIR / "cropchoice_master_test_data_100.xlsx"
    root_filepath = ROOT_DIR / "cropchoice_master_test_data_100.xlsx"

    wb = openpyxl.Workbook()
    # Remove default sheet
    wb.remove(wb.active)

    # 1. Farms sheet
    ws_farms = wb.create_sheet(title="Farms & Soil (100)")
    farm_headers = list(farms[0].keys())
    for row_idx, item in enumerate(farms, 2):
        for col_idx, h in enumerate(farm_headers, 1):
            ws_farms.cell(row=row_idx, column=col_idx, value=item[h])
    format_worksheet(ws_farms, farm_headers)

    # 2. Prices sheet
    ws_prices = wb.create_sheet(title="Mandi Prices (100)")
    price_headers = list(prices[0].keys())
    for row_idx, item in enumerate(prices, 2):
        for col_idx, h in enumerate(price_headers, 1):
            ws_prices.cell(row=row_idx, column=col_idx, value=item[h])
    format_worksheet(ws_prices, price_headers)

    # 3. Economics sheet
    ws_econ = wb.create_sheet(title="Economics (100)")
    econ_headers = list(economics[0].keys())
    for row_idx, item in enumerate(economics, 2):
        for col_idx, h in enumerate(econ_headers, 1):
            ws_econ.cell(row=row_idx, column=col_idx, value=item[h])
    format_worksheet(ws_econ, econ_headers)

    wb.save(filepath)
    wb.save(root_filepath)
    print(f"Saved Master 100-Row Excel: {filepath} & {root_filepath}")


if __name__ == "__main__":
    farms = generate_100_farms()
    prices = generate_100_prices()
    economics = generate_100_economics()

    print(f"Generated {len(farms)} farm rows, {len(prices)} price rows, {len(economics)} economics rows.")

    # 1. Save Farms
    farm_headers = list(farms[0].keys())
    save_to_csv(farms, "cropchoice_farms_100.csv", farm_headers)
    save_to_excel(farms, "cropchoice_farms_100.xlsx", "Farms & Soil", farm_headers)

    # 2. Save Prices
    price_headers = list(prices[0].keys())
    save_to_csv(prices, "cropchoice_prices_100.csv", price_headers)
    save_to_excel(prices, "cropchoice_prices_100.xlsx", "Mandi Prices", price_headers)

    # 3. Save Economics
    econ_headers = list(economics[0].keys())
    save_to_csv(economics, "cropchoice_economics_100.csv", econ_headers)
    save_to_excel(economics, "cropchoice_economics_100.xlsx", "Economics", econ_headers)

    # 4. Save Master Workbook
    save_master_excel(farms, prices, economics)
    print("ALL 100-ROW TEST DATASETS CREATED SUCCESSFULLY!")
