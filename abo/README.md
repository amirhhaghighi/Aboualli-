# پروژه ABO - سیستم مدیریت باشگاه ورزشی

## 📋 توضیحات پروژه

پروژه ABO یک سیستم جامع مدیریت باشگاه ورزشی است که شامل مدیریت مربیان، اعضا، کیف پول‌ها، تست‌ها و باشگاه‌ها می‌باشد.

## 🏗️ ساختار پروژه

### اپلیکیشن‌های موجود:

1. **coachpanel** - مدیریت مربیان و تخصیص تست‌ها
2. **fiatwallet** - کیف پول فیات (ریال)
3. **tokenwallet** - کیف پول توکن‌ها
4. **gympanel** - مدیریت باشگاه‌ها
5. **membership** - مدیریت اعضا و عضویت‌ها
6. **testprocess** - مدیریت تست‌های ورزشی

## 🚀 نصب و راه‌اندازی

### پیش‌نیازها:
- Python 3.8+
- pip

### مراحل نصب:

1. **کلون کردن پروژه:**
```bash
git clone <repository-url>
cd abo
```

2. **ایجاد محیط مجازی:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# یا
venv\Scripts\activate  # Windows
```

3. **نصب وابستگی‌ها:**
```bash
pip install -r requirements.txt
```

4. **اجرای مایگریشن‌ها:**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **ایجاد سوپر یوزر:**
```bash
python manage.py createsuperuser
```

6. **اجرای سرور:**
```bash
python manage.py runserver
```

## 📚 API Endpoints

### Coach Panel:
- `GET /api/coach/wallets/` - لیست کیف پول‌های مربیان
- `POST /api/coach/wallets/` - ایجاد کیف پول مربی
- `GET /api/coach/transactions/` - لیست تراکنش‌ها
- `GET /api/coach/deposits/` - لیست واریزها
- `GET /api/coach/withdrawals/` - لیست برداشت‌ها

### Fiat Wallet:
- `GET /api/fiat/wallets/` - لیست کیف پول‌های فیات
- `POST /api/fiat/deposits/` - درخواست واریز
- `POST /api/fiat/withdrawals/` - درخواست برداشت
- `GET /api/fiat/transactions/` - لیست تراکنش‌ها

### Token Wallet:
- `GET /api/token/wallets/` - لیست کیف پول‌های توکن
- `POST /api/token/deposits/` - درخواست واریز توکن
- `POST /api/token/withdrawals/` - درخواست برداشت توکن

### Gym Panel:
- `GET /api/gym/gyms/` - لیست باشگاه‌ها
- `POST /api/gym/gyms/` - ایجاد باشگاه جدید
- `GET /api/gym/equipment/` - لیست تجهیزات

### Membership:
- `GET /api/membership/members/` - لیست اعضا
- `POST /api/membership/members/` - ثبت عضو جدید
- `GET /api/membership/memberships/` - لیست عضویت‌ها

### Test Process:
- `GET /api/test/tests/` - لیست تست‌ها
- `POST /api/test/bookings/` - رزرو تست
- `GET /api/test/results/` - نتایج تست‌ها

## 🔧 تنظیمات

### متغیرهای محیطی:
- `SECRET_KEY` - کلید رمزنگاری Django
- `DEBUG` - حالت دیباگ
- `DATABASE_URL` - آدرس دیتابیس

### تنظیمات زبان:
- زبان پیش‌فرض: فارسی (fa-ir)
- منطقه زمانی: تهران (Asia/Tehran)

## 📊 ویژگی‌های کلیدی

### مدیریت مربیان:
- ثبت و مدیریت پروفایل مربیان
- تخصیص تست‌ها به مربیان
- مدیریت در دسترس بودن مربیان
- ثبت باشگاه‌های همکاری

### کیف پول‌ها:
- کیف پول فیات (ریال)
- کیف پول توکن‌ها
- تراکنش‌های واریز و برداشت
- تایید تراکنش‌ها توسط ادمین

### مدیریت باشگاه:
- ثبت باشگاه‌های ورزشی
- مدیریت تجهیزات
- برنامه‌ریزی کلاس‌ها
- مدیریت عضویت‌ها

### سیستم تست:
- تعریف تست‌های ورزشی
- رزرو تست‌ها
- ثبت نتایج
- گزارش‌گیری

## 🔒 امنیت

- احراز هویت برای تمام API ها
- مجوزهای مختلف برای ادمین و کاربران عادی
- محافظت از تراکنش‌های مالی
- لاگ کردن عملیات مهم

## 📝 لاگ‌ها

لاگ‌های سیستم در پوشه `logs/` ذخیره می‌شوند:
- `debug.log` - لاگ‌های دیباگ
- `error.log` - لاگ‌های خطا

## 🤝 مشارکت

برای مشارکت در پروژه:
1. Fork کنید
2. Branch جدید ایجاد کنید
3. تغییرات را commit کنید
4. Pull Request ارسال کنید

## 📄 لایسنس

این پروژه تحت لایسنس MIT منتشر شده است.

## 📞 پشتیبانی

برای سوالات و مشکلات:
- ایمیل: support@abo.com
- تلفن: 021-12345678 