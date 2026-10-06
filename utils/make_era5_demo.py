"""
make_era5_demo.py
------------------------------------------------------------------
สร้างไฟล์ NetCDF ที่มีโครงสร้างเหมือน ERA5 reanalysis ทุกประการ
(ชื่อตัวแปร มิติ หน่วย และ attribute ตาม CF convention)
สำหรับใช้สอนการพล็อตแผนที่อากาศ

ข้อมูลนี้ "ไม่ใช่" ERA5 ของจริง เป็นสนามจำลองที่สร้างด้วยสมการง่าย ๆ
ให้มีลักษณะทางอุตุนิยมวิทยาที่สอดคล้องกันเอง:
  - พายุดีเปรสชันเคลื่อนตัวจากอ่าวตังเกี๋ยเข้าสู่อินโดจีน
  - ลมหมุนทวนเข็มนาฬิกา (cyclonic) รอบศูนย์กลางความกดอากาศต่ำ
  - ลมมรสุมตะวันตกเฉียงใต้เป็นลมพื้นหลังที่ระดับ 850 hPa
  - ความชื้นและฝนกระจุกตัวรอบศูนย์กลาง
  - อุณหภูมิมีทั้ง gradient ตามละติจูดและ diurnal cycle

ข้อดีของการจำลอง: นักศึกษาเห็นความสัมพันธ์ระหว่างสนามความกดอากาศกับลม
ได้ชัดกว่าข้อมูลจริงที่มี noise เยอะ และไม่ต้องสมัคร CDS API ก่อนเข้าเรียน

เมื่อเปลี่ยนไปใช้ ERA5 จริง โค้ดพล็อตทุกบรรทัดใช้ได้เหมือนเดิม
เพราะชื่อตัวแปรและมิติตรงกันทุกตัว

รันแบบ stand-alone:
    python make_era5_demo.py --outdir ../data
"""

import argparse
import os

import numpy as np
import pandas as pd
import xarray as xr

# ---------------------------------------------------------------
# ค่าตั้งต้นของโดเมนและเวลา
# ---------------------------------------------------------------
LON_MIN, LON_MAX, DLON = 90.0, 115.0, 0.25
LAT_MIN, LAT_MAX, DLAT = 0.0, 25.0, 0.25
LEVELS = [1000, 925, 850, 700, 500, 200]
TIMES = pd.date_range("2025-09-14 00:00", periods=4, freq="6h")

# เส้นทางศูนย์กลางพายุ (lon, lat) ของแต่ละเวลา — เคลื่อนจากอ่าวตังเกี๋ยเข้าแผ่นดิน
TRACK = [(109.0, 15.5), (107.0, 16.2), (105.0, 16.8), (103.0, 17.2)]

RMAX_DEG = 2.2      # รัศมีลมแรงสูงสุด (องศา)
VMAX = 24.0         # ความเร็วลมสูงสุดที่ 850 hPa (m/s)
MSL_DEEP = 22.0     # ความลึกของหย่อมความกดอากาศต่ำ (hPa)


def _distance_deg(lon2d, lat2d, clon, clat):
    """ระยะเชิงมุมจากศูนย์กลาง ปรับ lon ตาม cos(lat) ให้ใกล้เคียงระยะจริง"""
    dx = (lon2d - clon) * np.cos(np.radians(lat2d))
    dy = lat2d - clat
    return np.sqrt(dx**2 + dy**2), dx, dy


def _vortex_wind(lon2d, lat2d, clon, clat, vmax, rmax):
    """
    โปรไฟล์ลมหมุนแบบ Rankine ที่ปรับให้เรียบ
    V(r) = vmax * (r/rmax) * exp(1 - r/rmax)  -> แรงสุดที่ r = rmax
    คืนค่า (u, v) ของลมหมุนทวนเข็มนาฬิกา (ซีกโลกเหนือ)
    """
    r, dx, dy = _distance_deg(lon2d, lat2d, clon, clat)
    r_safe = np.maximum(r, 1e-6)
    speed = vmax * (r_safe / rmax) * np.exp(1.0 - r_safe / rmax)
    # เวกเตอร์สัมผัสวงกลม หมุนทวนเข็ม: (-dy, dx)/r
    u = -speed * dy / r_safe
    v = speed * dx / r_safe
    return u, v, r


def build_dataset() -> xr.Dataset:
    lon = np.arange(LON_MIN, LON_MAX + DLON / 2, DLON)
    lat = np.arange(LAT_MAX, LAT_MIN - DLAT / 2, -DLAT)   # ERA5 เรียง lat จากมากไปน้อย
    lon2d, lat2d = np.meshgrid(lon, lat)

    nt, nz, ny, nx = len(TIMES), len(LEVELS), len(lat), len(lon)
    msl = np.zeros((nt, ny, nx))
    t2m = np.zeros((nt, ny, nx))
    tp = np.zeros((nt, ny, nx))
    u = np.zeros((nt, nz, ny, nx))
    v = np.zeros((nt, nz, ny, nx))
    z = np.zeros((nt, nz, ny, nx))
    r_h = np.zeros((nt, nz, ny, nx))

    rng = np.random.default_rng(914)

    for it, (t, (clon, clat)) in enumerate(zip(TIMES, TRACK)):
        dist, _, _ = _distance_deg(lon2d, lat2d, clon, clat)

        # ---- ความกดอากาศที่ระดับน้ำทะเล (hPa -> Pa) ----
        low = MSL_DEEP * np.exp(-(dist**2) / (2 * 3.0**2))
        ridge = 4.0 * np.exp(-((lat2d - 3.0) ** 2) / (2 * 5.0**2))   # สันความกดอากาศสูงใกล้ศูนย์สูตร
        msl_hpa = 1010.0 - low + ridge
        msl[it] = msl_hpa * 100.0

        # ---- อุณหภูมิ 2 เมตร (K) ----
        lat_grad = -0.55 * (lat2d - 10.0)                 # เหนือเย็นกว่าใต้
        diurnal = 2.8 * np.cos(np.radians((t.hour + 7 - 14) * 15.0))   # เวลาไทย = UTC+7 ร้อนสุดบ่าย 2
        cloud_cool = -4.5 * np.exp(-(dist**2) / (2 * 3.5**2))
        t2m[it] = 302.0 + lat_grad + diurnal + cloud_cool + rng.normal(0, 0.25, (ny, nx))

        # ---- ฝนสะสม (m ตามหน่วยของ ERA5) ----
        band = np.exp(-((dist - 1.6) ** 2) / (2 * 1.1**2))
        core = 0.45 * np.exp(-(dist**2) / (2 * 0.9**2))
        rain_mm = 26.0 * (band + core) * (0.75 + 0.25 * rng.random((ny, nx)))
        tp[it] = np.maximum(rain_mm, 0.0) / 1000.0

        for iz, lev in enumerate(LEVELS):
            # ความแรงของลมหมุนลดลงตามความสูง (vortex ตื้น)
            decay = {1000: 0.85, 925: 1.00, 850: 1.00, 700: 0.80, 500: 0.50, 200: 0.15}[lev]
            uu, vv, _ = _vortex_wind(lon2d, lat2d, clon, clat, VMAX * decay, RMAX_DEG)

            # ลมพื้นหลัง: มรสุมตะวันตกเฉียงใต้ชั้นล่าง, ลมตะวันออกชั้นบน
            if lev >= 700:
                bg_u, bg_v = 7.5, 2.5
            elif lev == 500:
                bg_u, bg_v = 4.0, 0.5
            else:
                bg_u, bg_v = -9.0, 0.0        # easterly ที่ 200 hPa
            u[it, iz] = uu + bg_u
            v[it, iz] = vv + bg_v

            # ---- geopotential (m2 s-2) จากความสูงมาตรฐานของแต่ละระดับ ----
            base_gpm = {1000: 110.0, 925: 780.0, 850: 1480.0,
                        700: 3120.0, 500: 5880.0, 200: 12420.0}[lev]
            tilt = -(lat2d - 10.0) * {1000: 1.5, 925: 2.0, 850: 2.6,
                                      700: 4.5, 500: 8.0, 200: 12.0}[lev]
            dip = -(MSL_DEEP * 8.0 * decay) * np.exp(-(dist**2) / (2 * 3.0**2))
            z[it, iz] = (base_gpm + tilt + dip) * 9.80665

            # ---- ความชื้นสัมพัทธ์ (%) ----
            moist_core = 38.0 * np.exp(-(dist**2) / (2 * 3.2**2))
            dry_aloft = {1000: 0, 925: 0, 850: -3, 700: -12, 500: -22, 200: -40}[lev]
            r_h[it, iz] = np.clip(
                58.0 + moist_core + dry_aloft - 0.8 * (lat2d - 10.0)
                + rng.normal(0, 1.5, (ny, nx)), 2.0, 100.0)

    ds = xr.Dataset(
        data_vars={
            "t2m": (("time", "latitude", "longitude"), t2m,
                    {"long_name": "2 metre temperature", "units": "K"}),
            "msl": (("time", "latitude", "longitude"), msl,
                    {"long_name": "Mean sea level pressure", "units": "Pa"}),
            "tp": (("time", "latitude", "longitude"), tp,
                   {"long_name": "Total precipitation", "units": "m"}),
            "u": (("time", "level", "latitude", "longitude"), u,
                  {"long_name": "U component of wind", "units": "m s**-1"}),
            "v": (("time", "level", "latitude", "longitude"), v,
                  {"long_name": "V component of wind", "units": "m s**-1"}),
            "z": (("time", "level", "latitude", "longitude"), z,
                  {"long_name": "Geopotential", "units": "m**2 s**-2"}),
            "r": (("time", "level", "latitude", "longitude"), r_h,
                  {"long_name": "Relative humidity", "units": "%"}),
        },
        coords={
            "longitude": ("longitude", lon,
                          {"long_name": "longitude", "units": "degrees_east"}),
            "latitude": ("latitude", lat,
                         {"long_name": "latitude", "units": "degrees_north"}),
            "level": ("level", np.array(LEVELS),
                      {"long_name": "pressure_level", "units": "millibars"}),
            "time": ("time", TIMES, {"long_name": "time"}),
        },
        attrs={
            "title": "Synthetic ERA5-like dataset for teaching",
            "Conventions": "CF-1.6",
            "institution": "สร้างขึ้นเพื่อการเรียนการสอน ไม่ใช่ข้อมูล ECMWF ของจริง",
            "source": "make_era5_demo.py",
            "comment": ("ข้อมูลสังเคราะห์ โครงสร้างเหมือน ERA5 reanalysis "
                        "ใช้ฝึกพล็อตแผนที่อากาศเท่านั้น ห้ามนำไปอ้างอิงทางวิชาการ"),
        },
    )
    return ds


def main(outdir: str = "data", filename: str = "era5_demo_20250914.nc") -> None:
    os.makedirs(outdir, exist_ok=True)
    ds = build_dataset()
    path = os.path.join(outdir, filename)
    comp = {"zlib": True, "complevel": 4, "dtype": "float32"}
    ds.to_netcdf(path, encoding={v: comp for v in ds.data_vars})

    size_mb = os.path.getsize(path) / 1024 / 1024
    print(f"เขียนไฟล์: {path}  ({size_mb:.2f} MB)")
    print(f"มิติ: {dict(ds.sizes)}")
    print(f"ตัวแปร: {list(ds.data_vars)}")
    print(f"ความกดอากาศต่ำสุด: {ds['msl'].min().item()/100:.1f} hPa")
    print(f"ลมแรงสุดที่ 850 hPa: "
          f"{np.sqrt(ds['u'].sel(level=850)**2 + ds['v'].sel(level=850)**2).max().item():.1f} m/s")
    print(f"ฝนสูงสุดต่อช่วงเวลา: {ds['tp'].max().item()*1000:.1f} mm")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--outdir", default="data")
    args = p.parse_args()
    main(args.outdir)
