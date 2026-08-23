# Account Record Cleaner

<div dir="rtl">

## فارسی

### این پوشه چیست؟

ابزار محلی برای حذف رکوردی که کلاینت دسکتاپ Windscribe روی ویندوز از **حساب منقضی‌شده‌ی قبلی** ذخیره می‌کند. این پوشه بخشی از مخزن رسمی Windscribe نیست و در `.gitignore` قرار داده شده است.

### مسئله

وقتی کلاینت یک حساب رایگان با وضعیت منقضی (`status == 2`) ببیند، مشخصات آن حساب — `username`، `userId` و `date` — را به‌صورت رمزگذاری‌شده در رجیستری ذخیره می‌کند. اسم کلید طوری انتخاب شده که شبیه کلیدهای خود ویندوز به نظر برسد:

</div>

```
HKCU\Software\Microsoft\Windows\CurrentVersion\NetControlPort
    Version  REG_DWORD    0x1
    State    REG_BINARY   <encrypted blob>
```

<div dir="rtl">

در اجرای بعدی، اگر حساب فعلی رایگان و متفاوت از رکورد ذخیره‌شده باشد، کلاینت وارد حالت `CONNECT_BLOCKED_MULTI_ACCOUNT` می‌شود و این پیام را نشان می‌دهد:

</div>

> Your original account `<username>` has expired.
> Creating multiple accounts to bypass free tier limitations is prohibited.

<div dir="rtl">

### مسیرهای مرتبط در کد

| فایل | نقش |
|---|---|
| `src/client/frontend/frontend-common/multipleaccountdetection/secretvalue_win.cpp` | خواندن/نوشتن/حذف کلید رجیستری (رمزگذاری با کلید ثابت `0xFA7234AAF37A31BE`) |
| `src/client/frontend/gui/mainwindow.cpp` | شرط تشخیص وضعیت چند-حسابی |
| `src/client/frontend/frontend-common/blockconnect.cpp` | ساخت متن پیام خطا |

### فایل‌ها

| فایل | توضیح |
|---|---|
| `clear-account-record.ps1` | اسکریپت اصلی پاک‌سازی |
| `clear-account-record.bat` | اجرا با دابل‌کلیک (ExecutionPolicy را دور می‌زند، خروجی را UTF-8 می‌کند) |
| `backups/` | بکاپ‌های `.reg` با تاریخ‌ومهر — در `.gitignore` است |
| `connection-error-fix.txt` | یادداشت‌های اولیه‌ی تحلیل |

### نحوه‌ی استفاده

</div>

```powershell
# حالت عادی — بکاپ می‌گیرد و حذف می‌کند
.\clear-account-record.ps1

# توصیه‌شده: اول کلاینت را ببند تا رکورد بلافاصله دوباره نوشته نشود
.\clear-account-record.ps1 -KillClient

# بدون بکاپ
.\clear-account-record.ps1 -NoBackup

# مسیر دلخواه برای بکاپ
.\clear-account-record.ps1 -BackupDir D:\backups
```

<div dir="rtl">

یا فقط `clear-account-record.bat` را دابل‌کلیک کنید.

### هر بار اجرا چه اتفاقی می‌افتد

۱. اگر `-KillClient` داده شده باشد، پروسه‌های `Windscribe` بسته می‌شوند.

۲. اگر کلید وجود نداشته باشد، پیام «تمیز است» و خروج با کد `0`. اجرای مکرر بی‌خطر است.

۳. محتوای فعلی کلید نمایش داده می‌شود (`Version` و پیش‌نمایش هگز `State`).

۴. بکاپ `.reg` با نام `netcontrolport-YYYYMMDD-HHMMSS.reg` ساخته می‌شود. اگر بکاپ ناموفق باشد، حذف انجام **نمی‌شود** و خروج با کد `1`.

۵. کلید حذف و حذف‌شدنش تأیید می‌شود. اگر هنوز موجود باشد، خروج با کد `1`.

### بازگردانی

</div>

```powershell
reg.exe import .\backups\netcontrolport-original.reg
```

<div dir="rtl">

### محدودیت‌ها

- **دائمی نیست.** تابع `setValue()` هر بار که کلاینت دوباره یک حساب منقضی ببیند، همین کلید را از نو می‌سازد. برای جلوگیری دائمی باید در سطح کد جلوی `MultipleAccountDetection_win::userBecomeExpired()` گرفته شود.
- **فقط محلی است.** هیچ تغییری در وضعیت سمت سرور Windscribe ایجاد نمی‌کند. اگر محدودیتی سمت سرور اعمال شده باشد، این ابزار تأثیری روی آن ندارد.
- **فقط ویندوز.** روی macOS و لینوکس از `multipleaccountdetection_posix.cpp` استفاده می‌شود که مکانیزم ذخیره‌سازی متفاوتی دارد.
- نیازی به دسترسی Administrator نیست — کلید زیر `HKCU` است.

</div>

---

## English

### What is this?

A local utility that removes the record the Windscribe desktop client keeps on Windows about a **previously expired account**. This folder is not part of the upstream Windscribe repository and is listed in `.gitignore`.

### The problem

When the client sees a free account whose status is expired (`status == 2`), it stores that account's `username`, `userId`, and `date` — encrypted — in the registry, under a key named to look like a stock Windows key:

```
HKCU\Software\Microsoft\Windows\CurrentVersion\NetControlPort
    Version  REG_DWORD    0x1
    State    REG_BINARY   <encrypted blob>
```

On a later run, if the current account is free and differs from the stored record, the client enters `CONNECT_BLOCKED_MULTI_ACCOUNT` and shows:

> Your original account `<username>` has expired.
> Creating multiple accounts to bypass free tier limitations is prohibited.

### Relevant source paths

| File | Role |
|---|---|
| `src/client/frontend/frontend-common/multipleaccountdetection/secretvalue_win.cpp` | Reads/writes/deletes the registry key (encrypted with fixed key `0xFA7234AAF37A31BE`) |
| `src/client/frontend/gui/mainwindow.cpp` | The multi-account detection condition |
| `src/client/frontend/frontend-common/blockconnect.cpp` | Builds the error message text |

### Files

| File | Description |
|---|---|
| `clear-account-record.ps1` | The cleanup script |
| `clear-account-record.bat` | Double-click launcher (bypasses ExecutionPolicy, sets UTF-8 output) |
| `backups/` | Timestamped `.reg` backups — gitignored |
| `connection-error-fix.txt` | Original analysis notes |

### Usage

```powershell
# Normal run — backs up, then deletes
.\clear-account-record.ps1

# Recommended: close the client first so the record isn't rewritten immediately
.\clear-account-record.ps1 -KillClient

# Skip the backup
.\clear-account-record.ps1 -NoBackup

# Custom backup location
.\clear-account-record.ps1 -BackupDir D:\backups
```

Or just double-click `clear-account-record.bat`.

### What each run does

1. If `-KillClient` was passed, terminates any `Windscribe` processes.
2. If the key does not exist, reports "clean" and exits `0`. Repeated runs are safe.
3. Prints the current key contents (`Version`, and a hex preview of `State`).
4. Writes a `.reg` backup named `netcontrolport-YYYYMMDD-HHMMSS.reg`. If the backup fails, **nothing is deleted** and it exits `1`.
5. Deletes the key and verifies it is gone. If it still exists, exits `1`.

### Restoring

```powershell
reg.exe import .\backups\netcontrolport-original.reg
```

### Limitations

- **Not permanent.** `setValue()` recreates the same key whenever the client next sees an expired account. Preventing that for good requires a code-level change around `MultipleAccountDetection_win::userBecomeExpired()`.
- **Local only.** It changes nothing server-side. If Windscribe has applied a restriction on their end, this tool has no effect on it.
- **Windows only.** macOS and Linux use `multipleaccountdetection_posix.cpp`, which stores the record differently.
- No Administrator rights needed — the key lives under `HKCU`.
