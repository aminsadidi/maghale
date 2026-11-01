# راهنمای ساخت ساختار و اجرای ۷ مرحله در SCAPS-1D
ساختار: ITO / TiO2 / MAGeI3 / (بافر: WOx، NiOx یا V2O5) / Spiro-OMeTAD / Au
همه‌ی اعداد از جدول‌های ۳-۱ تا ۳-۴ فصل سوم پایان‌نامه گرفته شده‌اند. مقادیری که در فصل ۳ نیامده‌اند با «فرض» مشخص شده‌اند.

> این راهنما و جدول‌ها هنوز با خود SCAPS آزمایش نشده‌اند و از روی فصل ۳ نوشته شده‌اند. بعد از اولین اجرا، نتایج را با اعداد حل‌گر پایتونی (پوشه‌ی `sim/`) مقایسه کن.

---
## ۱) تنظیمات کلی (پنجره‌ی Action / Working point)
| پارامتر | مقدار |
|---|---|
| دما | 300 K |
| ولتاژ کاری | 0 V |
| فرکانس | 1 kHz (= 1E+3 Hz) |
| نور | Light، طیف AM1_5G 1 sun.spe، از سمت چپ (left) |
| Front contact (ITO, سمت چپ) | Flat band، Sn = Sp = 1E+7 cm/s (فرض: پیش‌فرض SCAPS) |
| Back contact (Au, سمت راست) | Metal work function = 5.1 eV، Sn = Sp = 1E+7 cm/s (فرض) |
| بازتاب | 0 (فرض) |

## ۲) لایه‌ها (Set problem → add layer) به ترتیب از چپ به راست
| پارامتر | ITO | TiO2 | MAGeI3 | Spiro-OMeTAD |
|---|---|---|---|---|
| thickness (µm) | 0.200 | 0.100 (متغیر) | 0.600 (متغیر) | 0.100 (متغیر) |
| bandgap (eV) | 3.5 | 3.2 | 1.9 | 3.0 |
| electron affinity (eV) | 4.3 | 4.1 | 3.7 | 2.2 |
| dielectric permittivity | 9 | 35 | 10 | 3 |
| CB eff. DOS (cm⁻³) | 2.2E+18 | 2.2E+18 | 2.8E+18 | 1.0E+18 |
| VB eff. DOS (cm⁻³) | 1.8E+19 | 1.8E+19 | 2.8E+18 | 9.0E+16 |
| e⁻ thermal velocity (cm/s) | 1E+7 | 1E+7 | 1E+7 | 1E+7 |
| h⁺ thermal velocity (cm/s) | 1E+7 | 1E+7 | 1E+7 | 1E+7 |
| e⁻ mobility (cm²/Vs) | 40 | 20 | 10.1 | 2E-4 |
| h⁺ mobility (cm²/Vs) | 5 | 0.01 | 16.2 | 1E-4 |
| ND (cm⁻³) | 1E+19 | 2.1E+18 | 1E+18 | 0 |
| NA (cm⁻³) | 0 | 0 | 1.1E+18 | 1E+18 |
| absorption model | sqrt(hν−Eg)، A = 1E+5، B = 0 (پیش‌فرض SCAPS، فرض) | ← | ← | ← |

### لایه‌های بافر (جدول ۳-۲)
| پارامتر | WOx (ستون «MoOx» در جدول ۳-۲) | V2O5 | NiOx |
|---|---|---|---|
| thickness (µm) | 0 تا 0.050، گام 0.010 | ← | ← |
| bandgap (eV) | 3.0 | 3.99 | 3.25 |
| electron affinity (eV) | 2.3 | 2.3 | 2.05 |
| permittivity | 6 | 4.28 | 11.75 |
| Nc (cm⁻³) | 2.0E+18 | 2.2E+18 | 2.0E+18 |
| Nv (cm⁻³) | 1.8E+16 | 1.8E+19 | 2.0E+16 |
| e⁻ mobility | 1 | 1.26 | 8 |
| h⁺ mobility | 0.1 | 34.5 | 2 |
| ND | 0 | 1E+17 | 0 |
| NA | 7E+14 | 0 | 7E+14 |

## ۳) نقص‌های حجمی (جدول ۳-۳)
| لایه | نوع | σn = σp (cm²) | توزیع | Et (بالای Ev) | E_char | Nt (cm⁻³) |
|---|---|---|---|---|---|---|
| TiO2 | Neutral | 1E-15 | Single | 0.65 eV | 0.1 eV | 2.2E+15 |
| MAGeI3 | Donor | 1E-15 | Gauss | 0.60 eV | 0.1 eV | 1.0E+16 |
| Spiro-OMeTAD | Donor | 1E-15 | Gauss | 1.65 eV | 0.1 eV | 1.1E+15 |
| ITO | Neutral (فرض) | 1E-15 | Single | میانه‌ی گاف | – | 1E+15 (در جدول «۲۰۰» آمده که اشتباه تایپی به نظر می‌رسد) |
| بافرها | Neutral (فرض) | 1E-15 | Single | میانه‌ی گاف | – | 1E+15 |

## ۴) نقص‌های فصل مشترک (جدول ۳-۴) — Add interface
برای TiO2/MAGeI3 و MAGeI3/HTL (یا MAGeI3/بافر):
Neutral، Single، Et = 0.6 eV بالای Ev، σn = σp = 1E-15 cm² (فرض)، Nit = 1.1E+5 cm⁻²

## ۵) ذخیره
بعد از وارد کردن همه‌ی مقادیر: Set problem → **Save** → فایل‌ها را با این اسم‌ها ذخیره کن:
- `S1_noBuffer.def` (TiO2 = 100 nm، MAGeI3 = 600 nm، Spiro = 100 nm)
- `S4_WOx.def`، `S4_NiOx.def`، `S4_V2O5.def` (هر کدام با بافر 10 nm بین MAGeI3 و Spiro)

این فایل‌های .def همان «فایل اجرایی» SCAPS هستند که در جلسه‌ی دفاع باز می‌کنی.

## ۶) اجرای ۷ مرحله با Batch (دکمه‌ی Batch set-up)
در Action تیک‌های I-V (0 تا 1.6 V، گام 0.01)، QE (300 تا 900 nm، گام 10) و C-V (0 تا 1.4 V، 1 kHz) را بزن.

| مرحله | فایل | پارامتر batch | بازه |
|---|---|---|---|
| ۱ | S1_noBuffer | MAGeI3 → thickness | 0.1 تا 0.8 µm، 8 نقطه |
| ۲ | S1 با MAGeI3 بهینه | TiO2 → thickness | 0.001، 0.05، 0.1، … 0.4 |
| ۳ | S1 با MAGeI3 و TiO2 بهینه | Spiro → thickness | 0.001، 0.05، 0.1، 0.15، 0.2 |
| ۴ | S4_WOx / S4_NiOx / S4_V2O5 | buffer → thickness | 0 تا 0.05، 6 نقطه |
| ۵–۶ | چهار ساختار بهینه | — (Calculate single shot) | J-V |
| ۷ | چهار ساختار بهینه | — | QE |

بعد از هر اجرا در پنجره‌ی نتایج: **Save results** (فایل‌های .iv و .qe و .cv)، و در پنجره‌ی Energy bands: **Save**. این فایل‌ها را برای من بفرست تا نمودارها و تحلیل فصل ۴ را با نتایج SCAPS به‌روز کنم.
