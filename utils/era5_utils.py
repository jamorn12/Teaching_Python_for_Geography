"""
era5_utils.py
------------------------------------------------------------------
ฟังก์ชันช่วยพล็อตแผนที่อากาศจากข้อมูล ERA5 reanalysis

ออกแบบให้ทำงานกับไฟล์ ERA5 จริงที่ดาวน์โหลดจาก Copernicus Climate Data Store
และกับไฟล์สาธิตที่สร้างโดย make_era5_demo.py ได้เหมือนกัน
เพราะทั้งคู่ใช้ชื่อตัวแปรและมิติชุดเดียวกัน

ใช้ใน Colab:
    !wget -q https://raw.githubusercontent.com/jamorn12/Teaching_Python_for_Geography/main/utils/era5_utils.py
    import era5_utils as eu

ขั้นตอนมาตรฐานของการทำแผนที่อากาศหนึ่งใบ
    1. open_era5()        เปิดไฟล์ จัดชื่อมิติให้เป็นมาตรฐาน
    2. subset()           ตัดโดเมน / เลือกเวลา / เลือกระดับความกดอากาศ
    3. make_map_axes()    เตรียมแกนแผนที่พร้อมเส้นชายฝั่งและ gridline
    4. shade() / contour() / barbs()   วาดชั้นข้อมูลทีละชั้น
    5. finish()           ใส่ชื่อแผนที่ colorbar แล้วบันทึก
"""

from __future__ import annotations

import os
import urllib.request

import numpy as np
import xarray as xr

RAW_BASE = (
    "https://raw.githubusercontent.com/jamorn12/"
    "Teaching_Python_for_Geography/main/data/"
)

DEMO_FILE = "era5_demo_20250914.nc"

# กรอบที่ใช้บ่อย (lon_min, lon_max, lat_min, lat_max)
DOMAINS = {
    "indochina": (90.0, 115.0, 0.0, 25.0),
    "thailand": (96.0, 106.5, 5.0, 21.0),
    "upper_north": (97.0, 102.0, 16.0, 21.0),
    "east": (99.5, 103.5, 11.0, 14.5),
}


# ------------------------------------------------------------------
# STEP 1 : เปิดไฟล์
# ------------------------------------------------------------------
def fetch_demo(outdir: str = "data", filename: str = DEMO_FILE) -> str:
    """ดาวน์โหลดไฟล์สาธิตจาก GitHub ถ้ายังไม่มีในเครื่อง คืน path"""
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, filename)
    if not os.path.exists(path):
        urllib.request.urlretrieve(RAW_BASE + filename, path)
    return path


def open_era5(path: str) -> xr.Dataset:
    """
    เปิดไฟล์ ERA5 แล้วจัดชื่อมิติให้เป็นมาตรฐานเดียวกัน

    ไฟล์ ERA5 ที่โหลดจาก CDS คนละรุ่นใช้ชื่อไม่เหมือนกัน
    (longitude/lon, latitude/lat, level/pressure_level, time/valid_time)
    ฟังก์ชันนี้แปลงให้เป็น longitude / latitude / level / time เสมอ
    และเรียง latitude จากน้อยไปมาก เพื่อให้ sel(slice(...)) ใช้ได้ตรงไปตรงมา
    """
    ds = xr.open_dataset(path)

    rename = {}
    for src, dst in [("lon", "longitude"), ("lat", "latitude"),
                     ("pressure_level", "level"), ("valid_time", "time"),
                     ("isobaricInhPa", "level")]:
        if src in ds.dims or src in ds.coords:
            rename[src] = dst
    if rename:
        ds = ds.rename(rename)

    if "latitude" in ds.coords and ds["latitude"].size > 1:
        if ds["latitude"][0] > ds["latitude"][-1]:
            ds = ds.sortby("latitude")
    return ds


# ------------------------------------------------------------------
# STEP 2 : ตัดข้อมูล
# ------------------------------------------------------------------
def subset(ds: xr.Dataset, domain: str | tuple | None = None,
           time=None, level: int | None = None) -> xr.Dataset:
    """
    ตัดโดเมนและเลือกเวลา/ระดับความกดอากาศในคำสั่งเดียว

    domain : ชื่อใน DOMAINS หรือ tuple (lon_min, lon_max, lat_min, lat_max)
    time   : ค่าที่ .sel() รับได้ เช่น "2025-09-14T12:00"
    level  : ระดับความกดอากาศ (hPa) เช่น 850
    """
    out = ds
    if domain is not None:
        box = DOMAINS[domain] if isinstance(domain, str) else domain
        lon0, lon1, lat0, lat1 = box
        out = out.sel(longitude=slice(lon0, lon1), latitude=slice(lat0, lat1))
    if level is not None and "level" in out.dims:
        out = out.sel(level=level)
    if time is not None and "time" in out.dims:
        out = out.sel(time=time)
    return out


# ------------------------------------------------------------------
# STEP 3 : แปลงหน่วยให้เป็นหน่วยที่ใช้อ่านแผนที่
# ------------------------------------------------------------------
def to_celsius(da: xr.DataArray) -> xr.DataArray:
    """K -> °C"""
    out = da - 273.15
    out.attrs["units"] = "degC"
    return out


def to_hpa(da: xr.DataArray) -> xr.DataArray:
    """Pa -> hPa"""
    out = da / 100.0
    out.attrs["units"] = "hPa"
    return out


def to_gpm(da: xr.DataArray) -> xr.DataArray:
    """geopotential (m2 s-2) -> geopotential height (gpm)"""
    out = da / 9.80665
    out.attrs["units"] = "gpm"
    return out


def to_mm(da: xr.DataArray) -> xr.DataArray:
    """total precipitation (m) -> mm"""
    out = da * 1000.0
    out.attrs["units"] = "mm"
    return out


def wind_speed(u: xr.DataArray, v: xr.DataArray) -> xr.DataArray:
    """ความเร็วลมลัพธ์ (m/s)"""
    out = np.sqrt(u**2 + v**2)
    out.attrs["units"] = "m s**-1"
    out.attrs["long_name"] = "Wind speed"
    return out


def wind_direction(u: xr.DataArray, v: xr.DataArray) -> xr.DataArray:
    """
    ทิศลม (องศา) แบบอุตุนิยมวิทยา — ทิศที่ลม "พัดมาจาก"
    0 = เหนือ, 90 = ตะวันออก, 180 = ใต้, 270 = ตะวันตก
    """
    out = (270.0 - np.degrees(np.arctan2(v, u))) % 360.0
    out.attrs["units"] = "degrees"
    out.attrs["long_name"] = "Wind direction (from)"
    return out


# ------------------------------------------------------------------
# STEP 4 : เตรียมแกนแผนที่
# ------------------------------------------------------------------
def make_map_axes(ax=None, domain: str | tuple = "indochina",
                  figsize=(9, 7), coastlines: bool = True):
    """
    สร้างแกนแผนที่แบบ PlateCarree พร้อมเส้นชายฝั่ง เส้นพรมแดน และ gridline

    ถ้าดาวน์โหลดข้อมูลเส้นชายฝั่ง (Natural Earth) ไม่ได้ จะยังคืนแกนที่ใช้พล็อตได้
    แค่ไม่มีเส้นชายฝั่ง — ไม่ทำให้โปรแกรมล้ม
    """
    import cartopy.crs as ccrs
    import matplotlib.pyplot as plt

    box = DOMAINS[domain] if isinstance(domain, str) else domain

    if ax is None:
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

    ax.set_extent(box, crs=ccrs.PlateCarree())

    if coastlines:
        try:
            import cartopy.feature as cfeature

            # cartopy ดาวน์โหลดข้อมูล Natural Earth แบบ lazy คือไปโหลดตอนวาดรูป
            # ถ้าปล่อยไว้ เครือข่ายที่บล็อกการดาวน์โหลดจะทำให้พังตอน savefig
            # ซึ่งดักไม่ได้ จึงบังคับให้โหลดตั้งแต่ตอนนี้ เพื่อให้ except ทำงานทัน
            for feat in (cfeature.COASTLINE, cfeature.BORDERS,
                         cfeature.OCEAN, cfeature.LAND):
                next(iter(feat.geometries()), None)

            ax.add_feature(cfeature.OCEAN, facecolor="#eaf3fb", zorder=0)
            ax.add_feature(cfeature.LAND, facecolor="#f7f5f0", zorder=0)
            ax.add_feature(cfeature.COASTLINE, linewidth=0.8)
            ax.add_feature(cfeature.BORDERS, linewidth=0.5, linestyle=":")
        except Exception as exc:  # noqa: BLE001
            print("โหลดเส้นชายฝั่งไม่ได้ ->", exc)
            print("แผนที่จะไม่มีเส้นชายฝั่ง แต่ข้อมูลที่พล็อตยังถูกต้องทุกอย่าง")

    gl = ax.gridlines(draw_labels=True, linewidth=0.4,
                      color="gray", alpha=0.5, linestyle="--")
    gl.top_labels = False
    gl.right_labels = False
    return ax


def add_station_markers(ax, stations, color="red", size=28, label_col="station_id"):
    """วางจุดสถานีลงบนแผนที่ จาก DataFrame ที่มีคอลัมน์ lat / lon"""
    import cartopy.crs as ccrs

    ax.scatter(stations["lon"], stations["lat"], s=size, c=color,
               edgecolor="black", linewidth=0.6, zorder=6,
               transform=ccrs.PlateCarree())
    if label_col and label_col in stations.columns:
        for _, row in stations.iterrows():
            ax.text(row["lon"] + 0.12, row["lat"] + 0.12, row[label_col],
                    fontsize=8, zorder=6, transform=ccrs.PlateCarree())
    return ax


# ------------------------------------------------------------------
# STEP 5 : ชั้นข้อมูล
# ------------------------------------------------------------------
def shade(ax, da: xr.DataArray, cmap="viridis", levels=None, extend="both", **kw):
    """ระบายสีพื้น (filled contour) จาก DataArray 2 มิติ"""
    import cartopy.crs as ccrs

    return ax.contourf(da["longitude"], da["latitude"], da.values,
                       levels=levels, cmap=cmap, extend=extend,
                       transform=ccrs.PlateCarree(), **kw)


def contour(ax, da: xr.DataArray, levels=None, color="black",
            linewidth=0.9, label_fmt="%d", inline_fontsize=8, **kw):
    """เส้นชั้น (contour) พร้อมตัวเลขกำกับเส้น"""
    import cartopy.crs as ccrs

    cs = ax.contour(da["longitude"], da["latitude"], da.values,
                    levels=levels, colors=color, linewidths=linewidth,
                    transform=ccrs.PlateCarree(), **kw)
    if label_fmt:
        ax.clabel(cs, inline=True, fontsize=inline_fontsize, fmt=label_fmt)
    return cs


def barbs(ax, u: xr.DataArray, v: xr.DataArray, step: int = 6, length: float = 5.5, **kw):
    """
    ลมแบบ wind barb — step คือเว้นช่วงกริด ถ้าไม่เว้นจะทึบจนอ่านไม่ออก
    หมายเหตุ: barb อ่านค่าเป็น knots ตามธรรมเนียม จึงแปลงจาก m/s ให้ก่อน
    """
    import cartopy.crs as ccrs

    MS_TO_KT = 1.94384
    return ax.barbs(u["longitude"].values[::step], u["latitude"].values[::step],
                    u.values[::step, ::step] * MS_TO_KT,
                    v.values[::step, ::step] * MS_TO_KT,
                    length=length, linewidth=0.6,
                    transform=ccrs.PlateCarree(), **kw)


def streamlines(ax, u: xr.DataArray, v: xr.DataArray, density: float = 1.4, **kw):
    """เส้นกระแสลม (streamline) เหมาะกับการดูรูปแบบการไหลในเขตร้อน"""
    import cartopy.crs as ccrs

    return ax.streamplot(u["longitude"].values, u["latitude"].values,
                         u.values, v.values, density=density,
                         linewidth=0.7, arrowsize=0.8, color="dimgray",
                         transform=ccrs.PlateCarree(), **kw)


# ------------------------------------------------------------------
# STEP 6 : ตกแต่งและบันทึก
# ------------------------------------------------------------------
def finish(ax, title: str = "", mappable=None, cbar_label: str = "",
           savepath: str | None = None, dpi: int = 300):
    """ใส่ชื่อแผนที่ colorbar แล้วบันทึกไฟล์ (ถ้าระบุ savepath)"""
    import matplotlib.pyplot as plt

    if title:
        ax.set_title(title, fontsize=12, loc="left")
    if mappable is not None:
        cb = ax.figure.colorbar(mappable, ax=ax, orientation="vertical",
                                shrink=0.78, pad=0.04)
        if cbar_label:
            cb.set_label(cbar_label)
    if savepath:
        ax.figure.savefig(savepath, dpi=dpi, bbox_inches="tight")
        print("บันทึกรูป:", savepath)
    return ax


def setup_thai_font(verbose: bool = True) -> bool:
    """ติดตั้งฟอนต์ Sarabun ให้ matplotlib แสดงภาษาไทยได้ คืน True ถ้าสำเร็จ"""
    try:
        import matplotlib
        import matplotlib.font_manager as fm

        url = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Regular.ttf"
        path = "Sarabun-Regular.ttf"
        if not os.path.exists(path):
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


# ------------------------------------------------------------------
# วิเคราะห์เพิ่มเติม
# ------------------------------------------------------------------
def find_low_center(msl: xr.DataArray) -> dict:
    """
    หาตำแหน่งศูนย์กลางความกดอากาศต่ำสุดในสนาม 2 มิติ
    คืน dict: lon, lat, value
    """
    flat = msl.argmin(dim=["latitude", "longitude"])
    lat = float(msl["latitude"][flat["latitude"]].values)
    lon = float(msl["longitude"][flat["longitude"]].values)
    return {"lon": lon, "lat": lat, "value": float(msl.min().values)}


def area_mean(da: xr.DataArray) -> float:
    """
    ค่าเฉลี่ยเชิงพื้นที่แบบถ่วงน้ำหนักด้วย cos(latitude)

    จำเป็นเพราะกริดละติจูด–ลองจิจูดมีพื้นที่ต่อเซลล์ไม่เท่ากัน
    เซลล์ใกล้ขั้วโลกแคบกว่าเซลล์ใกล้ศูนย์สูตร ถ้าเฉลี่ยตรง ๆ จะให้น้ำหนักเกินจริง
    """
    weights = np.cos(np.radians(da["latitude"]))
    weights.name = "weights"
    return float(da.weighted(weights).mean(dim=["latitude", "longitude"]).values)
