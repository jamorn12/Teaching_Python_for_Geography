"""
era5_cases.py
------------------------------------------------------------------
ข้อมูลประกอบและฟังก์ชันวิเคราะห์ สำหรับกรณีศึกษาพายุที่ส่งผลต่อประเทศไทย 3 เหตุการณ์

ใช้คู่กับ era5_utils.py (ฟังก์ชันพื้นฐานในการเปิดไฟล์และพล็อตแผนที่)
และกับไฟล์ข้อมูลที่สร้างโดย fetch_case_data.py

ทุกเหตุการณ์กำหนดช่วงวิเคราะห์เป็น
    D-5 ถึง D+2   (5 วันก่อนเกิดเหตุ, วันเกิดเหตุ, 2 วันหลัง)

ข้อมูลวันเวลาและเหตุการณ์สำคัญทั้งหมดอ้างอิงจากประกาศกรมอุตุนิยมวิทยา
และรายงานข่าวที่ระบุไว้ในฟิลด์ `sources` ของแต่ละเคส

หมายเหตุสำคัญ: เส้นทางพายุในโน้ตบุ๊กไม่ได้คัดลอกมาจากข่าว
แต่ **คำนวณจากตำแหน่งความกดอากาศต่ำสุดในข้อมูล ERA5** เอง
ส่วนข้อมูลจากข่าวใช้เป็นจุดอ้างอิงเพื่อตรวจสอบว่าผลที่คำนวณได้สมเหตุสมผลหรือไม่
"""

from __future__ import annotations

import os
import urllib.request

import numpy as np
import pandas as pd
import xarray as xr

import era5_utils as eu

RAW_BASE = (
    "https://raw.githubusercontent.com/jamorn12/"
    "Teaching_Python_for_Geography/main/data/cases/"
)

# ------------------------------------------------------------------
# ข้อมูลประกอบของแต่ละเหตุการณ์
# ------------------------------------------------------------------
CASES = {
    "dianmu2021": {
        "id": "dianmu2021",
        "kind": "tropical_cyclone",
        "resolution": 0.5,
        "name_th": "พายุโซนร้อน เตี้ยนหมู่",
        "name_en": "Tropical Storm Dianmu",
        "year": 2021,
        "d0": "2021-09-24",
        "start": "2021-09-19",
        "end": "2021-09-26",
        "domain": (95.0, 115.0, 5.0, 25.0),
        "focus_domain": (99.0, 108.0, 13.0, 19.0),
        "impact_provinces": ["มุกดาหาร", "อำนาจเจริญ", "อุบลราชธานี", "ศรีสะเกษ",
                             "ชัยภูมิ", "นครราชสีมา"],
        "focus_points": {
            "อุบลราชธานี": (15.25, 104.87),
            "มุกดาหาร": (16.54, 104.72),
            "นครราชสีมา": (14.97, 102.08),
            "ชัยภูมิ": (15.81, 102.03),
        },
        "timeline": [
            ("2021-09-23 16:00 น.",
             "ดีเปรสชันในทะเลจีนใต้ตอนกลางทวีกำลังเป็นพายุโซนร้อน เตี้ยนหมู่"),
            ("2021-09-24",
             "ขึ้นฝั่งเวียดนาม แล้วอ่อนกำลังเป็นดีเปรสชัน เคลื่อนเข้าปกคลุม "
             "มุกดาหาร อำนาจเจริญ และอุบลราชธานี"),
            ("2021-09-24 ถึง 25",
             "ฝนตกหนักถึงหนักมากในภาคเหนือ อีสาน กลาง ตะวันออก กทม. และปริมณฑล"),
        ],
        "sources": [
            ("ประชาชาติธุรกิจ 23 ก.ย. 2564 — ประกาศกรมอุตุฯ เตือนพายุเตี้ยนหมู่เข้าไทย",
             "https://www.prachachat.net/general/news-767792"),
            ("กรุงเทพธุรกิจ 24 ก.ย. 2564 — ประกาศกรมอุตุนิยมวิทยา ฉบับที่ 5",
             "https://www.bangkokbiznews.com/news/962003"),
            ("ข่าวสด 24 ก.ย. 2564 — ประกาศฉบับที่ 5 ฝนถล่ม 31 จังหวัด",
             "https://www.khaosod.co.th/breaking-news/news_6638644"),
        ],
        "question": ("พายุที่ 'อ่อนกำลังลงแล้ว' ยังทำให้เกิดน้ำท่วมใหญ่ได้อย่างไร "
                     "ลองดูว่าความชื้นและฝนสัมพันธ์กับความแรงของลมหรือไม่"),
    },

    "noru2022": {
        "id": "noru2022",
        "kind": "tropical_cyclone",
        "resolution": 0.5,
        "name_th": "พายุไต้ฝุ่น/โซนร้อน โนรู",
        "name_en": "Typhoon / Tropical Storm Noru",
        "year": 2022,
        "d0": "2022-09-28",
        "start": "2022-09-23",
        "end": "2022-09-30",
        "domain": (95.0, 125.0, 5.0, 25.0),
        "focus_domain": (99.0, 108.0, 13.0, 19.0),
        "impact_provinces": ["อุบลราชธานี", "ศรีสะเกษ", "ยโสธร", "อำนาจเจริญ",
                             "นครราชสีมา", "ชัยภูมิ"],
        "focus_points": {
            "อุบลราชธานี": (15.25, 104.87),
            "โขงเจียม": (15.32, 105.50),
            "นครราชสีมา": (14.97, 102.08),
            "ขอนแก่น": (16.44, 102.83),
        },
        "timeline": [
            ("2022-09-23 13:00 น.",
             "ดีเปรสชันด้านตะวันออกของฟิลิปปินส์ทวีกำลังเป็นพายุโซนร้อน โนรู"),
            ("2022-09-28 เช้า",
             "ขึ้นฝั่งเวียดนามตอนกลาง บริเวณเมืองดานัง ในสถานะไต้ฝุ่น"),
            ("2022-09-28 เย็น",
             "เคลื่อนเข้าปกคลุมอีสานตอนล่าง บริเวณอำเภอโขงเจียม จังหวัดอุบลราชธานี"),
            ("2022-09-28 18:00 น.",
             "อ่อนกำลังเป็นดีเปรสชัน ศูนย์กลางบริเวณอำเภอศรีเมืองใหม่ อุบลราชธานี"),
        ],
        "sources": [
            ("กรุงเทพธุรกิจ 23 ก.ย. 2565 — ประกาศกรมอุตุฯ ฉบับที่ 1",
             "https://www.bangkokbiznews.com/news/news-update/1028631"),
            ("กรุงเทพธุรกิจ 28 ก.ย. 2565 — ประกาศฉบับที่ 15 เข้าปกคลุมอุบลราชธานี",
             "https://www.bangkokbiznews.com/health/social/1029470"),
            ("ข่าวสด 28 ก.ย. 2565 — ประกาศฉบับที่ 16 อ่อนกำลังเป็นดีเปรสชัน",
             "https://www.khaosod.co.th/breaking-news/news_7290408"),
        ],
        "question": ("โนรูเคยเป็นไต้ฝุ่นก่อนขึ้นฝั่ง ต่างจากเตี้ยนหมู่ที่เป็นโซนร้อน "
                     "ความแรงที่ต่างกันส่งผลต่อปริมาณฝนในไทยมากน้อยแค่ไหน"),
    },

    "yagi2024": {
        "id": "yagi2024",
        "kind": "tropical_cyclone",
        "resolution": 0.5,
        "name_th": "พายุไต้ฝุ่น ยางิ",
        "name_en": "Typhoon Yagi",
        "year": 2024,
        "d0": "2024-09-07",
        "start": "2024-09-02",
        "end": "2024-09-09",
        "domain": (95.0, 120.0, 5.0, 28.0),
        "focus_domain": (97.0, 105.0, 16.0, 22.0),
        "impact_provinces": ["เชียงราย", "พะเยา", "น่าน", "แพร่", "เชียงใหม่",
                             "หนองคาย", "บึงกาฬ", "เลย", "อุดรธานี"],
        "focus_points": {
            "เชียงราย": (19.91, 99.83),
            "แม่สาย": (20.43, 99.88),
            "น่าน": (18.78, 100.78),
            "หนองคาย": (17.88, 102.74),
        },
        "timeline": [
            ("2024-09-02 ถึง 03",
             "พายุโซนร้อน ยางิ ปกคลุมฟิลิปปินส์ มีแนวโน้มเคลื่อนลงทะเลจีนใต้ตอนบน"),
            ("2024-09-06",
             "ไต้ฝุ่น ยางิ อยู่ในทะเลจีนใต้ตอนบน เคลื่อนผ่านเกาะไหหลำและอ่าวตังเกี๋ย"),
            ("2024-09-07 ประมาณ 13:00 น.",
             "ขึ้นฝั่งเวียดนามตอนบน แล้วอ่อนกำลังลง คาดสลายตัวใน สปป.ลาว"),
            ("2024-09-07 ถึง 08",
             "ศูนย์กลางไม่เข้าไทย แต่ขอบพายุทำให้ภาคเหนือตอนบนและอีสานตอนบน "
             "มีฝนตกหนักถึงหนักมากและลมกระโชกแรง"),
        ],
        "sources": [
            ("ประชาชาติธุรกิจ 6 ก.ย. 2567 — กรมอุตุฯ อัปเดตเส้นทางไต้ฝุ่นยางิ",
             "https://www.prachachat.net/general/news-1646931"),
            ("กรมทรัพยากรน้ำ — รายงานสถานการณ์น้ำประจำวัน 5 ก.ย. 2567",
             "https://dwr.go.th/uploads/file/statuswater/2024/24h(343).pdf"),
            ("กรมทรัพยากรน้ำ — รายงานสถานการณ์น้ำประจำวัน 8 ก.ย. 2567",
             "https://dwr.go.th/uploads/file/statuswater/2024/24h(348).pdf"),
        ],
        "question": ("ศูนย์กลางพายุไม่เคยเข้าประเทศไทยเลย แล้วทำไมภาคเหนือตอนบน "
                     "ถึงมีฝนตกหนัก ลองหาคำตอบจากสนามลมและความชื้นที่ 850 hPa"),
    },

    "bangkok2026": {
        "id": "bangkok2026",
        "kind": "monsoon_low",
        "resolution": 0.25,
        "name_th": "น้ำท่วมกรุงเทพมหานคร",
        "name_en": "Bangkok urban flooding",
        "year": 2026,
        "d0": "2026-09-25",
        "start": "2026-09-20",
        "end": "2026-09-27",
        "domain": (95.0, 110.0, 5.0, 22.0),
        "focus_domain": (99.5, 102.0, 12.5, 15.0),
        "impact_provinces": ["กรุงเทพมหานคร", "นนทบุรี", "ปทุมธานี",
                             "สมุทรปราการ", "นครปฐม", "สมุทรสาคร"],
        "focus_points": {
            "กรุงเทพฯ (พระนคร)": (13.75, 100.50),
            "สายไหม": (13.92, 100.65),
            "มีนบุรี": (13.81, 100.75),
            "คลองสามวา": (13.86, 100.70),
        },
        "gauge_check": {
            "ปตร.ประชาร่วมใจ เขตมีนบุรี": 101.5,
            "ปตร.คลองสามวา เขตคลองสามวา": 97.5,
            "เขตสายไหม (ระลอกใหม่)": 92.5,
        },
        "timeline": [
            ("2026-09-22 กลางคืน",
             "เริ่มมีการเตือนล่วงหน้าว่าจะมีฝนตกหนักช่วง 24-27 ก.ย. "
             "ครอบคลุม กทม. ปริมณฑล และภาคตะวันออก"),
            ("2026-09-25 05:00 น.",
             "กรมอุตุนิยมวิทยาออกประกาศฉบับที่ 8 (224/2569) ฝนตกหนักถึงหนักมาก "
             "มีผลกระทบถึงวันที่ 27 ก.ย."),
            ("2026-09-25",
             "หย่อมความกดอากาศต่ำกำลังแรงบริเวณภาคตะวันออก เคลื่อนตามแนวร่องมรสุม "
             "ที่พาดผ่านภาคกลางตอนล่างและภาคตะวันออก ร่วมกับมรสุมตะวันตกเฉียงใต้ "
             "กำลังปานกลางที่แรงขึ้น ทำให้ กทม. มีฝนฟ้าคะนองร้อยละ 80 ของพื้นที่"),
            ("2026-09-25",
             "กทม. ประกาศเขตพื้นที่ประสบสาธารณภัยครบทั้ง 50 เขต "
             "ฝนสะสม 24 ชม. สูงสุดที่ ปตร.ประชาร่วมใจ เขตมีนบุรี 101.5 มม."),
            ("2026-09-26",
             "สถานการณ์ขึ้นสูงสุด ผู้ว่าฯ เรียกประชุมด่วน 50 เขต "
             "ประกาศเพิ่มพื้นที่อุทกภัยในเขตหนองจอก สวนหลวง คันนายาว"),
            ("2026-09-29",
             "ยกเลิกประกาศพื้นที่ภัยพิบัติ 21 เขต ยังคงเหลืออีก 29 เขต"),
        ],
        "sources": [
            ("กรมอุตุนิยมวิทยา — ประกาศฉบับที่ 8 (224/2569) 25 ก.ย. 2569 05:00 น.",
             "https://www.tmd.go.th/warning-and-events/warning-storm"),
            ("กรมอุตุนิยมวิทยา — พยากรณ์อากาศประจำวันที่ 25 ก.ย. 2569",
             "https://www.tmd.go.th/forecast/daily/250920260600"),
            ("THE STANDARD 25 ก.ย. 2569 — เตือนหย่อมความกดอากาศต่ำกำลังแรง",
             "https://thestandard.co/thai-met-warns-heavy-rain-nationwide/"),
            ("กรุงเทพธุรกิจ 25 ก.ย. 2569 — อัปเดตจุดน้ำท่วม กทม. และฝนสะสมรายเขต",
             "https://www.bangkokbiznews.com/news/news-update/1253494"),
            ("Thai PBS 29 ก.ย. 2569 — ยกเลิกพื้นที่ภัยพิบัติ 21 เขต เหลือ 29 เขต",
             "https://www.thaipbs.or.th/news/content/558864"),
            ("THE STANDARD — เทียบวิกฤตน้ำท่วม กทม. 2554 กับ 2569",
             "https://thestandard.co/bkk-flood-2554-2569-rain/"),
        ],
        "question": ("เหตุการณ์นี้ไม่มีพายุที่มีชื่อเรียกเลย แล้วอะไรทำให้ฝนตกหนัก "
                     "ต่อเนื่องหลายวันจนท่วมทั้ง 50 เขต "
                     "และ ERA5 ที่ความละเอียด 0.25 องศา มองเห็นฝนระดับเขตได้หรือไม่"),
    },
}

CASE_ORDER = ["dianmu2021", "noru2022", "yagi2024", "bangkok2026"]


# ------------------------------------------------------------------
# STEP 1 : โหลดข้อมูลของเคส
# ------------------------------------------------------------------
def case_info(case_id: str) -> dict:
    """คืน dict ข้อมูลประกอบของเคส"""
    if case_id not in CASES:
        raise KeyError(f"ไม่รู้จักเคส '{case_id}' เลือกได้: {list(CASES)}")
    return CASES[case_id]


def fetch_case(case_id: str, outdir: str = "data/cases") -> str:
    """ดาวน์โหลดไฟล์ข้อมูลของเคสจาก GitHub ถ้ายังไม่มีในเครื่อง คืน path"""
    os.makedirs(outdir, exist_ok=True)
    filename = f"{case_id}.nc"
    path = os.path.join(outdir, filename)
    if not os.path.exists(path):
        urllib.request.urlretrieve(RAW_BASE + filename, path)
    return path


def load_case(case_id: str, outdir: str = "data/cases") -> xr.Dataset:
    """
    โหลดข้อมูล ERA5 ของเคส พร้อมเพิ่มพิกัดช่วยงาน

    เพิ่ม coordinate ชื่อ `day_offset` = จำนวนวันเทียบกับวันเกิดเหตุ (D0)
    ทำให้เลือกข้อมูล 'วันก่อนเกิดเหตุ 3 วัน' ได้ด้วย ds.sel(day_offset=-3)
    """
    info = case_info(case_id)
    ds = eu.open_era5(fetch_case(case_id, outdir))

    d0 = pd.Timestamp(info["d0"])
    offsets = ((pd.to_datetime(ds["time"].values).normalize() - d0)
               .days.values.astype(int))
    ds = ds.assign_coords(day_offset=("time", offsets))
    return ds


def describe_case(case_id: str) -> str:
    """สรุปข้อมูลประกอบของเคสเป็นข้อความ พร้อมแหล่งอ้างอิง"""
    c = case_info(case_id)
    lines = [
        f"{c['name_th']} ({c['name_en']})",
        f"วันเกิดเหตุ (D0): {c['d0']}",
        f"ช่วงวิเคราะห์  : {c['start']} ถึง {c['end']}  (D-5 ถึง D+2)",
        f"จังหวัดที่ข่าวระบุว่าได้รับผลกระทบ: {', '.join(c['impact_provinces'])}",
        "",
        "ลำดับเหตุการณ์จากประกาศกรมอุตุนิยมวิทยาและรายงานข่าว",
    ]
    for when, what in c["timeline"]:
        lines.append(f"  {when}")
        lines.append(f"      {what}")
    lines.append("")
    lines.append("แหล่งอ้างอิง")
    for title, url in c["sources"]:
        lines.append(f"  - {title}")
        lines.append(f"    {url}")
    lines.append("")
    lines.append(f"คำถามชวนคิด: {c['question']}")
    return "\n".join(lines)


# ------------------------------------------------------------------
# STEP 2 : วิเคราะห์เส้นทางและความรุนแรง
# ------------------------------------------------------------------
def track_from_mslp(ds: xr.Dataset, search_domain: tuple | None = None) -> pd.DataFrame:
    """
    สร้างเส้นทางพายุจากตำแหน่งความกดอากาศต่ำสุดในแต่ละช่วงเวลา

    นี่คือวิธีประมาณอย่างง่าย ใช้ได้ดีเมื่อพายุเป็นระบบเด่นในโดเมน
    ถ้าในโดเมนมีหย่อมความกดอากาศต่ำหลายตัว ควรจำกัด search_domain ให้แคบลง

    คืน DataFrame: time, day_offset, lon, lat, mslp_hpa
    """
    data = ds if search_domain is None else eu.subset(ds, domain=search_domain)
    rows = []
    for t in data["time"].values:
        field = eu.to_hpa(data["msl"].sel(time=t))
        low = eu.find_low_center(field)
        rows.append({
            "time": pd.Timestamp(t),
            "day_offset": int(data["day_offset"].sel(time=t).values)
            if "day_offset" in data.coords else np.nan,
            "lon": low["lon"],
            "lat": low["lat"],
            "mslp_hpa": round(low["value"], 1),
        })
    return pd.DataFrame(rows)


def daily_rain(ds: xr.Dataset) -> xr.DataArray:
    """
    ฝนสะสมรายวัน (mm)

    ตัวแปร tp ในไฟล์ของเราคือฝนสะสมในช่วง 6 ชั่วโมงที่สิ้นสุด ณ เวลานั้น หน่วย mm
    จึงรวมทั้ง 4 ช่วงของแต่ละวันเพื่อให้ได้ฝนรายวัน
    """
    out = ds["tp"].resample(time="1D").sum()
    out.attrs["units"] = "mm"
    out.attrs["long_name"] = "Daily total precipitation"
    return out


def point_series(ds: xr.Dataset, points: dict) -> pd.DataFrame:
    """
    ดึงค่าตัวแปรที่พิกัดจุดที่สนใจ ทุกช่วงเวลา แล้วจัดเป็นตาราง

    points : dict ชื่อสถานที่ -> (lat, lon)
    """
    rows = []
    for name, (lat, lon) in points.items():
        p = ds.sel(latitude=lat, longitude=lon, method="nearest")
        for i, t in enumerate(ds["time"].values):
            pt = p.sel(time=t)
            u850 = float(pt["u"].sel(level=850))
            v850 = float(pt["v"].sel(level=850))
            rows.append({
                "place": name,
                "time": pd.Timestamp(t),
                "day_offset": int(pt["day_offset"].values)
                if "day_offset" in pt.coords else np.nan,
                "mslp_hpa": round(float(pt["msl"]) / 100, 1),
                "t2m_c": round(float(pt["t2m"]) - 273.15, 1),
                "rain_mm": round(float(pt["tp"]), 2),
                "rh850": round(float(pt["r"].sel(level=850)), 1),
                "ws850": round(float(np.sqrt(u850**2 + v850**2)), 1),
                "wdir850": round(float((270 - np.degrees(np.arctan2(v850, u850))) % 360)),
            })
    return pd.DataFrame(rows)


def case_summary(ds: xr.Dataset, case_id: str) -> pd.DataFrame:
    """ตารางสรุปรายวันของเคส: ความกดอากาศต่ำสุด ฝนสูงสุด ลมแรงสุด ความชื้นเฉลี่ย"""
    info = case_info(case_id)
    rain_d = daily_rain(ds)
    rows = []
    for day in rain_d["time"].values:
        day_ts = pd.Timestamp(day)
        sel = ds.sel(time=str(day_ts.date()))
        ws = eu.wind_speed(sel["u"].sel(level=850), sel["v"].sel(level=850))
        rows.append({
            "date": day_ts.date().isoformat(),
            "day_offset": int((day_ts.normalize() - pd.Timestamp(info["d0"])).days),
            "mslp_min_hpa": round(float(sel["msl"].min()) / 100, 1),
            "rain_max_mm": round(float(rain_d.sel(time=day).max()), 1),
            "ws850_max_ms": round(float(ws.max()), 1),
            "rh850_mean_pct": round(float(sel["r"].sel(level=850).mean()), 1),
        })
    return pd.DataFrame(rows)


# ------------------------------------------------------------------
# STEP 3 : แผนภาพสำเร็จรูป
# ------------------------------------------------------------------
def panel_daily(ds: xr.Dataset, case_id: str, variable: str = "rain",
                ncols: int = 4, figsize=(16, 8), savepath: str | None = None):
    """
    แผนที่รายวันเรียงเป็นตาราง ตั้งแต่ D-5 ถึง D+2

    variable : "rain"  = ฝนสะสมรายวัน + เส้นความกดอากาศ
               "wind"  = ลมและความเร็วลมที่ 850 hPa
               "rh"    = ความชื้นสัมพัทธ์ที่ 850 hPa
    """
    import cartopy.crs as ccrs
    import matplotlib.pyplot as plt

    info = case_info(case_id)
    rain_d = daily_rain(ds)
    days = rain_d["time"].values
    nrows = int(np.ceil(len(days) / ncols))

    fig, axes = plt.subplots(nrows, ncols, figsize=figsize,
                             subplot_kw={"projection": ccrs.PlateCarree()})
    axes = np.atleast_1d(axes).ravel()

    settings = {
        "rain": dict(cmap="GnBu", levels=[1, 5, 10, 20, 40, 60, 80, 120, 160],
                     label="ฝนสะสมรายวัน (mm)"),
        "wind": dict(cmap="YlGnBu", levels=np.arange(0, 31, 2.5),
                     label="ความเร็วลม 850 hPa (m s$^{-1}$)"),
        "rh": dict(cmap="BrBG", levels=np.arange(20, 101, 5),
                   label="ความชื้นสัมพัทธ์ 850 hPa (%)"),
    }[variable]

    cf = None
    for ax, day in zip(axes, days):
        day_str = str(pd.Timestamp(day).date())
        sel = ds.sel(time=day_str)
        eu.make_map_axes(ax=ax, domain=info["domain"])

        if variable == "rain":
            field = rain_d.sel(time=day)
        elif variable == "wind":
            field = eu.wind_speed(sel["u"].sel(level=850),
                                  sel["v"].sel(level=850)).mean(dim="time")
        else:
            field = sel["r"].sel(level=850).mean(dim="time")

        cf = eu.shade(ax, field, cmap=settings["cmap"], levels=settings["levels"],
                      extend="max")
        eu.contour(ax, eu.to_hpa(sel["msl"].mean(dim="time")),
                   levels=np.arange(960, 1021, 4), color="black",
                   linewidth=0.6, label_fmt="%d", inline_fontsize=6)

        offset = int((pd.Timestamp(day).normalize()
                      - pd.Timestamp(info["d0"])).days)
        tag = "D0 (วันเกิดเหตุ)" if offset == 0 else f"D{offset:+d}"
        ax.set_title(f"{day_str}  {tag}", fontsize=9, loc="left",
                     color="crimson" if offset == 0 else "black",
                     fontweight="bold" if offset == 0 else "normal")

    for ax in axes[len(days):]:
        ax.set_visible(False)

    if cf is not None:
        fig.colorbar(cf, ax=axes.tolist(), orientation="horizontal",
                     shrink=0.4, pad=0.04, label=settings["label"])
    fig.suptitle(f"{info['name_th']} — {settings['label']} รายวัน D-5 ถึง D+2",
                 fontsize=13)
    if savepath:
        fig.savefig(savepath, dpi=200, bbox_inches="tight")
        print("บันทึกรูป:", savepath)
    return fig


def plot_track(ds: xr.Dataset, case_id: str, savepath: str | None = None):
    """แผนที่เส้นทางพายุที่คำนวณจาก ERA5 พร้อมไล่สีตามความกดอากาศ"""
    import cartopy.crs as ccrs
    import matplotlib.pyplot as plt

    info = case_info(case_id)
    if info.get("kind") != "tropical_cyclone":
        print("หมายเหตุ: เหตุการณ์นี้ไม่ใช่พายุหมุนเขตร้อนที่มีศูนย์กลางชัดเจน")
        print("เส้นที่ได้คือ 'จุดความกดอากาศต่ำสุดในโดเมน' ซึ่งอาจกระโดดไปมา")
        print("ให้ดูสนามความกดอากาศและฝนสะสมแทนการติดตามศูนย์กลาง")
    track = track_from_mslp(ds)

    ax = eu.make_map_axes(domain=info["domain"], figsize=(10, 8))
    ax.plot(track["lon"], track["lat"], "-", color="gray", linewidth=1.2,
            transform=ccrs.PlateCarree(), zorder=4)
    sc = ax.scatter(track["lon"], track["lat"], c=track["mslp_hpa"],
                    cmap="plasma_r", s=55, edgecolor="black", linewidth=0.5,
                    transform=ccrs.PlateCarree(), zorder=5)

    for _, r in track[track["time"].dt.hour == 0].iterrows():
        ax.text(r["lon"] + 0.3, r["lat"] + 0.3,
                f"D{int(r['day_offset']):+d}", fontsize=8,
                transform=ccrs.PlateCarree(), zorder=6)

    for name, (lat, lon) in info["focus_points"].items():
        ax.plot(lon, lat, marker="^", color="red", markersize=8,
                transform=ccrs.PlateCarree(), zorder=6)
        ax.text(lon + 0.2, lat - 0.45, name, fontsize=8, color="darkred",
                transform=ccrs.PlateCarree(), zorder=6)

    eu.finish(ax, title=f"{info['name_th']} — เส้นทางศูนย์กลางที่คำนวณจาก ERA5",
              mappable=sc, cbar_label="ความกดอากาศที่ศูนย์กลาง (hPa)",
              savepath=savepath)
    return ax, track


def plot_intensity(ds: xr.Dataset, case_id: str, savepath: str | None = None):
    """กราฟความกดอากาศต่ำสุดและลมแรงสุดตามเวลา พร้อมเส้นแบ่งวันเกิดเหตุ"""
    import matplotlib.pyplot as plt

    info = case_info(case_id)
    track = track_from_mslp(ds)
    ws_max = [float(eu.wind_speed(ds["u"].sel(level=850, time=t),
                                  ds["v"].sel(level=850, time=t)).max())
              for t in ds["time"].values]

    fig, ax1 = plt.subplots(figsize=(11, 4.5))
    ax1.plot(track["time"], track["mslp_hpa"], "o-", color="navy",
             label="ความกดอากาศต่ำสุด")
    ax1.set_ylabel("ความกดอากาศต่ำสุด (hPa)", color="navy")
    ax1.tick_params(axis="y", labelcolor="navy")
    ax1.invert_yaxis()

    ax2 = ax1.twinx()
    ax2.plot(ds["time"].values, ws_max, "s--", color="darkred", markersize=4,
             label="ลมแรงสุด 850 hPa")
    ax2.set_ylabel("ความเร็วลมสูงสุด 850 hPa (m s$^{-1}$)", color="darkred")
    ax2.tick_params(axis="y", labelcolor="darkred")

    ax1.axvline(pd.Timestamp(info["d0"]), color="crimson", linestyle=":",
                linewidth=2)
    ax1.text(pd.Timestamp(info["d0"]), ax1.get_ylim()[0], " D0",
             color="crimson", fontweight="bold", va="bottom")

    ax1.set_title(f"{info['name_th']} — ความรุนแรงตามเวลา D-5 ถึง D+2", loc="left")
    ax1.grid(alpha=0.3)
    fig.autofmt_xdate()
    if savepath:
        fig.savefig(savepath, dpi=200, bbox_inches="tight")
        print("บันทึกรูป:", savepath)
    return fig


def compare_cases(datasets: dict) -> pd.DataFrame:
    """
    ตารางเปรียบเทียบทั้งสามเหตุการณ์

    datasets : dict case_id -> Dataset
    """
    rows = []
    for case_id, ds in datasets.items():
        info = case_info(case_id)
        track = track_from_mslp(ds)
        rain_d = daily_rain(ds)
        focus = eu.subset(ds, domain=info["focus_domain"])
        focus_rain = focus["tp"].sum(dim="time")
        rows.append({
            "เหตุการณ์": info["name_th"],
            "ปี": info["year"],
            "D0": info["d0"],
            "ความกดต่ำสุด (hPa)": track["mslp_hpa"].min(),
            "ฝนรายวันสูงสุดในโดเมน (mm)": round(float(rain_d.max()), 1),
            "ฝนรวมสูงสุดในพื้นที่ศึกษา (mm)": round(float(focus_rain.max()), 1),
            "ลมแรงสุด 850 hPa (m/s)": round(float(
                eu.wind_speed(ds["u"].sel(level=850), ds["v"].sel(level=850)).max()), 1),
        })
    return pd.DataFrame(rows)

def accumulated_rain(ds: xr.Dataset, start: str | None = None,
                     end: str | None = None) -> xr.DataArray:
    """
    ฝนสะสมรวมตลอดช่วงที่ระบุ (mm)

    start/end เป็นสตริงวันที่ เช่น "2026-09-24" ถ้าไม่ระบุจะรวมทั้งไฟล์
    """
    data = ds["tp"]
    if start or end:
        data = data.sel(time=slice(start, end))
    out = data.sum(dim="time")
    out.attrs = {"units": "mm", "long_name": "Accumulated precipitation"}
    return out


def plot_accumulated_rain(ds: xr.Dataset, case_id: str, start=None, end=None,
                          levels=None, savepath: str | None = None):
    """แผนที่ฝนสะสมตลอดช่วง พร้อมหมุดจุดที่สนใจ"""
    import cartopy.crs as ccrs
    import matplotlib.pyplot as plt

    info = case_info(case_id)
    acc = accumulated_rain(ds, start, end)
    if levels is None:
        levels = [10, 25, 50, 75, 100, 150, 200, 300, 400]

    ax = eu.make_map_axes(domain=info["domain"], figsize=(9.5, 8))
    cf = eu.shade(ax, acc, cmap="GnBu", levels=levels, extend="max")

    for name, (lat, lon) in info["focus_points"].items():
        ax.plot(lon, lat, "r^", markersize=8, transform=ccrs.PlateCarree(), zorder=6)
        ax.text(lon + 0.15, lat + 0.1, name, fontsize=8, color="darkred",
                transform=ccrs.PlateCarree(), zorder=6)

    span = f"{start or info['start']} ถึง {end or info['end']}"
    eu.finish(ax, title=f"{info['name_th']} — ฝนสะสม {span}",
              mappable=cf, cbar_label="ฝนสะสม (mm)", savepath=savepath)
    print(f"ฝนสะสมสูงสุดในโดเมน {float(acc.max()):.1f} mm")
    return ax, acc


def compare_with_gauge(ds: xr.Dataset, case_id: str, day: str | None = None) -> pd.DataFrame:
    """
    เทียบฝนสะสม 24 ชั่วโมงจาก ERA5 กับค่าที่สถานีตรวจวัดรายงานในข่าว

    ใช้ได้เฉพาะเคสที่มีฟิลด์ gauge_check
    จุดประสงค์คือให้เห็นว่า reanalysis กับการตรวจวัดจุดเดียวต่างกันอย่างไร
    ไม่ใช่เพื่อตัดสินว่าอันไหน "ถูก" — ทั้งคู่วัดคนละสิ่ง
    """
    info = case_info(case_id)
    if "gauge_check" not in info:
        raise KeyError(f"เคส {case_id} ไม่มีข้อมูล gauge_check")

    day = day or info["d0"]
    rows = []
    for name, (lat, lon) in info["focus_points"].items():
        era5 = float(ds["tp"].sel(latitude=lat, longitude=lon,
                                  method="nearest").sel(time=day).sum())
        rows.append({"จุด": name, "ERA5 ฝน 24 ชม. (mm)": round(era5, 1)})
    out = pd.DataFrame(rows)

    gauge = pd.DataFrame([{"สถานีตรวจวัดจากข่าว": k, "ฝน 24 ชม. (mm)": v}
                          for k, v in info["gauge_check"].items()])
    print("ค่าที่สถานีตรวจวัดรายงาน (จากข่าว)")
    print(gauge.to_string(index=False))
    print()
    return out
