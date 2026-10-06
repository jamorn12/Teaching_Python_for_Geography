# Teaching_Python_for_Geography

บทเรียน Python พื้นฐานสำหรับนักศึกษาภาควิชาภูมิศาสตร์ ชั้นปีที่ 2
ออกแบบให้เรียนจบใน **6 ครั้ง ครั้งละ 2 ชั่วโมง (รวม 12 ชั่วโมง)** สัปดาห์ละ 2 ครั้ง
ทุกบทรันบน **Google Colab** ได้ทันที ไม่ต้องติดตั้งอะไรในเครื่อง

เนื้อหาเรียงตามโครงสร้างของ [W3Schools Python Tutorial](https://www.w3schools.com/python/default.asp)
แต่เปลี่ยนตัวอย่างทั้งหมดให้เป็นข้อมูลเชิงภูมิศาสตร์และอุตุนิยมวิทยา
เพื่อให้ผู้เรียนเห็นว่าจะเอา Python ไปใช้กับงานในสาขาตัวเองได้อย่างไร

---

## วิธีใช้งาน

1. กดปุ่ม **Open in Colab** ของบทที่ต้องการ
2. กด **File → Save a copy in Drive** เพื่อให้ได้ notebook ของตัวเอง
3. รันทีละเซลล์ด้วย `Shift` + `Enter`
4. ในบทที่ 00–06 จะมีเซลล์ ✍️ ว่างไว้ใต้ทุกหัวข้อ — **ให้พิมพ์โค้ดตามด้วยตัวเอง ห้าม copy–paste**

> ทุกบทมีแบบฝึกหัดท้ายบท ผู้สอนจะแจกเฉลยหลังหมดเวลาทำในคาบ

---

## สารบัญบทเรียน

| # | บทเรียน | หัวข้อหลัก | Colab |
|---|---|---|---|
| 00 | Getting Started with Colab | cell, runtime, `print()`, การอ่าน error | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jamorn12/Teaching_Python_for_Geography/blob/main/00_Getting_Started_Colab.ipynb) |
| 01 | Variables & Data Types | variable, `int/float/str/bool`, casting, f-string, `input()` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jamorn12/Teaching_Python_for_Geography/blob/main/01_Variables_and_DataTypes.ipynb) |
| 02 | Operators & Strings | arithmetic/comparison/logical operator, slicing, `split`, `join` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jamorn12/Teaching_Python_for_Geography/blob/main/02_Operators_and_Strings.ipynb) |
| 03 | Conditions | `if` / `elif` / `else`, indentation, การจำแนกระดับฝน | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jamorn12/Teaching_Python_for_Geography/blob/main/03_Conditions_if_else.ipynb) |
| 04 | Loops | `for`, `range()`, `while`, `break`, `enumerate`, `zip` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jamorn12/Teaching_Python_for_Geography/blob/main/04_Loops_for_while.ipynb) |
| 05 | Lists & Tuples | list method, slicing, list comprehension, nested list, tuple | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jamorn12/Teaching_Python_for_Geography/blob/main/05_Lists_and_Tuples.ipynb) |
| 06 | Dictionaries & Sets | `key: value`, nested dict, counter pattern, set operation | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jamorn12/Teaching_Python_for_Geography/blob/main/06_Dictionaries_and_Sets.ipynb) |
| 07 | Functions & Modules | `def`, `return`, docstring, scope, `import`, สร้าง module เอง | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jamorn12/Teaching_Python_for_Geography/blob/main/07_Functions_and_Modules.ipynb) |
| 08 | Files & Error Handling | `with open()`, CSV, Colab file I/O, `try` / `except` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jamorn12/Teaching_Python_for_Geography/blob/main/08_Files_and_Error_Handling.ipynb) |
| 09 | NumPy & Pandas | array, vectorization, masking, `NaN`, DataFrame, `groupby` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jamorn12/Teaching_Python_for_Geography/blob/main/09_NumPy_and_Pandas_Basics.ipynb) |
| 10 | Matplotlib | line/bar/scatter/histogram, `subplots`, ฟอนต์ไทย, `savefig` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jamorn12/Teaching_Python_for_Geography/blob/main/10_Matplotlib_Visualization.ipynb) |
| 11 | Mini Project | วิเคราะห์ฝนรายวันจังหวัดชลบุรี ปี 2025 ครบกระบวนการ | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jamorn12/Teaching_Python_for_Geography/blob/main/11_MiniProject_Rainfall_Analysis.ipynb) |
| 12A | **บทเสริม** — พื้นฐานการพล็อตแผนที่อากาศ | projection vs transform, `contourf`, `contour`, `barbs`, colormap, levels | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jamorn12/Teaching_Python_for_Geography/blob/main/12A_Weather_Map_Plotting_Basics.ipynb) |
| 12B | **บทเสริม** — วินิจฉัยสภาพบรรยากาศรายวัน (เตี้ยนหมู่ 24 ก.ย. 2564) | vorticity, divergence, shear, thickness, advection, Hovmöller | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jamorn12/Teaching_Python_for_Geography/blob/main/12B_Atmospheric_Diagnostics.ipynb) |
| 12 | **บทเสริม** — วิเคราะห์เหตุการณ์ที่กระทบไทย 4 เหตุการณ์ | NetCDF, `xarray`, `cartopy`, เส้นทางพายุ, แผนที่รายวัน D-5 ถึง D+2 | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jamorn12/Teaching_Python_for_Geography/blob/main/12_ERA5_Weather_Maps.ipynb) |

---

## ตารางสอน 6 ครั้ง

| ครั้งที่ | บทเรียน | แก่นของวัน |
|---|---|---|
| 1 | 00 + 01 | เปิดเครื่องมือให้เป็น แล้วเก็บค่าลงตัวแปรให้ถูกชนิด |
| 2 | 02 + 03 | คำนวณ จัดการข้อความ และตัดสินใจด้วยเงื่อนไข |
| 3 | 04 + 05 | ทำซ้ำ และเก็บข้อมูลเป็นชุด |
| 4 | 06 + 07 | ข้อมูลแบบ key–value และการห่อโค้ดเป็นฟังก์ชัน |
| 5 | 08 + 09 | จากไฟล์จริงสู่ตารางข้อมูล |
| 6 | 10 + 11 | เห็นภาพ และทำงานจริงหนึ่งชิ้น |
| — | 12A | **บทเสริม** พื้นฐานการพล็อตแผนที่อากาศ เรียนก่อนบทที่ 12 |
| — | 12B | **บทเสริม** วินิจฉัยบรรยากาศวันเดียวแบบเจาะลึก เรียนหลัง 12A |
| — | 12 | **บทเสริม** วิเคราะห์เหตุการณ์จริง 4 กรณี ใช้เป็นคาบที่ 7 หรืองานกลุ่มปลายภาค |

แผนการสอนรายคาบและเฉลยแบบฝึกหัดอยู่ที่คลังของผู้สอน
ผู้สอนจะแจกเฉลยหลังหมดเวลาทำแบบฝึกหัดในแต่ละคาบ

---

## โครงสร้างโปรเจกต์

```
Teaching_Python_for_Geography/
├── README.md                  <- ไฟล์นี้
├── 00_Getting_Started_Colab.ipynb
├── 01_Variables_and_DataTypes.ipynb
├── ...
├── 11_MiniProject_Rainfall_Analysis.ipynb
├── 12A_Weather_Map_Plotting_Basics.ipynb
├── 12B_Atmospheric_Diagnostics.ipynb
├── 12_ERA5_Weather_Maps.ipynb     <- บทเสริม
├── data/
│   ├── stations.csv               <- ข้อมูลสถานี 4 แห่ง จ.ชลบุรี
│   ├── rainfall_daily_2025.csv    <- ฝนรายวัน 4 สถานี ตลอดปี 2025 (1,460 แถว)
│   ├── messy_rainfall.csv         <- ข้อมูลสกปรก ใช้สอน error handling
│   ├── era5_demo_20250914.nc      <- ข้อมูลกริดสาธิต (ไม่ได้ใช้แล้วตั้งแต่ปรับบทที่ 12)
│   └── cases/                     <- ERA5 จริงของพายุ 3 เหตุการณ์ ใช้ในบทที่ 12
│       ├── dianmu2021.nc          <- เตี้ยนหมู่ 24 ก.ย. 2564
│       ├── noru2022.nc            <- โนรู 28 ก.ย. 2565
│       ├── yagi2024.nc            <- ยางิ 7 ก.ย. 2567
│       └── bangkok2026.nc         <- น้ำท่วม กทม. 25 ก.ย. 2569
└── utils/
    ├── make_datasets.py           <- script สร้างชุดข้อมูลฝนใหม่ (เปลี่ยนปี/สถานีได้)
    ├── make_era5_demo.py          <- script สร้างชุดข้อมูลกริดสาธิต
    ├── fetch_case_data.py         <- script ดึง ERA5 จริงของกรณีศึกษา (ผู้สอนรันครั้งเดียว)
    ├── era5_cases.py              <- ข้อมูลประกอบและฟังก์ชันวิเคราะห์กรณีศึกษาพายุ
    ├── atmos_diag.py              <- สูตรคำนวณตัวแปรวินิจฉัย ใช้ในบทที่ 12B
    ├── geo_utils.py               <- ฟังก์ชันที่ใช้ซ้ำได้ ทั้งคอร์ส
    └── era5_utils.py              <- ฟังก์ชันเปิดไฟล์ ERA5 และพล็อตแผนที่อากาศ
```

โค้ดที่เป็น **"กระบวนการ"** ทั้งหมดอยู่ในโฟลเดอร์ `utils/` เป็นไฟล์ `.py`
แยกเป็นขั้นตอนไว้ให้หยิบไปใช้กับข้อมูลชุดอื่นได้ทันที ส่วน notebook ทำหน้าที่เป็นตัวเรียกใช้และเล่าเรื่อง

```python
# ใช้ utils ใน Colab
!wget -q https://raw.githubusercontent.com/jamorn12/Teaching_Python_for_Geography/main/utils/geo_utils.py
import geo_utils as gu

df = gu.load_rainfall("data/rainfall_daily_2025.csv")
gu.annual_summary(df)
```

---

## เกี่ยวกับข้อมูลที่ใช้

ชุดข้อมูลฝนในโฟลเดอร์ `data/` เป็น **ข้อมูลสังเคราะห์ (synthetic data)**
สร้างขึ้นด้วย `utils/make_datasets.py` ให้มีลักษณะทางสถิติใกล้เคียงฝนรายวันของภาคตะวันออก
(ฤดูฝนเด่นช่วงพฤษภาคม–ตุลาคมตามอิทธิพลของ southwest monsoon การแจกแจงแบบเบ้ขวา
และมีเหตุการณ์ฝนหนักมากปะปน)

**ไม่ใช่ข้อมูลตรวจวัดจริงของกรมอุตุนิยมวิทยา** ใช้เพื่อการเรียนการสอนเท่านั้น
ห้ามนำผลการวิเคราะห์ไปอ้างอิงทางวิชาการ

หากต้องการเปลี่ยนไปใช้ข้อมูลจริง ให้แทนที่ไฟล์ใน `data/` โดยคงชื่อคอลัมน์เดิมไว้
(`date`, `station_id`, `station_name`, `province`, `rain_mm`) โค้ดทุกบทจะทำงานต่อได้เลย

### ข้อมูลของบทที่ 12 เป็นของจริง

ไฟล์ใน `data/cases/` เป็น **ERA5 reanalysis ของ ECMWF ตัวจริง** ไม่ใช่ข้อมูลสังเคราะห์
ถูกตัดเฉพาะโดเมนและช่วงเวลาที่ใช้ แล้วลดความละเอียดเหลือ 0.5 องศา เพื่อให้ไฟล์เล็กพอ

| ไฟล์ | เหตุการณ์ | ช่วงเวลา | ความละเอียด |
|---|---|---|---|
| `dianmu2021.nc` | พายุโซนร้อนเตี้ยนหมู่ | 19–26 ก.ย. 2564 | 0.5° |
| `noru2022.nc` | ไต้ฝุ่น/โซนร้อนโนรู | 23–30 ก.ย. 2565 | 0.5° |
| `yagi2024.nc` | ไต้ฝุ่นยางิ | 2–9 ก.ย. 2567 | 0.5° |
| `bangkok2026.nc` | น้ำท่วมกรุงเทพมหานคร | 20–27 ก.ย. 2569 | 0.25° |

แต่ละไฟล์ครอบคลุม **5 วันก่อนเกิดเหตุ จนถึง 2 วันหลัง** (D-5 ถึง D+2) ราย 6 ชั่วโมง
6 ระดับความกดอากาศ พร้อมตัวแปร `msl`, `t2m`, `tp`, `u`, `v`, `z`, `r`

เคส กทม. ใช้ความละเอียดสูงกว่าเพราะเป็นเหตุการณ์ระดับเมือง แต่ถึงอย่างนั้น
กริด 0.25° (~28 กม.) ก็ยังหยาบเกินกว่าจะเห็นฝนระดับเขตได้ — บทเรียนข้อนี้อยู่ในหัวข้อ 4.5

เมื่อนำผลไปใช้ในรายงานหรืองานวิชาการ **ต้องอ้างอิงแหล่งข้อมูล**
Hersbach, H. et al. (2020). The ERA5 global reanalysis.
*Quarterly Journal of the Royal Meteorological Society*, 146(730), 1999–2049.

ลำดับเหตุการณ์ของทั้งสามกรณีอ้างอิงจากประกาศกรมอุตุนิยมวิทยาและรายงานข่าว
ดูรายการแหล่งอ้างอิงเต็มได้ในโน้ตบุ๊กบทที่ 12 หรือใน `utils/era5_cases.py`

---

## สิ่งที่นักศึกษาต้องเตรียม

- บัญชี Google (สำหรับ Colab และ Drive)
- โน้ตบุ๊กหรือคอมพิวเตอร์ที่ต่ออินเทอร์เน็ตได้ **หนึ่งเครื่องต่อหนึ่งคน**
- ไม่ต้องติดตั้ง Python, Anaconda หรือโปรแกรมใด ๆ

---

## ติดปัญหาระหว่างเรียน

- **รันเซลล์แล้วขึ้น error ที่ไม่เข้าใจ** — อ่านบรรทัดสุดท้ายของข้อความก่อน มันบอกชนิดของปัญหา
- **ตัวแปรมั่ว หรือแก้โค้ดแล้วผลไม่เปลี่ยน** — Runtime → Restart session แล้วรันใหม่ตั้งแต่เซลล์แรก
- **บท 08–12 หาไฟล์ข้อมูลไม่เจอ** — รันเซลล์แรกของบทนั้นก่อนเสมอ เซลล์นั้นทำหน้าที่ดาวน์โหลดข้อมูล
- **กราฟขึ้นเป็นสี่เหลี่ยม □□□** — ยังไม่ได้รันเซลล์ตั้งค่าฟอนต์ไทย
- **บท 12 ขึ้นว่าโหลดแผนที่ฐานไม่ได้** — เครือข่ายบล็อกการดาวน์โหลดข้อมูล Natural Earth
  แผนที่จะไม่มีเส้นชายฝั่ง แต่ข้อมูลที่พล็อตยังถูกต้องทุกอย่าง ใช้เรียนต่อได้
