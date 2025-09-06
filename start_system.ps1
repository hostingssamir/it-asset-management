# نظام إدارة الأصول التقنية - IT Asset Management System
# PowerShell Startup Script

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "نظام إدارة الأصول التقنية" -ForegroundColor Yellow
Write-Host "IT Asset Management System" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "جاري بدء تشغيل النظام..." -ForegroundColor Green
Write-Host "Starting the system..." -ForegroundColor Green
Write-Host ""

# الانتقال إلى مجلد المشروع
Set-Location "E:\Python\IT_Asset_Management"

# تحقق من وجود Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python Version: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "خطأ: Python غير مثبت أو غير موجود في PATH" -ForegroundColor Red
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    Read-Host "اضغط Enter للخروج / Press Enter to exit"
    exit 1
}

# تحقق من وجود المتطلبات
if (-not (Test-Path "requirements.txt")) {
    Write-Host "تحذير: ملف requirements.txt غير موجود" -ForegroundColor Yellow
    Write-Host "Warning: requirements.txt not found" -ForegroundColor Yellow
}

# تشغيل النظام
Write-Host "بدء تشغيل الخادم..." -ForegroundColor Green
Write-Host "Starting server..." -ForegroundColor Green
Write-Host ""
Write-Host "الرابط: http://127.0.0.1:5000" -ForegroundColor Cyan
Write-Host "Link: http://127.0.0.1:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "معلومات تسجيل الدخول الافتراضية:" -ForegroundColor Yellow
Write-Host "Default login credentials:" -ForegroundColor Yellow
Write-Host "اسم المستخدم / Username: admin" -ForegroundColor White
Write-Host "كلمة المرور / Password: admin123" -ForegroundColor White
Write-Host ""
Write-Host "للإيقاف اضغط Ctrl+C" -ForegroundColor Red
Write-Host "To stop press Ctrl+C" -ForegroundColor Red
Write-Host "================================================" -ForegroundColor Cyan

try {
    python app.py
} catch {
    Write-Host ""
    Write-Host "حدث خطأ في تشغيل النظام" -ForegroundColor Red
    Write-Host "An error occurred while running the system" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
} finally {
    Write-Host ""
    Write-Host "تم إيقاف النظام" -ForegroundColor Yellow
    Write-Host "System stopped" -ForegroundColor Yellow
    Read-Host "اضغط Enter للخروج / Press Enter to exit"
}