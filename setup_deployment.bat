@echo off
chcp 65001 >nul
title إعداد النشر السريع - نظام إدارة الأصول التقنية

echo.
echo ================================================================
echo                   إعداد النشر السريع
echo                نظام إدارة الأصول التقنية
echo                Quick Deployment Setup
echo ================================================================
echo.
echo 🚀 إعداد النظام للنشر على الاستضافة المجانية...
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

REM تشغيل إعداد النشر
echo 🔧 تشغيل إعداد النشر...
python quick_deploy.py

echo.
echo ================================================================
echo 📋 الخطوات التالية:
echo ================================================================
echo.
echo 1. أنشئ حساب GitHub إذا لم يكن لديك: https://github.com
echo 2. أنشئ مستودع جديد باسم: it-asset-management
echo 3. ارفع الكود باستخدام الأوامر المعروضة أعلاه
echo 4. اذهب إلى render.com وأنشئ حساب مجاني
echo 5. اتبع التعليمات في DEPLOYMENT_QUICK_GUIDE.md
echo.
echo 🌐 منصات الاستضافة المجانية المُوصى بها:
echo    • Render.com - الأسهل للمبتدئين
echo    • Railway.app - الأسرع في النشر
echo    • Vercel.com - للمطورين المتقدمين
echo.
echo 📖 دليل مفصل: DEPLOYMENT_QUICK_GUIDE.md
echo ================================================================
pause