#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ملف تشغيل نظام إدارة الأصول التقنية
IT Asset Management System Runner
"""

import os
import sys
from flask import Flask
from models import db, User, Category, Location
from config import config, DEFAULT_CATEGORIES, DEFAULT_LOCATIONS
from werkzeug.security import generate_password_hash

def create_app():
    """إنشاء وتكوين التطبيق"""
    app = Flask(__name__)
    
    # تحديد بيئة التشغيل
    config_name = os.environ.get('FLASK_CONFIG') or 'default'
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # تهيئة قاعدة البيانات
    db.init_app(app)
    
    return app

def init_database(app):
    """تهيئة قاعدة البيانات والبيانات الأساسية"""
    with app.app_context():
        # إنشاء الجداول
        db.create_all()
        
        # إنشاء مستخدم افتراضي إذا لم يكن موجوداً
        if not User.query.first():
            print("إنشاء مستخدم افتراضي...")
            admin = User(
                username='admin',
                email='admin@company.com',
                password_hash=generate_password_hash('admin123'),
                full_name='مدير النظام',
                role='admin'
            )
            db.session.add(admin)
            
            # إضافة فئات افتراضية
            print("إضافة الفئات الافتراضية...")
            for cat_data in DEFAULT_CATEGORIES:
                category = Category(**cat_data)
                db.session.add(category)
            
            # إضافة مواقع افتراضية
            print("إضافة المواقع الافتراضية...")
            for loc_data in DEFAULT_LOCATIONS:
                location = Location(**loc_data)
                db.session.add(location)
            
            db.session.commit()
            print("تم إنشاء البيانات الأساسية بنجاح!")
            print("معلومات تسجيل الدخول:")
            print("اسم المستخدم: admin")
            print("كلمة المرور: admin123")

def main():
    """الدالة الرئيسية لتشغيل النظام"""
    print("=" * 50)
    print("نظام إدارة الأصول التقنية")
    print("IT Asset Management System")
    print("=" * 50)
    
    # إنشاء التطبيق
    app = create_app()
    
    # تهيئة قاعدة البيانات
    init_database(app)
    
    # تسجيل المسارات
    from app import app as main_app
    
    print("\nبدء تشغيل النظام...")
    print("الرابط: http://127.0.0.1:5000")
    print("للإيقاف: اضغط Ctrl+C")
    print("-" * 50)
    
    # تشغيل التطبيق
    try:
        main_app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\nتم إيقاف النظام بنجاح!")
    except Exception as e:
        print(f"خطأ في تشغيل النظام: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()