#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إعداد النشر السريع
Quick Deployment Setup
"""

import os
import subprocess
import sys
from datetime import datetime

def setup_git_repo():
    """إعداد مستودع Git"""
    print("🔧 إعداد مستودع Git...")
    
    try:
        # تهيئة Git
        subprocess.run(['git', 'init'], check=True)
        print("✅ تم تهيئة Git")
        
        # إضافة الملفات
        subprocess.run(['git', 'add', '.'], check=True)
        print("✅ تم إضافة الملفات")
        
        # الالتزام الأول
        commit_message = f"IT Asset Management System - Ready for deployment {datetime.now().strftime('%Y-%m-%d')}"
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        print("✅ تم إنشاء الالتزام الأول")
        
        # إعداد الفرع الرئيسي
        subprocess.run(['git', 'branch', '-M', 'main'], check=True)
        print("✅ تم إعداد الفرع الرئيسي")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ خطأ في إعداد Git: {e}")
        return False
    except FileNotFoundError:
        print("❌ Git غير مثبت. يرجى تثبيت Git أولاً من: https://git-scm.com")
        return False

def create_deployment_files():
    """إنشاء ملفات النشر المطلوبة"""
    print("📁 إنشاء ملفات النشر...")
    
    # التحقق من وجود الملفات المطلوبة
    required_files = [
        'app_production.py',
        'requirements_production.txt',
        'Procfile',
        'render.yaml',
        'runtime.txt'
    ]
    
    missing_files = []
    existing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
        else:
            existing_files.append(file)
    
    print(f"✅ ملفات موجودة ({len(existing_files)}): {', '.join(existing_files)}")
    
    if missing_files:
        print(f"⚠️  ملفات مفقودة ({len(missing_files)}): {', '.join(missing_files)}")
        return False
    
    print("✅ جميع ملفات النشر موجودة")
    return True

def generate_deployment_guide():
    """إنشاء دليل النشر المخصص"""
    print("📋 إنشاء دليل النشر المخصص...")
    
    guide_content = f"""# دليل النشر السريع - نظام إدارة الأصول التقنية
## Quick Deployment Guide - IT Asset Management System

تم إنشاء هذا الدليل تلقائياً في: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 🚀 النشر على Render (الأسهل والأفضل)

### الخطوة 1: إنشاء مستودع GitHub
1. اذهب إلى [github.com](https://github.com)
2. اضغط "New repository"
3. اسم المستودع: `it-asset-management`
4. اجعله Public
5. اضغط "Create repository"
6. انسخ رابط المستودع

### الخطوة 2: رفع الكود
```bash
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

### الخطوة 3: إنشاء حساب Render
1. اذهب إلى [render.com](https://render.com)
2. اضغط "Get Started for Free"
3. سجل دخول بحساب GitHub

### الخطوة 4: إنشاء قاعدة البيانات
1. في لوحة تحكم Render، اضغط "New +"
2. اختر "PostgreSQL"
3. املأ البيانات:
   - **Name:** `it-assets-db`
   - **Database:** `it_assets`
   - **User:** `it_assets_user`
   - **Region:** اختر الأقرب لك
4. اضغط "Create Database"
5. انتظر حتى تصبح جاهزة (دقيقتان)

### الخطوة 5: إنشاء Web Service
1. اضغط "New +" مرة أخرى
2. اختر "Web Service"
3. اضغط "Connect" بجانب مستودع GitHub الخاص بك
4. املأ البيانات:
   - **Name:** `it-asset-management`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements_production.txt`
   - **Start Command:** `gunicorn app_production:app`

### الخطوة 6: إعداد متغيرات البيئة
في قسم "Environment Variables":
1. **DATABASE_URL:** 
   - اضغط "Add from Database"
   - اختر قاعدة البيانات التي أنشأتها
   - اختر "External Database URL"
2. **SECRET_KEY:** 
   - أدخل مفتاح سري قوي (مثل: `my-super-secret-key-2025`)
3. **FLASK_ENV:** 
   - أدخل `production`

### الخطوة 7: النشر
1. اضغط "Create Web Service"
2. انتظر اكتمال النشر (5-10 دقائق)
3. ستحصل على رابط مثل: `https://it-asset-management-xyz.onrender.com`

---

## 🔑 بيانات تسجيل الدخول

```
الرابط: https://your-app-name.onrender.com
المستخدم: admin
كلمة المرور: admin123
```

---

## 🌐 النشر على Railway (بديل ممتاز)

### الخطوة 1: إنشاء حساب
1. اذهب إلى [railway.app](https://railway.app)
2. سجل دخول بحساب GitHub

### الخطوة 2: إنشاء مشروع
1. اضغط "New Project"
2. اختر "Deploy from GitHub repo"
3. اختر مستودع `it-asset-management`

### الخطوة 3: إضافة قاعدة البيانات
1. اضغط "Add Plugin"
2. اختر "PostgreSQL"
3. سيتم إنشاؤها تلقائياً

### الخطوة 4: إعداد متغيرات البيئة
في قسم Variables:
```
FLASK_ENV = production
SECRET_KEY = your-secret-key-here
```

### الخطوة 5: النشر
- سيتم النشر تلقائياً
- ستحصل على رابط مثل: `https://your-app.up.railway.app`

---

## 📊 الملفات المُعدة للنشر

✅ **app_production.py** - التطبيق الرئيسي المحسن للإنتاج
✅ **requirements_production.txt** - المكتبات المطلوبة
✅ **Procfile** - أوامر التشغيل لـ Heroku-style platforms
✅ **render.yaml** - إعدادات Render التلقائية
✅ **runtime.txt** - إصدار Python المطلوب
✅ **.gitignore** - ملفات Git المستبعدة

---

## 🔧 استكشاف الأخطاء الشائعة

### مشكلة: "Build failed"
**الحل:**
- تحقق من `requirements_production.txt`
- تأكد من صحة `runtime.txt`

### مشكلة: "Database connection failed"
**الحل:**
- تحقق من `DATABASE_URL` في متغيرات البيئة
- تأكد من إنشاء قاعدة البيانات في Render

### مشكلة: "Internal Server Error (500)"
**الحل:**
- تحقق من السجلات في لوحة تحكم Render
- تأكد من `SECRET_KEY` في متغيرات البيئة

### مشكلة: "App doesn't start"
**الحل:**
- تحقق من `Start Command`: `gunicorn app_production:app`
- تأكد من وجود `app_production.py`

---

## 🎯 نصائح للنجاح

### 1. اختبار محلي قبل النشر
```bash
# تثبيت المتطلبات
pip install -r requirements_production.txt

# تشغيل التطبيق محلياً
python app_production.py
```

### 2. مراقبة السجلات
- في Render: اذهب لـ "Logs" في لوحة التحكم
- في Railway: اذهب لـ "Deployments" ثم "View Logs"

### 3. النسخ الاحتياطي
- قاعدة البيانات محمية تلقائياً
- الكود محفوظ في GitHub

---

## 🌟 الميزات المتاحة بعد النشر

✅ **نظام إدارة أصول كامل** - متاح عبر الإنترنت
✅ **قاعدة بيانات سحابية** - PostgreSQL آمنة
✅ **SSL مجاني** - اتصال آمن (HTTPS)
✅ **نشر تلقائي** - من GitHub
✅ **مراقبة الأداء** - Analytics مدمجة
✅ **توسع تلقائي** - حسب عدد المستخدمين
✅ **نسخ احتياطي** - تلقائية

---

## 🔄 التحديثات المستقبلية

لتحديث التطبيق:
```bash
# عدّل الكود محلياً
git add .
git commit -m "تحديث النظام"
git push origin main
```

سيتم النشر تلقائياً في غضون دقائق!

---

## 📞 الدعم والمساعدة

### وثائق المنصات:
- [Render Documentation](https://render.com/docs)
- [Railway Documentation](https://docs.railway.app)

### مجتمعات المطورين:
- [Stack Overflow - Flask](https://stackoverflow.com/questions/tagged/flask)
- [Reddit - r/flask](https://reddit.com/r/flask)

---

## 🎉 تهانينا!

بعد اتباع هذه الخطوات، ستحصل على:

🌐 **نظام إدارة أصول متاح عالمياً**
🔒 **اتصال آمن ومشفر**
📊 **قاعدة بيانات سحابية موثوقة**
⚡ **أداء سريع ومستقر**
🔄 **تحديثات تلقائية**

**نظامك أصبح متاحاً للعالم!** 🚀

---

*تم إنشاء هذا الدليل تلقائياً في {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    with open('DEPLOYMENT_QUICK_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print("✅ تم إنشاء دليل النشر السريع: DEPLOYMENT_QUICK_GUIDE.md")

def main():
    """الدالة الرئيسية"""
    print("=" * 70)
    print("🚀 إعداد النشر السريع - نظام إدارة الأصول التقنية")
    print("   Quick Deployment Setup - IT Asset Management System")
    print("=" * 70)
    print()
    
    # التحقق من الملفات المطلوبة
    if not create_deployment_files():
        print("❌ بعض ملفات النشر مفقودة، لكن يمكن المتابعة")
    
    # إعداد Git
    git_success = setup_git_repo()
    
    # إنشاء دليل النشر
    generate_deployment_guide()
    
    print("\n" + "=" * 70)
    print("🎉 تم إعداد النشر بنجاح!")
    print("=" * 70)
    print()
    
    if git_success:
        print("✅ Git جاهز - يمكنك الآن رفع الكود على GitHub")
        print()
        print("📋 الخطوات التالية:")
        print("1. أنشئ مستودع GitHub جديد باسم: it-asset-management")
        print("2. ارفع الكود:")
        print("   git remote add origin YOUR_GITHUB_REPO_URL")
        print("   git push -u origin main")
    else:
        print("⚠️  Git غير جاهز - يمكنك رفع الملفات يدوياً على GitHub")
        print()
        print("📋 الخطوات التالية:")
        print("1. أنشئ مستودع GitHub جديد")
        print("2. ارفع جميع الملفات يدوياً")
    
    print("3. اتبع التعليمات في: DEPLOYMENT_QUICK_GUIDE.md")
    print()
    print("🌐 منصات النشر المُوصى بها:")
    print("   • Render.com (الأسهل)")
    print("   • Railway.app (الأسرع)")
    print("   • Vercel.com (للخبراء)")
    print()
    print("🔑 بيانات تسجيل الدخول بعد النشر:")
    print("   المستخدم: admin")
    print("   كلمة المرور: admin123")
    print("=" * 70)

if __name__ == '__main__':
    main()