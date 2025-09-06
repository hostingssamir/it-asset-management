#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار تثبيت المكتبات
"""

def test_imports():
    """اختبار استيراد المكتبات المطلوبة"""
    try:
        import flask
        print("✅ Flask: تم التثبيت بنجاح")
        print(f"   الإصدار: {flask.__version__}")
    except ImportError:
        print("❌ Flask: غير مثبت")
        return False
    
    try:
        import flask_sqlalchemy
        print("✅ Flask-SQLAlchemy: تم التثبيت بنجاح")
    except ImportError:
        print("❌ Flask-SQLAlchemy: غير مثبت")
        return False
    
    try:
        import flask_login
        print("✅ Flask-Login: تم التثبيت بنجاح")
    except ImportError:
        print("❌ Flask-Login: غير مثبت")
        return False
    
    try:
        import qrcode
        print("✅ QRCode: تم التثبيت بنجاح")
    except ImportError:
        print("❌ QRCode: غير مثبت")
        return False
    
    try:
        import reportlab
        print("✅ ReportLab: تم التثبيت بنجاح")
    except ImportError:
        print("❌ ReportLab: غير مثبت")
        return False
    
    try:
        from PIL import Image
        print("✅ Pillow: تم التثبيت بنجاح")
    except ImportError:
        print("❌ Pillow: غير مثبت")
        return False
    
    return True

if __name__ == '__main__':
    print("=" * 50)
    print("🔍 اختبار تثبيت المكتبات المطلوبة")
    print("=" * 50)
    
    if test_imports():
        print("\n✅ جميع المكتبات مثبتة بنجاح!")
        print("يمكنك الآن تشغيل النظام باستخدام: python run.py")
    else:
        print("\n❌ بعض المكتبات غير مثبتة")
        print("يرجى تثبيت المكتبات المطلوبة باستخدام:")
        print("pip install -r requirements.txt")
    
    print("=" * 50)