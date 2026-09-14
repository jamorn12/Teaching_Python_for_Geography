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

> ทุกบทมีแบบฝึกหัดท้ายบทพร้อมเฉลย ผู้สอนสามารถลบส่วนเฉลยออกก่อนแจกได้

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

รายละเอียดการจัดเวลาแต่ละคาบ จุดประสงค์การเรียนรู้ และจุดที่นักศึกษามักติด
อยู่ใน [`COURSE_PLAN.md`](COURSE_PLAN.md)

---

## โครงสร้างโปรเจกต์

```
Teaching_Python_for_Geography/
├── README.md                  <- ไฟล์นี้
├── COURSE_PLAN.md             <- แผนการสอนละเอียดรายคาบ (สำหรับผู้สอน)
├── 00_Getting_Started_Colab.ipynb
├── 01_Variables_and_DataTypes.ipynb
├── ...
├── 11_MiniProject_Rainfall_Analysis.ipynb
├── data/
│   ├── stations.csv               <- ข้อมูลสถานี 4 แห่ง จ.ชลบุรี
│   ├── rainfall_daily_2025.csv    <- ฝนรายวัน 4 สถานี ตลอดปี 2025 (1,460 แถว)
│   └── messy_rainfall.csv         <- ข้อมูลสกปรก ใช้สอน error handling
└── utils/
    ├── make_datasets.py           <- script สร้างชุดข้อมูลใหม่ (เปลี่ยนปี/สถานีได้)
    └── geo_utils.py               <- ฟังก์ชันที่ใช้ซ้ำได้ ทั้งคอร์ส
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

---

## สิ่งที่นักศึกษาต้องเตรียม

- บัญชี Google (สำหรับ Colab และ Drive)
- โน้ตบุ๊กหรือคอมพิวเตอร์ที่ต่ออินเทอร์เน็ตได้ **หนึ่งเครื่องต่อหนึ่งคน**
- ไม่ต้องติดตั้ง Python, Anaconda หรือโปรแกรมใด ๆ

---

## หมายเหตุสำหรับผู้สอน

- ถ้าเปลี่ยนชื่อ repo หรือ GitHub account ให้แก้ URL ในตัวแปร `BASE`
  ที่เซลล์แรกของบทที่ 08–11 (บรรทัดเดียว) และแก้ลิงก์ badge ใน README
- บทที่ 11 มีเฉลยอ้างอิงอยู่ท้าย notebook ให้ลบออกก่อนแจกนักศึกษา
- แบบฝึกหัดท้ายบทของทุกบทมีเฉลยอยู่ใน text cell สุดท้ายเช่นกัน
