"""
geo_utils.py
------------------------------------------------------------------
ฟังก์ชันช่วยงานสำหรับคอร์ส "Python for Geography"
ออกแบบให้หยิบไปใช้ซ้ำได้กับข้อมูลชุดอื่น ไม่ผูกกับ notebook ใด notebook หนึ่ง

ใช้ใน Colab:
    !wget -q https://raw.githubusercontent.com/jamorn12/Teaching_Python_for_Geography/main/utils/geo_utils.py
    import geo_utils as gu
"""

from __future__ import annotations

import math
import os
import urllib.request

import numpy as np
import pandas as pd

RAW_BASE = (
    "https://raw.githubusercontent.com/jamorn12/"
    "Teaching_Python_for_Geography/main/data/"
)

# เกณฑ์ปริมาณฝนสะสม 24 ชม. (ตามการแบ่งระดับที่ใช้กันทั่วไปในไทย)
RAIN_CLASSES = [
    (0.1, "ไม่มีฝน"),
    (10.0, "ฝนเล็กน้อย"),
    (35.0, "ฝนปานกลาง"),
    (90.0, "ฝนหนัก"),
    (float("inf"), "ฝนหนักมาก"),
]


# ------------------------------------------------------------------
# STEP 1 : เตรียม / โหลดข้อมูล
# ------------------------------------------------------------------
def fetch_data(filename: str, outdir: str = "data") -> str:
    """
    ดาวน์โหลดไฟล์ข้อมูลจาก GitHub ถ้ายังไม่มีในเครื่อง แล้วคืน path
    ถ้าดาวน์โหลดไม่ได้จะ raise ให้ผู้เรียกจัดการ (เช่น สร้างข้อมูลเอง)
    """
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, filename)
    if not os.path.exists(path):
        urllib.request.urlretrieve(RAW_BASE + filename, path)
    return path


def load_rainfall(path: str = "data/rainfall_daily_2025.csv") -> pd.DataFrame:
    """อ่านไฟล์ฝนรายวัน แปลงคอลัมน์ date เป็น datetime และเพิ่มคอลัมน์ปี/เดือน"""
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    return df


def load_stations(path: str = "data/stations.csv") -> pd.DataFrame:
    """อ่านตาราง metadata ของสถานี"""
    return pd.read_csv(path)


# ------------------------------------------------------------------
# STEP 2 : ทำความสะอาดข้อมูล
# ------------------------------------------------------------------
def to_number(value, missing_flags=(-999, -9999)) -> float:
    """
    แปลงค่าที่อ่านจากไฟล์ให้เป็น float
    คืน np.nan เมื่อเป็นค่าว่าง / ข้อความ / missing flag
    """
    if value is None:
        return np.nan
    text = str(value).strip()
    if text == "" or text.lower() in {"na", "nan", "none", "trace"}:
        return np.nan
    try:
        number = float(text)
    except ValueError:
        return np.nan
    if number in missing_flags:
        return np.nan
    return number


def clean_rainfall(df: pd.DataFrame, column: str = "rain_mm") -> pd.DataFrame:
    """ทำความสะอาดคอลัมน์ฝนทั้งคอลัมน์ด้วย to_number()"""
    out = df.copy()
    out[column] = out[column].apply(to_number)
    return out


# ------------------------------------------------------------------
# STEP 3 : จำแนก / สรุปผล
# ------------------------------------------------------------------
def classify_rain(mm: float) -> str:
    """จำแนกระดับความรุนแรงของฝนรายวัน"""
    if mm is None or (isinstance(mm, float) and math.isnan(mm)):
        return "ไม่มีข้อมูล"
    for upper, label in RAIN_CLASSES:
        if mm < upper:
            return label
    return "ฝนหนักมาก"


def monthly_summary(df: pd.DataFrame, station_id: str | None = None) -> pd.DataFrame:
    """
    สรุปฝนรายเดือน: ผลรวม, ค่าสูงสุดรายวัน, จำนวนวันฝนตก (>= 0.1 mm)
    """
    data = df if station_id is None else df[df["station_id"] == station_id]
    grouped = data.groupby(["station_id", "month"])["rain_mm"]
    out = grouped.agg(
        total_mm="sum",
        max_daily_mm="max",
        rain_days=lambda s: int((s >= 0.1).sum()),
    ).reset_index()
    out["total_mm"] = out["total_mm"].round(1)
    return out


def annual_summary(df: pd.DataFrame) -> pd.DataFrame:
    """สรุปรายปีต่อสถานี"""
    grouped = df.groupby("station_id")["rain_mm"]
    out = grouped.agg(
        total_mm="sum",
        mean_daily_mm="mean",
        max_daily_mm="max",
        rain_days=lambda s: int((s >= 0.1).sum()),
    ).reset_index()
    return out.round(2)


# ------------------------------------------------------------------
# STEP 4 : คำนวณเชิงพื้นที่
# ------------------------------------------------------------------
def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """ระยะทางวงกลมใหญ่ระหว่างสองพิกัด (กิโลเมตร)"""
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def distance_matrix(stations: pd.DataFrame) -> pd.DataFrame:
    """ตารางระยะทางระหว่างทุกคู่สถานี (km)"""
    ids = stations["station_id"].tolist()
    m = pd.DataFrame(index=ids, columns=ids, dtype=float)
    for _, a in stations.iterrows():
        for _, b in stations.iterrows():
            m.loc[a["station_id"], b["station_id"]] = round(
                haversine(a["lat"], a["lon"], b["lat"], b["lon"]), 2
            )
    return m


# ------------------------------------------------------------------
# STEP 5 : ตั้งค่าฟอนต์ไทยสำหรับ matplotlib (ใช้ใน Colab)
# ------------------------------------------------------------------
def setup_thai_font(verbose: bool = True) -> bool:
    """
    ติดตั้งฟอนต์ Sarabun ให้ matplotlib แสดงภาษาไทยได้
    คืน True ถ้าสำเร็จ, False ถ้าไม่สำเร็จ (กราฟยังใช้ได้ แต่ label ไทยจะเป็นสี่เหลี่ยม)
    """
    try:
        import matplotlib
        import matplotlib.font_manager as fm

        url = (
            "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Regular.ttf"
        )
        path = "/usr/share/fonts/truetype/Sarabun-Regular.ttf"
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            urllib.request.urlretrieve(url, path)
        fm.fontManager.addfont(path)
        matplotlib.rc("font", family="Sarabun")
        matplotlib.rcParams["axes.unicode_minus"] = False
        if verbose:
            print("ตั้งค่าฟอนต์ไทย (Sarabun) เรียบร้อย")
        return True
    except Exception as exc:  # noqa: BLE001
        if verbose:
            print("ตั้งฟอนต์ไทยไม่สำเร็จ ->", exc, "| ใช้ label ภาษาอังกฤษแทนได้")
        return False
