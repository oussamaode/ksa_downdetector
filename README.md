<div dir="rtl">

# 🇸🇦 مراقب انقطاع خدمات السعودية — KSA Downdetector

</div>

<p align="center">
  <strong>Real-time status monitoring for the most popular Saudi Arabian platforms</strong><br>
  <em>مراقبة حالة أشهر المنصات السعودية في الوقت الفعلي</em>
</p>

<p align="center">
  <a href="#-english">English</a> •
  <a href="#-العربية">العربية</a>
</p>

---

## 🇬🇧 English

**KSA Downdetector** is a lightweight, fully client-side status page that tracks the availability of 29 popular Saudi platforms — government services, banks, e-commerce, delivery, telecoms and global apps — with a sleek dark UI, bilingual support (English / العربية with full RTL), live search, and automatic status updates via GitHub Actions.

### ✨ Features

- 🟢 **Real-time monitoring** — `monitor.py` checks every platform concurrently (10 threads) and records status + response time
- 🔄 **Auto-updates every 10 minutes** via GitHub Actions cron, committing fresh `status.json`
- 🌐 **Bilingual UI** — English ↔ Arabic toggle with full RTL layout and the Cairo font
- 🔍 **Live search** — filter platforms by name in either language
- 🎨 **Dark modern UI** — Tailwind CSS, animated status dots, card hover effects
- 🖼️ **Brand logos** — SVG logos with graceful initials fallback if a logo fails to load or times out (6s)
- 🛡️ **Anti-bot aware** — platforms behind bot protection (401/403/405/429) are reported as ONLINE since the server is responding
- 🔐 **Broken certificate tolerant** — platforms with incomplete TLS chains can opt out of SSL verification
- 📋 **Copy ID** — click any card to copy the platform ID to clipboard
- 🚀 **Zero backend** — pure static site, deployable anywhere (GitHub Pages, Netlify, any web server)

### 📂 Project structure

```
├── index.html               # Status page (UI + client logic)
├── monitor.py               # Health-check script (Python + requests)
├── plataformas_ksa.json     # Platform catalog (id, names, URL, logo)
├── status.json              # Latest check results (auto-generated)
└── .github/workflows/
    └── monitor_cron.yml     # Cron job: runs monitor every 10 min
```

### 🏃‍♂️ Local usage

```bash
# 1. Install dependency
pip install requests

# 2. Run the monitor (refreshes status.json)
python monitor.py

# 3. Serve the page (fetch() needs http, not file://)
python -m http.server 8000
# then open http://localhost:8000
```

### ➕ Adding a platform

Append an entry to `plataformas_ksa.json` under the right category:

```json
{"id": "my_platform", "nombre_en": "My Platform", "nombre_ar": "منصتي", "url": "https://example.com", "logo_url": "https://example.com/logo.svg"}
```

Add `"verify_ssl": false` only if the site serves an incomplete certificate chain (e.g. some Saudi banks).

Statuses: `ONLINE` (2xx/3xx response, or anti-bot 401/403/405/429), `ISSUE` (other HTTP code), `OFFLINE` (timeout / connection error).

### 🚀 Deployment

Push the repo to GitHub and enable **GitHub Pages** — the workflow keeps `status.json` fresh automatically.

---

## 🇸🇦 العربية

**مراقب انقطاع خدمات السعودية** هو صفحة حالة خفيفة وسهلة لمتابعة توفر 29 من أشهر المنصات السعودية — الخدمات الحكومية، البنوك، التجارة الإلكترونية، التوصيل، الاتصالات والتطبيقات العالمية — بواجهة داكنة عصرية، ودعم كامل للغتين (الإنجليزية / العربية مع اتجاه RTL)، وبحث فوري، وتحديث تلقائي لحالات المنصات عبر GitHub Actions.

### ✨ المميزات

- 🟢 **مراقبة لحظية** — يفحص `monitor.py` جميع المنصات بالتوازي (10 خيوط) ويسجل الحالة وزمن الاستجابة
- 🔄 **تحديث تلقائي كل 10 دقائق** عبر جدولة GitHub Actions مع تحديث ملف `status.json`
- 🌐 **واجهة ثنائية اللغة** — تبديل بين الإنجليزية والعربية مع دعم كامل لاتجاه RTL وخط Cairo
- 🔍 **بحث فوري** — تصفية المنصات بالاسم بالعربية أو الإنجليزية
- 🎨 **واجهة داكنة عصرية** — Tailwind CSS مع مؤشرات حالة متحركة وتأثيرات تفاعلية
- 🖼️ **شعارات المنصات** — شعارات SVG مع بديل أنيق بالأحرف الأولى إذا فشل تحميل الشعار
- 🛡️ **تجاوز حماية البوتات** — المنصات المحمية (401/403/405/429) تُسجَّل كـ ONLINE لأن الخادم يستجيب
- 🔐 **تحمّل الشهادات المعطوبة** — يمكن للمنصات ذات سلسلة الشهادات الناقصة تعطيل التحقق من SSL
- 📋 **نسخ المعرّف** — اضغط على أي بطاقة لنسخ معرّف المنصة
- 🚀 **بدون خادم** — موقع ثابت بحت يمكن استضافةه في أي مكان

### 📂 بنية المشروع

```
├── index.html               # صفحة الحالة (الواجهة ومنطق العميل)
├── monitor.py               # سكربت الفحص (بايثون + requests)
├── plataformas_ksa.json     # كتالوج المنصات (المعرّف، الأسماء، الرابط، الشعار)
├── status.json              # أحدث نتائج الفحص (يُولَّد تلقائيًا)
└── .github/workflows/
    └── monitor_cron.yml     # المهمة المجدولة: فحص كل 10 دقائق
```

### 🏃‍♂️ التشغيل محليًا

```bash
# 1. تثبيت المتطلب
pip install requests

# 2. تشغيل المراقب (يحدّث status.json)
python monitor.py

# 3. تشغيل الصفحة محليًا (fetch يحتاج http وليس file://)
python -m http.server 8000
# ثم افتح http://localhost:8000
```

### ➕ إضافة منصة

أضف عنصرًا إلى `plataformas_ksa.json` داخل الفئة المناسبة:

```json
{"id": "my_platform", "nombre_en": "My Platform", "nombre_ar": "منصتي", "url": "https://example.com", "logo_url": "https://example.com/logo.svg"}
```

أضف `"verify_ssl": false` فقط إذا كان الموقع يستخدم سلسلة شهادات ناقصة (مثل بعض البنوك السعودية).

الحالات المتاحة: `ONLINE` (استجابة 2xx/3xx أو حماية بوت 401/403/405/429)، `ISSUE` (رمز آخر)، `OFFLINE` (انتهاء مهلة أو خطأ اتصال).

### 🚀 النشر

ارفع المستودع إلى GitHub ثم فعّل **GitHub Pages** — ستحافظ المهمة المجدولة على تحديث `status.json` تلقائيًا.

---

<p align="center">
  Made with 💚 for Saudi Arabia
</p>
