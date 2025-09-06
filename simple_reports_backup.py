#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نسخة بسيطة مع التقارير - تعمل فوراً
Simple Version with Reports - Works Instantly
"""

import os
import sys
import sqlite3
import webbrowser
import threading
import time

def install_flask():
    """تثبيت Flask تلقائياً"""
    try:
        import flask
        return True
    except ImportError:
        print("📦 تثبيت Flask...")
        try:
            import subprocess
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'Flask'])
            print("✅ تم تثبيت Flask")
            return True
        except:
            print("❌ فشل في تثبيت Flask")
            return False

def create_simple_db():
    """إنشاء قاعدة بيانات بسيطة"""
    db_path = 'simple_reports.db'
    
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # جدول الأصول
    cursor.execute('''
        CREATE TABLE assets (
            id INTEGER PRIMARY KEY,
            tag TEXT,
            name TEXT,
            category TEXT,
            brand TEXT,
            cost REAL,
            status TEXT,
            assigned_to INTEGER,
            location TEXT,
            purchase_date TEXT,
            warranty_date TEXT,
            FOREIGN KEY (assigned_to) REFERENCES employees (id)
        )
    ''')
    
    # جدول الموظفين
    cursor.execute('''
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY,
            emp_id TEXT UNIQUE,
            name TEXT,
            national_id TEXT,
            phone TEXT,
            email TEXT,
            department TEXT,
            position TEXT,
            hire_date TEXT,
            status TEXT,
            manager_id INTEGER,
            office_location TEXT,
            FOREIGN KEY (manager_id) REFERENCES employees (id)
        )
    ''')
    
    # جدول تذاكر الدعم الفني
    cursor.execute('''
        CREATE TABLE support_tickets (
            id INTEGER PRIMARY KEY,
            ticket_number TEXT UNIQUE,
            employee_id INTEGER,
            asset_id INTEGER,
            title TEXT,
            description TEXT,
            category TEXT,
            priority TEXT,
            status TEXT,
            assigned_tech TEXT,
            created_date TEXT,
            updated_date TEXT,
            resolved_date TEXT,
            resolution TEXT,
            satisfaction_rating INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employees (id),
            FOREIGN KEY (asset_id) REFERENCES assets (id)
        )
    ''')
    
    # جدول تعليقات التذاكر
    cursor.execute('''
        CREATE TABLE ticket_comments (
            id INTEGER PRIMARY KEY,
            ticket_id INTEGER,
            author TEXT,
            comment TEXT,
            created_date TEXT,
            is_internal BOOLEAN,
            FOREIGN KEY (ticket_id) REFERENCES support_tickets (id)
        )
    ''')
    
    # جدول جلسات الدعم الفني عن بُعد
    cursor.execute('''
        CREATE TABLE remote_sessions (
            id INTEGER PRIMARY KEY,
            ticket_id INTEGER,
            employee_id INTEGER,
            session_code TEXT,
            status TEXT,
            started_date TEXT,
            ended_date TEXT,
            duration INTEGER,
            notes TEXT,
            FOREIGN KEY (ticket_id) REFERENCES support_tickets (id),
            FOREIGN KEY (employee_id) REFERENCES employees (id)
        )
    ''')
    
    # جدول الإدارات
    cursor.execute('''
        CREATE TABLE departments (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE,
            description TEXT,
            manager_id INTEGER,
            location TEXT,
            budget REAL,
            created_date TEXT,
            status TEXT,
            FOREIGN KEY (manager_id) REFERENCES employees (id)
        )
    ''')
    
    # جدول العهد (Asset Custody)
    cursor.execute('''
        CREATE TABLE asset_custody (
            id INTEGER PRIMARY KEY,
            asset_id INTEGER,
            employee_id INTEGER,
            custody_date TEXT,
            return_date TEXT,
            status TEXT,
            notes TEXT,
            witness_id INTEGER,
            custody_document TEXT,
            condition_received TEXT,
            condition_returned TEXT,
            FOREIGN KEY (asset_id) REFERENCES assets (id),
            FOREIGN KEY (employee_id) REFERENCES employees (id),
            FOREIGN KEY (witness_id) REFERENCES employees (id)
        )
    ''')
    
    # جدول المشتريات
    cursor.execute('''
        CREATE TABLE purchases (
            id INTEGER PRIMARY KEY,
            purchase_number TEXT UNIQUE,
            supplier_name TEXT,
            purchase_date TEXT,
            category TEXT,
            item_name TEXT,
            description TEXT,
            quantity INTEGER,
            unit_price REAL,
            total_amount REAL,
            currency TEXT,
            status TEXT,
            delivery_date TEXT,
            warranty_period INTEGER,
            warranty_end_date TEXT,
            purchase_type TEXT,
            department TEXT,
            requested_by INTEGER,
            approved_by INTEGER,
            notes TEXT,
            created_date TEXT,
            FOREIGN KEY (requested_by) REFERENCES employees (id),
            FOREIGN KEY (approved_by) REFERENCES employees (id)
        )
    ''')
    
    # جدول الفواتير
    cursor.execute('''
        CREATE TABLE invoices (
            id INTEGER PRIMARY KEY,
            invoice_number TEXT UNIQUE,
            purchase_id INTEGER,
            supplier_name TEXT,
            invoice_date TEXT,
            due_date TEXT,
            amount REAL,
            tax_amount REAL,
            total_amount REAL,
            currency TEXT,
            status TEXT,
            payment_date TEXT,
            payment_method TEXT,
            reference_number TEXT,
            notes TEXT,
            created_date TEXT,
            reminder_sent INTEGER DEFAULT 0,
            days_overdue INTEGER DEFAULT 0,
            FOREIGN KEY (purchase_id) REFERENCES purchases (id)
        )
    ''')
    
    # جدول التراخيص
    cursor.execute('''
        CREATE TABLE licenses (
            id INTEGER PRIMARY KEY,
            license_number TEXT UNIQUE,
            software_name TEXT,
            vendor TEXT,
            license_type TEXT,
            purchase_date TEXT,
            expiry_date TEXT,
            cost REAL,
            currency TEXT,
            seats_count INTEGER,
            used_seats INTEGER,
            status TEXT,
            renewal_date TEXT,
            auto_renewal INTEGER DEFAULT 0,
            department TEXT,
            assigned_to INTEGER,
            notes TEXT,
            created_date TEXT,
            reminder_sent INTEGER DEFAULT 0,
            days_to_expiry INTEGER DEFAULT 0,
            FOREIGN KEY (assigned_to) REFERENCES employees (id)
        )
    ''')
    
    # جدول الإشعارات
    cursor.execute('''
        CREATE TABLE notifications (
            id INTEGER PRIMARY KEY,
            type TEXT,
            title TEXT,
            message TEXT,
            related_id INTEGER,
            related_table TEXT,
            priority TEXT,
            status TEXT,
            created_date TEXT,
            read_date TEXT,
            due_date TEXT,
            assigned_to INTEGER,
            FOREIGN KEY (assigned_to) REFERENCES employees (id)
        )
    ''')
    
    # إدراج بيانات الموظفين التجريبية
    employees = [
        (1, 'EMP001', 'أحمد محمد علي', '1234567890', '0501234567', 'ahmed.ali@company.com', 'تقنية المعلومات', 'مدير تقنية المعلومات', '2020-01-15', 'نشط', None, 'الطابق الثالث - مكتب 301'),
        (2, 'EMP002', 'فاطمة أحمد السالم', '1234567891', '0501234568', 'fatima.salem@company.com', 'الموارد البشرية', 'مديرة الموارد البشرية', '2019-03-10', 'نشط', None, 'الطابق الثاني - مكتب 201'),
        (3, 'EMP003', 'محمد عبدالله الأحمد', '1234567892', '0501234569', 'mohammed.ahmed@company.com', 'تقنية المعلومات', 'مطور أنظمة', '2021-06-01', 'نشط', 1, 'الطابق الثالث - مكتب 305'),
        (4, 'EMP004', 'سارة خالد المطيري', '1234567893', '0501234570', 'sara.mutairi@company.com', 'المالية', 'محاسبة', '2020-09-15', 'نشط', None, 'الطابق الأول - مكتب 105'),
        (5, 'EMP005', 'عبدالرحمن سعد القحطاني', '1234567894', '0501234571', 'abdulrahman.qahtani@company.com', 'تقنية المعلومات', 'فني دعم تقني', '2022-02-01', 'نشط', 1, 'الطابق الثالث - مكتب 310'),
        (6, 'EMP006', 'نورا عبدالعزيز الشمري', '1234567895', '0501234572', 'nora.shamri@company.com', 'التسويق', 'أخصائية تسويق', '2021-11-20', 'نشط', None, 'الطابق الثاني - مكتب 210'),
        (7, 'EMP007', 'خالد محمد الدوسري', '1234567896', '0501234573', 'khalid.dosari@company.com', 'المبيعات', 'مندوب مبيعات', '2020-05-10', 'نشط', None, 'الطابق الأول - مكتب 110'),
        (8, 'EMP008', 'ريم أحمد العتيبي', '1234567897', '0501234574', 'reem.otaibi@company.com', 'تقنية المعلومات', 'مديرة أمن المعلومات', '2019-08-01', 'نشط', 1, 'الطابق الثالث - مكتب 302')
    ]
    
    for employee in employees:
        cursor.execute("INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", employee)
    
    # إدراج بيانات الأصول التجريبية (محدثة مع تخصيص للموظفين)
    assets = [
        (1, 'PC001', 'جهاز كمبيوتر Dell OptiPlex 7090', 'أجهزة الكمبيوتر', 'Dell', 2500, 'نشط', 1, 'الطابق الثالث - مكتب 301', '2023-01-15', '2026-01-15'),
        (2, 'LP001', 'جهاز لابتوب HP EliteBook 850', 'أجهزة الكمبيوتر', 'HP', 3200, 'نشط', 3, 'الطابق الثالث - مكتب 305', '2023-02-10', '2026-02-10'),
        (3, 'PR001', 'طابعة Canon imageRUNNER', 'الطابعات', 'Canon', 800, 'نشط', None, 'الطابق الثاني - منطقة مشتركة', '2022-12-01', '2025-12-01'),
        (4, 'SW001', 'سويتش Cisco Catalyst 2960', 'الشبكة', 'Cisco', 1500, 'نشط', None, 'غرفة الخوادم', '2022-11-15', '2027-11-15'),
        (5, 'SV001', 'خادم Dell PowerEdge R740', 'الخوادم', 'Dell', 8500, 'نشط', None, 'غرفة الخوادم', '2022-10-01', '2027-10-01'),
        (6, 'PH001', 'هاتف IP Cisco 8841', 'الهواتف', 'Cisco', 350, 'نشط', 2, 'الطابق الثاني - مكتب 201', '2023-03-01', '2026-03-01'),
        (7, 'PC002', 'جهاز HP ProDesk 400', 'أجهزة الكمبيوتر', 'HP', 2200, 'صيانة', 4, 'الطابق الأول - مكتب 105', '2022-08-15', '2025-08-15'),
        (8, 'PR002', 'طابعة HP LaserJet Pro', 'الطابعات', 'HP', 1200, 'نشط', None, 'الطابق الأول - منطقة مشتركة', '2023-01-20', '2026-01-20'),
        (9, 'RT001', 'راوتر Cisco ISR 4331', 'الشبكة', 'Cisco', 2200, 'نشط', None, 'غرفة الخوادم', '2022-09-10', '2027-09-10'),
        (10, 'TB001', 'تابلت Samsung Galaxy Tab S8', 'أجهزة الكمبيوتر', 'Samsung', 1800, 'نشط', 6, 'الطابق الثاني - مكتب 210', '2023-04-01', '2026-04-01')
    ]
    
    for asset in assets:
        cursor.execute("INSERT INTO assets VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", asset)
    
    # إدراج تذاكر الدعم الفني التجريبية
    tickets = [
        (1, 'TKT-2025-001', 4, 7, 'جهاز الكمبيوتر لا يعمل', 'الجهاز لا يقلع عند الضغط على زر التشغيل، لا توجد أضواء أو أصوات', 'أجهزة', 'عالية', 'مفتوح', 'عبدالرحمن القحطاني', '2025-01-10 09:00:00', '2025-01-10 09:00:00', None, None, None),
        (2, 'TKT-2025-002', 3, 2, 'بطء في الأداء', 'اللابتوب أصبح بطيئاً جداً في الأسبوع الماضي، خاصة عند فتح البرامج', 'أجهزة', 'متوسطة', 'قيد المعالجة', 'عبدالرحمن القحطاني', '2025-01-09 14:30:00', '2025-01-10 08:15:00', None, None, None),
        (3, 'TKT-2025-003', 6, None, 'مشكلة في الإيميل', 'لا أستطيع إرسال الإيميلات، أحصل على رسالة خطأ', 'برمجيات', 'متوسطة', 'مفتوح', 'أحمد علي', '2025-01-10 11:15:00', '2025-01-10 11:15:00', None, None, None),
        (4, 'TKT-2025-004', 7, None, 'طلب تثبيت برنامج', 'أحتاج تثبيت برنامج Adobe Photoshop للعمل على التصاميم', 'برمجيات', 'منخفضة', 'مكتمل', 'محمد الأحمد', '2025-01-08 10:00:00', '2025-01-09 16:30:00', '2025-01-09 16:30:00', 'تم تثبيت البرنامج وتفعيله بنجاح', 5),
        (5, 'TKT-2025-005', 2, 6, 'الهاتف لا يرن', 'هاتف المكتب لا يرن عند استقبال المكالمات', 'شبكة', 'عالية', 'قيد المعالجة', 'أحمد علي', '2025-01-10 13:45:00', '2025-01-10 13:45:00', None, None, None)
    ]
    
    for ticket in tickets:
        cursor.execute("INSERT INTO support_tickets VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", ticket)
    
    # إدراج تعليقات التذاكر
    comments = [
        (1, 2, 'عبدالرحمن القحطاني', 'تم فحص الجهاز، يبدو أن المشكلة في الذاكرة العشوائية. سأقوم بتنظيف الجهاز وإعادة تثبيت الذاكرة.', '2025-01-10 08:15:00', False),
        (2, 2, 'محمد الأحمد', 'شكراً لك، أنتظر التحديث', '2025-01-10 09:30:00', False),
        (3, 4, 'محمد الأحمد', 'تم تثبيت البرنامج بنجاح. يرجى التأكد من عمله بشكل صحيح.', '2025-01-09 16:30:00', False),
        (4, 4, 'خالد الدوسري', 'ممتاز، البرنامج يعمل بشكل مثالي. شكراً لكم', '2025-01-09 17:00:00', False),
        (5, 5, 'أحمد علي', 'سأقوم بفحص إعدادات الهاتف والشبكة', '2025-01-10 14:00:00', True)
    ]
    
    for comment in comments:
        cursor.execute("INSERT INTO ticket_comments VALUES (?, ?, ?, ?, ?, ?)", comment)
    
    # إدراج بيانات الإدارات التجريبية
    departments = [
        (1, 'تقنية المعلومات', 'إدارة الأنظمة والشبكات والدعم الفني', 1, 'الطابق الثالث', 500000, '2020-01-01', 'نشط'),
        (2, 'الموارد البشرية', 'إدارة شؤون الموظفين والتوظيف', 2, 'الطابق الثاني', 200000, '2020-01-01', 'نشط'),
        (3, 'المالية', 'إدارة الحسابات والميزانيات', None, 'الطابق الأول', 300000, '2020-01-01', 'نشط'),
        (4, 'التسويق', 'إدارة التسويق والعلاقات العامة', None, 'الطابق الثاني', 250000, '2020-01-01', 'نشط'),
        (5, 'المبيعات', 'إدارة المبيعات وخدمة العملاء', None, 'الطابق الأول', 400000, '2020-01-01', 'نشط'),
        (6, 'العمليات', 'إدارة العمليات والإنتاج', None, 'الطابق الأرضي', 600000, '2020-01-01', 'نشط')
    ]
    
    for department in departments:
        cursor.execute("INSERT INTO departments VALUES (?, ?, ?, ?, ?, ?, ?, ?)", department)
    
    # إدراج بيانات العهد التجريبية
    custody_records = [
        (1, 1, 1, '2023-01-15', None, 'نشط', 'جهاز كمبيوتر مكتبي للاستخدام اليومي', 8, 'CUST-2023-001', 'ممتاز', None),
        (2, 2, 3, '2023-02-10', None, 'نشط', 'لابتوب للعمل والتطوير', 1, 'CUST-2023-002', 'جيد جداً', None),
        (3, 6, 2, '2023-03-01', None, 'نشط', 'هاتف IP للمكتب', 1, 'CUST-2023-003', 'ممتاز', None),
        (4, 7, 4, '2022-08-15', None, 'صيانة', 'جهاز كمبيوتر - يحتاج صيانة', 2, 'CUST-2022-004', 'جيد', None),
        (5, 10, 6, '2023-04-01', None, 'نشط', 'تابلت للعروض التقديمية', 2, 'CUST-2023-005', 'ممتاز', None)
    ]
    
    for custody in custody_records:
        cursor.execute("INSERT INTO asset_custody VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", custody)
    
    # إدراج بيانات المشتريات التجريبية
    purchases = [
        (1, 'PUR-2024-001', 'شركة الحاسوب المتقدم', '2024-01-15', 'أجهزة', 'أجهزة كمبيوتر مكتبية', 'أجهزة Dell OptiPlex 7090', 5, 2500.00, 12500.00, 'SAR', 'مكتمل', '2024-01-25', 36, '2027-01-25', 'هاردوير', 'تقنية المعلومات', 1, 1, 'أجهزة للموظفين الجدد', '2024-01-15'),
        (2, 'PUR-2024-002', 'مايكروسوفت السعودية', '2024-02-01', 'برمجيات', 'تراخيص Office 365', 'تراخيص Office 365 Business Premium', 50, 120.00, 6000.00, 'SAR', 'مكتمل', '2024-02-01', 12, '2025-02-01', 'ترخيص', 'تقنية المعلومات', 1, 1, 'تراخيص سنوية للموظفين', '2024-02-01'),
        (3, 'PUR-2024-003', 'شركة الشبكات الذكية', '2024-03-10', 'شبكة', 'معدات شبكة', 'Switch Cisco 48 Port + Access Points', 1, 8500.00, 8500.00, 'SAR', 'قيد التوريد', '2024-03-20', 60, '2029-03-10', 'هاردوير', 'تقنية المعلومات', 5, 1, 'تحديث البنية التحتية للشبكة', '2024-03-10'),
        (4, 'PUR-2024-004', 'Adobe الشرق الأوسط', '2024-04-05', 'برمجيات', 'Adobe Creative Suite', 'تراخيص Adobe Creative Cloud للتصميم', 10, 300.00, 3000.00, 'SAR', 'مكتمل', '2024-04-05', 12, '2025-04-05', 'ترخيص', 'التسويق', 6, 2, 'برامج التصميم لفريق التسويق', '2024-04-05'),
        (5, 'PUR-2024-005', 'شركة الأمان الرقمي', '2024-05-15', 'أمان', 'برنامج مكافحة الفيروسات', 'Kaspersky Endpoint Security', 100, 45.00, 4500.00, 'SAR', 'مكتمل', '2024-05-15', 12, '2025-05-15', 'ترخيص', 'تقنية المعلومات', 8, 1, 'حماية شاملة لجميع الأجهزة', '2024-05-15')
    ]
    
    for purchase in purchases:
        cursor.execute("INSERT INTO purchases VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", purchase)
    
    # إدراج بيانات الفواتير التجريبية
    invoices = [
        (1, 'INV-2024-001', 1, 'شركة الحاسوب المتقدم', '2024-01-25', '2024-02-25', 12500.00, 1875.00, 14375.00, 'SAR', 'مدفوع', '2024-02-20', 'تحويل بنكي', 'TRF-2024-001', 'تم السداد في الموعد', '2024-01-25', 0, 0),
        (2, 'INV-2024-002', 2, 'مايكروسوفت السعودية', '2024-02-01', '2024-03-01', 6000.00, 900.00, 6900.00, 'SAR', 'مدفوع', '2024-02-28', 'بطاقة ائتمان', 'CC-2024-002', 'سداد تلقائي', '2024-02-01', 0, 0),
        (3, 'INV-2024-003', 3, 'شركة الشبكات الذكية', '2024-03-20', '2024-04-20', 8500.00, 1275.00, 9775.00, 'SAR', 'معلق', None, None, None, 'في انتظار السداد', '2024-03-20', 1, 5),
        (4, 'INV-2024-004', 4, 'Adobe الشرق الأوسط', '2024-04-05', '2024-05-05', 3000.00, 450.00, 3450.00, 'SAR', 'مدفوع', '2024-04-30', 'تحويل بنكي', 'TRF-2024-004', 'تم السداد', '2024-04-05', 0, 0),
        (5, 'INV-2024-005', 5, 'شركة الأمان الرقمي', '2024-05-15', '2024-06-15', 4500.00, 675.00, 5175.00, 'SAR', 'متأخر', None, None, None, 'متأخر 10 أيام', '2024-05-15', 2, 10)
    ]
    
    for invoice in invoices:
        cursor.execute("INSERT INTO invoices VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", invoice)
    
    # إدراج بيانات التراخيص التجريبية
    licenses = [
        (1, 'LIC-OFF365-2024', 'Microsoft Office 365', 'Microsoft', 'اشتراك سنوي', '2024-02-01', '2025-02-01', 6000.00, 'SAR', 50, 48, 'نشط', '2025-02-01', 1, 'تقنية المعلومات', 1, 'تجديد تلقائي مفعل', '2024-02-01', 0, 45),
        (2, 'LIC-ADOBE-2024', 'Adobe Creative Cloud', 'Adobe', 'اشتراك سنوي', '2024-04-05', '2025-04-05', 3000.00, 'SAR', 10, 8, 'نشط', '2025-04-05', 0, 'التسويق', 6, 'للفريق الإبداعي', '2024-04-05', 0, 120),
        (3, 'LIC-KASPER-2024', 'Kaspersky Endpoint Security', 'Kaspersky', 'ترخيص سنوي', '2024-05-15', '2025-05-15', 4500.00, 'SAR', 100, 95, 'نشط', '2025-05-15', 1, 'تقنية المعلومات', 8, 'حماية شاملة', '2024-05-15', 1, 135),
        (4, 'LIC-WIN-SRV-2024', 'Windows Server 2022', 'Microsoft', 'ترخيص دائم', '2024-01-10', '2027-01-10', 15000.00, 'SAR', 2, 2, 'نشط', None, 0, 'تقنية المعلومات', 1, 'خوادم الشركة', '2024-01-10', 0, 1095),
        (5, 'LIC-AUTOCAD-2024', 'AutoCAD 2024', 'Autodesk', 'اشتراك سنوي', '2024-03-01', '2025-03-01', 2400.00, 'SAR', 3, 3, 'نشط', '2025-03-01', 0, 'الهندسة', None, 'للمهندسين', '2024-03-01', 0, 90)
    ]
    
    for license_data in licenses:
        cursor.execute("INSERT INTO licenses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", license_data)
    
    # إدراج بيانات الإشعارات التجريبية
    notifications = [
        (1, 'فاتورة', 'فاتورة متأخرة', 'فاتورة شركة الأمان الرقمي متأخرة 10 أيام', 5, 'invoices', 'عالية', 'غير مقروء', '2024-06-25', None, '2024-06-15', 1),
        (2, 'ترخيص', 'انتهاء ترخيص قريب', 'ترخيص Office 365 سينتهي خلال 45 يوم', 1, 'licenses', 'متوسطة', 'غير مقروء', '2024-12-15', None, '2025-02-01', 1),
        (3, 'فاتورة', 'فاتورة معلقة', 'فاتورة شركة الشبكات الذكية في انتظار السداد', 3, 'invoices', 'متوسطة', 'غير مقروء', '2024-04-25', None, '2024-04-20', 1),
        (4, 'ترخيص', 'تجديد ترخيص', 'ترخيص Adobe Creative Cloud يحتاج تجديد خلال 120 يوم', 2, 'licenses', 'منخفضة', 'مقروء', '2024-12-05', '2024-12-06', '2025-04-05', 6),
        (5, 'صيانة', 'صيانة دورية', 'حان موعد الصيانة الدورية للخوادم', None, 'assets', 'متوسطة', 'غير مقروء', '2025-01-01', None, '2025-01-15', 5)
    ]
    
    for notification in notifications:
        cursor.execute("INSERT INTO notifications VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", notification)
    
    conn.commit()
    conn.close()
    print("✅ تم إنشاء قاعدة البيانات مع 10 أصول")

def create_simple_app():
    """إنشاء تطبيق Flask بسيط"""
    from flask import Flask, render_template_string, session, redirect, url_for, request
    
    app = Flask(__name__)
    app.secret_key = 'simple-reports-2025'
    
    def get_db():
        conn = sqlite3.connect('simple_reports.db')
        conn.row_factory = sqlite3.Row
        return conn
    
    @app.route('/')
    def index():
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        
        conn = get_db()
        total_assets = conn.execute('SELECT COUNT(*) as count FROM assets').fetchone()['count']
        active_assets = conn.execute('SELECT COUNT(*) as count FROM assets WHERE status = "نشط"').fetchone()['count']
        total_cost = conn.execute('SELECT SUM(cost) as total FROM assets').fetchone()['total'] or 0
        
        recent_assets = conn.execute('SELECT * FROM assets ORDER BY id DESC LIMIT 5').fetchall()
        conn.close()
        
        return render_template_string(DASHBOARD_TEMPLATE, 
            total_assets=total_assets,
            active_assets=active_assets,
            total_cost=total_cost,
            recent_assets=recent_assets)
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            if request.form['username'] == 'admin' and request.form['password'] == 'admin123':
                session['logged_in'] = True
                return redirect(url_for('index'))
            else:
                return render_template_string(LOGIN_TEMPLATE, error='بيانات خاطئة')
        return render_template_string(LOGIN_TEMPLATE)
    
    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('login'))
    
    @app.route('/assets')
    def assets():
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        
        conn = get_db()
        assets = conn.execute('SELECT * FROM assets ORDER BY id DESC').fetchall()
        conn.close()
        
        return render_template_string(ASSETS_TEMPLATE, assets=assets)
    
    @app.route('/reports')
    def reports():
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        
        conn = get_db()
        
        # إحصائيات عامة
        total_assets = conn.execute('SELECT COUNT(*) as count FROM assets').fetchone()['count']
        active_assets = conn.execute('SELECT COUNT(*) as count FROM assets WHERE status = "نشط"').fetchone()['count']
        maintenance_assets = conn.execute('SELECT COUNT(*) as count FROM assets WHERE status = "صيانة"').fetchone()['count']
        total_cost = conn.execute('SELECT SUM(cost) as total FROM assets').fetchone()['total'] or 0
        
        # إحصائيات الفئات
        category_stats = conn.execute('''
            SELECT category, COUNT(*) as count, SUM(cost) as total_value
            FROM assets 
            GROUP BY category
            ORDER BY count DESC
        ''').fetchall()
        
        # أشهر العلامات التجارية
        brand_stats = conn.execute('''
            SELECT brand, COUNT(*) as count, SUM(cost) as total_value
            FROM assets 
            GROUP BY brand
            ORDER BY count DESC
            LIMIT 5
        ''').fetchall()
        
        # الأصول الأعلى قيمة
        expensive_assets = conn.execute('''
            SELECT * FROM assets 
            ORDER BY cost DESC
            LIMIT 5
        ''').fetchall()
        
        conn.close()
        
        return render_template_string(REPORTS_TEMPLATE,
            total_assets=total_assets,
            active_assets=active_assets,
            maintenance_assets=maintenance_assets,
            total_cost=total_cost,
            category_stats=category_stats,
            brand_stats=brand_stats,
            expensive_assets=expensive_assets)
    
    @app.route('/add_asset', methods=['GET', 'POST'])
    def add_asset():
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        
        if request.method == 'POST':
            # الحصول على البيانات من النموذج
            tag = request.form['tag']
            name = request.form['name']
            category = request.form['category']
            brand = request.form['brand']
            cost = float(request.form['cost']) if request.form['cost'] else 0
            status = request.form['status']
            
            # التحقق من عدم تكرار رقم الأصل
            conn = get_db()
            existing = conn.execute('SELECT id FROM assets WHERE tag = ?', (tag,)).fetchone()
            
            if existing:
                conn.close()
                return render_template_string(ADD_ASSET_TEMPLATE, 
                    error='رقم الأصل موجود مسبقاً، يرجى استخدام رقم آخر',
                    form_data=request.form)
            
            # إضافة الأصل الجديد
            try:
                conn.execute('''
                    INSERT INTO assets (tag, name, category, brand, cost, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (tag, name, category, brand, cost, status))
                conn.commit()
                conn.close()
                
                return render_template_string(ADD_ASSET_TEMPLATE, 
                    success=f'تم إضافة الأصل {tag} بنجاح!')
            except Exception as e:
                conn.close()
                return render_template_string(ADD_ASSET_TEMPLATE, 
                    error=f'حدث خطأ أثناء إضافة الأصل: {str(e)}',
                    form_data=request.form)
        
        return render_template_string(ADD_ASSET_TEMPLATE)
    
    @app.route('/delete_asset/<int:asset_id>')
    def delete_asset(asset_id):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        
        conn = get_db()
        conn.execute('DELETE FROM assets WHERE id = ?', (asset_id,))
        conn.commit()
        conn.close()
        
        return redirect(url_for('assets'))
    
    @app.route('/employees')
    def employees():
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        
        conn = get_db()
        employees = conn.execute('''
            SELECT e.*, m.name as manager_name 
            FROM employees e 
            LEFT JOIN employees m ON e.manager_id = m.id 
            ORDER BY e.department, e.name
        ''').fetchall()
        conn.close()
        
        return render_template_string(EMPLOYEES_TEMPLATE, employees=employees)
    
    @app.route('/add_employee', methods=['GET', 'POST'])
    def add_employee():
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        
        if request.method == 'POST':
            # الحصول على البيانات من النموذج
            emp_id = request.form['emp_id']
            name = request.form['name']
            national_id = request.form['national_id']
            phone = request.form['phone']
            email = request.form['email']
            department = request.form['department']
            position = request.form['position']
            hire_date = request.form['hire_date']
            status = request.form['status']
            manager_id = request.form['manager_id'] if request.form['manager_id'] else None
            office_location = request.form['office_location']
            
            # التحقق من عدم تكرار رقم الموظف
            conn = get_db()
            existing = conn.execute('SELECT id FROM employees WHERE emp_id = ?', (emp_id,)).fetchone()
            
            if existing:
                managers = conn.execute('SELECT id, name FROM employees WHERE position LIKE "%مدير%" ORDER BY name').fetchall()
                conn.close()
                return render_template_string(ADD_EMPLOYEE_TEMPLATE, 
                    error='رقم الموظف موجود مسبقاً، يرجى استخدام رقم آخر',
                    form_data=request.form, managers=managers)
            
            # إضافة الموظف الجديد
            try:
                conn.execute('''
                    INSERT INTO employees (emp_id, name, national_id, phone, email, department, position, hire_date, status, manager_id, office_location)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (emp_id, name, national_id, phone, email, department, position, hire_date, status, manager_id, office_location))
                conn.commit()
                conn.close()
                
                return render_template_string(ADD_EMPLOYEE_TEMPLATE, 
                    success=f'تم إضافة الموظف {name} بنجاح!')
            except Exception as e:
                conn.close()
                managers = conn.execute('SELECT id, name FROM employees WHERE position LIKE "%مدير%" ORDER BY name').fetchall()
                return render_template_string(ADD_EMPLOYEE_TEMPLATE, 
                    error=f'حدث خطأ أثناء إضافة الموظف: {str(e)}',
                    form_data=request.form, managers=managers)
        
        # عرض النموذج
        conn = get_db()
        managers = conn.execute('SELECT id, name FROM employees WHERE position LIKE "%مدير%" ORDER BY name').fetchall()
        conn.close()
        
        return render_template_string(ADD_EMPLOYEE_TEMPLATE, managers=managers)
    
    @app.route('/support')
    def support():
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        
        conn = get_db()
        
        # إحصائيات التذاكر
        total_tickets = conn.execute('SELECT COUNT(*) as count FROM support_tickets').fetchone()['count']
        open_tickets = conn.execute('SELECT COUNT(*) as count FROM support_tickets WHERE status IN ("مفتوح", "قيد المعالجة")').fetchone()['count']
        closed_tickets = conn.execute('SELECT COUNT(*) as count FROM support_tickets WHERE status = "مكتمل"').fetchone()['count']
        high_priority = conn.execute('SELECT COUNT(*) as count FROM support_tickets WHERE priority = "عالية" AND status != "مكتمل"').fetchone()['count']
        
        # التذاكر الحديثة
        recent_tickets = conn.execute('''
            SELECT st.*, e.name as employee_name, a.tag as asset_tag
            FROM support_tickets st
            LEFT JOIN employees e ON st.employee_id = e.id
            LEFT JOIN assets a ON st.asset_id = a.id
            ORDER BY st.created_date DESC
            LIMIT 10
        ''').fetchall()
        
        conn.close()
        
        return render_template_string(SUPPORT_TEMPLATE,
            total_tickets=total_tickets,
            open_tickets=open_tickets,
            closed_tickets=closed_tickets,
            high_priority=high_priority,
            recent_tickets=recent_tickets)
    
    @app.route('/create_ticket', methods=['GET', 'POST'])
    def create_ticket():
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        
        if request.method == 'POST':
            # إنشاء رقم تذكرة جديد
            import datetime
            ticket_number = f"TKT-{datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S')}"
            
            employee_id = request.form['employee_id']
            asset_id = request.form['asset_id'] if request.form['asset_id'] else None
            title = request.form['title']
            description = request.form['description']
            category = request.form['category']
            priority = request.form['priority']
            
            conn = get_db()
            try:
                conn.execute('''
                    INSERT INTO support_tickets (ticket_number, employee_id, asset_id, title, description, category, priority, status, created_date, updated_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (ticket_number, employee_id, asset_id, title, description, category, priority, 'مفتوح', 
                      datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                      datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                conn.commit()
                conn.close()
                
                return render_template_string(CREATE_TICKET_TEMPLATE, 
                    success=f'تم إنشاء التذكرة {ticket_number} بنجاح!')
            except Exception as e:
                conn.close()
                return render_template_string(CREATE_TICKET_TEMPLATE, 
                    error=f'حدث خطأ أثناء إنشاء التذكرة: {str(e)}')
        
        # عرض النموذج
        conn = get_db()
        employees = conn.execute('SELECT id, name, emp_id FROM employees WHERE status = "نشط" ORDER BY name').fetchall()
        assets = conn.execute('SELECT id, tag, name FROM assets ORDER BY tag').fetchall()
        conn.close()
        
        return render_template_string(CREATE_TICKET_TEMPLATE, employees=employees, assets=assets)
    
    @app.route('/remote_support')
    def remote_support():
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        
        return render_template_string(REMOTE_SUPPORT_TEMPLATE)
    
    @app.route('/departments')
    def departments():
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        
        conn = get_db()
        departments = conn.execute('''
            SELECT d.*, e.name as manager_name,
                   (SELECT COUNT(*) FROM employees WHERE department = d.name) as employee_count
            FROM departments d 
            LEFT JOIN employees e ON d.manager_id = e.id 
            ORDER BY d.name
        ''').fetchall()
        conn.close()
        
        return render_template_string(DEPARTMENTS_TEMPLATE, departments=departments)
    
    @app.route('/add_department', methods=['GET', 'POST'])
    def add_department():
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            manager_id = request.form['manager_id'] if request.form['manager_id'] else None
            location = request.form['location']
            budget = float(request.form['budget']) if request.form['budget'] else 0
            status = request.form['status']
            
            conn = get_db()
            existing = conn.execute('SELECT id FROM departments WHERE name = ?', (name,)).fetchone()
            
            if existing:
                managers = conn.execute('SELECT id, name FROM employees WHERE position LIKE "%مدير%" ORDER BY name').fetchall()
                conn.close()
                return render_template_string(ADD_DEPARTMENT_TEMPLATE, 
                    error='اسم الإدارة موجود مسبقاً',
                    form_data=request.form, managers=managers)
            
            try:
                import datetime
                conn.execute('''
                    INSERT INTO departments (name, description, manager_id, location, budget, created_date, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (name, description, manager_id, location, budget, datetime.datetime.now().strftime('%Y-%m-%d'), status))
                conn.commit()
                conn.close()
                
                return render_template_string(ADD_DEPARTMENT_TEMPLATE, 
                    success=f'تم إضافة الإدارة {name} بنجاح!')
            except Exception as e:
                conn.close()
                managers = conn.execute('SELECT id, name FROM employees WHERE position LIKE "%مدير%" ORDER BY name').fetchall()
                return render_template_string(ADD_DEPARTMENT_TEMPLATE, 
                    error=f'حدث خطأ: {str(e)}',
                    form_data=request.form, managers=managers)
        
        conn = get_db()
        managers = conn.execute('SELECT id, name FROM employees WHERE position LIKE "%مدير%" ORDER BY name').fetchall()
        conn.close()
        
        return render_template_string(ADD_DEPARTMENT_TEMPLATE, managers=managers)
    
    @app.route('/edit_asset/<int:asset_id>', methods=['GET', 'POST'])
    def edit_asset(asset_id):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        
        conn = get_db()
        
        if request.method == 'POST':
            tag = request.form['tag']
            name = request.form['name']
            category = request.form['category']
            brand = request.form['brand']
            cost = float(request.form['cost']) if request.form['cost'] else 0
            status = request.form['status']
            assigned_to = request.form['assigned_to'] if request.form['assigned_to'] else None
            location = request.form['location']
            purchase_date = request.form['purchase_date']
            warranty_date = request.form['warranty_date']
            
            try:
                conn.execute('''
                    UPDATE assets 
                    SET tag=?, name=?, category=?, brand=?, cost=?, status=?, assigned_to=?, location=?, purchase_date=?, warranty_date=?
                    WHERE id=?
                ''', (tag, name, category, brand, cost, status, assigned_to, location, purchase_date, warranty_date, asset_id))
                conn.commit()
                conn.close()
                
                return redirect(url_for('assets'))
            except Exception as e:
                asset = conn.execute('SELECT * FROM assets WHERE id = ?', (asset_id,)).fetchone()
                employees = conn.execute('SELECT id, name, emp_id FROM employees WHERE status = "نشط" ORDER BY name').fetchall()
                conn.close()
                return render_template_string(EDIT_ASSET_TEMPLATE, 
                    error=f'حدث خطأ: {str(e)}',
                    asset=asset, employees=employees)
        
        asset = conn.execute('SELECT * FROM assets WHERE id = ?', (asset_id,)).fetchone()
        employees = conn.execute('SELECT id, name, emp_id FROM employees WHERE status = "نشط" ORDER BY name').fetchall()
        conn.close()
        
        if not asset:
            return redirect(url_for('assets'))
        
        return render_template_string(EDIT_ASSET_TEMPLATE, asset=asset, employees=employees)
    
    @app.route('/edit_employee/<int:employee_id>', methods=['GET', 'POST'])
    def edit_employee(employee_id):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        
        conn = get_db()
        
        if request.method == 'POST':
            emp_id = request.form['emp_id']
            name = request.form['name']
            national_id = request.form['national_id']
            phone = request.form['phone']
            email = request.form['email']
            department = request.form['department']
            position = request.form['position']
            hire_date = request.form['hire_date']
            status = request.form['status']
            manager_id = request.form['manager_id'] if request.form['manager_id'] else None
            office_location = request.form['office_location']
            
            try:
                conn.execute('''
                    UPDATE employees 
                    SET emp_id=?, name=?, national_id=?, phone=?, email=?, department=?, position=?, hire_date=?, status=?, manager_id=?, office_location=?
                    WHERE id=?
                ''', (emp_id, name, national_id, phone, email, department, position, hire_date, status, manager_id, office_location, employee_id))
                conn.commit()
                conn.close()
                
                return redirect(url_for('employees'))
            except Exception as e:
                employee = conn.execute('SELECT * FROM employees WHERE id = ?', (employee_id,)).fetchone()
                managers = conn.execute('SELECT id, name FROM employees WHERE position LIKE "%مدير%" AND id != ? ORDER BY name', (employee_id,)).fetchall()
                departments = conn.execute('SELECT DISTINCT name FROM departments ORDER BY name').fetchall()
                conn.close()
                return render_template_string(EDIT_EMPLOYEE_TEMPLATE, 
                    error=f'حدث خطأ: {str(e)}',
                    employee=employee, managers=managers, departments=departments)
        
        employee = conn.execute('SELECT * FROM employees WHERE id = ?', (employee_id,)).fetchone()
        managers = conn.execute('SELECT id, name FROM employees WHERE position LIKE "%مدير%" AND id != ? ORDER BY name', (employee_id,)).fetchall()
        departments = conn.execute('SELECT DISTINCT name FROM departments ORDER BY name').fetchall()
        conn.close()
        
        if not employee:
            return redirect(url_for('employees'))
        
        return render_template_string(EDIT_EMPLOYEE_TEMPLATE, employee=employee, managers=managers, departments=departments)
    
    @app.route('/delete_employee/<int:employee_id>')
    def delete_employee(employee_id):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        
        conn = get_db()
        # التحقق من وجود أصول مخصصة للموظف
        assets = conn.execute('SELECT COUNT(*) as count FROM assets WHERE assigned_to = ?', (employee_id,)).fetchone()['count']
        
        if assets > 0:
            conn.close()
            return redirect(url_for('employees') + '?error=لا يمكن حذف الموظف لوجود أصول مخصصة له')
        
        conn.execute('DELETE FROM employees WHERE id = ?', (employee_id,))
        conn.commit()
        conn.close()
        
        return redirect(url_for('employees'))
    
    @app.route('/custody')
    def custody():
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        
        conn = get_db()
        custody_records = conn.execute('''
            SELECT ac.*, a.tag, a.name as asset_name, e.name as employee_name, e.emp_id,
                   w.name as witness_name
            FROM asset_custody ac
            LEFT JOIN assets a ON ac.asset_id = a.id
            LEFT JOIN employees e ON ac.employee_id = e.id
            LEFT JOIN employees w ON ac.witness_id = w.id
            ORDER BY ac.custody_date DESC
        ''').fetchall()
        conn.close()
        
        return render_template_string(CUSTODY_TEMPLATE, custody_records=custody_records)
    
    @app.route('/create_custody', methods=['GET', 'POST'])
    def create_custody():
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        
        if request.method == 'POST':
            asset_id = request.form['asset_id']
            employee_id = request.form['employee_id']
            custody_date = request.form['custody_date']
            notes = request.form['notes']
            witness_id = request.form['witness_id'] if request.form['witness_id'] else None
            condition_received = request.form['condition_received']
            
            # إنشاء رقم وثيقة العهدة
            import datetime
            custody_document = f"CUST-{datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S')}"
            
            conn = get_db()
            try:
                # إنشاء سجل العهدة
                conn.execute('''
                    INSERT INTO asset_custody (asset_id, employee_id, custody_date, status, notes, witness_id, custody_document, condition_received)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (asset_id, employee_id, custody_date, 'نشط', notes, witness_id, custody_document, condition_received))
                
                # تحديث الأصل ليصبح مخصص للموظف
                conn.execute('UPDATE assets SET assigned_to = ? WHERE id = ?', (employee_id, asset_id))
                
                conn.commit()
                conn.close()
                
                return render_template_string(CREATE_CUSTODY_TEMPLATE, 
                    success=f'تم إنشاء العهدة {custody_document} بنجاح!')
            except Exception as e:
                conn.close()
                return render_template_string(CREATE_CUSTODY_TEMPLATE, 
                    error=f'حدث خطأ: {str(e)}')
        
        conn = get_db()
        # الأصول غير المخصصة
        assets = conn.execute('SELECT id, tag, name FROM assets WHERE assigned_to IS NULL ORDER BY tag').fetchall()
        employees = conn.execute('SELECT id, name, emp_id FROM employees WHERE status = "نشط" ORDER BY name').fetchall()
        witnesses = conn.execute('SELECT id, name FROM employees WHERE status = "نشط" ORDER BY name').fetchall()
        conn.close()
        
        return render_template_string(CREATE_CUSTODY_TEMPLATE, assets=assets, employees=employees, witnesses=witnesses)
    
    @app.route('/purchases')
    def purchases():
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        
        conn = get_db()
        purchases = conn.execute('''
            SELECT p.*, e1.name as requested_by_name, e2.name as approved_by_name
            FROM purchases p
            LEFT JOIN employees e1 ON p.requested_by = e1.id
            LEFT JOIN employees e2 ON p.approved_by = e2.id
            ORDER BY p.purchase_date DESC
        ''').fetchall()
        
        # إحصائيات المشتريات
        total_purchases = conn.execute('SELECT COUNT(*) as count FROM purchases').fetchone()['count']
        total_amount = conn.execute('SELECT SUM(total_amount) as total FROM purchases').fetchone()['total'] or 0
        pending_purchases = conn.execute('SELECT COUNT(*) as count FROM purchases WHERE status = "قيد التوريد"').fetchone()['count']
        
        conn.close()
        
        return render_template_string(PURCHASES_TEMPLATE, 
            purchases=purchases, 
            total_purchases=total_purchases,
            total_amount=total_amount,
            pending_purchases=pending_purchases)
    
    @app.route('/add_purchase', methods=['GET', 'POST'])
    def add_purchase():
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        
        if request.method == 'POST':
            import datetime
            purchase_number = f"PUR-{datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S')}"
            
            supplier_name = request.form['supplier_name']
            purchase_date = request.form['purchase_date']
            category = request.form['category']
            item_name = request.form['item_name']
            description = request.form['description']
            quantity = int(request.form['quantity'])
            unit_price = float(request.form['unit_price'])
            total_amount = quantity * unit_price
            currency = request.form['currency']
            delivery_date = request.form['delivery_date']
            warranty_period = int(request.form['warranty_period']) if request.form['warranty_period'] else 0
            purchase_type = request.form['purchase_type']
            department = request.form['department']
            requested_by = request.form['requested_by']
            notes = request.form['notes']
            
            # حساب تاريخ انتهاء الضمان
            if warranty_period > 0:
                from datetime import datetime, timedelta
                delivery_dt = datetime.strptime(delivery_date, '%Y-%m-%d')
                warranty_end_date = (delivery_dt + timedelta(days=warranty_period*30)).strftime('%Y-%m-%d')
            else:
                warranty_end_date = None
            
            conn = get_db()
            try:
                conn.execute('''
                    INSERT INTO purchases (purchase_number, supplier_name, purchase_date, category, item_name, description, 
                                         quantity, unit_price, total_amount, currency, status, delivery_date, warranty_period, 
                                         warranty_end_date, purchase_type, department, requested_by, notes, created_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (purchase_number, supplier_name, purchase_date, category, item_name, description, quantity, unit_price, 
                      total_amount, currency, 'قيد التوريد', delivery_date, warranty_period, warranty_end_date, 
                      purchase_type, department, requested_by, notes, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                conn.commit()
                conn.close()
                
                return render_template_string(ADD_PURCHASE_TEMPLATE, 
                    success=f'تم إضافة المشترى {purchase_number} بنجاح!')
            except Exception as e:
                conn.close()
                return render_template_string(ADD_PURCHASE_TEMPLATE, 
                    error=f'حدث خطأ: {str(e)}')
        
        conn = get_db()
        employees = conn.execute('SELECT id, name, emp_id FROM employees WHERE status = "نشط" ORDER BY name').fetchall()
        departments = conn.execute('SELECT DISTINCT name FROM departments ORDER BY name').fetchall()
        conn.close()
        
        return render_template_string(ADD_PURCHASE_TEMPLATE, employees=employees, departments=departments)
    
    @app.route('/invoices')
    def invoices():
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        
        conn = get_db()
        invoices = conn.execute('''
            SELECT i.*, p.item_name, p.purchase_number
            FROM invoices i
            LEFT JOIN purchases p ON i.purchase_id = p.id
            ORDER BY i.invoice_date DESC
        ''').fetchall()
        
        # إحصائيات الفواتير
        total_invoices = conn.execute('SELECT COUNT(*) as count FROM invoices').fetchone()['count']
        total_amount = conn.execute('SELECT SUM(total_amount) as total FROM invoices').fetchone()['total'] or 0
        pending_amount = conn.execute('SELECT SUM(total_amount) as total FROM invoices WHERE status IN ("معلق", "متأخر")').fetchone()['total'] or 0
        overdue_count = conn.execute('SELECT COUNT(*) as count FROM invoices WHERE status = "متأخر"').fetchone()['count']
        
        conn.close()
        
        return render_template_string(INVOICES_TEMPLATE, 
            invoices=invoices,
            total_invoices=total_invoices,
            total_amount=total_amount,
            pending_amount=pending_amount,
            overdue_count=overdue_count)
    
    @app.route('/licenses')
    def licenses():
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        
        conn = get_db()
        licenses = conn.execute('''
            SELECT l.*, e.name as assigned_to_name
            FROM licenses l
            LEFT JOIN employees e ON l.assigned_to = e.id
            ORDER BY l.expiry_date ASC
        ''').fetchall()
        
        # إحصائيات التراخيص
        total_licenses = conn.execute('SELECT COUNT(*) as count FROM licenses').fetchone()['count']
        active_licenses = conn.execute('SELECT COUNT(*) as count FROM licenses WHERE status = "نشط"').fetchone()['count']
        expiring_soon = conn.execute('SELECT COUNT(*) as count FROM licenses WHERE days_to_expiry <= 90 AND status = "نشط"').fetchone()['count']
        total_cost = conn.execute('SELECT SUM(cost) as total FROM licenses WHERE status = "نشط"').fetchone()['total'] or 0
        
        conn.close()
        
        return render_template_string(LICENSES_TEMPLATE,
            licenses=licenses,
            total_licenses=total_licenses,
            active_licenses=active_licenses,
            expiring_soon=expiring_soon,
            total_cost=total_cost)
    
    @app.route('/notifications')
    def notifications():
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        
        conn = get_db()
        notifications = conn.execute('''
            SELECT n.*, e.name as assigned_to_name
            FROM notifications n
            LEFT JOIN employees e ON n.assigned_to = e.id
            ORDER BY n.created_date DESC
        ''').fetchall()
        
        # إحصائيات الإشعارات
        total_notifications = conn.execute('SELECT COUNT(*) as count FROM notifications').fetchone()['count']
        unread_notifications = conn.execute('SELECT COUNT(*) as count FROM notifications WHERE status = "غير مقروء"').fetchone()['count']
        high_priority = conn.execute('SELECT COUNT(*) as count FROM notifications WHERE priority = "عالية" AND status = "غير مقروء"').fetchone()['count']
        
        conn.close()
        
        return render_template_string(NOTIFICATIONS_TEMPLATE,
            notifications=notifications,
            total_notifications=total_notifications,
            unread_notifications=unread_notifications,
            high_priority=high_priority)
    
    return app

# قوالب HTML
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>تسجيل الدخول - نظام إدارة الأصول</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Cairo', sans-serif;
            background: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #f5576c);
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            position: relative;
        }
        
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        /* خلفية متحركة */
        .background-animation {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            z-index: 1;
        }
        
        .floating-shapes {
            position: absolute;
            width: 100%;
            height: 100%;
        }
        
        .shape {
            position: absolute;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 50%;
            animation: float 20s infinite linear;
        }
        
        .shape:nth-child(1) {
            width: 80px;
            height: 80px;
            left: 10%;
            animation-delay: 0s;
        }
        
        .shape:nth-child(2) {
            width: 120px;
            height: 120px;
            left: 20%;
            animation-delay: 2s;
        }
        
        .shape:nth-child(3) {
            width: 60px;
            height: 60px;
            left: 70%;
            animation-delay: 4s;
        }
        
        .shape:nth-child(4) {
            width: 100px;
            height: 100px;
            left: 80%;
            animation-delay: 6s;
        }
        
        .shape:nth-child(5) {
            width: 90px;
            height: 90px;
            left: 50%;
            animation-delay: 8s;
        }
        
        @keyframes float {
            0% {
                transform: translateY(100vh) rotate(0deg);
                opacity: 0;
            }
            10% {
                opacity: 1;
            }
            90% {
                opacity: 1;
            }
            100% {
                transform: translateY(-100px) rotate(360deg);
                opacity: 0;
            }
        }
        
        /* بطاقة تسجيل الدخول */
        .login-container {
            position: relative;
            z-index: 10;
            width: 100%;
            max-width: 450px;
            margin: 0 auto;
        }
        
        .login-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 25px;
            box-shadow: 
                0 25px 50px rgba(0, 0, 0, 0.2),
                0 0 0 1px rgba(255, 255, 255, 0.1);
            padding: 3rem;
            transform: translateY(0);
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .login-card:hover {
            transform: translateY(-5px);
            box-shadow: 
                0 35px 70px rgba(0, 0, 0, 0.25),
                0 0 0 1px rgba(255, 255, 255, 0.2);
        }
        
        /* العنوان والشعار */
        .login-header {
            text-align: center;
            margin-bottom: 2.5rem;
        }
        
        .logo-container {
            width: 80px;
            height: 80px;
            margin: 0 auto 1.5rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        .logo-container i {
            font-size: 2.5rem;
            color: white;
        }
        
        .login-title {
            font-size: 1.8rem;
            font-weight: 700;
            color: #2d3748;
            margin-bottom: 0.5rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .login-subtitle {
            color: #718096;
            font-size: 1rem;
            font-weight: 400;
        }
        
        /* حقول الإدخال */
        .form-group {
            margin-bottom: 1.5rem;
            position: relative;
        }
        
        .form-label {
            font-weight: 600;
            color: #4a5568;
            margin-bottom: 0.5rem;
            font-size: 0.9rem;
        }
        
        .form-control {
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            padding: 0.75rem 1rem;
            font-size: 1rem;
            transition: all 0.3s ease;
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(10px);
        }
        
        .form-control:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            background: rgba(255, 255, 255, 0.95);
            transform: translateY(-1px);
        }
        
        .input-icon {
            position: absolute;
            left: 1rem;
            top: 50%;
            transform: translateY(-50%);
            color: #a0aec0;
            font-size: 1.1rem;
        }
        
        .form-control.with-icon {
            padding-left: 3rem;
        }
        
        /* زر تسجيل الدخول */
        .login-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 12px;
            padding: 0.875rem 2rem;
            font-size: 1.1rem;
            font-weight: 600;
            color: white;
            width: 100%;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .login-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
        }
        
        .login-btn:active {
            transform: translateY(0);
        }
        
        .login-btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: left 0.5s;
        }
        
        .login-btn:hover::before {
            left: 100%;
        }
        
        /* معلومات التجربة */
        .demo-info {
            background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
            border-radius: 15px;
            padding: 1.5rem;
            margin-top: 2rem;
            border: 1px solid rgba(226, 232, 240, 0.8);
            text-align: center;
        }
        
        .demo-title {
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 0.75rem;
            font-size: 0.95rem;
        }
        
        .demo-credentials {
            display: flex;
            justify-content: space-between;
            margin-bottom: 1rem;
        }
        
        .credential-item {
            background: white;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-size: 0.85rem;
            color: #4a5568;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        
        .demo-features {
            display: flex;
            justify-content: space-around;
            margin-top: 1rem;
        }
        
        .feature-badge {
            background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 500;
        }
        
        .feature-badge.info {
            background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
        }
        
        /* رسائل الخطأ */
        .alert {
            border-radius: 12px;
            border: none;
            padding: 1rem;
            margin-bottom: 1.5rem;
            animation: slideIn 0.3s ease;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .alert-danger {
            background: linear-gradient(135deg, #fed7d7 0%, #feb2b2 100%);
            color: #c53030;
            border-left: 4px solid #e53e3e;
        }
        
        /* تأثيرات متجاوبة */
        @media (max-width: 768px) {
            .login-card {
                margin: 1rem;
                padding: 2rem;
            }
            
            .login-title {
                font-size: 1.5rem;
            }
            
            .demo-credentials {
                flex-direction: column;
                gap: 0.5rem;
            }
        }
        
        /* تأثير التحميل */
        .loading {
            position: relative;
        }
        
        .loading::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 20px;
            height: 20px;
            margin: -10px 0 0 -10px;
            border: 2px solid transparent;
            border-top: 2px solid white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <!-- خلفية متحركة -->
    <div class="background-animation">
        <div class="floating-shapes">
            <div class="shape"></div>
            <div class="shape"></div>
            <div class="shape"></div>
            <div class="shape"></div>
            <div class="shape"></div>
        </div>
    </div>

    <!-- بطاقة تسجيل الدخول -->
    <div class="login-container">
        <div class="login-card">
            <div class="login-header">
                <div class="logo-container">
                    <i class="fas fa-chart-line"></i>
                </div>
                <h1 class="login-title">نظام إدارة الأصول</h1>
                <p class="login-subtitle">مع التقارير المتقدمة والرسوم البيانية</p>
            </div>
            
            {% if error %}
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    {{ error }}
                </div>
            {% endif %}
            
            <form method="POST" id="loginForm">
                <div class="form-group">
                    <label class="form-label">
                        <i class="fas fa-user me-2"></i>
                        اسم المستخدم
                    </label>
                    <input type="text" class="form-control" name="username" value="admin" required>
                </div>
                
                <div class="form-group">
                    <label class="form-label">
                        <i class="fas fa-lock me-2"></i>
                        كلمة المرور
                    </label>
                    <input type="password" class="form-control" name="password" value="admin123" required>
                </div>
                
                <button type="submit" class="login-btn" id="loginButton">
                    <i class="fas fa-sign-in-alt me-2"></i>
                    تسجيل الدخول
                </button>
            </form>
            
            <div class="demo-info">
                <div class="demo-title">
                    <i class="fas fa-info-circle me-2"></i>
                    بيانات التجربة
                </div>
                
                <div class="demo-credentials">
                    <div class="credential-item">
                        <strong>المستخدم:</strong> admin
                    </div>
                    <div class="credential-item">
                        <strong>كلمة المرور:</strong> admin123
                    </div>
                </div>
                
                <div class="demo-features">
                    <span class="feature-badge">
                        <i class="fas fa-database me-1"></i>
                        10 أصول تجريبية
                    </span>
                    <span class="feature-badge info">
                        <i class="fas fa-chart-bar me-1"></i>
                        تقارير شاملة
                    </span>
                </div>
            </div>
        </div>
    </div>

    <script>
        // تأثير التحميل عند الإرسال
        document.getElementById('loginForm').addEventListener('submit', function() {
            const button = document.getElementById('loginButton');
            button.classList.add('loading');
            button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>جاري تسجيل الدخول...';
            button.disabled = true;
        });
        
        // تأثير التركيز على الحقول
        document.querySelectorAll('.form-control').forEach(input => {
            input.addEventListener('focus', function() {
                this.parentElement.style.transform = 'translateY(-2px)';
            });
            
            input.addEventListener('blur', function() {
                this.parentElement.style.transform = 'translateY(0)';
            });
        });
    </script>
</body>
</html>
'''

DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>لوحة التحكم</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; }
        .navbar-custom { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .stats-card { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            border-radius: 15px; 
        }
        .card { border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 15px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/">
                🚀 نظام إدارة الأصول
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link text-white active" href="/">🏠 الرئيسية</a></li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle text-white" href="#" role="button" data-bs-toggle="dropdown">
                            💼 الأصول
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="/assets">📋 عرض الأصول</a></li>
                            <li><a class="dropdown-item" href="/add_asset">➕ إضافة أصل</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="/custody">📋 إدارة العهد</a></li>
                        </ul>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle text-white" href="#" role="button" data-bs-toggle="dropdown">
                            👥 الموظفين
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="/employees">👥 عرض الموظفين</a></li>
                            <li><a class="dropdown-item" href="/add_employee">➕ إضافة موظف</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="/departments">🏢 الإدارات</a></li>
                        </ul>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle text-white" href="#" role="button" data-bs-toggle="dropdown">
                            💰 المشتريات
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="/purchases">🛒 عرض المشتريات</a></li>
                            <li><a class="dropdown-item" href="/add_purchase">➕ إضافة مشترى</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="/invoices">🧾 الفواتير</a></li>
                            <li><a class="dropdown-item" href="/licenses">🔑 التراخيص</a></li>
                        </ul>
                    </li>
                    <li class="nav-item"><a class="nav-link text-white" href="/support">🎧 الدعم الفني</a></li>
                    <li class="nav-item"><a class="nav-link text-white" href="/reports">📊 التقارير</a></li>
                    <li class="nav-item"><a class="nav-link text-white" href="/logout">🚪 خروج</a></li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="alert alert-success">
            <i class="fas fa-check-circle"></i> 
            <strong>النظام يعمل بنجاح على http://localhost:5000</strong> 
            {{ total_assets }} أصل مع تقارير شاملة
        </div>
        
        <div class="row mb-4">
            <div class="col-lg-4 col-md-6 mb-3">
                <div class="stats-card p-4 text-center">
                    <i class="fas fa-laptop fa-3x mb-3"></i>
                    <h3>{{ total_assets }}</h3>
                    <p class="mb-0">إجمالي الأصول</p>
                </div>
            </div>
            <div class="col-lg-4 col-md-6 mb-3">
                <div class="stats-card p-4 text-center">
                    <i class="fas fa-check-circle fa-3x mb-3"></i>
                    <h3>{{ active_assets }}</h3>
                    <p class="mb-0">أصول نشطة</p>
                </div>
            </div>
            <div class="col-lg-4 col-md-6 mb-3">
                <div class="stats-card p-4 text-center">
                    <i class="fas fa-dollar-sign fa-3x mb-3"></i>
                    <h3>{{ "%.0f"|format(total_cost) }}</h3>
                    <p class="mb-0">إجمالي القيمة (ريال)</p>
                </div>
            </div>
        </div>

        <div class="row">
            <div class="col-lg-8 mb-4">
                <div class="card">
                    <div class="card-header d-flex justify-content-between">
                        <h5 class="mb-0">الأصول الحديثة</h5>
                        <a href="/reports" class="btn btn-success btn-sm">
                            <i class="fas fa-chart-bar"></i> التقارير
                        </a>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>رقم الأصل</th>
                                        <th>الاسم</th>
                                        <th>الفئة</th>
                                        <th>القيمة</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for asset in recent_assets %}
                                    <tr>
                                        <td><strong>{{ asset.tag }}</strong></td>
                                        <td>{{ asset.name }}</td>
                                        <td><span class="badge bg-secondary">{{ asset.category }}</span></td>
                                        <td>{{ "%.0f"|format(asset.cost) }} ريال</td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <div class="col-lg-4 mb-4">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">الإجراءات السريعة</h5>
                    </div>
                    <div class="card-body">
                        <div class="d-grid gap-2">
                            <a href="/assets" class="btn btn-outline-info">
                                <i class="fas fa-list"></i> عرض جميع الأصول
                            </a>
                            <a href="/add_asset" class="btn btn-outline-primary">
                                <i class="fas fa-plus"></i> إضافة أصل جديد
                            </a>
                            <a href="/employees" class="btn btn-outline-info">
                                <i class="fas fa-users"></i> إدارة الموظفين
                            </a>
                            <a href="/departments" class="btn btn-outline-secondary">
                                <i class="fas fa-building"></i> إدارة الإدارات
                            </a>
                            <a href="/custody" class="btn btn-outline-dark">
                                <i class="fas fa-clipboard-list"></i> إدارة العهد
                            </a>
                            <a href="/support" class="btn btn-outline-warning">
                                <i class="fas fa-headset"></i> الدعم الفني
                            </a>
                            <a href="/reports" class="btn btn-outline-success">
                                <i class="fas fa-chart-bar"></i> التقارير والإحصائيات
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

ADD_ASSET_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>إضافة أصل جديد</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body { 
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            font-family: 'Cairo', sans-serif;
        }
        .navbar-custom { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .card { 
            border: none; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.1); 
            border-radius: 20px;
            background: white;
        }
        .form-control {
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            padding: 0.75rem 1rem;
            transition: all 0.3s ease;
            background: rgba(255, 255, 255, 0.9);
        }
        .form-control:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            transform: translateY(-1px);
        }
        .form-label {
            font-weight: 600;
            color: #4a5568;
            margin-bottom: 0.5rem;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 12px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
        }
        .btn-secondary {
            border-radius: 12px;
            padding: 0.75rem 2rem;
            font-weight: 600;
        }
        .alert {
            border-radius: 15px;
            border: none;
            padding: 1rem 1.5rem;
            margin-bottom: 1.5rem;
        }
        .alert-success {
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            color: #155724;
            border-left: 4px solid #28a745;
        }
        .alert-danger {
            background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
            color: #721c24;
            border-left: 4px solid #dc3545;
        }
        .form-section {
            background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
            border-radius: 15px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid rgba(0,0,0,0.05);
        }
        .section-title {
            color: #667eea;
            font-weight: 700;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #667eea;
        }
        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
        }
        .input-group-text {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px 0 0 12px;
        }
        .form-control.with-icon {
            border-radius: 0 12px 12px 0;
        }
        .quick-fill {
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        .quick-fill-btn {
            background: #2196f3;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.25rem 0.75rem;
            font-size: 0.8rem;
            margin: 0.25rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .quick-fill-btn:hover {
            background: #1976d2;
            transform: scale(1.05);
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/">🚀 نظام إدارة الأصول</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link text-white" href="/">🏠 الرئيسية</a></li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle text-white active" href="#" role="button" data-bs-toggle="dropdown">💼 الأصول</a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="/assets">📋 عرض الأصول</a></li>
                            <li><a class="dropdown-item" href="/add_asset">➕ إضافة أصل</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="/custody">📋 إدارة العهد</a></li>
                        </ul>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle text-white" href="#" role="button" data-bs-toggle="dropdown">👥 الموظفين</a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="/employees">👥 عرض الموظفين</a></li>
                            <li><a class="dropdown-item" href="/add_employee">➕ إضافة موظف</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="/departments">🏢 الإدارات</a></li>
                        </ul>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle text-white" href="#" role="button" data-bs-toggle="dropdown">💰 المشتريات</a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="/purchases">🛒 عرض المشتريات</a></li>
                            <li><a class="dropdown-item" href="/add_purchase">➕ إضافة مشترى</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="/invoices">🧾 الفواتير</a></li>
                            <li><a class="dropdown-item" href="/licenses">🔑 التراخيص</a></li>
                        </ul>
                    </li>
                    <li class="nav-item"><a class="nav-link text-white" href="/support">🎧 الدعم الفني</a></li>
                    <li class="nav-item"><a class="nav-link text-white" href="/reports">📊 التقارير</a></li>
                    <li class="nav-item"><a class="nav-link text-white" href="/logout">🚪 خروج</a></li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row justify-content-center">
            <div class="col-lg-8">
                <div class="card">
                    <div class="card-header bg-transparent border-0 pt-4">
                        <div class="text-center">
                            <div class="d-inline-flex align-items-center justify-content-center bg-primary rounded-circle mb-3" style="width: 80px; height: 80px;">
                                <i class="fas fa-plus fa-2x text-white"></i>
                            </div>
                            <h2 class="mb-1">إضافة أصل جديد</h2>
                            <p class="text-muted">أضف أصل تقني جديد إلى النظام</p>
                        </div>
                    </div>
                    
                    <div class="card-body p-4">
                        {% if success %}
                            <div class="alert alert-success">
                                <i class="fas fa-check-circle me-2"></i>
                                {{ success }}
                                <div class="mt-2">
                                    <a href="/assets" class="btn btn-success btn-sm me-2">
                                        <i class="fas fa-list me-1"></i>
                                        عرض جميع الأصول
                                    </a>
                                    <a href="/add_asset" class="btn btn-outline-success btn-sm">
                                        <i class="fas fa-plus me-1"></i>
                                        إضافة أصل آخر
                                    </a>
                                </div>
                            </div>
                        {% endif %}
                        
                        {% if error %}
                            <div class="alert alert-danger">
                                <i class="fas fa-exclamation-triangle me-2"></i>
                                {{ error }}
                            </div>
                        {% endif %}
                        
                        <!-- ملء سريع -->
                        <div class="quick-fill">
                            <h6 class="mb-2"><i class="fas fa-magic me-2"></i>ملء سريع - أمثلة:</h6>
                            <button type="button" class="quick-fill-btn" onclick="fillExample('computer')">جهاز كمبيوتر</button>
                            <button type="button" class="quick-fill-btn" onclick="fillExample('laptop')">لابتوب</button>
                            <button type="button" class="quick-fill-btn" onclick="fillExample('printer')">طابعة</button>
                            <button type="button" class="quick-fill-btn" onclick="fillExample('server')">خادم</button>
                            <button type="button" class="quick-fill-btn" onclick="fillExample('phone')">هاتف</button>
                        </div>
                        
                        <form method="POST" id="assetForm">
                            <!-- معلومات أساسية -->
                            <div class="form-section">
                                <h5 class="section-title">
                                    <i class="fas fa-info-circle me-2"></i>
                                    المعلومات الأساسية
                                </h5>
                                <div class="form-grid">
                                    <div class="mb-3">
                                        <label class="form-label">
                                            <i class="fas fa-tag me-2"></i>
                                            رقم الأصل *
                                        </label>
                                        <div class="input-group">
                                            <span class="input-group-text">
                                                <i class="fas fa-hashtag"></i>
                                            </span>
                                            <input type="text" class="form-control with-icon" name="tag" 
                                                   value="{{ form_data.tag if form_data else '' }}" 
                                                   placeholder="مثال: PC001, LP001, PR001" required>
                                        </div>
                                    </div>
                                    
                                    <div class="mb-3">
                                        <label class="form-label">
                                            <i class="fas fa-desktop me-2"></i>
                                            اسم الأصل *
                                        </label>
                                        <div class="input-group">
                                            <span class="input-group-text">
                                                <i class="fas fa-edit"></i>
                                            </span>
                                            <input type="text" class="form-control with-icon" name="name" 
                                                   value="{{ form_data.name if form_data else '' }}" 
                                                   placeholder="مثال: جهاز كمبيوتر Dell OptiPlex" required>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- تصنيف الأصل -->
                            <div class="form-section">
                                <h5 class="section-title">
                                    <i class="fas fa-layer-group me-2"></i>
                                    تصنيف الأصل
                                </h5>
                                <div class="form-grid">
                                    <div class="mb-3">
                                        <label class="form-label">
                                            <i class="fas fa-folder me-2"></i>
                                            الفئة *
                                        </label>
                                        <div class="input-group">
                                            <span class="input-group-text">
                                                <i class="fas fa-list"></i>
                                            </span>
                                            <select class="form-control with-icon" name="category" required>
                                                <option value="">اختر الفئة</option>
                                                <option value="أجهزة الكمبيوتر" {{ 'selected' if form_data and form_data.category == 'أجهزة الكمبيوتر' else '' }}>أجهزة الكمبيوتر</option>
                                                <option value="الطابعات" {{ 'selected' if form_data and form_data.category == 'الطابعات' else '' }}>الطابعات</option>
                                                <option value="الشبكة" {{ 'selected' if form_data and form_data.category == 'الشبكة' else '' }}>الشبكة</option>
                                                <option value="الخوادم" {{ 'selected' if form_data and form_data.category == 'الخوادم' else '' }}>الخوادم</option>
                                                <option value="الهواتف" {{ 'selected' if form_data and form_data.category == 'الهواتف' else '' }}>الهواتف</option>
                                                <option value="أخرى" {{ 'selected' if form_data and form_data.category == 'أخرى' else '' }}>أخرى</option>
                                            </select>
                                        </div>
                                    </div>
                                    
                                    <div class="mb-3">
                                        <label class="form-label">
                                            <i class="fas fa-building me-2"></i>
                                            العلامة التجارية
                                        </label>
                                        <div class="input-group">
                                            <span class="input-group-text">
                                                <i class="fas fa-trademark"></i>
                                            </span>
                                            <input type="text" class="form-control with-icon" name="brand" 
                                                   value="{{ form_data.brand if form_data else '' }}" 
                                                   placeholder="مثال: Dell, HP, Canon, Cisco">
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- معلومات مالية وحالة -->
                            <div class="form-section">
                                <h5 class="section-title">
                                    <i class="fas fa-dollar-sign me-2"></i>
                                    المعلومات المالية والحالة
                                </h5>
                                <div class="form-grid">
                                    <div class="mb-3">
                                        <label class="form-label">
                                            <i class="fas fa-money-bill me-2"></i>
                                            التكلفة (ريال)
                                        </label>
                                        <div class="input-group">
                                            <span class="input-group-text">
                                                <i class="fas fa-coins"></i>
                                            </span>
                                            <input type="number" class="form-control with-icon" name="cost" 
                                                   value="{{ form_data.cost if form_data else '' }}" 
                                                   placeholder="0" min="0" step="0.01">
                                        </div>
                                    </div>
                                    
                                    <div class="mb-3">
                                        <label class="form-label">
                                            <i class="fas fa-check-circle me-2"></i>
                                            الحالة *
                                        </label>
                                        <div class="input-group">
                                            <span class="input-group-text">
                                                <i class="fas fa-info"></i>
                                            </span>
                                            <select class="form-control with-icon" name="status" required>
                                                <option value="">اختر الحالة</option>
                                                <option value="نشط" {{ 'selected' if form_data and form_data.status == 'نشط' else '' }}>نشط</option>
                                                <option value="صيانة" {{ 'selected' if form_data and form_data.status == 'صيانة' else '' }}>صيانة</option>
                                                <option value="متوقف" {{ 'selected' if form_data and form_data.status == 'متوقف' else '' }}>متوقف</option>
                                                <option value="مستبعد" {{ 'selected' if form_data and form_data.status == 'مستبعد' else '' }}>مستبعد</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- أزرار الإجراءات -->
                            <div class="d-flex justify-content-between align-items-center mt-4">
                                <div>
                                    <button type="submit" class="btn btn-primary btn-lg me-3">
                                        <i class="fas fa-save me-2"></i>
                                        حفظ الأصل
                                    </button>
                                    <button type="reset" class="btn btn-secondary btn-lg">
                                        <i class="fas fa-undo me-2"></i>
                                        إعادة تعيين
                                    </button>
                                </div>
                                <a href="/assets" class="btn btn-outline-primary">
                                    <i class="fas fa-arrow-right me-2"></i>
                                    العودة للأصول
                                </a>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // أمثلة الملء السريع
        const examples = {
            computer: {
                tag: 'PC' + String(Math.floor(Math.random() * 900) + 100),
                name: 'جهاز كمبيوتر مكتبي',
                category: 'أجهزة الكمبيوتر',
                brand: 'Dell',
                cost: '2500',
                status: 'نشط'
            },
            laptop: {
                tag: 'LP' + String(Math.floor(Math.random() * 900) + 100),
                name: 'جهاز لابتوب',
                category: 'أجهزة الكمبيوتر',
                brand: 'HP',
                cost: '3200',
                status: 'نشط'
            },
            printer: {
                tag: 'PR' + String(Math.floor(Math.random() * 900) + 100),
                name: 'طابعة ليزر',
                category: 'الطابعات',
                brand: 'Canon',
                cost: '800',
                status: 'نشط'
            },
            server: {
                tag: 'SV' + String(Math.floor(Math.random() * 900) + 100),
                name: 'خادم رئيسي',
                category: 'الخوادم',
                brand: 'Dell',
                cost: '8500',
                status: 'نشط'
            },
            phone: {
                tag: 'PH' + String(Math.floor(Math.random() * 900) + 100),
                name: 'هاتف IP',
                category: 'الهواتف',
                brand: 'Cisco',
                cost: '350',
                status: 'نشط'
            }
        };
        
        function fillExample(type) {
            const example = examples[type];
            if (example) {
                document.querySelector('input[name="tag"]').value = example.tag;
                document.querySelector('input[name="name"]').value = example.name;
                document.querySelector('select[name="category"]').value = example.category;
                document.querySelector('input[name="brand"]').value = example.brand;
                document.querySelector('input[name="cost"]').value = example.cost;
                document.querySelector('select[name="status"]').value = example.status;
            }
        }
        
        // تأثيرات التفاعل
        document.querySelectorAll('.form-control').forEach(input => {
            input.addEventListener('focus', function() {
                this.parentElement.style.transform = 'translateY(-2px)';
            });
            
            input.addEventListener('blur', function() {
                this.parentElement.style.transform = 'translateY(0)';
            });
        });
        
        // تأكيد الإرسال
        document.getElementById('assetForm').addEventListener('submit', function(e) {
            const tag = document.querySelector('input[name="tag"]').value;
            const name = document.querySelector('input[name="name"]').value;
            
            if (!confirm(`هل أنت متأكد من إضافة الأصل "${name}" برقم "${tag}"؟`)) {
                e.preventDefault();
            }
        });
    </script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

ASSETS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>الأصول</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; }
        .navbar-custom { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .card { border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 15px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/">🚀 نظام إدارة الأصول</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link text-white" href="/">🏠 الرئيسية</a></li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle text-white active" href="#" role="button" data-bs-toggle="dropdown">💼 الأصول</a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="/assets">📋 عرض الأصول</a></li>
                            <li><a class="dropdown-item" href="/add_asset">➕ إضافة أصل</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="/custody">📋 إدارة العهد</a></li>
                        </ul>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle text-white" href="#" role="button" data-bs-toggle="dropdown">👥 الموظفين</a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="/employees">👥 عرض الموظفين</a></li>
                            <li><a class="dropdown-item" href="/add_employee">➕ إضافة موظف</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="/departments">🏢 الإدارات</a></li>
                        </ul>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle text-white" href="#" role="button" data-bs-toggle="dropdown">💰 المشتريات</a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="/purchases">🛒 عرض المشتريات</a></li>
                            <li><a class="dropdown-item" href="/add_purchase">➕ إضافة مشترى</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="/invoices">🧾 الفواتير</a></li>
                            <li><a class="dropdown-item" href="/licenses">🔑 التراخيص</a></li>
                        </ul>
                    </li>
                    <li class="nav-item"><a class="nav-link text-white" href="/support">🎧 الدعم الفني</a></li>
                    <li class="nav-item"><a class="nav-link text-white" href="/reports">📊 التقارير</a></li>
                    <li class="nav-item"><a class="nav-link text-white" href="/logout">🚪 خروج</a></li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="fas fa-desktop text-primary"></i> جميع الأصول</h2>
            <div>
                <a href="/add_asset" class="btn btn-primary me-2">
                    <i class="fas fa-plus"></i> إضافة أصل جديد
                </a>
                <a href="/reports" class="btn btn-success">
                    <i class="fas fa-chart-bar"></i> التقارير
                </a>
            </div>
        </div>

        <div class="card">
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead class="table-dark">
                            <tr>
                                <th>رقم الأصل</th>
                                <th>الاسم</th>
                                <th>الفئة</th>
                                <th>العلامة التجارية</th>
                                <th>التكلفة</th>
                                <th>الحالة</th>
                                <th>الإجراءات</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for asset in assets %}
                            <tr>
                                <td><strong class="text-primary">{{ asset.tag }}</strong></td>
                                <td>{{ asset.name }}</td>
                                <td><span class="badge bg-secondary">{{ asset.category }}</span></td>
                                <td>{{ asset.brand }}</td>
                                <td><strong class="text-success">{{ "%.0f"|format(asset.cost) }} ريال</strong></td>
                                <td>
                                    <span class="badge bg-{{ 'success' if asset.status == 'نشط' else 'warning' }}">
                                        {{ asset.status }}
                                    </span>
                                </td>
                                <td>
                                    <button class="btn btn-primary btn-sm me-1" onclick="editAsset({{ asset.id }})">
                                        <i class="fas fa-edit"></i>
                                    </button>
                                    <button class="btn btn-danger btn-sm" onclick="deleteAsset({{ asset.id }}, '{{ asset.tag }}', '{{ asset.name }}')">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script>
        function editAsset(assetId) {
            window.location.href = `/edit_asset/${assetId}`;
        }
        
        function deleteAsset(assetId, assetTag, assetName) {
            if (confirm(`هل أنت متأكد من حذف الأصل "${assetName}" برقم "${assetTag}"؟\n\nهذا الإجراء لا يمكن التراجع عنه!`)) {
                window.location.href = `/delete_asset/${assetId}`;
            }
        }
    </script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

EMPLOYEES_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>إدارة الموظفين</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; font-family: 'Cairo', sans-serif; }
        .navbar-custom { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .card { border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 15px; }
        .employee-card { transition: transform 0.2s; }
        .employee-card:hover { transform: translateY(-2px); }
        .department-badge { font-size: 0.8rem; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/">🚀 نظام إدارة الأصول</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="/">الرئيسية</a>
                <a class="nav-link text-white" href="/assets">الأصول</a>
                <a class="nav-link text-white" href="/add_asset">➕ إضافة أصل</a>
                <a class="nav-link text-white active" href="/employees">👥 الموظفين</a>
                <a class="nav-link text-white" href="/support">🎧 الدعم الفني</a>
                <a class="nav-link text-white" href="/reports">📊 التقارير</a>
                <a class="nav-link text-white" href="/logout">خروج</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="fas fa-users text-primary"></i> إدارة الموظفين</h2>
            <div>
                <a href="/add_employee" class="btn btn-primary me-2">
                    <i class="fas fa-user-plus"></i> إضافة موظف جديد
                </a>
                <a href="/support" class="btn btn-success">
                    <i class="fas fa-headset"></i> الدعم الفني
                </a>
            </div>
        </div>

        <div class="row">
            {% for employee in employees %}
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="card employee-card">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <div class="bg-primary rounded-circle d-flex align-items-center justify-content-center me-3" style="width: 50px; height: 50px;">
                                <i class="fas fa-user text-white"></i>
                            </div>
                            <div>
                                <h5 class="mb-1">{{ employee.name }}</h5>
                                <small class="text-muted">{{ employee.emp_id }}</small>
                            </div>
                        </div>
                        
                        <div class="mb-2">
                            <span class="badge bg-secondary department-badge">{{ employee.department }}</span>
                            <span class="badge bg-info department-badge ms-1">{{ employee.position }}</span>
                        </div>
                        
                        <div class="mb-2">
                            <small class="text-muted">
                                <i class="fas fa-phone me-1"></i>{{ employee.phone }}
                            </small>
                        </div>
                        
                        <div class="mb-2">
                            <small class="text-muted">
                                <i class="fas fa-envelope me-1"></i>{{ employee.email }}
                            </small>
                        </div>
                        
                        <div class="mb-2">
                            <small class="text-muted">
                                <i class="fas fa-map-marker-alt me-1"></i>{{ employee.office_location }}
                            </small>
                        </div>
                        
                        {% if employee.manager_name %}
                        <div class="mb-2">
                            <small class="text-muted">
                                <i class="fas fa-user-tie me-1"></i>المدير: {{ employee.manager_name }}
                            </small>
                        </div>
                        {% endif %}
                        
                        <div class="d-flex justify-content-between align-items-center mt-3">
                            <span class="badge bg-{{ 'success' if employee.status == 'نشط' else 'warning' }}">
                                {{ employee.status }}
                            </span>
                            <div>
                                <button class="btn btn-sm btn-outline-info me-1" onclick="editEmployee({{ employee.id }})">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-primary me-1" onclick="createTicketForEmployee({{ employee.id }}, '{{ employee.name }}')">
                                    <i class="fas fa-ticket-alt"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-success me-1" onclick="remoteSupport({{ employee.id }}, '{{ employee.name }}')">
                                    <i class="fas fa-desktop"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-danger" onclick="deleteEmployee({{ employee.id }}, '{{ employee.name }}')">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>

    <script>
        function editEmployee(employeeId) {
            window.location.href = `/edit_employee/${employeeId}`;
        }
        
        function createTicketForEmployee(employeeId, employeeName) {
            if (confirm(`إنشاء تذكرة دعم فني للموظف: ${employeeName}؟`)) {
                window.location.href = `/create_ticket?employee_id=${employeeId}`;
            }
        }
        
        function remoteSupport(employeeId, employeeName) {
            if (confirm(`بدء جلسة دعم فني عن بُعد للموظف: ${employeeName}؟`)) {
                window.location.href = `/remote_support?employee_id=${employeeId}`;
            }
        }
        
        function deleteEmployee(employeeId, employeeName) {
            if (confirm(`هل أنت متأكد من حذف الموظف "${employeeName}"؟\n\nسيتم التحقق من عدم وجود أصول مخصصة له.`)) {
                window.location.href = `/delete_employee/${employeeId}`;
            }
        }
    </script>
</body>
</html>
'''

ADD_EMPLOYEE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>إضافة موظف جديد</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; font-family: 'Cairo', sans-serif; }
        .navbar-custom { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .card { border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 15px; }
        .form-control { border-radius: 10px; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; border-radius: 10px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/">🚀 نظام إدارة الأصول</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="/">الرئيسية</a>
                <a class="nav-link text-white" href="/assets">الأصول</a>
                <a class="nav-link text-white" href="/add_asset">➕ إضافة أصل</a>
                <a class="nav-link text-white active" href="/employees">👥 الموظفين</a>
                <a class="nav-link text-white" href="/support">🎧 الدعم الفني</a>
                <a class="nav-link text-white" href="/reports">📊 التقارير</a>
                <a class="nav-link text-white" href="/logout">خروج</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row justify-content-center">
            <div class="col-lg-8">
                <div class="card">
                    <div class="card-header bg-transparent text-center">
                        <h2><i class="fas fa-user-plus text-primary"></i> إضافة موظف جديد</h2>
                    </div>
                    <div class="card-body">
                        {% if success %}
                            <div class="alert alert-success">
                                <i class="fas fa-check-circle me-2"></i>{{ success }}
                                <div class="mt-2">
                                    <a href="/employees" class="btn btn-success btn-sm me-2">عرض الموظفين</a>
                                    <a href="/add_employee" class="btn btn-outline-success btn-sm">إضافة موظف آخر</a>
                                </div>
                            </div>
                        {% endif %}
                        
                        {% if error %}
                            <div class="alert alert-danger">
                                <i class="fas fa-exclamation-triangle me-2"></i>{{ error }}
                            </div>
                        {% endif %}
                        
                        <form method="POST">
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">رقم الموظف *</label>
                                    <input type="text" class="form-control" name="emp_id" value="{{ form_data.emp_id if form_data else '' }}" placeholder="EMP001" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">الاسم الكامل *</label>
                                    <input type="text" class="form-control" name="name" value="{{ form_data.name if form_data else '' }}" required>
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">رقم الهوية *</label>
                                    <input type="text" class="form-control" name="national_id" value="{{ form_data.national_id if form_data else '' }}" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">رقم الهاتف *</label>
                                    <input type="text" class="form-control" name="phone" value="{{ form_data.phone if form_data else '' }}" placeholder="05xxxxxxxx" required>
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">البريد الإلكتروني *</label>
                                <input type="email" class="form-control" name="email" value="{{ form_data.email if form_data else '' }}" required>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">الإدارة *</label>
                                    <select class="form-control" name="department" required>
                                        <option value="">اختر الإدارة</option>
                                        <option value="تقنية المعلومات" {{ 'selected' if form_data and form_data.department == 'تقنية المعلومات' else '' }}>تقنية المعلومات</option>
                                        <option value="الموارد البشرية" {{ 'selected' if form_data and form_data.department == 'الموارد البشرية' else '' }}>الموارد البشرية</option>
                                        <option value="المالية" {{ 'selected' if form_data and form_data.department == 'المالية' else '' }}>المالية</option>
                                        <option value="التسويق" {{ 'selected' if form_data and form_data.department == 'التسويق' else '' }}>التسويق</option>
                                        <option value="المبيعات" {{ 'selected' if form_data and form_data.department == 'المبيعات' else '' }}>المبيعات</option>
                                        <option value="العمليات" {{ 'selected' if form_data and form_data.department == 'العمليات' else '' }}>العمليات</option>
                                    </select>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">المسمى الوظيفي *</label>
                                    <input type="text" class="form-control" name="position" value="{{ form_data.position if form_data else '' }}" required>
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">تاريخ التوظيف *</label>
                                    <input type="date" class="form-control" name="hire_date" value="{{ form_data.hire_date if form_data else '' }}" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">الحالة *</label>
                                    <select class="form-control" name="status" required>
                                        <option value="">اختر الحالة</option>
                                        <option value="نشط" {{ 'selected' if form_data and form_data.status == 'نشط' else '' }}>نشط</option>
                                        <option value="إجازة" {{ 'selected' if form_data and form_data.status == 'إجازة' else '' }}>إجازة</option>
                                        <option value="متوقف" {{ 'selected' if form_data and form_data.status == 'متوقف' else '' }}>متوقف</option>
                                    </select>
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">المدير المباشر</label>
                                    <select class="form-control" name="manager_id">
                                        <option value="">لا يوجد</option>
                                        {% for manager in managers %}
                                        <option value="{{ manager.id }}" {{ 'selected' if form_data and form_data.manager_id == manager.id|string else '' }}>{{ manager.name }}</option>
                                        {% endfor %}
                                    </select>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">موقع المكتب</label>
                                    <input type="text" class="form-control" name="office_location" value="{{ form_data.office_location if form_data else '' }}" placeholder="الطابق الأول - مكتب 101">
                                </div>
                            </div>
                            
                            <div class="d-flex justify-content-between">
                                <button type="submit" class="btn btn-primary btn-lg">
                                    <i class="fas fa-save me-2"></i>حفظ الموظف
                                </button>
                                <a href="/employees" class="btn btn-outline-secondary">
                                    <i class="fas fa-arrow-right me-2"></i>العودة للموظفين
                                </a>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
'''

SUPPORT_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>الدعم الفني</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; font-family: 'Cairo', sans-serif; }
        .navbar-custom { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .card { border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 15px; }
        .stats-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px; }
        .priority-high { border-left: 4px solid #dc3545; }
        .priority-medium { border-left: 4px solid #ffc107; }
        .priority-low { border-left: 4px solid #28a745; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/">🚀 نظام إدارة الأصول</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="/">الرئيسية</a>
                <a class="nav-link text-white" href="/assets">الأصول</a>
                <a class="nav-link text-white" href="/add_asset">➕ إضافة أصل</a>
                <a class="nav-link text-white" href="/employees">👥 الموظفين</a>
                <a class="nav-link text-white active" href="/support">🎧 الدعم الفني</a>
                <a class="nav-link text-white" href="/reports">📊 التقارير</a>
                <a class="nav-link text-white" href="/logout">خروج</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="fas fa-headset text-primary"></i> مركز الدعم الفني</h2>
            <div>
                <a href="/create_ticket" class="btn btn-primary me-2">
                    <i class="fas fa-plus"></i> إنشاء تذكرة جديدة
                </a>
                <a href="/remote_support" class="btn btn-success">
                    <i class="fas fa-desktop"></i> الدعم عن بُعد
                </a>
            </div>
        </div>

        <!-- إحصائيات التذاكر -->
        <div class="row mb-4">
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="stats-card p-4 text-center">
                    <i class="fas fa-ticket-alt fa-3x mb-3"></i>
                    <h3>{{ total_tickets }}</h3>
                    <p class="mb-0">إجمالي التذاكر</p>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="stats-card p-4 text-center">
                    <i class="fas fa-clock fa-3x mb-3"></i>
                    <h3>{{ open_tickets }}</h3>
                    <p class="mb-0">تذاكر مفتوحة</p>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="stats-card p-4 text-center">
                    <i class="fas fa-check-circle fa-3x mb-3"></i>
                    <h3>{{ closed_tickets }}</h3>
                    <p class="mb-0">تذاكر مكتملة</p>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="stats-card p-4 text-center">
                    <i class="fas fa-exclamation-triangle fa-3x mb-3"></i>
                    <h3>{{ high_priority }}</h3>
                    <p class="mb-0">أولوية عالية</p>
                </div>
            </div>
        </div>

        <!-- التذاكر الحديثة -->
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">التذاكر الحديثة</h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>رقم التذكرة</th>
                                <th>الموظف</th>
                                <th>العنوان</th>
                                <th>الفئة</th>
                                <th>الأولوية</th>
                                <th>الحالة</th>
                                <th>المسؤول</th>
                                <th>الإجراءات</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for ticket in recent_tickets %}
                            <tr class="priority-{{ 'high' if ticket.priority == 'عالية' else 'medium' if ticket.priority == 'متوسطة' else 'low' }}">
                                <td><strong>{{ ticket.ticket_number }}</strong></td>
                                <td>{{ ticket.employee_name }}</td>
                                <td>{{ ticket.title }}</td>
                                <td><span class="badge bg-secondary">{{ ticket.category }}</span></td>
                                <td>
                                    <span class="badge bg-{{ 'danger' if ticket.priority == 'عالية' else 'warning' if ticket.priority == 'متوسطة' else 'success' }}">
                                        {{ ticket.priority }}
                                    </span>
                                </td>
                                <td>
                                    <span class="badge bg-{{ 'success' if ticket.status == 'مكتمل' else 'primary' if ticket.status == 'قيد المعالجة' else 'secondary' }}">
                                        {{ ticket.status }}
                                    </span>
                                </td>
                                <td>{{ ticket.assigned_tech or 'غير محدد' }}</td>
                                <td>
                                    <button class="btn btn-sm btn-outline-primary" onclick="viewTicket('{{ ticket.ticket_number }}')">
                                        <i class="fas fa-eye"></i>
                                    </button>
                                    {% if ticket.status != 'مكتمل' %}
                                    <button class="btn btn-sm btn-outline-success" onclick="startRemoteSession({{ ticket.id }}, '{{ ticket.employee_name }}')">
                                        <i class="fas fa-desktop"></i>
                                    </button>
                                    {% endif %}
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script>
        function viewTicket(ticketNumber) {
            alert(`عرض تفاصيل التذكرة: ${ticketNumber}`);
            // يمكن إضافة modal أو صفحة منفصلة لعرض التفاصيل
        }
        
        function startRemoteSession(ticketId, employeeName) {
            if (confirm(`بدء جلسة دعم فني عن بُعد للموظف: ${employeeName}؟`)) {
                window.location.href = `/remote_support?ticket_id=${ticketId}`;
            }
        }
    </script>
</body>
</html>
'''

CREATE_TICKET_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>إنشاء تذكرة دعم فني</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; font-family: 'Cairo', sans-serif; }
        .navbar-custom { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .card { border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 15px; }
        .form-control { border-radius: 10px; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; border-radius: 10px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/">🚀 نظام إدارة الأصول</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="/">الرئيسية</a>
                <a class="nav-link text-white" href="/assets">الأصول</a>
                <a class="nav-link text-white" href="/add_asset">➕ إضافة أصل</a>
                <a class="nav-link text-white" href="/employees">👥 الموظفين</a>
                <a class="nav-link text-white active" href="/support">🎧 الدعم الفني</a>
                <a class="nav-link text-white" href="/reports">📊 التقارير</a>
                <a class="nav-link text-white" href="/logout">خروج</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row justify-content-center">
            <div class="col-lg-8">
                <div class="card">
                    <div class="card-header bg-transparent text-center">
                        <h2><i class="fas fa-ticket-alt text-primary"></i> إنشاء تذكرة دعم فني</h2>
                    </div>
                    <div class="card-body">
                        {% if success %}
                            <div class="alert alert-success">
                                <i class="fas fa-check-circle me-2"></i>{{ success }}
                                <div class="mt-2">
                                    <a href="/support" class="btn btn-success btn-sm me-2">عرض التذاكر</a>
                                    <a href="/create_ticket" class="btn btn-outline-success btn-sm">إنشاء تذكرة أخرى</a>
                                </div>
                            </div>
                        {% endif %}
                        
                        {% if error %}
                            <div class="alert alert-danger">
                                <i class="fas fa-exclamation-triangle me-2"></i>{{ error }}
                            </div>
                        {% endif %}
                        
                        <form method="POST">
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">الموظف *</label>
                                    <select class="form-control" name="employee_id" required>
                                        <option value="">اختر الموظف</option>
                                        {% for employee in employees %}
                                        <option value="{{ employee.id }}">{{ employee.name }} ({{ employee.emp_id }})</option>
                                        {% endfor %}
                                    </select>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">الأصل المتأثر</label>
                                    <select class="form-control" name="asset_id">
                                        <option value="">لا يوجد أصل محدد</option>
                                        {% for asset in assets %}
                                        <option value="{{ asset.id }}">{{ asset.tag }} - {{ asset.name }}</option>
                                        {% endfor %}
                                    </select>
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">عنوان المشكلة *</label>
                                <input type="text" class="form-control" name="title" required placeholder="وصف مختصر للمشكلة">
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">وصف تفصيلي للمشكلة *</label>
                                <textarea class="form-control" name="description" rows="4" required placeholder="اشرح المشكلة بالتفصيل..."></textarea>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">فئة المشكلة *</label>
                                    <select class="form-control" name="category" required>
                                        <option value="">اختر الفئة</option>
                                        <option value="أجهزة">أجهزة</option>
                                        <option value="برمجيات">برمجيات</option>
                                        <option value="شبكة">شبكة</option>
                                        <option value="طابعات">طابعات</option>
                                        <option value="أمان">أمان</option>
                                        <option value="أخرى">أخرى</option>
                                    </select>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">الأولوية *</label>
                                    <select class="form-control" name="priority" required>
                                        <option value="">اختر الأولوية</option>
                                        <option value="عالية">عالية - يوقف العمل</option>
                                        <option value="متوسطة">متوسطة - يؤثر على الأداء</option>
                                        <option value="منخفضة">منخفضة - لا يؤثر على العمل</option>
                                    </select>
                                </div>
                            </div>
                            
                            <div class="d-flex justify-content-between">
                                <button type="submit" class="btn btn-primary btn-lg">
                                    <i class="fas fa-paper-plane me-2"></i>إرسال التذكرة
                                </button>
                                <a href="/support" class="btn btn-outline-secondary">
                                    <i class="fas fa-arrow-right me-2"></i>العودة للدعم الفني
                                </a>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
'''

REMOTE_SUPPORT_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>الدعم الفني عن بُعد</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; font-family: 'Cairo', sans-serif; }
        .navbar-custom { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .card { border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 15px; }
        .remote-screen { background: #000; border-radius: 10px; min-height: 400px; display: flex; align-items: center; justify-content: center; color: white; }
        .control-panel { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/">🚀 نظام إدارة الأصول</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="/">الرئيسية</a>
                <a class="nav-link text-white" href="/assets">الأصول</a>
                <a class="nav-link text-white" href="/add_asset">➕ إضافة أصل</a>
                <a class="nav-link text-white" href="/employees">👥 الموظفين</a>
                <a class="nav-link text-white active" href="/support">🎧 الدعم الفني</a>
                <a class="nav-link text-white" href="/reports">📊 التقارير</a>
                <a class="nav-link text-white" href="/logout">خروج</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="fas fa-desktop text-primary"></i> الدعم الفني عن بُعد</h2>
            <div>
                <button class="btn btn-success me-2" onclick="startSession()">
                    <i class="fas fa-play"></i> بدء الجلسة
                </button>
                <button class="btn btn-danger" onclick="endSession()">
                    <i class="fas fa-stop"></i> إنهاء الجلسة
                </button>
            </div>
        </div>

        <div class="row">
            <div class="col-lg-9 mb-4">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">شاشة الموظف</h5>
                        <small class="text-muted">جلسة مشاركة الشاشة</small>
                    </div>
                    <div class="card-body p-0">
                        <div class="remote-screen">
                            <div class="text-center">
                                <i class="fas fa-desktop fa-5x mb-3"></i>
                                <h4>في انتظار الاتصال...</h4>
                                <p>رمز الجلسة: <strong id="sessionCode">RST-2025-001</strong></p>
                                <button class="btn btn-primary" onclick="generateCode()">
                                    <i class="fas fa-refresh"></i> إنشاء رمز جديد
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="col-lg-3 mb-4">
                <div class="card">
                    <div class="card-header control-panel">
                        <h6 class="mb-0 text-white">لوحة التحكم</h6>
                    </div>
                    <div class="card-body">
                        <div class="d-grid gap-2">
                            <button class="btn btn-outline-primary btn-sm">
                                <i class="fas fa-mouse-pointer"></i> التحكم بالماوس
                            </button>
                            <button class="btn btn-outline-primary btn-sm">
                                <i class="fas fa-keyboard"></i> التحكم بلوحة المفاتيح
                            </button>
                            <button class="btn btn-outline-info btn-sm">
                                <i class="fas fa-file-transfer"></i> نقل الملفات
                            </button>
                            <button class="btn btn-outline-warning btn-sm">
                                <i class="fas fa-camera"></i> لقطة شاشة
                            </button>
                            <button class="btn btn-outline-success btn-sm">
                                <i class="fas fa-microphone"></i> الصوت
                            </button>
                            <button class="btn btn-outline-secondary btn-sm">
                                <i class="fas fa-cog"></i> الإعدادات
                            </button>
                        </div>
                        
                        <hr>
                        
                        <h6>معلومات الجلسة</h6>
                        <small class="text-muted">
                            <div>الحالة: <span class="text-success">متصل</span></div>
                            <div>المدة: <span id="duration">00:00:00</span></div>
                            <div>جودة الاتصال: <span class="text-success">ممتازة</span></div>
                        </small>
                    </div>
                </div>

                <div class="card mt-3">
                    <div class="card-header">
                        <h6 class="mb-0">الدردشة</h6>
                    </div>
                    <div class="card-body">
                        <div class="chat-messages" style="height: 200px; overflow-y: auto; border: 1px solid #eee; padding: 10px; border-radius: 5px;">
                            <div class="mb-2">
                                <small class="text-muted">الفني:</small><br>
                                <span>مرحباً، سأساعدك في حل المشكلة</span>
                            </div>
                            <div class="mb-2">
                                <small class="text-muted">الموظف:</small><br>
                                <span>شكراً لك، الجهاز لا يعمل</span>
                            </div>
                        </div>
                        <div class="mt-2">
                            <div class="input-group">
                                <input type="text" class="form-control form-control-sm" placeholder="اكتب رسالة...">
                                <button class="btn btn-primary btn-sm">
                                    <i class="fas fa-paper-plane"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let sessionStartTime = new Date();
        
        function startSession() {
            document.querySelector('.remote-screen').innerHTML = `
                <div class="text-center">
                    <i class="fas fa-desktop fa-5x mb-3 text-success"></i>
                    <h4 class="text-success">متصل بنجاح!</h4>
                    <p>جلسة نشطة مع الموظف</p>
                    <div class="row mt-4">
                        <div class="col-6">
                            <div class="bg-secondary p-3 rounded">
                                <i class="fas fa-window-maximize fa-2x"></i>
                                <br>نافذة التطبيق
                            </div>
                        </div>
                        <div class="col-6">
                            <div class="bg-dark p-3 rounded">
                                <i class="fas fa-terminal fa-2x"></i>
                                <br>سطر الأوامر
                            </div>
                        </div>
                    </div>
                </div>
            `;
            updateDuration();
        }
        
        function endSession() {
            if (confirm('هل أنت متأكد من إنهاء الجلسة؟')) {
                document.querySelector('.remote-screen').innerHTML = `
                    <div class="text-center">
                        <i class="fas fa-desktop fa-5x mb-3"></i>
                        <h4>تم إنهاء الجلسة</h4>
                        <p>شكراً لاستخدام خدمة الدعم الفني</p>
                        <button class="btn btn-primary" onclick="location.reload()">
                            <i class="fas fa-refresh"></i> جلسة جديدة
                        </button>
                    </div>
                `;
            }
        }
        
        function generateCode() {
            const code = 'RST-' + new Date().getFullYear() + '-' + String(Math.floor(Math.random() * 1000)).padStart(3, '0');
            document.getElementById('sessionCode').textContent = code;
        }
        
        function updateDuration() {
            setInterval(() => {
                const now = new Date();
                const diff = now - sessionStartTime;
                const hours = Math.floor(diff / 3600000);
                const minutes = Math.floor((diff % 3600000) / 60000);
                const seconds = Math.floor((diff % 60000) / 1000);
                document.getElementById('duration').textContent = 
                    String(hours).padStart(2, '0') + ':' + 
                    String(minutes).padStart(2, '0') + ':' + 
                    String(seconds).padStart(2, '0');
            }, 1000);
        }
    </script>
</body>
</html>
'''

DEPARTMENTS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>إدارة الإدارات</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; font-family: 'Cairo', sans-serif; }
        .navbar-custom { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .card { border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 15px; }
        .dept-card { transition: transform 0.2s; }
        .dept-card:hover { transform: translateY(-2px); }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/">🚀 نظام إدارة الأصول</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="/">الرئيسية</a>
                <a class="nav-link text-white" href="/assets">الأصول</a>
                <a class="nav-link text-white" href="/employees">👥 الموظفين</a>
                <a class="nav-link text-white active" href="/departments">🏢 الإدارات</a>
                <a class="nav-link text-white" href="/custody">📋 العهد</a>
                <a class="nav-link text-white" href="/support">🎧 الدعم الفني</a>
                <a class="nav-link text-white" href="/reports">📊 التقارير</a>
                <a class="nav-link text-white" href="/logout">خروج</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="fas fa-building text-primary"></i> إدارة الإدارات</h2>
            <a href="/add_department" class="btn btn-primary">
                <i class="fas fa-plus"></i> إضافة إدارة جديدة
            </a>
        </div>

        <div class="row">
            {% for dept in departments %}
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="card dept-card">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <div class="bg-primary rounded-circle d-flex align-items-center justify-content-center me-3" style="width: 50px; height: 50px;">
                                <i class="fas fa-building text-white"></i>
                            </div>
                            <div>
                                <h5 class="mb-1">{{ dept.name }}</h5>
                                <small class="text-muted">{{ dept.employee_count }} موظف</small>
                            </div>
                        </div>
                        
                        <p class="text-muted mb-3">{{ dept.description }}</p>
                        
                        <div class="mb-2">
                            <small class="text-muted">
                                <i class="fas fa-map-marker-alt me-1"></i>{{ dept.location }}
                            </small>
                        </div>
                        
                        {% if dept.manager_name %}
                        <div class="mb-2">
                            <small class="text-muted">
                                <i class="fas fa-user-tie me-1"></i>المدير: {{ dept.manager_name }}
                            </small>
                        </div>
                        {% endif %}
                        
                        <div class="mb-3">
                            <small class="text-muted">
                                <i class="fas fa-dollar-sign me-1"></i>الميزانية: {{ "{:,.0f}".format(dept.budget) }} ريال
                            </small>
                        </div>
                        
                        <div class="d-flex justify-content-between align-items-center">
                            <span class="badge bg-{{ 'success' if dept.status == 'نشط' else 'warning' }}">
                                {{ dept.status }}
                            </span>
                            <div>
                                <button class="btn btn-sm btn-outline-primary" onclick="editDepartment({{ dept.id }})">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-danger" onclick="deleteDepartment({{ dept.id }}, '{{ dept.name }}')">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>

    <script>
        function editDepartment(deptId) {
            window.location.href = `/edit_department/${deptId}`;
        }
        
        function deleteDepartment(deptId, deptName) {
            if (confirm(`هل أنت متأكد من حذف الإدارة "${deptName}"؟`)) {
                window.location.href = `/delete_department/${deptId}`;
            }
        }
    </script>
</body>
</html>
'''

ADD_DEPARTMENT_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>إضافة إدارة جديدة</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; font-family: 'Cairo', sans-serif; }
        .navbar-custom { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .card { border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 15px; }
        .form-control { border-radius: 10px; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; border-radius: 10px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/">🚀 نظام إدارة الأصول</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="/">الرئيسية</a>
                <a class="nav-link text-white" href="/assets">الأصول</a>
                <a class="nav-link text-white" href="/employees">👥 الموظفين</a>
                <a class="nav-link text-white active" href="/departments">🏢 الإدارات</a>
                <a class="nav-link text-white" href="/custody">📋 العهد</a>
                <a class="nav-link text-white" href="/support">🎧 الدعم الفني</a>
                <a class="nav-link text-white" href="/reports">📊 التقارير</a>
                <a class="nav-link text-white" href="/logout">خروج</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row justify-content-center">
            <div class="col-lg-8">
                <div class="card">
                    <div class="card-header bg-transparent text-center">
                        <h2><i class="fas fa-building text-primary"></i> إضافة إدارة جديدة</h2>
                    </div>
                    <div class="card-body">
                        {% if success %}
                            <div class="alert alert-success">
                                <i class="fas fa-check-circle me-2"></i>{{ success }}
                                <div class="mt-2">
                                    <a href="/departments" class="btn btn-success btn-sm me-2">عرض الإدارات</a>
                                    <a href="/add_department" class="btn btn-outline-success btn-sm">إضافة إدارة أخرى</a>
                                </div>
                            </div>
                        {% endif %}
                        
                        {% if error %}
                            <div class="alert alert-danger">
                                <i class="fas fa-exclamation-triangle me-2"></i>{{ error }}
                            </div>
                        {% endif %}
                        
                        <form method="POST">
                            <div class="mb-3">
                                <label class="form-label">اسم الإدارة *</label>
                                <input type="text" class="form-control" name="name" value="{{ form_data.name if form_data else '' }}" required>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">الوصف</label>
                                <textarea class="form-control" name="description" rows="3">{{ form_data.description if form_data else '' }}</textarea>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">المدير</label>
                                    <select class="form-control" name="manager_id">
                                        <option value="">لا يوجد</option>
                                        {% for manager in managers %}
                                        <option value="{{ manager.id }}" {{ 'selected' if form_data and form_data.manager_id == manager.id|string else '' }}>{{ manager.name }}</option>
                                        {% endfor %}
                                    </select>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">الموقع</label>
                                    <input type="text" class="form-control" name="location" value="{{ form_data.location if form_data else '' }}">
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">الميزانية (ريال)</label>
                                    <input type="number" class="form-control" name="budget" value="{{ form_data.budget if form_data else '' }}" min="0" step="0.01">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">الحالة *</label>
                                    <select class="form-control" name="status" required>
                                        <option value="">اختر الحالة</option>
                                        <option value="نشط" {{ 'selected' if form_data and form_data.status == 'نشط' else '' }}>نشط</option>
                                        <option value="متوقف" {{ 'selected' if form_data and form_data.status == 'متوقف' else '' }}>متوقف</option>
                                    </select>
                                </div>
                            </div>
                            
                            <div class="d-flex justify-content-between">
                                <button type="submit" class="btn btn-primary btn-lg">
                                    <i class="fas fa-save me-2"></i>حفظ الإدارة
                                </button>
                                <a href="/departments" class="btn btn-outline-secondary">
                                    <i class="fas fa-arrow-right me-2"></i>العودة للإدارات
                                </a>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
'''

EDIT_ASSET_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>تعديل الأصل</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; font-family: 'Cairo', sans-serif; }
        .navbar-custom { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .card { border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 15px; }
        .form-control { border-radius: 10px; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; border-radius: 10px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/">🚀 نظام إدارة الأصول</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="/">الرئيسية</a>
                <a class="nav-link text-white active" href="/assets">الأصول</a>
                <a class="nav-link text-white" href="/employees">👥 الموظفين</a>
                <a class="nav-link text-white" href="/departments">🏢 الإدارات</a>
                <a class="nav-link text-white" href="/custody">📋 العهد</a>
                <a class="nav-link text-white" href="/support">🎧 الدعم الفني</a>
                <a class="nav-link text-white" href="/reports">📊 التقارير</a>
                <a class="nav-link text-white" href="/logout">خروج</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row justify-content-center">
            <div class="col-lg-8">
                <div class="card">
                    <div class="card-header bg-transparent text-center">
                        <h2><i class="fas fa-edit text-primary"></i> تعديل الأصل: {{ asset.tag }}</h2>
                    </div>
                    <div class="card-body">
                        {% if error %}
                            <div class="alert alert-danger">
                                <i class="fas fa-exclamation-triangle me-2"></i>{{ error }}
                            </div>
                        {% endif %}
                        
                        <form method="POST">
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">رقم الأصل *</label>
                                    <input type="text" class="form-control" name="tag" value="{{ asset.tag }}" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">اسم الأصل *</label>
                                    <input type="text" class="form-control" name="name" value="{{ asset.name }}" required>
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">الفئة *</label>
                                    <select class="form-control" name="category" required>
                                        <option value="">اختر الفئة</option>
                                        <option value="أجهزة الكمبيوتر" {{ 'selected' if asset.category == 'أجهزة الكمبيوتر' else '' }}>أجهزة الكمبيوتر</option>
                                        <option value="الطابعات" {{ 'selected' if asset.category == 'الطابعات' else '' }}>الطابعات</option>
                                        <option value="الشبكة" {{ 'selected' if asset.category == 'الشبكة' else '' }}>الشبكة</option>
                                        <option value="الخوادم" {{ 'selected' if asset.category == 'الخوادم' else '' }}>الخوادم</option>
                                        <option value="الهواتف" {{ 'selected' if asset.category == 'الهواتف' else '' }}>الهواتف</option>
                                        <option value="أخرى" {{ 'selected' if asset.category == 'أخرى' else '' }}>أخرى</option>
                                    </select>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">العلامة التجارية</label>
                                    <input type="text" class="form-control" name="brand" value="{{ asset.brand or '' }}">
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">التكلفة (ريال)</label>
                                    <input type="number" class="form-control" name="cost" value="{{ asset.cost or '' }}" min="0" step="0.01">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">الحالة *</label>
                                    <select class="form-control" name="status" required>
                                        <option value="">اختر الحالة</option>
                                        <option value="نشط" {{ 'selected' if asset.status == 'نشط' else '' }}>نشط</option>
                                        <option value="صيانة" {{ 'selected' if asset.status == 'صيانة' else '' }}>صيانة</option>
                                        <option value="متوقف" {{ 'selected' if asset.status == 'متوقف' else '' }}>متوقف</option>
                                        <option value="مستبعد" {{ 'selected' if asset.status == 'مستبعد' else '' }}>مستبعد</option>
                                    </select>
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">مخصص للموظف</label>
                                    <select class="form-control" name="assigned_to">
                                        <option value="">غير مخصص</option>
                                        {% for employee in employees %}
                                        <option value="{{ employee.id }}" {{ 'selected' if asset.assigned_to == employee.id else '' }}>{{ employee.name }} ({{ employee.emp_id }})</option>
                                        {% endfor %}
                                    </select>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">الموقع</label>
                                    <input type="text" class="form-control" name="location" value="{{ asset.location or '' }}">
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">تاريخ الشراء</label>
                                    <input type="date" class="form-control" name="purchase_date" value="{{ asset.purchase_date or '' }}">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">تاريخ انتهاء الضمان</label>
                                    <input type="date" class="form-control" name="warranty_date" value="{{ asset.warranty_date or '' }}">
                                </div>
                            </div>
                            
                            <div class="d-flex justify-content-between">
                                <button type="submit" class="btn btn-primary btn-lg">
                                    <i class="fas fa-save me-2"></i>حفظ التعديلات
                                </button>
                                <a href="/assets" class="btn btn-outline-secondary">
                                    <i class="fas fa-arrow-right me-2"></i>العودة للأصول
                                </a>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
'''

EDIT_EMPLOYEE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>تعديل الموظف</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; font-family: 'Cairo', sans-serif; }
        .navbar-custom { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .card { border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 15px; }
        .form-control { border-radius: 10px; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; border-radius: 10px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/">🚀 نظام إدارة الأصول</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="/">الرئيسية</a>
                <a class="nav-link text-white" href="/assets">الأصول</a>
                <a class="nav-link text-white active" href="/employees">👥 الموظفين</a>
                <a class="nav-link text-white" href="/departments">🏢 الإدارات</a>
                <a class="nav-link text-white" href="/custody">📋 العهد</a>
                <a class="nav-link text-white" href="/support">🎧 الدعم الفني</a>
                <a class="nav-link text-white" href="/reports">📊 التقارير</a>
                <a class="nav-link text-white" href="/logout">خروج</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row justify-content-center">
            <div class="col-lg-8">
                <div class="card">
                    <div class="card-header bg-transparent text-center">
                        <h2><i class="fas fa-user-edit text-primary"></i> تعديل الموظف: {{ employee.name }}</h2>
                    </div>
                    <div class="card-body">
                        {% if error %}
                            <div class="alert alert-danger">
                                <i class="fas fa-exclamation-triangle me-2"></i>{{ error }}
                            </div>
                        {% endif %}
                        
                        <form method="POST">
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">رقم الموظف *</label>
                                    <input type="text" class="form-control" name="emp_id" value="{{ employee.emp_id }}" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">الاسم الكامل *</label>
                                    <input type="text" class="form-control" name="name" value="{{ employee.name }}" required>
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">رقم الهوية *</label>
                                    <input type="text" class="form-control" name="national_id" value="{{ employee.national_id }}" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">رقم الهاتف *</label>
                                    <input type="text" class="form-control" name="phone" value="{{ employee.phone }}" required>
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">البريد الإلكتروني *</label>
                                <input type="email" class="form-control" name="email" value="{{ employee.email }}" required>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">الإدارة *</label>
                                    <select class="form-control" name="department" required>
                                        <option value="">اختر الإدارة</option>
                                        {% for dept in departments %}
                                        <option value="{{ dept.name }}" {{ 'selected' if employee.department == dept.name else '' }}>{{ dept.name }}</option>
                                        {% endfor %}
                                    </select>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">المسمى الوظيفي *</label>
                                    <input type="text" class="form-control" name="position" value="{{ employee.position }}" required>
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">تاريخ التوظيف *</label>
                                    <input type="date" class="form-control" name="hire_date" value="{{ employee.hire_date }}" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">الحالة *</label>
                                    <select class="form-control" name="status" required>
                                        <option value="">اختر الحالة</option>
                                        <option value="نشط" {{ 'selected' if employee.status == 'نشط' else '' }}>نشط</option>
                                        <option value="إجازة" {{ 'selected' if employee.status == 'إجازة' else '' }}>إجازة</option>
                                        <option value="متوقف" {{ 'selected' if employee.status == 'متوقف' else '' }}>متوقف</option>
                                    </select>
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">المدير المباشر</label>
                                    <select class="form-control" name="manager_id">
                                        <option value="">لا يوجد</option>
                                        {% for manager in managers %}
                                        <option value="{{ manager.id }}" {{ 'selected' if employee.manager_id == manager.id else '' }}>{{ manager.name }}</option>
                                        {% endfor %}
                                    </select>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">موقع المكتب</label>
                                    <input type="text" class="form-control" name="office_location" value="{{ employee.office_location or '' }}">
                                </div>
                            </div>
                            
                            <div class="d-flex justify-content-between">
                                <button type="submit" class="btn btn-primary btn-lg">
                                    <i class="fas fa-save me-2"></i>حفظ التعديلات
                                </button>
                                <a href="/employees" class="btn btn-outline-secondary">
                                    <i class="fas fa-arrow-right me-2"></i>العودة للموظفين
                                </a>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
'''

CUSTODY_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>إدارة العهد</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; font-family: 'Cairo', sans-serif; }
        .navbar-custom { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .card { border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 15px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/">🚀 نظام إدارة الأصول</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="/">الرئيسية</a>
                <a class="nav-link text-white" href="/assets">الأصول</a>
                <a class="nav-link text-white" href="/employees">👥 الموظفين</a>
                <a class="nav-link text-white" href="/departments">🏢 الإدارات</a>
                <a class="nav-link text-white active" href="/custody">📋 العهد</a>
                <a class="nav-link text-white" href="/support">🎧 الدعم الفني</a>
                <a class="nav-link text-white" href="/reports">📊 التقارير</a>
                <a class="nav-link text-white" href="/logout">خروج</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="fas fa-clipboard-list text-primary"></i> إدارة العهد</h2>
            <a href="/create_custody" class="btn btn-primary">
                <i class="fas fa-plus"></i> إنشاء عهدة جديدة
            </a>
        </div>

        <div class="card">
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead class="table-dark">
                            <tr>
                                <th>رقم الوثيقة</th>
                                <th>الأصل</th>
                                <th>الموظف</th>
                                <th>تاريخ العهدة</th>
                                <th>الحالة</th>
                                <th>الشاهد</th>
                                <th>حالة الاستلام</th>
                                <th>الإجراءات</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for custody in custody_records %}
                            <tr>
                                <td><strong>{{ custody.custody_document }}</strong></td>
                                <td>{{ custody.tag }} - {{ custody.asset_name }}</td>
                                <td>{{ custody.employee_name }} ({{ custody.emp_id }})</td>
                                <td>{{ custody.custody_date }}</td>
                                <td>
                                    <span class="badge bg-{{ 'success' if custody.status == 'نشط' else 'warning' if custody.status == 'صيانة' else 'secondary' }}">
                                        {{ custody.status }}
                                    </span>
                                </td>
                                <td>{{ custody.witness_name or 'غير محدد' }}</td>
                                <td>
                                    <span class="badge bg-{{ 'success' if custody.condition_received == 'ممتاز' else 'info' if custody.condition_received == 'جيد جداً' else 'warning' }}">
                                        {{ custody.condition_received }}
                                    </span>
                                </td>
                                <td>
                                    <button class="btn btn-sm btn-outline-primary" onclick="viewCustody({{ custody.id }})">
                                        <i class="fas fa-eye"></i>
                                    </button>
                                    {% if custody.status == 'نشط' %}
                                    <button class="btn btn-sm btn-outline-warning" onclick="returnAsset({{ custody.id }})">
                                        <i class="fas fa-undo"></i> إرجاع
                                    </button>
                                    {% endif %}
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script>
        function viewCustody(custodyId) {
            alert(`عرض تفاصيل العهدة رقم: ${custodyId}`);
        }
        
        function returnAsset(custodyId) {
            if (confirm('هل تريد تسجيل إرجاع هذا الأصل؟')) {
                window.location.href = `/return_asset/${custodyId}`;
            }
        }
    </script>
</body>
</html>
'''

CREATE_CUSTODY_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>إنشاء عهدة جديدة</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; font-family: 'Cairo', sans-serif; }
        .navbar-custom { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .card { border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 15px; }
        .form-control { border-radius: 10px; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; border-radius: 10px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/">🚀 نظام إدارة الأصول</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="/">الرئيسية</a>
                <a class="nav-link text-white" href="/assets">الأصول</a>
                <a class="nav-link text-white" href="/employees">👥 الموظفين</a>
                <a class="nav-link text-white" href="/departments">🏢 الإدارات</a>
                <a class="nav-link text-white active" href="/custody">📋 العهد</a>
                <a class="nav-link text-white" href="/support">🎧 الدعم الفني</a>
                <a class="nav-link text-white" href="/reports">📊 التقارير</a>
                <a class="nav-link text-white" href="/logout">خروج</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row justify-content-center">
            <div class="col-lg-8">
                <div class="card">
                    <div class="card-header bg-transparent text-center">
                        <h2><i class="fas fa-clipboard-list text-primary"></i> إنشاء عهدة جديدة</h2>
                    </div>
                    <div class="card-body">
                        {% if success %}
                            <div class="alert alert-success">
                                <i class="fas fa-check-circle me-2"></i>{{ success }}
                                <div class="mt-2">
                                    <a href="/custody" class="btn btn-success btn-sm me-2">عرض العهد</a>
                                    <a href="/create_custody" class="btn btn-outline-success btn-sm">إنشاء عهدة أخرى</a>
                                </div>
                            </div>
                        {% endif %}
                        
                        {% if error %}
                            <div class="alert alert-danger">
                                <i class="fas fa-exclamation-triangle me-2"></i>{{ error }}
                            </div>
                        {% endif %}
                        
                        <form method="POST">
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">الأصل *</label>
                                    <select class="form-control" name="asset_id" required>
                                        <option value="">اختر الأصل</option>
                                        {% for asset in assets %}
                                        <option value="{{ asset.id }}">{{ asset.tag }} - {{ asset.name }}</option>
                                        {% endfor %}
                                    </select>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">الموظف *</label>
                                    <select class="form-control" name="employee_id" required>
                                        <option value="">اختر الموظف</option>
                                        {% for employee in employees %}
                                        <option value="{{ employee.id }}">{{ employee.name }} ({{ employee.emp_id }})</option>
                                        {% endfor %}
                                    </select>
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">تاريخ العهدة *</label>
                                    <input type="date" class="form-control" name="custody_date" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">الشاهد</label>
                                    <select class="form-control" name="witness_id">
                                        <option value="">لا يوجد</option>
                                        {% for witness in witnesses %}
                                        <option value="{{ witness.id }}">{{ witness.name }}</option>
                                        {% endfor %}
                                    </select>
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">حالة الأصل عند الاستلام *</label>
                                <select class="form-control" name="condition_received" required>
                                    <option value="">اختر الحالة</option>
                                    <option value="ممتاز">ممتاز</option>
                                    <option value="جيد جداً">جيد جداً</option>
                                    <option value="جيد">جيد</option>
                                    <option value="مقبول">مقبول</option>
                                    <option value="يحتاج صيانة">يحتاج صيانة</option>
                                </select>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">ملاحظات</label>
                                <textarea class="form-control" name="notes" rows="3" placeholder="أي ملاحظات إضافية..."></textarea>
                            </div>
                            
                            <div class="d-flex justify-content-between">
                                <button type="submit" class="btn btn-primary btn-lg">
                                    <i class="fas fa-save me-2"></i>إنشاء العهدة
                                </button>
                                <a href="/custody" class="btn btn-outline-secondary">
                                    <i class="fas fa-arrow-right me-2"></i>العودة للعهد
                                </a>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // تعيين التاريخ الحالي كافتراضي
        document.querySelector('input[name="custody_date"]').value = new Date().toISOString().split('T')[0];
    </script>
</body>
</html>
'''

PURCHASES_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>إدارة المشتريات</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; font-family: 'Cairo', sans-serif; }
        .navbar-custom { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .card { border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 15px; }
        .stats-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/">🚀 نظام إدارة الأصول</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link text-white" href="/">🏠 الرئيسية</a></li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle text-white" href="#" role="button" data-bs-toggle="dropdown">💼 الأصول</a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="/assets">📋 عرض الأصول</a></li>
                            <li><a class="dropdown-item" href="/add_asset">➕ إضافة أصل</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="/custody">📋 إدارة العهد</a></li>
                        </ul>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle text-white" href="#" role="button" data-bs-toggle="dropdown">👥 الموظفين</a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="/employees">👥 عرض الموظفين</a></li>
                            <li><a class="dropdown-item" href="/add_employee">➕ إضافة موظف</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="/departments">🏢 الإدارات</a></li>
                        </ul>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle text-white active" href="#" role="button" data-bs-toggle="dropdown">💰 المشتريات</a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="/purchases">🛒 عرض المشتريات</a></li>
                            <li><a class="dropdown-item" href="/add_purchase">➕ إضافة مشترى</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="/invoices">🧾 الفواتير</a></li>
                            <li><a class="dropdown-item" href="/licenses">🔑 التراخيص</a></li>
                        </ul>
                    </li>
                    <li class="nav-item"><a class="nav-link text-white" href="/support">🎧 الدعم الفني</a></li>
                    <li class="nav-item"><a class="nav-link text-white" href="/reports">📊 التقارير</a></li>
                    <li class="nav-item"><a class="nav-link text-white" href="/logout">🚪 خروج</a></li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="fas fa-shopping-cart text-primary"></i> إدارة المشتريات</h2>
            <div>
                <a href="/add_purchase" class="btn btn-primary me-2">
                    <i class="fas fa-plus"></i> إضافة مشترى جديد
                </a>
                <a href="/invoices" class="btn btn-success me-2">
                    <i class="fas fa-file-invoice"></i> الفواتير
                </a>
                <a href="/licenses" class="btn btn-warning">
                    <i class="fas fa-key"></i> التراخيص
                </a>
            </div>
        </div>

        <!-- إحصائيات المشتريات -->
        <div class="row mb-4">
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="stats-card p-4 text-center">
                    <i class="fas fa-shopping-bag fa-3x mb-3"></i>
                    <h3>{{ total_purchases }}</h3>
                    <p class="mb-0">إجمالي المشتريات</p>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="stats-card p-4 text-center">
                    <i class="fas fa-dollar-sign fa-3x mb-3"></i>
                    <h3>{{ "{:,.0f}".format(total_amount) }}</h3>
                    <p class="mb-0">إجمالي القيمة (ريال)</p>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="stats-card p-4 text-center">
                    <i class="fas fa-clock fa-3x mb-3"></i>
                    <h3>{{ pending_purchases }}</h3>
                    <p class="mb-0">قيد التوريد</p>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="stats-card p-4 text-center">
                    <i class="fas fa-chart-line fa-3x mb-3"></i>
                    <h3>{{ "{:,.0f}".format(total_amount / total_purchases if total_purchases > 0 else 0) }}</h3>
                    <p class="mb-0">متوسط قيمة المشترى</p>
                </div>
            </div>
        </div>

        <!-- جدول المشتريات -->
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">قائمة المشتريات</h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead class="table-dark">
                            <tr>
                                <th>رقم المشترى</th>
                                <th>المورد</th>
                                <th>الصنف</th>
                                <th>الفئة</th>
                                <th>الكمية</th>
                                <th>القيمة الإجمالية</th>
                                <th>الحالة</th>
                                <th>تاريخ التوريد</th>
                                <th>الإجراءات</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for purchase in purchases %}
                            <tr>
                                <td><strong>{{ purchase.purchase_number }}</strong></td>
                                <td>{{ purchase.supplier_name }}</td>
                                <td>{{ purchase.item_name }}</td>
                                <td><span class="badge bg-secondary">{{ purchase.category }}</span></td>
                                <td>{{ purchase.quantity }}</td>
                                <td>{{ "{:,.2f}".format(purchase.total_amount) }} {{ purchase.currency }}</td>
                                <td>
                                    <span class="badge bg-{{ 'success' if purchase.status == 'مكتمل' else 'warning' if purchase.status == 'قيد التوريد' else 'secondary' }}">
                                        {{ purchase.status }}
                                    </span>
                                </td>
                                <td>{{ purchase.delivery_date }}</td>
                                <td>
                                    <button class="btn btn-sm btn-outline-primary" onclick="viewPurchase('{{ purchase.purchase_number }}')">
                                        <i class="fas fa-eye"></i>
                                    </button>
                                    <button class="btn btn-sm btn-outline-success" onclick="createInvoice({{ purchase.id }})">
                                        <i class="fas fa-file-invoice"></i>
                                    </button>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function viewPurchase(purchaseNumber) {
            alert(`عرض تفاصيل المشترى: ${purchaseNumber}`);
        }
        
        function createInvoice(purchaseId) {
            if (confirm('إنشاء فاتورة لهذا المشترى؟')) {
                window.location.href = `/create_invoice?purchase_id=${purchaseId}`;
            }
        }
    </script>
</body>
</html>
'''

# تشغيل التطبيق
if __name__ == '__main__':
    print("=" * 70)
    print("🚀 نظام إدارة الأصول البسيط مع التقارير")
    print("   Simple Asset Management System with Reports")
    print("=" * 70)
    
    # إنشاء قاعدة البيانات والبيانات التجريبية
    print("📊 إنشاء قاعدة البيانات...")
    create_database()
    print("✅ تم إنشاء قاعدة البيانات مع 10 أصول")
    
    # إنشاء التطبيق
    print("🔧 إنشاء التطبيق...")
    app = create_app()
    print("✅ النظام جاهز!")
    
    print("🌐 الرابط: http://localhost:5000")
    print("👤 المستخدم: admin")
    print("🔑 كلمة المرور: admin123")
    print("📊 التقارير: اضغط على 'التقارير' في القائمة")
    print("🔧 للإيقاف: اضغط Ctrl+C")
    print("=" * 70)
    
    # تشغيل الخادم
    app.run(debug=False, host='0.0.0.0', port=5000)