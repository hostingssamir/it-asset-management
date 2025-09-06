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
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ ملفات مفقودة: {', '.join(missing_files)}")
        return False
    
    print("✅ جميع ملفات النشر موجودة")
    return True

def test_production_app():
    """اختبار تطبيق الإنتاج محلياً"""
    print("🧪 اختبار التطبيق محلياً...")
    
    try:
        # تثبيت المتطلبات
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements_production.txt'], 
                      check=True, capture_output=True)
        print("✅ تم تثبيت المتطلبات")
        
        # اختبار استيراد التطبيق
        import app_production
        print("✅ تم استيراد التطبيق بنجاح")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ خطأ في تثبيت المتطلبات: {e}")
        return False
    except ImportError as e:
        print(f"❌ خطأ في استيراد التطبيق: {e}")
        return False

def generate_deployment_guide():
    """إنشاء دليل النشر المخصص"""
    print("📋 إنشاء دليل النشر المخصص...")
    
    guide_content = f"""# دليل النشر السريع
## Quick Deployment Guide

تم إنشاء هذا الدليل تلقائياً في: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🚀 خطوات النشر على Render

### 1. رفع على GitHub
```bash
# إذا لم تكن قد أنشأت مستودع GitHub بعد:
# 1. اذهب إلى github.com
# 2. أنشئ مستودع جديد باسم "it-asset-management"
# 3. انسخ رابط المستودع

git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

### 2. النشر على Render
1. اذهب إلى [render.com](https://render.com)
2. أنشئ حساب جديد
3. اضغط "New +" → "PostgreSQL"
4. أنشئ قاعدة بيانات:
   - Name: `it-assets-db`
   - Database: `it_assets`
   - User: `it_assets_user`
5. اضغط "New +" → "Web Service"
6. اربط مع GitHub repository
7. إعدادات التطبيق:
   - Name: `it-asset-management`
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements_production.txt`
   - Start Command: `gunicorn app_production:app`
8. أضف متغيرات البيئة:
   - `DATABASE_URL`: من قاعدة البيانات
   - `SECRET_KEY`: مفتاح سري قوي
   - `FLASK_ENV`: `production`

### 3. الوصول للتطبيق
- الرابط: `https://your-app-name.onrender.com`
- المستخدم: `admin`
- كلمة المرور: `admin123`

## 📊 الملفات المُعدة للنشر

✅ app_production.py - التطبيق الرئيسي
✅ requirements_production.txt - المكتبات المطلوبة
✅ Procfile - أوامر التشغيل
✅ render.yaml - إعدادات Render
✅ runtime.txt - إصدار Python
✅ .gitignore - ملفات Git المستبعدة

## 🔧 استكشاف الأخطاء

### مشكلة: فشل في البناء
- تحقق من requirements_production.txt
- تأكد من صحة إصدار Python في runtime.txt

### مشكلة: فشل في الاتصال بقاعدة البيانات
- تحقق من DATABASE_URL في متغيرات البيئة
- تأكد من إنشاء قاعدة البيانات في Render

### مشكلة: خطأ 500
- تحقق من السجلات في لوحة تحكم Render
- تأكد من SECRET_KEY في متغيرات البيئة

## 📞 الدعم
- وثائق Render: https://render.com/docs
- دعم GitHub: https://github.com/community

---
تم إنشاء هذا الدليل تلقائياً بواسطة deploy_setup.py
"""
    
    with open('DEPLOYMENT_QUICK_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print("✅ تم إنشاء دليل النشر السريع: DEPLOYMENT_QUICK_GUIDE.md")

def main():
    """الدالة الرئيسية"""
    print("=" * 60)
    print("🚀 إعداد النشر السريع - نظام إدارة الأصول التقنية")
    print("   Quick Deployment Setup - IT Asset Management")
    print("=" * 60)
    print()
    
    # التحقق من الملفات المطلوبة
    if not create_deployment_files():
        print("❌ فشل في التحقق من ملفات النشر")
        return
    
    # اختبار التطبيق
    if not test_production_app():
        print("⚠️  تحذير: فشل في اختبار التطبيق، لكن يمكن المتابعة")
    
    # إعداد Git
    if setup_git_repo():
        print("✅ تم إعداد Git بنجاح")
    else:
        print("⚠️  تحذير: فشل في إعداد Git")
    
    # إنشاء دليل النشر
    generate_deployment_guide()
    
    print("\n" + "=" * 60)
    print("🎉 تم إعداد النشر بنجاح!")
    print("=" * 60)
    print()
    print("📋 الخطوات التالية:")
    print("1. أنشئ مستودع GitHub جديد")
    print("2. ارفع الكود:")
    print("   git remote add origin YOUR_GITHUB_REPO_URL")
    print("   git push -u origin main")
    print("3. اذهب إلى render.com وأنشئ حساب جديد")
    print("4. اتبع التعليمات في DEPLOYMENT_QUICK_GUIDE.md")
    print()
    print("🌐 بعد النشر ستحصل على رابط مثل:")
    print("   https://your-app-name.onrender.com")
    print()
    print("🔑 بيانات تسجيل الدخول:")
    print("   المستخدم: admin")
    print("   كلمة المرور: admin123")
    print("=" * 60)

if __name__ == '__main__':
    main()