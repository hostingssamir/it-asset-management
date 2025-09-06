#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ملف تشغيل نظام إدارة الأصول التقنية
IT Asset Management System Runner
"""

from app import app, db
from datetime import datetime

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 نظام إدارة الأصول التقنية")
    print("   IT Asset Management System")
    print("=" * 60)
    print(f"⏰ وقت البدء: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🌐 الخادم: http://localhost:5000")
    print("👤 المستخدم الافتراضي: admin")
    print("🔑 كلمة المرور الافتراضية: admin123")
    print("=" * 60)
    print("📋 الميزات المتاحة:")
    print("   ✅ إدارة الأصول التقنية")
    print("   ✅ تتبع الصيانة")
    print("   ✅ إنشاء QR Codes")
    print("   ✅ التقارير")
    print("   ✅ واجهة عربية متكاملة")
    print("=" * 60)
    print("🔧 للإيقاف: اضغط Ctrl+C")
    print("=" * 60)
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("⏹️  تم إيقاف النظام بنجاح")
        print("=" * 60)