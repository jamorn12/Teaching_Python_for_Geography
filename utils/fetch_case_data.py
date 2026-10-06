"""
fetch_case_data.py
------------------------------------------------------------------
ดึงข้อมูล ERA5 reanalysis **ของจริง** สำหรับกรณีศึกษาพายุ 3 เหตุการณ์
แล้วเขียนเป็นไฟล์ NetCDF เล็ก ๆ ที่พร้อมอัปขึ้น GitHub

ผู้สอนรันไฟล์นี้ครั้งเดียว แล้ว commit ผลลัพธ์ขึ้น repo
จากนั้นนักศึกษาโหลดไฟล์จาก GitHub ได้เลย ไม่ต้องสมัคร CDS ไม่ต้องรอคิว

------------------------------------------------------------------
วิธีใช้ (แนะนำให้รันบน Google Colab เพราะดาวน์โหลดเร็วกว่า)

  แหล่งที่ 1 — Google Cloud (ARCO-ERA5) ไม่ต้องสมัครอะไรเลย
      !pip install -q gcsfs zarr xarray netcdf4
      !python fetch_case_data.py --source gcs --outdir data/cases

  แหล่งที่ 2 — Copernicus CDS (ต้องสมัครบัญชีฟรี และกดยอมรับ license ก่อน)
      !pip install -q cdsapi
      # เขียนไฟล์ ~/.cdsapirc ให้เรียบร้อยก่อน (ดูภาคผนวกในโน้ตบุ๊กบทที่ 12)
      !python fetch_case_data.py --source cds --outdir data/cases

  ดึงเฉพาะบางเคส
      !python fetch_case_data.py --source gcs --cases dianmu2021 noru2022

------------------------------------------------------------------
⚠️ เหตุการณ์ที่เพิ่งเกิดไม่นาน (เช่น bangkok2026) ให้ใช้ --source cds

ERA5 รุ่นสมบูรณ์ออกช้ากว่าเวลาจริงประมาณ 2-3 เดือน ส่วนรุ่นเบื้องต้น (ERA5T)
ออกเร็วกว่ามากและเข้าถึงได้ผ่าน CDS แต่สำเนาบน Google Cloud มักตามหลังหลายเดือน
ถ้า --source gcs แล้วได้ข้อมูลเปล่าหรือ error เรื่องช่วงเวลา ให้เปลี่ยนไปใช้ CDS

      !python fetch_case_data.py --source cds --cases bangkok2026

------------------------------------------------------------------
โครงสร้างไฟล์ผลลัพธ์ (เหมือนกันทุกเคส และเหมือนไฟล์สาธิต era5_demo)

  มิติ      time (ราย 6 ชั่วโมง) x level x latitude x longitude
  level     1000, 925, 850, 700, 500, 200 hPa
  ความละเอียด 0.5 องศา (ปรับได้ด้วย --resolution)
  ตัวแปร    msl, t2m, tp, u, v, z, r

  หน่วยถูกเก็บตามต้นฉบับ ERA5 ทุกตัว **ยกเว้น tp**
  ซึ่งแปลงเป็น **มิลลิเมตรสะสมในช่วง 6 ชั่วโมงที่สิ้นสุด ณ เวลานั้น**
  เพราะ tp ต้นฉบับเป็นค่าสะสมรายชั่วโมงหน่วยเมตร ถ้าสุ่มเอาทุก 6 ชั่วโมงตรง ๆ
  ฝนจะหายไป 5 ใน 6 ส่วน ซึ่งเป็นกับดักที่คนใช้ ERA5 ครั้งแรกพลาดกันบ่อยที่สุด
"""

from __future__ import annotations

import argparse
import os
import sys

import numpy as np
import pandas as pd
import xarray as xr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from era5_cases import CASE_ORDER, CASES  # noqa: E402

LEVELS = [1000, 925, 850, 700, 500, 200]

# ชื่อตัวแปรแบบเต็มของ ARCO-ERA5 -> ชื่อย่อแบบ CDS ที่โน้ตบุ๊กใช้
GCS_RENAME = {
    "2m_temperature": "t2m",
    "mean_sea_level_pressure": "msl",
    "total_precipitation": "tp",
    "u_component_of_wind": "u",
    "v_component_of_wind": "v",
    "geopotential": "z",
    "relative_humidity": "r",
}

ARCO_STORE = (
    "gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3"
)


# ------------------------------------------------------------------
# แหล่งที่ 1 : Google Cloud ARCO-ERA5 (ไม่ต้องสมัคร)
# ------------------------------------------------------------------
def fetch_from_gcs(case: dict, resolution: float) -> xr.Dataset:
    """อ่าน ERA5 จาก public zarr store บน Google Cloud แบบไม่ต้องยืนยันตัวตน"""
    import gcsfs  # noqa: F401  ต้องติดตั้งไว้ ถึงจะเปิด gs:// ได้

    print("  เปิด zarr store บน Google Cloud (อ่านเฉพาะส่วนที่ใช้ ไม่โหลดทั้งก้อน)")
    full = xr.open_zarr(ARCO_STORE, chunks=None, storage_options={"token": "anon"})

    lon0, lon1, lat0, lat1 = case["domain"]
    start = pd.Timestamp(case["start"])
    end = pd.Timestamp(case["end"]) + pd.Timedelta(hours=23)

    store_end = pd.Timestamp(full["time"].values[-1])
    if end > store_end:
        raise RuntimeError(
            f"ข้อมูลบน Google Cloud มีถึง {store_end:%Y-%m-%d} เท่านั้น "
            f"แต่เคสนี้ต้องการถึง {end:%Y-%m-%d}\n"
            "เหตุการณ์ที่เพิ่งเกิดยังไม่ถูก mirror ขึ้น GCS ให้ใช้ --source cds แทน")

    wanted = [v for v in GCS_RENAME if v in full.data_vars]
    sub = full[wanted].sel(time=slice(start, end))

    # ARCO-ERA5 เรียง latitude จากมากไปน้อย จึง slice กลับด้าน
    lat_desc = float(sub["latitude"][0]) > float(sub["latitude"][-1])
    sub = sub.sel(latitude=slice(lat1, lat0) if lat_desc else slice(lat0, lat1),
                  longitude=slice(lon0, lon1))
    if "level" in sub.dims:
        sub = sub.sel(level=[l for l in LEVELS if l in sub["level"].values])

    sub = sub.rename({k: v for k, v in GCS_RENAME.items() if k in sub})
    print("  กำลังโหลดข้อมูลลงหน่วยความจำ")
    return _finalize(sub.load(), case, resolution, tp_in_metres=True)


# ------------------------------------------------------------------
# แหล่งที่ 2 : Copernicus CDS (ต้องสมัคร)
# ------------------------------------------------------------------
def fetch_from_cds(case: dict, resolution: float, workdir: str) -> xr.Dataset:
    """ขอข้อมูลจาก Copernicus Climate Data Store สองชุดแล้วรวมกัน"""
    import cdsapi

    client = cdsapi.Client()
    days = pd.date_range(case["start"], case["end"], freq="D")
    years = sorted({f"{d.year}" for d in days})
    months = sorted({f"{d.month:02d}" for d in days})
    daynums = sorted({f"{d.day:02d}" for d in days})
    hours = [f"{h:02d}:00" for h in range(24)]
    lon0, lon1, lat0, lat1 = case["domain"]
    area = [lat1, lon0, lat0, lon1]          # เหนือ ตะวันตก ใต้ ตะวันออก

    pl_path = os.path.join(workdir, f"_{case['id']}_pl.nc")
    sl_path = os.path.join(workdir, f"_{case['id']}_sl.nc")

    if not os.path.exists(pl_path):
        print("  ขอข้อมูล pressure levels จาก CDS (อาจรอคิวสักครู่)")
        client.retrieve(
            "reanalysis-era5-pressure-levels",
            {
                "product_type": "reanalysis",
                "format": "netcdf",
                "variable": ["geopotential", "relative_humidity",
                             "u_component_of_wind", "v_component_of_wind"],
                "pressure_level": [str(l) for l in LEVELS],
                "year": years, "month": months, "day": daynums,
                "time": [f"{h:02d}:00" for h in range(0, 24, 6)],
                "area": area,
                "grid": [resolution, resolution],
            },
            pl_path,
        )

    if not os.path.exists(sl_path):
        print("  ขอข้อมูล single levels จาก CDS (ขอรายชั่วโมงเพราะต้องรวมฝน)")
        client.retrieve(
            "reanalysis-era5-single-levels",
            {
                "product_type": "reanalysis",
                "format": "netcdf",
                "variable": ["2m_temperature", "mean_sea_level_pressure",
                             "total_precipitation"],
                "year": years, "month": months, "day": daynums,
                "time": hours,
                "area": area,
                "grid": [resolution, resolution],
            },
            sl_path,
        )

    import era5_utils as eu
    pl = eu.open_era5(pl_path)
    sl = eu.open_era5(sl_path)
    merged = xr.merge([pl, sl], compat="override", join="inner")
    return _finalize(merged, case, resolution=None, tp_in_metres=True)


# ------------------------------------------------------------------
# จัดรูปข้อมูลให้เป็นมาตรฐานเดียวกัน
# ------------------------------------------------------------------
def _finalize(ds: xr.Dataset, case: dict, resolution: float | None,
              tp_in_metres: bool) -> xr.Dataset:
    """ลดความละเอียด รวมฝนเป็นราย 6 ชั่วโมง และใส่ attribute ให้ครบ"""
    if "latitude" in ds.coords and float(ds["latitude"][0]) > float(ds["latitude"][-1]):
        ds = ds.sortby("latitude")

    # ลดความละเอียดเชิงพื้นที่ (ERA5 ต้นฉบับ 0.25 องศา)
    if resolution:
        step = max(int(round(resolution / 0.25)), 1)
        if step > 1:
            ds = ds.isel(latitude=slice(None, None, step),
                         longitude=slice(None, None, step))

    # ---- ฝน: รวมรายชั่วโมงเป็นราย 6 ชั่วโมง แล้วแปลงเป็นมิลลิเมตร ----
    if "tp" in ds:
        tp = ds["tp"]
        if tp_in_metres:
            tp = tp * 1000.0
        hours = pd.to_datetime(tp["time"].values)
        if len(hours) > 1 and (hours[1] - hours[0]) < pd.Timedelta(hours=6):
            tp = tp.resample(time="6h", closed="right", label="right").sum()
        tp.attrs = {"long_name": "Total precipitation (6-hour accumulation)",
                    "units": "mm"}
        ds = ds.drop_vars("tp")
    else:
        tp = None

    # ---- ตัวแปรอื่น: เก็บทุก 6 ชั่วโมง ----
    ds = ds.sel(time=ds["time"].dt.hour.isin([0, 6, 12, 18]))
    if tp is not None:
        ds["tp"] = tp.sel(time=ds["time"])

    ds.attrs.update({
        "title": f"ERA5 subset for case study: {case['name_en']}",
        "case_id": case["id"],
        "case_name_th": case["name_th"],
        "d0": case["d0"],
        "source": "ECMWF ERA5 reanalysis (Hersbach et al., 2020)",
        "licence": "Copernicus Climate Change Service (C3S) — ต้องอ้างอิงแหล่งข้อมูลเมื่อนำไปใช้",
        "processing": ("ตัดโดเมนและช่วงเวลา, ลดความละเอียดเชิงพื้นที่, "
                       "tp รวมเป็นฝนสะสมราย 6 ชั่วโมงหน่วยมิลลิเมตร"),
        "created_by": "fetch_case_data.py",
    })
    return ds


def write_case(ds: xr.Dataset, case_id: str, outdir: str) -> str:
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, f"{case_id}.nc")
    enc = {v: {"zlib": True, "complevel": 4, "dtype": "float32"} for v in ds.data_vars}
    ds.to_netcdf(path, encoding=enc)
    size = os.path.getsize(path) / 1024 / 1024
    print(f"  เขียนไฟล์ {path}  ({size:.2f} MB)")
    print(f"  มิติ {dict(ds.sizes)}")
    if "msl" in ds:
        print(f"  ความกดอากาศต่ำสุดในช่วงนี้ {float(ds['msl'].min())/100:.1f} hPa")
    if "tp" in ds:
        print(f"  ฝนสูงสุดต่อ 6 ชั่วโมง {float(ds['tp'].max()):.1f} mm")
    return path


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--source", choices=["gcs", "cds"], default="gcs")
    p.add_argument("--outdir", default="data/cases")
    p.add_argument("--workdir", default=".")
    p.add_argument("--resolution", type=float, default=0.5,
                   help="ความละเอียดเริ่มต้น ใช้เมื่อเคสไม่ได้ระบุไว้เอง")
    p.add_argument("--resolution-override", type=float, default=None,
                   help="บังคับใช้ความละเอียดนี้กับทุกเคส ทับค่าที่เคสกำหนดไว้")
    p.add_argument("--cases", nargs="*", default=CASE_ORDER)
    args = p.parse_args()

    for case_id in args.cases:
        case = CASES[case_id]
        print(f"\n=== {case['name_th']} ({case['start']} ถึง {case['end']}) ===")
        res = case.get("resolution", args.resolution)
        if args.resolution_override is not None:
            res = args.resolution_override
        print(f"  ความละเอียด {res} องศา | ชนิดเหตุการณ์ {case.get('kind', '-')}")
        if args.source == "gcs":
            ds = fetch_from_gcs(case, res)
        else:
            ds = fetch_from_cds(case, res, args.workdir)
        write_case(ds, case_id, args.outdir)

    print("\nเสร็จแล้ว — commit โฟลเดอร์ data/cases/ ขึ้น GitHub ได้เลย")


if __name__ == "__main__":
    main()
