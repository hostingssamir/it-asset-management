#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# سكريبت لإضافة أزرار العودة للرئيسية في جميع الصفحات

import re

def add_home_buttons_to_file(file_path):
    """إضافة أزرار العودة للرئيسية في جميع الصفحات"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # البحث عن الأنماط التي تحتاج لإضافة زر العودة
        patterns_to_update = [
            # نمط الأصول
            (
                r'(<div class="d-flex justify-content-between align-items-center mb-4">\s*<h2><i class="fas fa-laptop[^>]*></i>[^<]*الأصول[^<]*</h2>\s*)<button',
                r'\1<div>\n                <a href="/" class="btn btn-outline-success me-2">\n                    <i class="fas fa-home me-1"></i>الرئيسية\n                </a>\n                <button'
            ),
            # نمط الموظفين
            (
                r'(<div class="d-flex justify-content-between align-items-center mb-4">\s*<h2><i class="fas fa-users[^>]*></i>[^<]*الموظفين[^<]*</h2>\s*)<button',
                r'\1<div>\n                <a href="/" class="btn btn-outline-success me-2">\n                    <i class="fas fa-home me-1"></i>الرئيسية\n                </a>\n                <button'
            ),
            # نمط المشتريات
            (
                r'(<div class="d-flex justify-content-between align-items-center mb-4">\s*<h2><i class="fas fa-shopping[^>]*></i>[^<]*المشتريات[^<]*</h2>\s*)<button',
                r'\1<div>\n                <a href="/" class="btn btn-outline-success me-2">\n                    <i class="fas fa-home me-1"></i>الرئيسية\n                </a>\n                <button'
            ),
            # إضافة إغلاق div للأزرار
            (
                r'(<button[^>]*onclick="add[^"]*"[^>]*>[^<]*</button>)\s*</div>',
                r'\1\n            </div>\n        </div>'
            )
        ]
        
        # تطبيق التحديثات
        updated_content = content
        for pattern, replacement in patterns_to_update:
            updated_content = re.sub(pattern, replacement, updated_content, flags=re.MULTILINE | re.DOTALL)
        
        # حفظ الملف المحدث
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("✅ تم تحديث الملف بنجاح!")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في تحديث الملف: {e}")
        return False

def create_updated_templates():
    """إنشاء قوالب محدثة مع أزرار العودة"""
    
    # قالب الأصول المحدث
    assets_template = '''
    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="fas fa-laptop text-primary me-2"></i>إدارة الأصول</h2>
            <div>
                <a href="/" class="btn btn-outline-success me-2">
                    <i class="fas fa-home me-1"></i>الرئيسية
                </a>
                <button class="btn btn-primary" onclick="addAsset()">
                    <i class="fas fa-plus me-2"></i>إضافة أصل جديد
                </button>
            </div>
        </div>
    '''
    
    # قالب الموظفين المحدث
    employees_template = '''
    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="fas fa-users text-primary me-2"></i>إدارة الموظفين</h2>
            <div>
                <a href="/" class="btn btn-outline-success me-2">
                    <i class="fas fa-home me-1"></i>الرئيسية
                </a>
                <button class="btn btn-primary" onclick="addEmployee()">
                    <i class="fas fa-plus me-2"></i>إضافة موظف جديد
                </button>
            </div>
        </div>
    '''
    
    # قالب المشتريات المحدث
    purchases_template = '''
    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="fas fa-shopping-cart text-primary me-2"></i>إدارة المشتريات</h2>
            <div>
                <a href="/" class="btn btn-outline-success me-2">
                    <i class="fas fa-home me-1"></i>الرئيسية
                </a>
                <button class="btn btn-primary" onclick="addPurchase()">
                    <i class="fas fa-plus me-2"></i>إضافة مشترى جديد
                </button>
            </div>
        </div>
    '''
    
    print("✅ تم إنشاء القوالب المحدثة!")
    return {
        'assets': assets_template,
        'employees': employees_template,
        'purchases': purchases_template
    }

if __name__ == "__main__":
    print("🔄 بدء تحديث أزرار العودة للرئيسية...")
    
    # إنشاء القوالب المحدثة
    templates = create_updated_templates()
    
    # تحديث الملف الرئيسي
    file_path = "e:/Python/IT_Asset_Management/working_system.py"
    success = add_home_buttons_to_file(file_path)
    
    if success:
        print("🎉 تم تحديث جميع الصفحات بنجاح!")
        print("✅ أزرار العودة للرئيسية متاحة الآن في جميع الصفحات")
    else:
        print("❌ فشل في التحديث")