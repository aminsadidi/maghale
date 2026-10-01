# برنامه‌ی ویرایش نسخه‌ی فعلی مقاله (PDF ۲۲ صفحه‌ای، شهریور ۱۴۰۵)

> توجه: سورس LaTeX داخل `manuscript/` نسخه‌ی قدیمی است (اعداد ۲۰۲۰ و ۶۰۷.۹ nm).
> نسخه‌ی جدید (همان PDF) در مخزن نیست؛ بنابراین همه‌ی اصلاحات زیر به‌صورت
> «متن آماده برای جای‌گذاری» نوشته شده‌اند. شماره‌ی صفحه‌ها مطابق همان PDF است.

---

## ۱. سه ارجاعِ جاافتاده

| # | محل در PDF | جمله‌ی فعلی | اصلاح |
|---|---|---|---|
| ۱ | ص ۶، بخش ۳.۱ | «…(مدل چندضریبی با حداکثر شش ضریب و تحمل برازش ۰.۱)…» | بعد از «تحمل برازش ۰.۱)» بیفزایید: `[34, 35]` |
| ۲ | ص ۹ (اعتبار پاسخ موضعی) و ص ۱۴ (بخش ۴.۴) | «$\gamma=\gamma_{\rm bulk}+Av_F/R$» | بلافاصله بعد از رابطه: `[36, 37]` |
| ۳ | ص ۱۵، بخش ۴.۵، پاراگراف دوم | «…چون نرخ غیرتابشی نزدیک فلز با $d^{-3}$ رشد می‌کند…» | بعد از «رشد می‌کند» بیفزایید: `[6, 15]` (مرجع جدید لازم نیست) |

متن پیشنهادی کامل برای مورد ۱ (ص ۶):

> …نرم‌افزار آن را با تنظیمات پیش‌فرض خود (مدل چندضریبی با حداکثر شش ضریب و
> تحمل برازش ۰٫۱) در بازه‌ی شبیه‌سازی برازش می‌کند [34, 35]؛ رویکردی که برای
> وارد کردن پاشندگی طلا در FDTD متداول است [34].

متن پیشنهادی برای مورد ۲ (ص ۹):

> …و افزایش میرایی ناشی از پراکندگی سطحی الکترون‌ها
> ($\gamma=\gamma_{\rm bulk}+Av_F/R$) [36, 37] در شعاع ۱۰ نانومتر.

> **نکته‌ی شماره‌گذاری:** اگر سبک مجله «به ترتیب ظهور در متن» است، مراجع جدید
> باید در جای خود شماره بگیرند و بقیه جابه‌جا شوند. ساده‌ترین راه بی‌خطا این است که
> آن‌ها را به‌صورت [34] تا [39] به انتهای فهرست اضافه کنید و هنگام قالب‌بندی نهایی
> مجله (BibTeX با `sorting=none`) شماره‌گذاری خودکار انجام شود.

---

## ۲. یکدست‌سازی فهرست مراجع

### ایرادهای فعلی (مهم‌تر از آن‌چه در گزارش قبلی آمده بود)

1. **فهرست مراجع شماره ندارد.** در متن [1] تا [33] ارجاع شده ولی در فهرست
   هیچ شماره‌ای نیست؛ داور نمی‌تواند [27] را پیدا کند. این مهم‌ترین ایراد قالبی است.
2. **مرجع ۳۱ (Priyanka et al.)** مقاله‌ی داوری‌شده نیست؛ پیش‌انتشار SSRN است
   (SSRN 7011197). در ص ۱۴ همراه Sauvan برای «چارچوب مدهای شبه‌نرمال» به آن
   ارجاع شده، در حالی که موضوعش نانولیزر است. پیشنهاد: با مرور مرجعِ QNM
   (Lalanne et al. 2018، پایین) **جایگزین شود**. اگر می‌خواهید بماند، حتماً
   «Preprint, SSRN 7011197 (2025)» نوشته شود.
3. خرابی‌های تبدیل LaTeX: `Barreda \.,` ← **Barreda Á. I.**؛ `S\'aenz` ← **Sáenz**.
4. Sauvan: `Hugonin J.` ← **Hugonin J.-P.**
5. کتاب‌ها ویرایش و شهر ناشر ندارند؛ قالب سال یکدست نیست («(1946).» با نقطه‌ی اضافه).

### قالب واحد پیشنهادی

`[n] نام خانوادگی حروف اول., … عنوان. *نام کامل مجله* **جلد**, صفحه (سال). doi:…`
کتاب: `[n] نویسنده. *عنوان*, ویرایش. ناشر, شهر (سال). doi:…`

### فهرست اصلاح‌شده (برای جای‌گذاری)

[1] Purcell E. M. Spontaneous emission probabilities at radio frequencies. *Physical Review* **69**, 681 (1946). doi:10.1103/PhysRev.69.674.2
[2] Maier S. A. *Plasmonics: Fundamentals and Applications*. Springer, New York (2007). doi:10.1007/0-387-37825-1
[3] Chen J., Deng S. Z., Chen J., Li Z. L., Xu N. S. Subwavelength localized plasmon resonance properties of isolated gold nanorods. *Optics Express* **17**, 15998–16008 (2009). doi:10.1364/OE.17.015998
[4] Anger P., Bharadwaj P., Novotny L. Enhancement and quenching of single-molecule fluorescence. *Physical Review Letters* **96**, 113002 (2006). doi:10.1103/PhysRevLett.96.113002
[5] Koenderink A. F. Single-photon nanoantennas. *ACS Photonics* **4**, 710–722 (2017). doi:10.1021/acsphotonics.7b00061
[6] Ford G. W., Weber W. H. Electromagnetic interactions of molecules with metal surfaces. *Physics Reports* **113**, 195–287 (1984). doi:10.1016/0370-1573(84)90098-X
[7] Mohammadi A., Sandoghdar V., Agio M. Gold nanorods and nanospheroids for enhancing spontaneous emission. *New Journal of Physics* **10**, 105015 (2008). doi:10.1088/1367-2630/10/10/105015
[8] Kühn S., Håkanson U., Rogobete L., Sandoghdar V. Enhancement of single-molecule fluorescence using a gold nanoparticle as an optical nanoantenna. *Physical Review Letters* **97**, 017402 (2006). doi:10.1103/PhysRevLett.97.017402
[9] Griffiths D. J., Schroeter D. F. *Introduction to Quantum Mechanics*, 3rd ed. Cambridge University Press, Cambridge (2018). doi:10.1017/9781316995433
[10] Jackson J. D. *Classical Electrodynamics*, 3rd ed. Wiley, New York (1999).
[11] Prodan E., Radloff C., Halas N. J., Nordlander P. A hybridization model for the plasmon response of complex nanostructures. *Science* **302**, 419–422 (2003). doi:10.1126/science.1089171
[12] Sönnichsen C., Franzl T., Wilk T., von Plessen G., Feldmann J., Wilson O., et al. Drastic reduction of plasmon damping in gold nanorods. *Physical Review Letters* **88**, 077402 (2002). doi:10.1103/PhysRevLett.88.077402
[13] Bharadwaj P., Novotny L. Spectral dependence of single molecule fluorescence enhancement. *Optics Express* **15**, 14266–14274 (2007). doi:10.1364/OE.15.014266
[14] Carminati R., Greffet J.-J., Henkel C., Vigoureux J. M. Radiative and non-radiative decay of a single molecule close to a metallic nanoparticle. *Optics Communications* **261**, 368–375 (2006). doi:10.1016/j.optcom.2005.12.009
[15] Novotny L., Hecht B. *Principles of Nano-Optics*, 2nd ed. Cambridge University Press, Cambridge (2012). doi:10.1017/CBO9780511794193
[16] Novotny L., van Hulst N. Antennas for light. *Nature Photonics* **5**, 83–90 (2011). doi:10.1038/nphoton.2010.237
[17] Lee H. W., Schmidt M. A., Tyagi H. K., Sempere L. P., Russell P. St. J. Polarization-dependent coupling to plasmon modes on submicron gold wire in photonic crystal fiber. *Applied Physics Letters* **93**, 111102 (2008). doi:10.1063/1.2982083
[18] Schmidt M. A., Russell P. St. J. Long-range spiralling surface plasmon modes on metallic nanowires. *Optics Express* **16**, 13617–13623 (2008). doi:10.1364/OE.16.013617
[19] Taflove A., Hagness S. C. *Computational Electrodynamics: The Finite-Difference Time-Domain Method*, 3rd ed. Artech House, Boston (2005).
[20] Johnson P. B., Christy R. W. Optical constants of the noble metals. *Physical Review B* **6**, 4370–4379 (1972). doi:10.1103/PhysRevB.6.4370
[21] Ruppin R. Decay of an excited molecule near a small metal sphere. *The Journal of Chemical Physics* **76**, 1681–1684 (1982). doi:10.1063/1.443196
[22] Kim Y. S., Leung P. T., George T. F. Classical decay rates for molecules in the presence of a spherical surface: A complete treatment. *Surface Science* **195**, 1–14 (1988). doi:10.1016/0039-6028(88)90776-5
[23] Mertens H., Koenderink A. F., Polman A. Plasmon-enhanced luminescence near noble-metal nanospheres: Comparison of exact theory and an improved Gersten and Nitzan model. *Physical Review B* **76**, 115123 (2007). doi:10.1103/PhysRevB.76.115123
[24] Xu Y., Ji J., Guo Q., Wu Y., Ding T., Mao L., et al. Quantum plasmonics in nanocavities and its application. *Chinese Science Bulletin* **68**, 4086–4102 (2023). doi:10.1360/TB-2023-0350
[25] Babicheva V. E. Optical processes behind plasmonic applications. *Nanomaterials* **13**, 1270 (2023). doi:10.3390/nano13071270
[26] Bharadwaj P., Deutsch B., Novotny L. Optical antennas. *Advances in Optics and Photonics* **1**, 438–483 (2009). doi:10.1364/AOP.1.000438
[27] Andreussi O., Corni S., Mennucci B., Tomasi J. Radiative and nonradiative decay rates of a molecule close to a metal particle of complex shape. *The Journal of Chemical Physics* **121**, 10190–10202 (2004). doi:10.1063/1.1806819
[28] Carminati R., Sáenz J. J., Greffet J.-J., Nieto-Vesperinas M. Light emission by a dipole close to a rough surface: transition between near-field and far-field regimes. *Physical Review A* **62**, 012712 (2000). doi:10.1103/PhysRevA.62.012712
[29] Barreda Á. I., Vitale F., Minovich A. E., Ronning C., Staude I. Applications of hybrid metal–dielectric nanostructures: State of the art. *Advanced Photonics Research* **3**, 2100286 (2022). doi:10.1002/adpr.202100286
[30] Sauvan C., Hugonin J.-P., Maksymov I. S., Lalanne P. Theory of the spontaneous optical emission of nanosize photonic and plasmon resonators. *Physical Review Letters* **110**, 237401 (2013). doi:10.1103/PhysRevLett.110.237401
[31] **جایگزین پیشنهادی:** Lalanne P., Yan W., Vynck K., Sauvan C., Hugonin J.-P. Light interaction with photonic and plasmonic resonances. *Laser & Photonics Reviews* **12**, 1700113 (2018). doi:10.1002/lpor.201700113
  — (اگر Priyanka بماند: Priyanka, Tadi R., Soorat R. Design and numerical analysis of hybrid plasmonic–photonic crystal quantum-dot nanolasers with enhanced spontaneous emission. Preprint, SSRN 7011197 (2025).)
[32] Al-hamadani A., Al-Dulaimi A., Bartschmid T., Menath J., Muravitskaya A., Vogel N., et al. Tuning the spontaneous emission of CdTe quantum dots with hybrid silicon–gold nanogaps. *RSC Advances* **15**, 29053–29062 (2025). doi:10.1039/D5RA04583E
[33] Nikoobakht B., El-Sayed M. A. Preparation and growth mechanism of gold nanorods (NRs) using seed-mediated growth method. *Chemistry of Materials* **15**, 1957–1962 (2003). doi:10.1021/cm020732l

**مراجع جدید:**

[34] Vial A., Grimault A.-S., Macías D., Barchiesi D., Lamy de la Chapelle M. Improved analytical fit of gold dispersion: Application to the modeling of extinction spectra with a finite-difference time-domain method. *Physical Review B* **71**, 085416 (2005). doi:10.1103/PhysRevB.71.085416
[35] Ansys Lumerical. *Multi-coefficient material model (MCM)*. Ansys Lumerical FDTD 2024 R1 documentation / Ansys Optics Knowledge Base (2024).
[36] Kreibig U., Vollmer M. *Optical Properties of Metal Clusters*. Springer Series in Materials Science, Vol. 25. Springer, Berlin (1995). doi:10.1007/978-3-662-09109-8
[37] Coronado E. A., Schatz G. C. Surface plasmon broadening for arbitrary shape nanoparticles: A geometrical probability approach. *The Journal of Chemical Physics* **119**, 3926–3934 (2003). doi:10.1063/1.1587686
[38] Aharonovich I., Englund D., Toth M. Solid-state single-photon emitters. *Nature Photonics* **10**, 631–641 (2016). doi:10.1038/nphoton.2016.186
[39] Hoang T. B., Akselrod G. M., Mikkelsen M. H. Ultrafast room-temperature single photon emission from quantum dots coupled to plasmonic nanocavities. *Nano Letters* **16**, 270–275 (2016). doi:10.1021/acs.nanolett.5b03724

> پیش از ارسال، DOI مراجع ۳۴ تا ۳۹ را یک‌بار در doi.org باز کنید (از حافظه نوشته
> شده‌اند و خطای یک رقم ممکن است). عنوان مرجع ۵ هم در PDF فعلی «…: review» آمده؛
> عنوان رسمی مقاله‌ی Koenderink در ACS Photonics «Single-photon nanoantennas» است — چک شود.

---

## ۳. جمله‌های کاربردی (چشمه‌ی تک‌فوتونی): نسخه‌ی اصلاح‌شده‌ی یادداشت‌های دست‌نویس

یادداشت‌های «تو این صفحه هر جا AI گفت» ایده‌ی درستی دارند ولی دو خطای فیزیکی
و یک ناسازگاری با اعداد خودِ مقاله در آن‌ها هست. نسخه‌های زیر اصلاح‌شده‌اند.

### ۳.۱ مقدمه، پایان پاراگراف ۲ (ص ۲–۳)

> این رقابت به‌ویژه در توسعه‌ی چشمه‌های تک‌فوتونیِ تحریک پالسی (on-demand)
> برای شبکه‌های توزیع کلید کوانتومی (QKD) اهمیت بنیادی دارد [5, 38]: نرخ واپاشی
> کل، بیشینه‌ی نرخ تکرار چشمه را تعیین می‌کند و برای تولید فوتون‌های نامتمایز،
> طول‌عمر تابشی گسیلنده باید در مقایسه با زمان ناهمدوسی (dephasing time) کوتاه
> باشد [38, 39]. بنابراین سنجش دقیق سهم کانال‌های تابشی و اتلافی مشخص می‌کند در
> چه فاصله‌ای چشمه بیشترین فوتونِ قابل جمع‌آوری (روشنایی، Brightness) را بدون
> افتادن در دام اتلاف اهمی فلز تولید می‌کند.

(اصلاح: در یادداشت آمده بود «نرخ… سریع‌تر از **زمان** ناهمدوسی»؛ نرخ و زمان قابل
مقایسه نیستند — «طول‌عمر کوتاه‌تر از زمان ناهمدوسی» درست است.)

### ۳.۲ بخش ۲.۱، بعد از رابطه‌ی (۲) (ص ۴)

> در چارچوب الکترودینامیک کوانتومی و در رژیم جفت‌شدگی ضعیف، بخش موهومی تانسور
> گرین مستقیماً متناسب با LDOS تصویرشده بر جهت دوقطبی است [15]. از این رو
> ناهمسانگردی شدید این تانسور در نانومیله به این معناست که جهت‌گیری گسیلنده
> خود یک پارامتر طراحی است: هم‌راستا کردن دوقطبی گسیلنده با محور طولی، کانال
> تابشی را به‌مراتب بیش از کانال اتلافی تقویت می‌کند (بخش ۴.۲).

(کد خام `$\text{Im}[\overleftrightarrow{G}…]$` که در یادداشت آمده حذف شود؛ رابطه‌ی
(۲) همین را دارد.)

### ۳.۳ پایان بخش ۳.۱ (ص ۶–۷)

> در رژیم جفت‌شدگی ضعیف، دوقطبی نقطه‌ای کلاسیک مدل استاندارد یک گسیلنده‌ی
> دوترازه است: نسبت توان دوقطبی کلاسیک در حضور ساختار به توان آن در محیط همگن
> برابر نسبت نرخ گذار خودبه‌خودی کوانتومی ($A_{21}$) در همان دو محیط است
> [6, 15]. این هم‌ارزی تا زمانی برقرار است که جفت‌شدگی قوی (شکافت رابی) رخ ندهد.

### ۳.۴ بخش ۴.۴، پس از پاراگراف اول (ص ۱۳) — مهم: یادداشت فعلی با داده‌ها نمی‌خواند

یادداشت دست‌نویس می‌گوید «روشنایی ∝ $F_p\times\eta_a$ و گاف ۱۰–۱۵ nm بهینه است».
اما $F_p\times\eta_a=T$، و طبق جدول ۳، $T$ با افزایش گاف **کم** می‌شود
(۲۵۲ → ۱۱۹ → ۴۶.۸ → ۹.۹). پس اگر روشنایی را $T$ بگیریم، گاف کوچک بهینه است، نه
۱۰–۱۵ nm. (گاف ۱۵ nm هم اصلاً شبیه‌سازی نشده.) متن درست باید دو رژیم را جدا کند:

> از دید طراحی چشمه‌ی تک‌فوتونی، دو کمیت این پژوهش دو نقش متفاوت دارند:
> $F_p$ طول‌عمر برانگیختگی را تعیین می‌کند ($\tau=\tau_0/F_p$) و $\eta_a$
> احتمال آن را که هر برانگیختگی به یک فوتون در میدان دور تبدیل شود. اگر نرخ
> تکرار چشمه با خود گسیلنده محدود شود، آهنگ فوتون با $F_p\,\eta_a=T$ متناسب است؛
> اما در عمل نرخ تکرار با لیزر پالسی (ده‌ها مگاهرتز تا گیگاهرتز) تعیین می‌شود و
> طول‌عمر گسیلنده در هر سه گاف از دوره‌ی پالس بسیار کوتاه‌تر است؛ در این رژیم
> تعداد فوتون در هر پالس، و در نتیجه روشنایی، با $\eta_a$ متناسب است، نه با
> $F_p$. از این منظر گاف ۳ نانومتر با وجود $F_p\approx7\times10^3$ و $\eta_a$
> حدود ۰٫۰۵٪ عملاً چشمه‌ی ناکارآمدی است، و گاف‌های ۱۰ تا ۲۰ نانومتر — با
> طول‌عمر هنوز ۱۰^۲ تا ۵×۱۰^۲ برابر کوتاه‌تر و بازده ۹ تا ۱۲ درصد در قله‌ی تابشی —
> مصالحه‌ی معقول‌تری میان سرعت و روشنایی ارائه می‌کنند [5, 39].

### ۳.۵ نتیجه‌گیری، پایان پاراگراف ۲ (ص ۱۹)

> برای تحلیل داده‌های تجربی چشمه‌های تک‌فوتونی (مانند نقاط کوانتومیِ جفت‌شده با
> نانومیله)، این نتایج نشان می‌دهد که کوتاه‌شدن طول‌عمر در اندازه‌گیری TRPL
> به‌تنهایی بیانگر فوتون بیشتر نیست، زیرا $F_p$ کانال غیرتابشی را هم در بر دارد؛
> ارزیابی کامل نیازمند سنجش هم‌زمان بازده (یا شمارش فوتون) و تابع همبستگی
> $g^{(2)}(0)$ است.

### ۳.۶ چکیده (ص ۲)

- حذف جمله‌ی اول (علامت ①) قبول — ولی جمله‌ی «در این مقاله…» آن‌گاه با «در این
  مقاله» شروع شود.
- جمله‌ی آخر (②، «بنابراین نتایج… استوارند…») را **کامل حذف نکنید**؛ صداقت درباره‌ی
  عدم‌قطعیت نقطه‌ی قوت مقاله است. پیشنهاد جایگزین:

> پویش گاف نشان می‌دهد که در گاف‌های ۱۰ تا ۲۰ نانومتر، با وجود تقویت کمتر،
> بازده تابشی تا ۱۲٪ در قله و تا ۷۴٪ در بیشینه‌ی طیفی می‌رسد، که برای
> چشمه‌های تک‌فوتونی مصالحه‌ی مناسب‌تری است. نتایج بر مکان تشدیدها، بازده و
> نسبت‌های هم‌مش استوارند، نه بر رقم دقیق ارتفاع قله‌ها.

(«تا ۷۴٪» در یادداشت بدون قید آمده بود؛ ۷۴٪ بیشینه‌ی طیفی خارج از تشدید در گاف
۲۰ است، نه بازده در قله — باید قید شود وگرنه داور آن را گمراه‌کننده می‌داند.)

- عنوان: حذف زیرعنوان «محدودیت توصیف همسانگرد…» درست است؛ عنوان کوتاه‌تر بهتر است.

---

## ۴. کجا شانس چاپ دارد و چطور بدون تغییر اساسی بیشترش کنیم

### ارزیابی صادقانه

نقاط قوت: کنترل‌های درست (فضای آزاد، کره‌ی هم‌حجم، چرخش دوقطبی)، اعتبارسنجی با
حل تحلیلی می، و گزارش صریح عدم‌قطعیت — این‌ها در کارهای کارشناسی کم‌یاب‌اند.

نقاط ضعف از نگاه داور:
1. عدم‌قطعیت ±۴۰٪ در ارتفاع قله‌ها و مش ۲ nm در گاف ۵ nm (فقط ۲.۵ سلول).
   اجرای ۱.۵ nm یک قله‌ی ۳۷۵۲ غیرفیزیکی در ۵۴۰ nm دارد که داور حتماً می‌پرسد.
2. نرمال‌سازی فضای آزاد ±۱۳٪ با $\eta_B>1$ (غیرفیزیکی).
3. نوآوری: ناهمسانگردی LDOS کنار نانومیله و رقابت تقویت–خاموشی در ادبیات
   شناخته‌شده است (Mohammadi 2008، Anger 2006). سهم جدید «کمّی‌کردن تفکیک
   سهم هندسی/تشدیدی با کنترل کره‌ی هم‌حجم» است و باید همین برجسته شود.
4. بخش ۲ (اوربیتال اتمی و برچسب‌های $l,m$) برای مجله‌ی پژوهشی طولانی و آموزشی است.

### مقصدهای واقع‌بینانه (به ترتیب شانس)

| مقصد | زبان | شانس با نسخه‌ی فعلی | توضیح |
|---|---|---|---|
| کنفرانس اپتیک و فوتونیک ایران (ICOP) یا کنفرانس ملی نانو | فارسی | بالا | نسخه‌ی ۴–۶ صفحه‌ای؛ مناسب‌ترین گام اول برای پروژه‌ی کارشناسی |
| مجلات فارسی علمی‌پژوهشی فیزیک (مثل «پژوهش فیزیک ایران» یا «فیزیک کاربردی ایران») | فارسی | متوسط | ساختار فعلی مناسب است؛ بخش ۲ کوتاه شود |
| Journal of Optoelectronical Nanostructures و مجلات انگلیسی داخلی مشابه | انگلیسی | متوسط | نیاز به ترجمه |
| *Optical and Quantum Electronics* یا *Plasmonics* (Springer) | انگلیسی | پایین تا متوسط | فقط اگر دو اجرای اضافه‌ی زیر انجام شود |
| *Optics Express*، *JOSA B*، *ACS Photonics* | انگلیسی | پایین | نوآوری و همگرایی کافی نیست |

> پیش از ارسال به هر مجله، فهرست مجلات نامعتبر وزارت علوم و صفحه‌ی رسمی مجله
> (رتبه، هزینه‌ی چاپ، زبان) را چک کنید؛ این جدول ارزیابی کلی است، نه فهرست تأییدشده.

### کارهای کم‌هزینه که شانس را بالا می‌برند (بدون تغییر اساسی)

1. **یک اجرای مش ۱ nm برای حالت A** با چشمه‌ی دقیقاً روی گره (همان چیزی که خودتان
   در بخش ۴.۵ پیشنهاد داده‌اید). اگر ±۴۰٪ به حدود ±۱۰٪ برسد، بزرگ‌ترین ایراد
   داور برطرف می‌شود. این یک اجرای شبیه‌سازی است، نه تغییر مقاله.
2. **تکرار حالت B با جعبه‌ی شبیه‌سازی/PML بزرگ‌تر** تا $\eta_B>1$ حذف شود.
3. **گزارش RMSE برازش مدل چندضریبی** (یک عدد از Lumerical) — جدول ۴ کامل می‌شود.
4. **کوتاه کردن بخش ۲** به حدود نصف (جدول ۱ بماند، بحث فلسفی‌تر حذف).
5. یکی کردن پیام: عنوان و چکیده حول یک جمله — «تقویت پورسل بدون بازده معیار کافی
   نیست؛ کنترل کره‌ی هم‌حجم سهم تشدید طولی را ۱۵ تا ۲۶ برابر جدا می‌کند».
6. اصلاحات این فایل (مراجع شماره‌دار، حذف پیش‌انتشار، جمله‌های کاربردی).
7. برای مجله‌ی انگلیسی: ترجمه‌ی روان + Cover letter که سهم نو را صریح بگوید
   + بخش «Data availability» (فایل‌های ۲۰۱ نقطه‌ای و اسکریپت lsf موجود است).
