#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إنشاء حزمة السورس كود
Create Source Code Package
"""

import os
import shutil
import zipfile
from datetime import datetime

def create_source_package():
    """إنشاء حزمة السورس كود"""
    
    # اسم الحزمة
    package_name = f"IT_Asset_Management_SourceCode_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    package_dir = f"packages/{package_name}"
    
    # إنشاء مجلد الحزمة
    os.makedirs(package_dir, exist_ok=True)
    os.makedirs("packages", exist_ok=True)
    
    # قائمة الملفات المهمة
    important_files = [
        # الملفات الرئيسية
        'fixed_app.py',           # النسخة الويب المحدثة
        'desktop_app.py',         # نسخة ديسك توب
        'quick_start.py',         # النسخة السريعة
        'app.py',                 # النسخة الكاملة
        'admin.py',               # وحدة الإدارة
        'config.py',              # الإعدادات
        'utils.py',               # وظائف مساعدة
        'run.py',                 # ملف التشغيل
        'setup.py',               # إعداد النظام
        
        # ملفات التشغيل
        'start_fixed.bat',        # تشغيل النسخة المحدثة
        'start_desktop.bat',      # تشغيل نسخة ديسك توب
        'start.bat',              # تشغيل النسخة الكاملة
        
        # ملفات الإعداد
        'requirements.txt',       # المكتبات المطلوبة
        
        # ملفات التوثيق
        'README.md',              # دليل المشروع
        'USER_GUIDE.md',          # دليل المستخدم
        'PROJECT_SUMMARY.md',     # ملخص المشروع
        'SOLUTION_GUIDE.md',      # دليل حل المشاكل
        'SOURCE_CODE_COMPLETE.md' # دليل السورس كود
    ]
    
    # نسخ الملفات
    copied_files = []
    missing_files = []
    
    for file_name in important_files:
        if os.path.exists(file_name):
            try:
                shutil.copy2(file_name, package_dir)
                copied_files.append(file_name)
                print(f"✅ تم نسخ: {file_name}")
            except Exception as e:
                print(f"❌ خطأ في نسخ {file_name}: {e}")
                missing_files.append(file_name)
        else:
            print(f"⚠️  ملف غير موجود: {file_name}")
            missing_files.append(file_name)
    
    # إنشاء ملف معلومات الحزمة
    package_info = f"""# حزمة السورس كود - نظام إدارة الأصول التقنية
## Source Code Package - IT Asset Management System

**تاريخ الإنشاء:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**إصدار الحزمة:** 1.0

---

## 📁 محتويات الحزمة

### الملفات المنسوخة ({len(copied_files)}):
"""
    
    for file in copied_files:
        file_size = os.path.getsize(os.path.join(package_dir, file))
        package_info += f"- ✅ {file} ({file_size:,} بايت)\n"
    
    if missing_files:
        package_info += f"\n### الملفات المفقودة ({len(missing_files)}):\n"
        for file in missing_files:
            package_info += f"- ❌ {file}\n"
    
    package_info += f"""

---

## 🚀 طريقة الاستخدام

### 1. النسخة الويب المحدثة (مُوصى بها):
```bash
python fixed_app.py
```
ثم افتح: http://localhost:5000

### 2. نسخة ديسك توب:
```bash
python desktop_app.py
```

### 3. النسخة السريعة:
```bash
python quick_start.py
```

### 4. النسخة الكاملة:
```bash
python app.py
```

---

## 🔑 بيانات تسجيل الدخول

**جميع النسخ:**
- اسم المستخدم: `admin`
- كلمة المرور: `admin123`

---

## 📋 متطلبات التشغيل

### الحد الأدنى:
- Python 3.8+
- المكتبات الأساسية (مدمجة)

### للميزات المتقدمة:
```bash
pip install -r requirements.txt
```

---

## 📞 الدعم

للحصول على المساعدة، راجع:
- README.md - دليل المشروع
- USER_GUIDE.md - دليل المستخدم التفصيلي
- SOLUTION_GUIDE.md - حل المشاكل الشائعة

---

**تم إنشاء هذه الحزمة تلقائياً** 🤖
"""
    
    # حفظ ملف معلومات الحزمة
    with open(os.path.join(package_dir, 'PACKAGE_INFO.md'), 'w', encoding='utf-8') as f:
        f.write(package_info)
    
    # إنشاء ملف ZIP
    zip_path = f"packages/{package_name}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, package_dir)
                zipf.write(file_path, arcname)
    
    # حساب حجم الحزمة
    package_size = os.path.getsize(zip_path)
    
    print("\n" + "="*60)
    print("🎉 تم إنشاء حزمة السورس كود بنجاح!")
    print("="*60)
    print(f"📁 مجلد الحزمة: {package_dir}")
    print(f"📦 ملف ZIP: {zip_path}")
    print(f"📊 حجم الحزمة: {package_size:,} بايت ({package_size/1024:.1f} KB)")
    print(f"📋 عدد الملفات: {len(copied_files) + 1}")  # +1 لملف PACKAGE_INFO
    print("\n📋 ملخص:")
    print(f"  ✅ ملفات منسوخة: {len(copied_files)}")
    print(f"  ❌ ملفات مفقودة: {len(missing_files)}")
    print("\n🚀 الحزمة جاهزة للاستخدام!")
    print("="*60)
    
    return zip_path, package_dir

def main():
    """الدالة الرئيسية"""
    print("📦 إنشاء حزمة السورس كود...")
    print("🔄 جاري نسخ الملفات...")
    
    try:
        zip_path, package_dir = create_source_package()
        
        # عرض محتويات الحزمة
        print(f"\n📂 محتويات الحزمة في: {package_dir}")
        for file in os.listdir(package_dir):
            file_path = os.path.join(package_dir, file)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                print(f"  📄 {file} ({size:,} بايت)")
        
        print(f"\n💾 يمكنك الآن مشاركة الملف: {zip_path}")
        
    except Exception as e:
        print(f"❌ خطأ في إنشاء الحزمة: {e}")

if __name__ == '__main__':
    main()