فایل‌های ساختار SCAPS-1D برای پایان‌نامه MAGeI3
=================================================

فایل‌ها (همه با پارامترهای جدول‌های ۳-۱ تا ۳-۴ فصل سوم):
  01_Step1_noBuffer_MAGeI3-batch.def  : ساختار اولیه (TiO2=100، MAGeI3=500، Spiro=100 nm) برای گام ۱
  02_noBuffer_reference.def           : ساختار بدون بافر (MAGeI3=600 nm)
  03_WOx_buffer_10nm.def              : با بافر WOx به ضخامت ۱۰ nm
  04_NiOx_buffer_10nm.def             : با بافر NiOx به ضخامت ۱۰ nm
  05_V2O5_buffer_10nm.def             : با بافر V2O5 به ضخامت ۱۰ nm

ترتیب لایه‌ها در SCAPS (چپ به راست):  Au (back) | Spiro | [buffer] | MAGeI3 | TiO2 | ITO (front)
نور از سمت راست (ITO) می‌تابد.

مرحله ۰ - کپی
  این پنج فایل را در پوشه def برنامه SCAPS کپی کن (همان پوشه‌ای که برایم فرستادی).

مرحله ۱ - باز کردن
  SCAPS را اجرا کن → Set Problem → Load → فایل 02_noBuffer_reference.def → OK
  اگر پیغام خطا آمد، متن دقیق یا عکسش را برایم بفرست.

مرحله ۲ - تنظیمات پنجره اصلی (Action panel)
  Temperature = 300 K ، Voltage = 0 V ، Frequency = 1E+3 Hz
  Illumination: Light ، spectrum: AM1_5G 1 sun.spe
  تیک I-V: V1 = 0 ، V2 = 1.6 ، increment = 0.01
  تیک QE (IPCE): WL1 = 300 ، WL2 = 900 ، increment = 10
  تیک C-V: V1 = 0 ، V2 = 1.4 ، increment = 0.02 (فرکانس 1E+3 Hz)

مرحله ۳ - تست
  Calculate: single shot → در پنجره نتایج Voc ، Jsc ، FF و Eta را یادداشت کن و برایم بفرست.
  (پیش‌بینی حل‌گر پایتونی برای ساختار بدون بافر: Voc ≈ 1.49 V ، Jsc ≈ 13.3 mA/cm2 ، FF ≈ 77 % ، PCE ≈ 15.3 %
   اختلاف چند درصدی طبیعی است.)

مرحله ۴ - هفت گام با Batch set-up
  گام ۱: فایل 01 → Batch set-up → layer "MAGeI3" → thickness → از 0.1 تا 0.8 um با 8 نقطه → Calculate batch
  گام ۲: ضخامت MAGeI3 را روی بهینه بگذار → batch روی TiO2 thickness: 0.001 ، 0.05 ، ... ، 0.4 um
  گام ۳: batch روی Spiro thickness: 0.001 ، 0.05 ، 0.1 ، 0.15 ، 0.2 um
  گام ۴: فایل‌های 03، 04، 05 → batch روی ضخامت بافر: 0 تا 0.05 um با 6 نقطه
  گام ۵ و ۶: هر چهار ساختار بهینه را single shot اجرا کن (J-V)
  گام ۷: QE هر چهار ساختار

مرحله ۵ - ذخیره خروجی‌ها
  در پنجره I-V ، QE ، C-V و Energy bands دکمه "save" (یا "Save graphs") را بزن.
  فایل‌های .iv ، .qe ، .cv ، .eb و نتایج batch را زیپ کن و برایم بفرست.
