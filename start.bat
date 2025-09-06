@echo off
chcp 65001 >nul
title نظام إدارة الأصول التقنية - IT Asset Management System

echo.
echo ================================================================
echo                   نظام إدارة الأصول التقنية
echo                IT Asset Management System
echo ================================================================
echo.
echo 🚀 بدء تشغيل النظام...
echo.

REM التحقق من وجود Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ خطأ: Python غير مثبت على النظام
    echo يرجى تثبيت Python من: https://python.org
    pause
    exit /b 1
)

REM التحقق من وجود المكتبات المطلوبة
echo 🔍 التحقق من المكتبات المطلوبة...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  المكتبات غير مثبتة، جاري التثبيت...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ فشل في تثبيت المكتبات
        pause
        exit /b 1
    )
)

echo ✅ جميع المكتبات مثبتة بنجاح
echo.
echo 🌐 تشغيل الخادم...
echo 📍 الرابط: http://localhost:5000
echo 👤 المستخدم: admin
echo 🔑 كلمة المرور: admin123
echo.
echo 🔧 للإيقاف: اضغط Ctrl+C
echo ================================================================
echo.

REM تشغيل النظام
python run.py

echo.
echo ================================================================
echo ⏹️  تم إيقاف النظام
echo ================================================================
pause