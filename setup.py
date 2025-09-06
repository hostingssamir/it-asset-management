#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إعداد نظام إدارة الأصول التقنية
IT Asset Management System Setup
"""

import os
import sys
import subprocess
import sqlite3
from datetime import datetime

def print_header():
    """طباعة رأس الإعداد"""
    print("=" * 70)
    print("🚀 إعداد نظام إدارة الأصول التقنية")
    print("   IT Asset Management System Setup")
    print("=" * 70)
    print()

def check_python_version():
    """التحقق من إصدار Python"""
    print("🔍 التحقق من إصدار Python...")
    
    if sys.version_info < (3, 8):
        print("❌ خطأ: يتطلب Python 3.8 أو أحدث")
        print(f"   الإصدار الحالي: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} - متوافق")
    return True

def install_requirements():
    """تثبيت المكتبات المطلوبة"""
    print("\n📦 تثبيت المكتبات المطلوبة...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ تم تثبيت جميع المكتبات بنجاح")
        return True
    except subprocess.CalledProcessError:
        print("❌ فشل في تثبيت المكتبات")
        return False

def create_directories():
    """إنشاء المجلدات المطلوبة"""
    print("\n📁 إنشاء المجلدات المطلوبة...")
    
    directories = [
        'static/uploads',
        'static/reports',
        'backups',
        'logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ تم إنشاء مجلد: {directory}")

def setup_database():
    """إعداد قاعدة البيانات"""
    print("\n🗄️  إعداد قاعدة البيانات...")
    
    try:
        # استيراد التطبيق وإنشاء الجداول
        from app import app, db
        
        with app.app_context():
            db.create_all()
            print("✅ تم إنشاء جداول قاعدة البيانات")
            
            # التحقق من وجود المستخدم الافتراضي
            from app import User
            if not User.query.first():
                print("ℹ️  سيتم إنشاء البيانات الافتراضية عند أول تشغيل")
            else:
                print("ℹ️  البيانات الافتراضية موجودة مسبقاً")
        
        return True
    except Exception as e:
        print(f"❌ خطأ في إعداد قاعدة البيانات: {e}")
        return False

def create_config_file():
    """إنشاء ملف الإعدادات"""
    print("\n⚙️  إنشاء ملف الإعدادات...")
    
    config_content = f"""# إعدادات نظام إدارة الأصول التقنية
# تم الإنشاء في: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# إعدادات الخادم
HOST = '0.0.0.0'
PORT = 5000
DEBUG = True

# إعدادات قاعدة البيانات
DATABASE_URL = 'sqlite:///it_assets.db'

# إعدادات الأمان
SECRET_KEY = 'change-this-in-production-{datetime.now().strftime("%Y%m%d%H%M%S")}'

# إعدادات رفع الملفات
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx']

# إعدادات النظام
ASSETS_PER_PAGE = 20
MAINTENANCE_REMINDER_DAYS = 30
WARRANTY_REMINDER_DAYS = 60
"""
    
    try:
        with open('local_config.py', 'w', encoding='utf-8') as f:
            f.write(config_content)
        print("✅ تم إنشاء ملف الإعدادات: local_config.py")
        return True
    except Exception as e:
        print(f"❌ خطأ في إنشاء ملف الإعدادات: {e}")
        return False

def test_installation():
    """اختبار التثبيت"""
    print("\n🧪 اختبار التثبيت...")
    
    try:
        # اختبار استيراد المكتبات الأساسية
        import flask
        import flask_sqlalchemy
        import flask_login
        import qrcode
        import reportlab
        
        print("✅ جميع المكتبات تعمل بشكل صحيح")
        
        # اختبار الاتصال بقاعدة البيانات
        if os.path.exists('it_assets.db'):
            conn = sqlite3.connect('it_assets.db')
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            conn.close()
            
            if tables:
                print(f"✅ قاعدة البيانات تحتوي على {len(tables)} جدول")
            else:
                print("⚠️  قاعدة البيانات فارغة")
        
        return True
    except ImportError as e:
        print(f"❌ خطأ في استيراد المكتبة: {e}")
        return False
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        return False

def print_completion_message():
    """طباعة رسالة الإكمال"""
    print("\n" + "=" * 70)
    print("🎉 تم إعداد النظام بنجاح!")
    print("=" * 70)
    print()
    print("📋 خطوات التشغيل:")
    print("   1. تشغيل النظام:")
    print("      • Windows: انقر مرتين على start.bat")
    print("      • أو: python run.py")
    print()
    print("   2. فتح المتصفح والذهاب إلى:")
    print("      http://localhost:5000")
    print()
    print("   3. تسجيل الدخول:")
    print("      • اسم المستخدم: admin")
    print("      • كلمة المرور: admin123")
    print()
    print("📚 للمساعدة:")
    print("   • دليل المستخدم: USER_GUIDE.md")
    print("   • ملف README: README.md")
    print()
    print("⚠️  تنبيهات مهمة:")
    print("   • غيّر كلمة المرور الافتراضية")
    print("   • أنشئ نسخ احتياطية دورية")
    print("   • احتفظ بملف local_config.py آمناً")
    print()
    print("=" * 70)

def main():
    """الدالة الرئيسية للإعداد"""
    print_header()
    
    # التحقق من إصدار Python
    if not check_python_version():
        return False
    
    # تثبيت المكتبات
    if not install_requirements():
        return False
    
    # إنشاء المجلدات
    create_directories()
    
    # إعداد قاعدة البيانات
    if not setup_database():
        return False
    
    # إنشاء ملف الإعدادات
    create_config_file()
    
    # اختبار التثبيت
    if not test_installation():
        print("⚠️  هناك مشاكل في التثبيت، لكن يمكن المتابعة")
    
    # رسالة الإكمال
    print_completion_message()
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        if success:
            input("\nاضغط Enter للخروج...")
        else:
            input("\nحدثت أخطاء في الإعداد. اضغط Enter للخروج...")
    except KeyboardInterrupt:
        print("\n\n⏹️  تم إلغاء الإعداد بواسطة المستخدم")
    except Exception as e:
        print(f"\n❌ خطأ غير متوقع: {e}")
        input("اضغط Enter للخروج...")