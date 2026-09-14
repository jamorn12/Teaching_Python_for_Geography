"""
make_datasets.py
------------------------------------------------------------------
สร้างชุดข้อมูลสังเคราะห์ (synthetic dataset) สำหรับใช้สอน Python
วิชาภูมิศาสตร์ ชั้นปีที่ 2

ข้อมูลนี้ "ไม่ใช่" ข้อมูลตรวจวัดจริงของกรมอุตุนิยมวิทยา
แต่ถูกสร้างให้มีลักษณะทางสถิติใกล้เคียงฝนรายวันของภาคตะวันออก
(ฤดูฝนเด่นช่วง พ.ค.–ต.ค. ตามอิทธิพลของ southwest monsoon)
เพื่อให้ผู้เรียนฝึกวิเคราะห์ได้โดยไม่ติดเรื่องลิขสิทธิ์ข้อมูล

รันแบบ stand-alone:
    python make_datasets.py --outdir ../data
"""

import argparse
import os

import numpy as np
import pandas as pd

# ---------------------------------------------------------------
# 1) รายชื่อสถานี (พิกัดจริงโดยประมาณ ใช้เพื่อการสอนเท่านั้น)
# ---------------------------------------------------------------
STATIONS = [
    # station_id, name_th,        province, lat,     lon,      elev_m, factor
    ("CHB01", "ชลบุรี", "ชลบุรี", 13.367, 100.983, 3, 1.00),
    ("SRC01", "เกาะสีชัง", "ชลบุรี", 13.163, 100.803, 4, 0.82),
    ("NYI01", "หนองใหญ่", "ชลบุรี", 13.150, 101.350, 45, 1.18),
    ("STH01", "สัตหีบ", "ชลบุรี", 12.680, 100.983, 16, 0.92),
]

# โอกาสเกิดฝนรายวัน และความแรงเฉลี่ยของฝน แยกตามเดือน (ม.ค.–ธ.ค.)
RAIN_PROB = [0.05, 0.06, 0.12, 0.20, 0.40, 0.45, 0.45, 0.50, 0.60, 0.45, 0.15, 0.06]
RAIN_SCALE = [3.0, 4.0, 6.0, 8.0, 12.0, 12.0, 12.0, 14.0, 16.0, 12.0, 6.0, 3.0]

YEAR = 2025
SEED = 2025


def make_station_table() -> pd.DataFrame:
    """ตารางข้อมูลสถานี (station metadata)"""
    rows = [
        {
            "station_id": sid,
            "station_name": name,
            "province": prov,
            "lat": lat,
            "lon": lon,
            "elevation_m": elev,
        }
        for sid, name, prov, lat, lon, elev, _ in STATIONS
    ]
    return pd.DataFrame(rows)


def make_rainfall_table(year: int = YEAR, seed: int = SEED) -> pd.DataFrame:
    """ฝนรายวันของทุกสถานีในหนึ่งปี (daily rainfall, หน่วย mm)"""
    rng = np.random.default_rng(seed)
    dates = pd.date_range(f"{year}-01-01", f"{year}-12-31", freq="D")

    records = []
    for sid, name, prov, lat, lon, elev, factor in STATIONS:
        for d in dates:
            m = d.month - 1
            if rng.random() < RAIN_PROB[m]:
                # gamma distribution ให้ค่าฝนเบ้ขวา เหมือนฝนจริง
                value = rng.gamma(shape=0.9, scale=RAIN_SCALE[m]) * factor
            else:
                value = 0.0
            records.append(
                {
                    "date": d.strftime("%Y-%m-%d"),
                    "station_id": sid,
                    "station_name": name,
                    "province": prov,
                    "rain_mm": round(float(value), 1),
                }
            )

    df = pd.DataFrame(records)

    # แทรกเหตุการณ์ฝนหนักมาก (extreme event) ให้มีตัวอย่างให้วิเคราะห์
    extreme_days = [
        ("CHB01", f"{year}-09-14", 118.6),
        ("CHB01", f"{year}-10-02", 96.4),
        ("NYI01", f"{year}-09-14", 142.3),
        ("NYI01", f"{year}-08-21", 101.7),
        ("SRC01", f"{year}-09-15", 88.2),
        ("STH01", f"{year}-10-03", 93.5),
    ]
    for sid, day, val in extreme_days:
        mask = (df["station_id"] == sid) & (df["date"] == day)
        df.loc[mask, "rain_mm"] = val

    return df


def make_messy_table(df_clean: pd.DataFrame) -> pd.DataFrame:
    """
    เวอร์ชัน 'ข้อมูลสกปรก' สำหรับสอนเรื่อง error handling และ data cleaning
    ใส่ค่าว่าง, ข้อความ, ค่า -999 (missing flag) และช่องว่างหน้าหลังตัวเลข
    """
    d = df_clean[df_clean["station_id"] == "CHB01"].head(90).copy()
    d["rain_mm"] = d["rain_mm"].astype(object)

    idx = d.index.tolist()
    d.loc[idx[5], "rain_mm"] = ""
    d.loc[idx[12], "rain_mm"] = "NA"
    d.loc[idx[23], "rain_mm"] = "-999"
    d.loc[idx[31], "rain_mm"] = " 8.4 "
    d.loc[idx[44], "rain_mm"] = "ไม่มีข้อมูล"
    d.loc[idx[57], "rain_mm"] = "-999"
    d.loc[idx[66], "rain_mm"] = ""
    d.loc[idx[78], "rain_mm"] = "trace"
    return d


def main(outdir: str = "data") -> None:
    os.makedirs(outdir, exist_ok=True)

    stations = make_station_table()
    rainfall = make_rainfall_table()
    messy = make_messy_table(rainfall)

    stations.to_csv(os.path.join(outdir, "stations.csv"), index=False, encoding="utf-8-sig")
    rainfall.to_csv(os.path.join(outdir, "rainfall_daily_2025.csv"), index=False, encoding="utf-8-sig")
    messy.to_csv(os.path.join(outdir, "messy_rainfall.csv"), index=False, encoding="utf-8-sig")

    print(f"stations.csv            : {len(stations):>5} rows")
    print(f"rainfall_daily_2025.csv : {len(rainfall):>5} rows")
    print(f"messy_rainfall.csv      : {len(messy):>5} rows")
    total = rainfall.groupby("station_id")["rain_mm"].sum().round(1)
    print("\nฝนรวมทั้งปี (mm) ต่อสถานี:")
    print(total.to_string())


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--outdir", default="data")
    args = p.parse_args()
    main(args.outdir)
