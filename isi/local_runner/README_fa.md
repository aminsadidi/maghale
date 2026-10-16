# راهنمای راه‌اندازی کامپیوتر استاد برای شبیه‌سازی خودکار

کامپیوتر استاد یک بار به مخزن GitHub وصل می‌شود. از آن به بعد هر کاری که در فایل `isi/local_runner/jobs.txt`
تعریف شود را خودش برمی‌دارد، با MATLAB همان کامپیوتر اجرا می‌کند و نتیجه را به GitHub برمی‌گرداند.
لازم نیست کد را دستی منتقل کنید.

## مرحله ۰: بررسی سیستم (۲ دقیقه، هیچ چیزی را تغییر نمی‌دهد)

1. PowerShell را باز کنید (منوی Start، بنویسید PowerShell).
2. این دستور را کپی و اجرا کنید:

```powershell
cd $HOME\Desktop; iwr https://raw.githubusercontent.com/aminsadidi/maghale/claude/sleepy-rubin-e80q4k/isi/local_runner/check_pc.ps1 -OutFile check_pc.ps1; powershell -ExecutionPolicy Bypass -File .\check_pc.ps1
```

3. فایل `pc_report.txt` روی Desktop ساخته می‌شود. متنش را برای من بفرستید: نشان می‌دهد MATLAB، COMSOL و Lumerical
   نصب هستند یا نه، و حافظه و پردازنده چقدر است.

(اگر دانلود کار نکرد، مخزن احتمالاً خصوصی است: فایل `check_pc.ps1` را از سایت GitHub دانلود کنید و فقط خط آخر را اجرا کنید.)

## مرحله ۱: نصب Git (اگر در گزارش «git: not found» بود)

```powershell
winget install --id Git.Git -e
```

بعد از نصب، PowerShell را ببندید و دوباره باز کنید.

## مرحله ۲: وصل کردن کامپیوتر به GitHub (۱۰ دقیقه)

1. در مرورگر بروید به صفحه‌ی مخزن: `github.com/aminsadidi/maghale`
2. **Settings → Actions → Runners → New self-hosted runner**
3. گزینه‌ی **Windows** و **x64** را انتخاب کنید.
4. GitHub چند دستور نشان می‌دهد (بخش Download و Configure). آن‌ها را **به همان ترتیب** در PowerShell کپی و اجرا کنید.
   - اولین دستور یک پوشه به نام `actions-runner` می‌سازد؛ بهتر است در `C:\` باشد (`cd C:\` قبلش).
5. دستور `config.cmd` چند سؤال می‌پرسد:
   - runner group: فقط Enter
   - **name**: مثلاً `lab-pc`
   - **additional labels**: حتماً بنویسید: `lab32`
   - work folder: فقط Enter
   - **run as service?** بنویسید: `N`. اجرا به‌صورت سرویس زیر یک حساب دیگر ویندوز است و ممکن است لایسنس MATLAB
     را نبیند.
6. در آخر اجرا کنید:

```powershell
.\run.cmd
```

پیام `Listening for Jobs` یعنی همه‌چیز درست است. **این پنجره را باز بگذارید** (می‌توانید minimize کنید).

## مرحله ۳: تنظیمات ویندوز

- **Settings → System → Power**: حالت Sleep را روی **Never** بگذارید؛ وگرنه شبیه‌سازی‌های طولانی قطع می‌شوند.
- بعد از هر بار روشن شدن کامپیوتر، فقط پوشه‌ی `C:\actions-runner` را باز کنید و `run.cmd` را اجرا کنید.

## مرحله ۴: امنیت (یک بار، در سایت GitHub)

**Settings → Actions → General → Fork pull request workflows from outside collaborators**:
گزینه‌ی **Require approval for all external contributors** را انتخاب کنید.
با این تنظیم هیچ کس بیرون از گروه ما نمی‌تواند روی این کامپیوتر برنامه اجرا کند.

## بعد از راه‌اندازی

به من خبر بدهید. یک کار آزمایشی کوچک (چند دقیقه) می‌فرستم. اگر نتیجه‌اش برگشت، کارهای سنگین را
(مش ریز، تریمرهای بزرگ، و در صورت وجود COMSOL یا Lumerical، تأیید مستقل با FEM/FDTD) روی این کامپیوتر اجرا می‌کنیم.

برای قطع کردن: در پنجره‌ی `run.cmd` کلید Ctrl+C را بزنید. برای حذف کامل: در همان پوشه
`.\config.cmd remove` را اجرا کنید (توکن را GitHub در همان صفحه‌ی Runners می‌دهد).
