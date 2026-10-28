<h1 align="center">Account Record Cleaner</h1>

<p align="center">
  <em>Removes the local "expired account" record the Windscribe Windows client stores in the registry.</em>
</p>

<p align="center">
  <img alt="Platform" src="https://img.shields.io/badge/platform-Windows-0078D6?logo=windows&logoColor=white">
  <img alt="Python" src="https://img.shields.io/badge/python-3.9%2B-3776AB?logo=python&logoColor=white">
  <img alt="Admin rights" src="https://img.shields.io/badge/admin%20rights-not%20required-brightgreen">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-blue">
</p>

<p align="center">
  <a href="#english">English</a> &nbsp;&middot;&nbsp; <a href="#persian">فارسی</a>
</p>

---

<h2 id="english">English</h2>

### What is this?

A small Python tool (with ready-made `.exe` builds) that backs up and deletes the registry key in
which the **Windscribe desktop client for Windows** records a *previously expired* free account.

It touches **one key under `HKCU`** and nothing else. It is not a patch, a crack, or a modified
client — it removes a local record and keeps a `.reg` backup so you can put it back.

> [!IMPORTANT]
> Local cleanup only. It does **not** change anything on Windscribe's servers and does not grant,
> extend, or restore any subscription. See [Limitations](#limitations).

### The problem

When the client sees a free account whose status is expired (`status == 2`), it stores that
account's `username`, `userId`, and `date` — encrypted — under a key named to look like a stock
Windows key:

```
HKCU\Software\Microsoft\Windows\CurrentVersion\NetControlPort
    Version  REG_DWORD    0x1
    State    REG_BINARY   <encrypted blob>
```

On a later run, if the current account is free and differs from the stored record, the client
enters `CONNECT_BLOCKED_MULTI_ACCOUNT` and shows:

> Your original account `<username>` has expired.
> Creating multiple accounts to bypass free tier limitations is prohibited.

The message is not about a wrong password or a broken connection — it is this local record.

### Download

Get the latest build from **[Releases](../../releases/latest)**:

| File | What it is |
|---|---|
| `AccountRecordCleaner.exe` | Small window — double-click, pick options, press the button |
| `AccountRecordCleaner-cli.exe` | Console version for terminals and scripts |
| `SHA256SUMS.txt` | Checksums — compare with `Get-FileHash <file>` |

The executables are built by GitHub Actions from this repository's source
(`.github/workflows/release.yml`). They are not code-signed, so Windows SmartScreen may warn on
first launch.

### Usage

```powershell
AccountRecordCleaner-cli.exe --kill-client      # close Windscribe, back up, delete
AccountRecordCleaner-cli.exe --dry-run          # show what would happen, change nothing
AccountRecordCleaner-cli.exe --restore          # re-import the newest backup
AccountRecordCleaner-cli.exe --list-backups
```

| Option | Meaning |
|---|---|
| `--kill-client` | Ask Windscribe to close (so it disconnects cleanly), force it only if needed, wait until it is gone |
| `--no-backup` | Delete without a `.reg` backup |
| `--backup-dir DIR` | Where backups are written / read |
| `--dry-run` | Report only |
| `--restore [FILE]` | Import a backup (default: newest) instead of cleaning |
| `--list-backups` | List backups and exit |

| Exit code | Meaning |
|---|---|
| `0` | Key deleted / restored, or no key was present |
| `1` | Backup failed, delete failed, or the client could not be closed |
| `2` | Not running on Windows |

If a backup cannot be written, **nothing is deleted**. Backups are never overwritten (a numeric
suffix is added if two runs share a timestamp). They go to `backups/` next to the program, or to
`%LOCALAPPDATA%\AccountRecordCleaner\backups` if that folder is not writable.

> [!WARNING]
> `backups/` and `*.reg` are gitignored on purpose — a backup contains your encrypted account
> record. Never commit one.

### Run from source

```powershell
python -m pip install -e .
python -m account_cleaner --kill-client
python -m account_cleaner.gui          # the window
```

### Build the exe yourself

```powershell
python -m pip install -e ".[dev]"
python packaging/build.py              # -> dist/AccountRecordCleaner*.exe
```

To publish a release: push a tag such as `v1.0.0`. The *Release* workflow builds on a Windows
runner, runs the tests and a smoke test, and attaches the files to a GitHub Release.

### Development

```
account_cleaner/   core logic, registry backend, process handling, CLI, GUI
tests/             unit tests (in-memory registry fake) + opt-in real-registry test
packaging/         PyInstaller entry points and build script
.github/workflows/ CI, exe build, release
```

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
```

### Where this comes from

These paths live in the **upstream Windscribe client source**
([Windscribe/Desktop-App](https://github.com/Windscribe/Desktop-App)), not in this repository, and
are listed so the behaviour can be verified rather than taken on trust:

| File | Role |
|---|---|
| `src/client/frontend/frontend-common/multipleaccountdetection/secretvalue_win.cpp` | Reads/writes/deletes the registry key |
| `src/client/frontend/gui/mainwindow.cpp` | The multi-account detection condition |
| `src/client/frontend/frontend-common/blockconnect.cpp` | Builds the error message text |

The detection fires when all of these hold: a previous free account with `status == 2` is on
record, that record exists in local storage, the current account is free rather than premium, it
differs from the stored one (username or user ID), and it is otherwise active.

### Limitations

- **Not permanent.** The client recreates the key whenever it next sees an expired account.
- **Local only.** Nothing changes server-side. If Windscribe applied a restriction on their end,
  this tool has no effect on it.
- **Windows only.** macOS and Linux store the record differently.

### Disclaimer

Published for research and educational purposes — documenting how a client-side detection
mechanism stores state on your own machine, and how to inspect and reset it. Complying with
Windscribe's Terms of Service is your responsibility. Not affiliated with or endorsed by
Windscribe. No warranty; use at your own risk.

### License

MIT — see [LICENSE](LICENSE).

---

<div dir="rtl">

<h2 id="persian">فارسی</h2>

### این چیست؟

یک ابزار کوچک Python (با نسخه‌ی آماده‌ی `.exe`) که از کلید رجیستریِ مربوط به رکورد حساب منقضی‌شده در کلاینت دسکتاپ Windscribe روی ویندوز بکاپ می‌گیرد و سپس آن را حذف می‌کند.

فقط یک کلید زیر `HKCU` را دست می‌زند. نه پچ است، نه کرک، نه کلاینت دستکاری‌شده — یک رکورد محلی را حذف می‌کند و بکاپ `.reg` نگه می‌دارد تا بتوانید برش گردانید.

> [!IMPORTANT]
> این ابزار فقط محلی است. هیچ تغییری در سمت سرور Windscribe ایجاد نمی‌کند و هیچ اشتراکی را تمدید یا فعال نمی‌کند.

### مسئله

وقتی کلاینت یک حساب رایگان با وضعیت منقضی (`status == 2`) ببیند، مشخصات آن حساب — `username`، `userId` و `date` — را رمزگذاری‌شده در رجیستری ذخیره می‌کند. اسم کلید طوری انتخاب شده که شبیه کلیدهای خود ویندوز باشد:

</div>

```
HKCU\Software\Microsoft\Windows\CurrentVersion\NetControlPort
    Version  REG_DWORD    0x1
    State    REG_BINARY   <encrypted blob>
```

<div dir="rtl">

در اجرای بعدی، اگر حساب فعلی رایگان و متفاوت از رکورد ذخیره‌شده باشد، کلاینت وارد حالت `CONNECT_BLOCKED_MULTI_ACCOUNT` می‌شود و پیام «Your original account ... has expired» را نشان می‌دهد. علتش اشتباه‌بودن رمز یا قطع‌بودن اینترنت نیست؛ همین رکورد محلی است.

### دانلود

آخرین نسخه را از **[Releases](../../releases/latest)** بگیرید:

| فایل | توضیح |
|---|---|
| `AccountRecordCleaner.exe` | پنجره‌ی ساده — دابل‌کلیک، انتخاب گزینه‌ها، زدن دکمه |
| `AccountRecordCleaner-cli.exe` | نسخه‌ی کنسولی برای ترمینال و اسکریپت |
| `SHA256SUMS.txt` | چک‌سام — با `Get-FileHash <file>` مقایسه کنید |

فایل‌های exe با GitHub Actions از سورس همین مخزن ساخته می‌شوند. امضای دیجیتال ندارند، پس ممکن است SmartScreen در اولین اجرا هشدار بدهد.

### نحوه‌ی استفاده

</div>

```powershell
AccountRecordCleaner-cli.exe --kill-client      # بستن Windscribe، بکاپ، حذف
AccountRecordCleaner-cli.exe --dry-run          # فقط نشان بده چه می‌شود
AccountRecordCleaner-cli.exe --restore          # برگرداندن جدیدترین بکاپ
AccountRecordCleaner-cli.exe --list-backups
```

<div dir="rtl">

گزینه‌ها: `--kill-client` (ابتدا بستن تمیز، فقط در صورت نیاز اجبارا بستن، و صبر تا بسته‌شدن کامل)، `--no-backup`، `--backup-dir DIR`، `--dry-run`، `--restore [FILE]`، `--list-backups`.

کد خروج: `0` موفق (یا رکوردی نبود)، `1` شکست در بکاپ/حذف/بستن کلاینت، `2` ویندوز نیست.

اگر بکاپ ساخته نشود، **هیچ چیزی حذف نمی‌شود**. بکاپ‌ها هرگز بازنویسی نمی‌شوند و در پوشه‌ی `backups/` کنار برنامه (یا در `%LOCALAPPDATA%\AccountRecordCleaner\backups` اگر آن پوشه قابل نوشتن نبود) ذخیره می‌شوند.

> [!WARNING]
> پوشه‌ی `backups/` و فایل‌های `*.reg` عمداً در `.gitignore` هستند — هر بکاپ حاوی رکورد رمزگذاری‌شده‌ی حساب شماست. هرگز آن را commit نکنید.

### اجرا از سورس

</div>

```powershell
python -m pip install -e .
python -m account_cleaner --kill-client
python -m account_cleaner.gui          # پنجره
```

<div dir="rtl">

### ساخت exe توسط خودتان

</div>

```powershell
python -m pip install -e ".[dev]"
python packaging/build.py              # -> dist/AccountRecordCleaner*.exe
```

<div dir="rtl">

برای انتشار: یک تگ مثل `v1.0.0` پوش کنید؛ workflow با نام *Release* روی ویندوز تست و build می‌کند و فایل‌ها را به Release اضافه می‌کند.

### ساختار

| مسیر | توضیح |
|---|---|
| `account_cleaner/` | هسته، دسترسی به رجیستری، مدیریت پروسه، CLI و GUI |
| `tests/` | تست‌های واحد و یک تست اختیاری روی رجیستری واقعی |
| `packaging/` | نقطه‌ی ورود PyInstaller و اسکریپت ساخت |
| `.github/workflows/` | CI، ساخت exe، انتشار |

### محدودیت‌ها

- دائمی نیست؛ کلاینت هر بار که دوباره حساب منقضی ببیند، کلید را از نو می‌سازد.
- فقط محلی است؛ اگر محدودیتی سمت سرور اعمال شده باشد، تأثیری روی آن ندارد.
- فقط ویندوز؛ macOS و لینوکس رکورد را متفاوت ذخیره می‌کنند.

### سلب مسئولیت

این مخزن با هدف پژوهشی و آموزشی منتشر شده است. رعایت شرایط استفاده‌ی (ToS) شرکت Windscribe بر عهده‌ی خود شماست. این پروژه هیچ وابستگی یا تأییدی از سوی Windscribe ندارد. بدون هیچ ضمانتی ارائه می‌شود؛ مسئولیت استفاده با شماست.

### لایسنس

MIT — فایل [LICENSE](LICENSE) را ببینید.

</div>
