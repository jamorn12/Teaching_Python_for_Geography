"""
atmos_diag.py
------------------------------------------------------------------
คำนวณตัวแปรวินิจฉัยทางอุตุนิยมวิทยา จากตัวแปรพื้นฐานของ ERA5

ERA5 ให้ตัวแปรดิบมาไม่กี่ตัว (u, v, z, t2m, msl, tp) แต่สิ่งที่นักอุตุนิยมวิทยา
ใช้อ่านสถานการณ์จริง ๆ ส่วนใหญ่เป็นตัวแปรที่ "คำนวณต่อ" จากของดิบเหล่านี้

ทุกฟังก์ชันรับและคืน xarray object ที่มีมิติ latitude / longitude
จึงนำไปพล็อตด้วย contourf ได้ทันที

หน่วยที่ใช้
    ระยะทาง  เมตร
    ความเร็ว m/s
    vorticity, divergence   s^-1
    advection               K/s (มักแปลงเป็น K/day ตอนแสดงผล)
"""

from __future__ import annotations

import numpy as np
import xarray as xr

# ค่าคงที่
EARTH_RADIUS = 6.371e6        # รัศมีโลก (m)
OMEGA = 7.292e-5              # อัตราการหมุนของโลก (rad/s)
GRAVITY = 9.80665             # ความเร่งโน้มถ่วง (m/s2)
R_DRY = 287.05                # ค่าคงที่แก๊สของอากาศแห้ง (J/kg/K)


# ------------------------------------------------------------------
# STEP 1 : เครื่องมือพื้นฐาน — ระยะทางจริงบนกริดละติจูด-ลองจิจูด
# ------------------------------------------------------------------
def grid_spacing(field: xr.DataArray) -> tuple:
    """
    คืนระยะห่างจริงของกริดเป็นเมตร (dx, dy)

    กริดละติจูด–ลองจิจูดมีระยะห่างไม่คงที่ — หนึ่งองศาลองจิจูดสั้นลง
    เมื่อเข้าใกล้ขั้วโลก ต้องคูณ cos(latitude) เสมอ
    ถ้าไม่ปรับ ค่า vorticity และ divergence จะผิดเป็นระบบ
    """
    lat = field["latitude"]
    lon = field["longitude"]

    dlat = float(lat[1] - lat[0])
    dlon = float(lon[1] - lon[0])

    dy = np.deg2rad(dlat) * EARTH_RADIUS
    dx = np.deg2rad(dlon) * EARTH_RADIUS * np.cos(np.deg2rad(lat))
    return dx, dy


def coriolis(field: xr.DataArray) -> xr.DataArray:
    """พารามิเตอร์ Coriolis f = 2 * omega * sin(latitude)  หน่วย s^-1"""
    f = 2 * OMEGA * np.sin(np.deg2rad(field["latitude"]))
    f.name = "f"
    f.attrs = {"long_name": "Coriolis parameter", "units": "s**-1"}
    return f


def _ddx(field: xr.DataArray) -> xr.DataArray:
    """อนุพันธ์ตามแนวตะวันออก-ตะวันตก ด้วยผลต่างกลาง"""
    dx, _ = grid_spacing(field)
    out = xr.apply_ufunc(
        lambda a: np.gradient(a, axis=-1),
        field, dask="parallelized", output_dtypes=[float])
    return out / dx


def _ddy(field: xr.DataArray) -> xr.DataArray:
    """อนุพันธ์ตามแนวเหนือ-ใต้ ด้วยผลต่างกลาง"""
    _, dy = grid_spacing(field)
    out = xr.apply_ufunc(
        lambda a: np.gradient(a, axis=-2),
        field, dask="parallelized", output_dtypes=[float])
    return out / dy


# ------------------------------------------------------------------
# STEP 2 : ตัวแปรวินิจฉัยจากสนามลม
# ------------------------------------------------------------------
def wind_speed(u: xr.DataArray, v: xr.DataArray) -> xr.DataArray:
    """ความเร็วลมลัพธ์ (m/s)"""
    out = np.sqrt(u**2 + v**2)
    out.attrs = {"long_name": "Wind speed", "units": "m s**-1"}
    return out


def wind_direction(u: xr.DataArray, v: xr.DataArray) -> xr.DataArray:
    """ทิศลมแบบอุตุนิยมวิทยา องศา (ทิศที่ลมพัดมาจาก)"""
    out = (270.0 - np.degrees(np.arctan2(v, u))) % 360.0
    out.attrs = {"long_name": "Wind direction (from)", "units": "degrees"}
    return out


def relative_vorticity(u: xr.DataArray, v: xr.DataArray) -> xr.DataArray:
    """
    ความหมุนวนสัมพัทธ์  zeta = dv/dx - du/dy   หน่วย s^-1

    ค่าบวกในซีกโลกเหนือ = หมุนทวนเข็มนาฬิกา = หย่อมความกดอากาศต่ำ
    ค่าทั่วไปของระบบอากาศเขตร้อนอยู่ราว 1e-5 ถึง 5e-4 s^-1
    จึงนิยมแสดงผลเป็นหน่วย 1e-5 s^-1 เพื่อให้อ่านง่าย
    """
    out = _ddx(v) - _ddy(u)
    out.attrs = {"long_name": "Relative vorticity", "units": "s**-1"}
    return out


def absolute_vorticity(u: xr.DataArray, v: xr.DataArray) -> xr.DataArray:
    """ความหมุนวนสัมบูรณ์ = zeta + f (รวมการหมุนของโลกเข้าไปด้วย)"""
    out = relative_vorticity(u, v) + coriolis(u)
    out.attrs = {"long_name": "Absolute vorticity", "units": "s**-1"}
    return out


def divergence(u: xr.DataArray, v: xr.DataArray) -> xr.DataArray:
    """
    การแยกตัวของอากาศ  div = du/dx + dv/dy   หน่วย s^-1

    ค่าลบ = convergence อากาศไหลเข้าหากัน
    ค่าบวก = divergence อากาศไหลออกจากกัน

    ภาพคลาสสิกของฝนตกหนัก คือ convergence ที่ชั้นล่าง (850 hPa)
    คู่กับ divergence ที่ชั้นบน (200 hPa) ซึ่งช่วยดูดอากาศขึ้นไป
    """
    out = _ddx(u) + _ddy(v)
    out.attrs = {"long_name": "Divergence", "units": "s**-1"}
    return out


def deep_layer_shear(u: xr.DataArray, v: xr.DataArray,
                     lower: int = 850, upper: int = 200) -> xr.DataArray:
    """
    ลมเฉือนตามแนวดิ่งระหว่างสองระดับ (m/s)

    คำนวณจากขนาดของเวกเตอร์ผลต่าง ไม่ใช่ผลต่างของขนาด
    สองอย่างนี้ไม่เท่ากัน ถ้าทิศลมเปลี่ยนตามความสูง

    ความหมายสำหรับพายุหมุนเขตร้อน
      ต่ำกว่า 10 m/s   เอื้อให้พายุทวีกำลัง
      10 ถึง 20 m/s    เริ่มจำกัดการพัฒนา
      สูงกว่า 20 m/s   ฉีกโครงสร้างพายุ ทำให้อ่อนกำลัง
    """
    du = u.sel(level=upper) - u.sel(level=lower)
    dv = v.sel(level=upper) - v.sel(level=lower)
    out = np.sqrt(du**2 + dv**2)
    out.attrs = {"long_name": f"Deep layer shear {lower}-{upper} hPa",
                 "units": "m s**-1"}
    return out


def temperature_advection(u: xr.DataArray, v: xr.DataArray,
                          temp: xr.DataArray) -> xr.DataArray:
    """
    การพาความร้อนในแนวราบ  -(u * dT/dx + v * dT/dy)   หน่วย K/s

    ค่าบวก = warm advection ลมพาอากาศอุ่นเข้ามา มักมาพร้อมการยกตัวและเมฆ
    ค่าลบ = cold advection ลมพาอากาศเย็นเข้ามา มักมาพร้อมอากาศจมตัวและท้องฟ้าโปร่ง
    """
    out = -(u * _ddx(temp) + v * _ddy(temp))
    out.attrs = {"long_name": "Temperature advection", "units": "K s**-1"}
    return out


# ------------------------------------------------------------------
# STEP 3 : ตัวแปรวินิจฉัยจากสนามความสูง
# ------------------------------------------------------------------
def geopotential_height(z: xr.DataArray) -> xr.DataArray:
    """geopotential (m2/s2) -> geopotential height (gpm)"""
    out = z / GRAVITY
    out.attrs = {"long_name": "Geopotential height", "units": "gpm"}
    return out


def thickness(z: xr.DataArray, lower: int = 1000, upper: int = 500) -> xr.DataArray:
    """
    ความหนาของชั้นบรรยากาศระหว่างสองระดับความกดอากาศ (gpm)

    ความหนาแปรผันตรงกับอุณหภูมิเฉลี่ยของชั้นนั้น ตามสมการ hypsometric
    ชั้นหนา = อากาศอุ่น · ชั้นบาง = อากาศเย็น

    ค่าอ้างอิงของชั้น 1000-500 hPa
      ต่ำกว่า 5400 gpm   มวลอากาศเย็นมาก (เส้นหิมะคลาสสิกในเขตอบอุ่น)
      ราว 5700-5800      เขตอบอุ่น
      สูงกว่า 5850       มวลอากาศร้อนชื้นแบบเขตร้อน
    """
    out = (z.sel(level=upper) - z.sel(level=lower)) / GRAVITY
    out.attrs = {"long_name": f"Thickness {lower}-{upper} hPa", "units": "gpm"}
    return out


def layer_mean_temperature(z: xr.DataArray, lower: int = 1000,
                           upper: int = 500) -> xr.DataArray:
    """
    อุณหภูมิเฉลี่ยของชั้น คำนวณย้อนกลับจากความหนา (K)

    จากสมการ hypsometric:  Z2 - Z1 = (R * Tbar / g) * ln(p1 / p2)
    จึงได้  Tbar = g * (Z2 - Z1) / (R * ln(p1 / p2))

    มีประโยชน์มากเมื่อไฟล์ข้อมูลไม่มีตัวแปรอุณหภูมิที่ระดับความกดอากาศมาให้
    แต่มี geopotential ซึ่งเป็นกรณีที่พบบ่อย
    """
    dz = (z.sel(level=upper) - z.sel(level=lower)) / GRAVITY
    tbar = GRAVITY * dz / (R_DRY * np.log(lower / upper))
    tbar.attrs = {"long_name": f"Layer mean temperature {lower}-{upper} hPa",
                  "units": "K"}
    return tbar


def geostrophic_wind(z: xr.DataArray) -> tuple:
    """
    ลม geostrophic จากความชันของสนาม geopotential  คืน (ug, vg) หน่วย m/s

      ug = -(1/f) * d(phi)/dy
      vg =  (1/f) * d(phi)/dx

    ใช้ไม่ได้ใกล้เส้นศูนย์สูตร เพราะ f เข้าใกล้ศูนย์แล้วค่าระเบิด
    จึงกรองบริเวณละติจูดต่ำกว่า 5 องศาออก
    """
    f = coriolis(z)
    f = f.where(np.abs(f["latitude"]) > 5.0)

    ug = -(1.0 / f) * _ddy(z)
    vg = (1.0 / f) * _ddx(z)
    ug.attrs = {"long_name": "Geostrophic u", "units": "m s**-1"}
    vg.attrs = {"long_name": "Geostrophic v", "units": "m s**-1"}
    return ug, vg


# ------------------------------------------------------------------
# STEP 4 : สรุปค่าเชิงพื้นที่
# ------------------------------------------------------------------
def area_mean(field: xr.DataArray) -> float:
    """ค่าเฉลี่ยเชิงพื้นที่ ถ่วงน้ำหนักด้วย cos(latitude)"""
    w = np.cos(np.deg2rad(field["latitude"]))
    return float(field.weighted(w).mean(dim=["latitude", "longitude"]).values)


def value_at(field: xr.DataArray, lat: float, lon: float) -> float:
    """ค่าที่จุดพิกัดที่ใกล้ที่สุด"""
    return float(field.sel(latitude=lat, longitude=lon, method="nearest").values)


def extreme_location(field: xr.DataArray, kind: str = "max") -> dict:
    """ตำแหน่งและค่าของจุดสูงสุดหรือต่ำสุดในสนาม คืน dict lat / lon / value"""
    idx = (field.argmax if kind == "max" else field.argmin)(
        dim=["latitude", "longitude"])
    return {
        "lat": float(field["latitude"][idx["latitude"]].values),
        "lon": float(field["longitude"][idx["longitude"]].values),
        "value": float((field.max() if kind == "max" else field.min()).values),
    }
