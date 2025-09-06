@echo off
chcp 65001 > nul
title نظام إدارة الأصول التقنية - IT Asset Management System

echo ================================================
echo نظام إدارة الأصول التقنية
echo IT Asset Management System
echo ================================================
echo.

echo جاري بدء تشغيل النظام...
echo Starting the system...
echo.

cd /d "E:\Python\IT_Asset_Management"

REM تحقق من وجود Python
python --version > nul 2>&1
if errorlevel 1 (
    echo خطأ: Python غير مثبت أو غير موجود في PATH
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM تحقق من وجود المتطلبات
if not exist requirements.txt (
    echo تحذير: ملف requirements.txt غير موجود
    echo Warning: requirements.txt not found
)

REM تشغيل النظام
echo بدء تشغيل الخادم...
echo Starting server...
echo.
echo الرابط: http://127.0.0.1:5000
echo Link: http://127.0.0.1:5000
echo.
echo معلومات تسجيل الدخول الافتراضية:
echo Default login credentials:
echo اسم المستخدم / Username: admin
echo كلمة المرور / Password: admin123
echo.
echo للإيقاف اضغط Ctrl+C
echo To stop press Ctrl+C
echo ================================================

python app.py

echo.
echo تم إيقاف النظام
echo System stopped
pause