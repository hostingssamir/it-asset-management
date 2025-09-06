@echo off
chcp 65001 >nul
title نظام إدارة الأصول التقنية - الإصدار المحدث

echo.
echo ================================================================
echo                   نظام إدارة الأصول التقنية
echo                      الإصدار المحدث
echo                IT Asset Management System
echo ================================================================
echo.
echo 🚀 تشغيل النسخة المحدثة (حل مشكلة SQLAlchemy)...
echo.

REM التحقق من وجود Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ خطأ: Python غير مثبت على النظام
    echo يرجى تثبيت Python من: https://python.org
    pause
    exit /b 1
)

echo ✅ Python متوفر
echo.
echo 🌐 تشغيل النسخة الويب...
echo 📍 الرابط: http://localhost:5000
echo 👤 المستخدم: admin
echo 🔑 كلمة المرور: admin123
echo.
echo 🔧 للإيقاف: اضغط Ctrl+C
echo ================================================================
echo.

REM تشغيل النسخة المحدثة
python fixed_app.py

echo.
echo ================================================================
echo ⏹️  تم إيقاف النظام
echo ================================================================
pause