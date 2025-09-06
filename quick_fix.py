#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# إصلاح سريع لإضافة أزرار العودة للرئيسية

import os
import shutil

def fix_working_system():
    """إصلاح الملف الرئيسي وإضافة أزرار العودة"""
    
    # إنشاء نسخة احتياطية
    backup_file = "e:/Python/IT_Asset_Management/working_system_backup.py"
    original_file = "e:/Python/IT_Asset_Management/working_system.py"
    
    try:
        # إنشاء نسخة احتياطية
        shutil.copy2(original_file, backup_file)
        print("✅ تم إنشاء نسخة احتياطية")
        
        # قراءة الملف الأصلي
        with open(original_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # إضافة أزرار العودة للرئيسية في الأماكن المناسبة
        updates = [
            # تحديث قالب الأصول
            ('إدارة الأصول</h2>', 'إدارة الأصول</h2>\n            <div>\n                <a href="/" class="btn btn-outline-success me-2">\n                    <i class="fas fa-home me-1"></i>الرئيسية\n                </a>'),
            
            # تحديث قالب الموظفين
            ('إدارة الموظفين</h2>', 'إدارة الموظفين</h2>\n            <div>\n                <a href="/" class="btn btn-outline-success me-2">\n                    <i class="fas fa-home me-1"></i>الرئيسية\n                </a>'),
            
            # تحديث قالب المشتريات
            ('إدارة المشتريات</h2>', 'إدارة المشتريات</h2>\n            <div>\n                <a href="/" class="btn btn-outline-success me-2">\n                    <i class="fas fa-home me-1"></i>الرئيسية\n                </a>'),
        ]
        
        # تطبيق التحديثات
        updated_content = content
        for old_text, new_text in updates:
            if old_text in updated_content:
                updated_content = updated_content.replace(old_text, new_text)
                print(f"✅ تم تحديث: {old_text}")
        
        # حفظ الملف المحدث
        with open(original_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("🎉 تم تحديث الملف بنجاح!")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في التحديث: {e}")
        # استعادة النسخة الاحتياطية في حالة الخطأ
        if os.path.exists(backup_file):
            shutil.copy2(backup_file, original_file)
            print("🔄 تم استعادة النسخة الاحتياطية")
        return False

def create_simple_home_button_script():
    """إنشاء سكريبت بسيط لإضافة أزرار العودة"""
    
    script_content = '''
    // إضافة أزرار العودة للرئيسية في جميع الصفحات
    document.addEventListener('DOMContentLoaded', function() {
        // البحث عن العناوين الرئيسية
        const headers = document.querySelectorAll('h2');
        
        headers.forEach(header => {
            const parent = header.parentElement;
            if (parent && parent.classList.contains('d-flex')) {
                // التحقق من وجود زر العودة
                const homeButton = parent.querySelector('a[href="/"]');
                if (!homeButton) {
                    // إنشاء زر العودة
                    const homeBtn = document.createElement('a');
                    homeBtn.href = '/';
                    homeBtn.className = 'btn btn-outline-success me-2';
                    homeBtn.innerHTML = '<i class="fas fa-home me-1"></i>الرئيسية';
                    
                    // إضافة الزر
                    const buttonContainer = parent.querySelector('div') || parent;
                    buttonContainer.insertBefore(homeBtn, buttonContainer.firstChild);
                }
            }
        });
    });
    '''
    
    with open('e:/Python/IT_Asset_Management/home_buttons.js', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("✅ تم إنشاء سكريبت أزرار العودة")

if __name__ == "__main__":
    print("🔄 بدء الإصلاح السريع...")
    
    # تطبيق الإصلاح
    success = fix_working_system()
    
    # إنشاء سكريبت إضافي
    create_simple_home_button_script()
    
    if success:
        print("🎉 تم الإصلاح بنجاح!")
        print("✅ أزرار العودة للرئيسية متاحة الآن")
        print("🚀 يمكنك تشغيل النظام الآن")
    else:
        print("❌ فشل الإصلاح - تحقق من الملفات")