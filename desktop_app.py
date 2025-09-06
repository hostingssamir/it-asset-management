#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نسخة ديسك توب لنظام إدارة الأصول التقنية
Desktop Version - IT Asset Management System
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import sqlite3
import os
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
import webbrowser
import threading
import subprocess
import sys

class ITAssetManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("نظام إدارة الأصول التقنية - IT Asset Management")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # متغيرات النظام
        self.db_path = 'it_assets_desktop.db'
        self.current_user = None
        self.web_server_process = None
        
        # إنشاء قاعدة البيانات
        self.create_database()
        
        # إنشاء الواجهة
        self.create_widgets()
        
        # عرض شاشة تسجيل الدخول
        self.show_login()
    
    def create_database(self):
        """إنشاء قاعدة البيانات"""
        if os.path.exists(self.db_path):
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # جدول المستخدمين
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(80) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(100) NOT NULL,
                role VARCHAR(20) DEFAULT 'user',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول الفئات
        cursor.execute('''
            CREATE TABLE categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول الأصول
        cursor.execute('''
            CREATE TABLE assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_tag VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                category_id INTEGER,
                brand VARCHAR(100),
                model VARCHAR(100),
                serial_number VARCHAR(100),
                purchase_date DATE,
                purchase_cost DECIMAL(10,2),
                warranty_expiry DATE,
                status VARCHAR(20) DEFAULT 'active',
                condition VARCHAR(20) DEFAULT 'good',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        ''')
        
        # جدول الصيانة
        cursor.execute('''
            CREATE TABLE maintenance_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_id INTEGER NOT NULL,
                maintenance_type VARCHAR(20) NOT NULL,
                description TEXT NOT NULL,
                maintenance_date TIMESTAMP,
                technician VARCHAR(100),
                cost DECIMAL(10,2),
                status VARCHAR(20) DEFAULT 'scheduled',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (asset_id) REFERENCES assets (id)
            )
        ''')
        
        # إدراج البيانات الافتراضية
        admin_password = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, full_name, role)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', 'admin@company.com', admin_password, 'مدير النظام', 'admin'))
        
        # الفئات الافتراضية
        categories = [
            ('أجهزة الكمبيوتر', 'أجهزة الكمبيوتر المكتبية والمحمولة'),
            ('الخوادم', 'خوادم الشبكة وقواعد البيانات'),
            ('معدات الشبكة', 'أجهزة التوجيه والتبديل'),
            ('الطابعات', 'أجهزة الطباعة والمسح'),
            ('الهواتف', 'الهواتف الثابتة والذكية')
        ]
        
        for name, desc in categories:
            cursor.execute('INSERT INTO categories (name, description) VALUES (?, ?)', (name, desc))
        
        conn.commit()
        conn.close()
    
    def create_widgets(self):
        """إنشاء عناصر الواجهة"""
        # إطار رئيسي
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # شريط القوائم
        self.create_menu()
        
        # شريط الأدوات
        self.create_toolbar()
        
        # المحتوى الرئيسي
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # شريط الحالة
        self.status_bar = ttk.Label(self.root, text="جاهز", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_menu(self):
        """إنشاء شريط القوائم"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # قائمة الملف
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ملف", menu=file_menu)
        file_menu.add_command(label="نسخة احتياطية", command=self.backup_database)
        file_menu.add_command(label="استعادة", command=self.restore_database)
        file_menu.add_separator()
        file_menu.add_command(label="خروج", command=self.root.quit)
        
        # قائمة الأصول
        assets_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="الأصول", menu=assets_menu)
        assets_menu.add_command(label="عرض الأصول", command=self.show_assets)
        assets_menu.add_command(label="إضافة أصل", command=self.add_asset)
        assets_menu.add_command(label="البحث", command=self.search_assets)
        
        # قائمة الصيانة
        maintenance_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="الصيانة", menu=maintenance_menu)
        maintenance_menu.add_command(label="سجل الصيانة", command=self.show_maintenance)
        maintenance_menu.add_command(label="إضافة صيانة", command=self.add_maintenance)
        
        # قائمة التقارير
        reports_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="التقارير", menu=reports_menu)
        reports_menu.add_command(label="تقرير الأصول", command=self.assets_report)
        reports_menu.add_command(label="تقرير الصيانة", command=self.maintenance_report)
        
        # قائمة الويب
        web_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="الويب", menu=web_menu)
        web_menu.add_command(label="تشغيل الخادم", command=self.start_web_server)
        web_menu.add_command(label="إيقاف الخادم", command=self.stop_web_server)
        web_menu.add_command(label="فتح في المتصفح", command=self.open_in_browser)
        
        # قائمة المساعدة
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="مساعدة", menu=help_menu)
        help_menu.add_command(label="حول البرنامج", command=self.show_about)
        help_menu.add_command(label="دليل المستخدم", command=self.show_help)
    
    def create_toolbar(self):
        """إنشاء شريط الأدوات"""
        toolbar = ttk.Frame(self.main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        # أزرار سريعة
        ttk.Button(toolbar, text="🏠 الرئيسية", command=self.show_dashboard).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="💻 الأصول", command=self.show_assets).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🔧 الصيانة", command=self.show_maintenance).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="📊 التقارير", command=self.assets_report).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🌐 الويب", command=self.start_web_server).pack(side=tk.LEFT, padx=2)
        
        # معلومات المستخدم
        user_frame = ttk.Frame(toolbar)
        user_frame.pack(side=tk.RIGHT)
        
        if self.current_user:
            ttk.Label(user_frame, text=f"مرحباً {self.current_user['full_name']}").pack(side=tk.RIGHT, padx=10)
            ttk.Button(user_frame, text="تسجيل خروج", command=self.logout).pack(side=tk.RIGHT, padx=2)
    
    def show_login(self):
        """عرض شاشة تسجيل الدخول"""
        # مسح المحتوى
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # إطار تسجيل الدخول
        login_frame = ttk.LabelFrame(self.content_frame, text="تسجيل الدخول", padding=20)
        login_frame.pack(expand=True)
        
        # حقول الإدخال
        ttk.Label(login_frame, text="اسم المستخدم:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(login_frame, width=30)
        self.username_entry.grid(row=0, column=1, pady=5, padx=10)
        self.username_entry.insert(0, "admin")  # قيمة افتراضية
        
        ttk.Label(login_frame, text="كلمة المرور:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(login_frame, width=30, show="*")
        self.password_entry.grid(row=1, column=1, pady=5, padx=10)
        self.password_entry.insert(0, "admin123")  # قيمة افتراضية
        
        # زر تسجيل الدخول
        ttk.Button(login_frame, text="تسجيل الدخول", command=self.login).grid(row=2, column=0, columnspan=2, pady=20)
        
        # ربط Enter بتسجيل الدخول
        self.password_entry.bind('<Return>', lambda e: self.login())
        
        # تركيز على حقل اسم المستخدم
        self.username_entry.focus()
    
    def login(self):
        """تسجيل الدخول"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("خطأ", "يرجى إدخال اسم المستخدم وكلمة المرور")
            return
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            self.current_user = dict(user)
            self.show_dashboard()
            self.update_status(f"تم تسجيل الدخول بنجاح - مرحباً {user['full_name']}")
        else:
            messagebox.showerror("خطأ", "اسم المستخدم أو كلمة المرور غير صحيحة")
    
    def logout(self):
        """تسجيل الخروج"""
        self.current_user = None
        self.show_login()
        self.update_status("تم تسجيل الخروج")
    
    def show_dashboard(self):
        """عرض لوحة التحكم"""
        if not self.current_user:
            self.show_login()
            return
        
        # مسح المحتوى
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # عنوان
        title_label = ttk.Label(self.content_frame, text="لوحة التحكم الرئيسية", font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # إحصائيات
        stats_frame = ttk.LabelFrame(self.content_frame, text="الإحصائيات", padding=10)
        stats_frame.pack(fill=tk.X, pady=10)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # حساب الإحصائيات
        total_assets = cursor.execute('SELECT COUNT(*) FROM assets').fetchone()[0]
        active_assets = cursor.execute('SELECT COUNT(*) FROM assets WHERE status = "active"').fetchone()[0]
        maintenance_assets = cursor.execute('SELECT COUNT(*) FROM assets WHERE status = "maintenance"').fetchone()[0]
        total_maintenance = cursor.execute('SELECT COUNT(*) FROM maintenance_records').fetchone()[0]
        
        conn.close()
        
        # عرض الإحصائيات
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack()
        
        ttk.Label(stats_grid, text=f"إجمالي الأصول: {total_assets}", font=('Arial', 12)).grid(row=0, column=0, padx=20, pady=5)
        ttk.Label(stats_grid, text=f"أصول نشطة: {active_assets}", font=('Arial', 12)).grid(row=0, column=1, padx=20, pady=5)
        ttk.Label(stats_grid, text=f"قيد الصيانة: {maintenance_assets}", font=('Arial', 12)).grid(row=1, column=0, padx=20, pady=5)
        ttk.Label(stats_grid, text=f"عمليات الصيانة: {total_maintenance}", font=('Arial', 12)).grid(row=1, column=1, padx=20, pady=5)
        
        # الإجراءات السريعة
        actions_frame = ttk.LabelFrame(self.content_frame, text="الإجراءات السريعة", padding=10)
        actions_frame.pack(fill=tk.X, pady=10)
        
        actions_grid = ttk.Frame(actions_frame)
        actions_grid.pack()
        
        ttk.Button(actions_grid, text="➕ إضافة أصل جديد", command=self.add_asset).grid(row=0, column=0, padx=10, pady=5, sticky=tk.EW)
        ttk.Button(actions_grid, text="🔍 البحث في الأصول", command=self.search_assets).grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)
        ttk.Button(actions_grid, text="🔧 إضافة صيانة", command=self.add_maintenance).grid(row=1, column=0, padx=10, pady=5, sticky=tk.EW)
        ttk.Button(actions_grid, text="📊 إنشاء تقرير", command=self.assets_report).grid(row=1, column=1, padx=10, pady=5, sticky=tk.EW)
        
        # تحديث شريط الأدوات
        self.create_toolbar()
    
    def show_assets(self):
        """عرض قائمة الأصول"""
        if not self.current_user:
            self.show_login()
            return
        
        # مسح المحتوى
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # عنوان
        title_label = ttk.Label(self.content_frame, text="قائمة الأصول", font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # أزرار الإجراءات
        buttons_frame = ttk.Frame(self.content_frame)
        buttons_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(buttons_frame, text="➕ إضافة أصل", command=self.add_asset).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="🔄 تحديث", command=self.show_assets).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="🔍 بحث", command=self.search_assets).pack(side=tk.LEFT, padx=5)
        
        # جدول الأصول
        columns = ('ID', 'رقم الأصل', 'الاسم', 'الفئة', 'الحالة', 'تاريخ الإضافة')
        self.assets_tree = ttk.Treeview(self.content_frame, columns=columns, show='headings', height=15)
        
        # تعريف الأعمدة
        for col in columns:
            self.assets_tree.heading(col, text=col)
            self.assets_tree.column(col, width=150)
        
        # شريط التمرير
        scrollbar = ttk.Scrollbar(self.content_frame, orient=tk.VERTICAL, command=self.assets_tree.yview)
        self.assets_tree.configure(yscrollcommand=scrollbar.set)
        
        # تخطيط الجدول
        self.assets_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # تحميل البيانات
        self.load_assets_data()
        
        # ربط النقر المزدوج
        self.assets_tree.bind('<Double-1>', self.edit_selected_asset)
    
    def load_assets_data(self):
        """تحميل بيانات الأصول"""
        # مسح البيانات الحالية
        for item in self.assets_tree.get_children():
            self.assets_tree.delete(item)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT a.id, a.asset_tag, a.name, c.name as category_name, a.status, a.created_at
            FROM assets a
            LEFT JOIN categories c ON a.category_id = c.id
            ORDER BY a.created_at DESC
        ''')
        
        assets = cursor.fetchall()
        conn.close()
        
        # إضافة البيانات للجدول
        for asset in assets:
            # تنسيق التاريخ
            created_date = asset[5][:10] if asset[5] else 'غير محدد'
            
            # تنسيق الحالة
            status_text = {
                'active': 'نشط',
                'maintenance': 'صيانة',
                'retired': 'متقاعد',
                'lost': 'مفقود'
            }.get(asset[4], asset[4])
            
            self.assets_tree.insert('', tk.END, values=(
                asset[0],  # ID
                asset[1],  # رقم الأصل
                asset[2],  # الاسم
                asset[3] or 'غير محدد',  # الفئة
                status_text,  # الحالة
                created_date  # تاريخ الإضافة
            ))
        
        self.update_status(f"تم تحميل {len(assets)} أصل")
    
    def add_asset(self):
        """إضافة أصل جديد"""
        if not self.current_user:
            self.show_login()
            return
        
        # نافذة إضافة أصل
        add_window = tk.Toplevel(self.root)
        add_window.title("إضافة أصل جديد")
        add_window.geometry("500x600")
        add_window.resizable(False, False)
        
        # جعل النافذة في المقدمة
        add_window.transient(self.root)
        add_window.grab_set()
        
        # إطار النموذج
        form_frame = ttk.Frame(add_window, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # حقول الإدخال
        fields = {}
        
        # رقم الأصل
        ttk.Label(form_frame, text="رقم الأصل *:").grid(row=0, column=0, sticky=tk.W, pady=5)
        fields['asset_tag'] = ttk.Entry(form_frame, width=30)
        fields['asset_tag'].grid(row=0, column=1, pady=5, padx=10, sticky=tk.EW)
        
        # اسم الأصل
        ttk.Label(form_frame, text="اسم الأصل *:").grid(row=1, column=0, sticky=tk.W, pady=5)
        fields['name'] = ttk.Entry(form_frame, width=30)
        fields['name'].grid(row=1, column=1, pady=5, padx=10, sticky=tk.EW)
        
        # الوصف
        ttk.Label(form_frame, text="الوصف:").grid(row=2, column=0, sticky=tk.W, pady=5)
        fields['description'] = tk.Text(form_frame, width=30, height=3)
        fields['description'].grid(row=2, column=1, pady=5, padx=10, sticky=tk.EW)
        
        # الفئة
        ttk.Label(form_frame, text="الفئة:").grid(row=3, column=0, sticky=tk.W, pady=5)
        fields['category'] = ttk.Combobox(form_frame, width=27)
        fields['category'].grid(row=3, column=1, pady=5, padx=10, sticky=tk.EW)
        
        # تحميل الفئات
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM categories ORDER BY name')
        categories = cursor.fetchall()
        conn.close()
        
        category_values = [f"{cat[1]} ({cat[0]})" for cat in categories]
        fields['category']['values'] = category_values
        
        # العلامة التجارية
        ttk.Label(form_frame, text="العلامة التجارية:").grid(row=4, column=0, sticky=tk.W, pady=5)
        fields['brand'] = ttk.Entry(form_frame, width=30)
        fields['brand'].grid(row=4, column=1, pady=5, padx=10, sticky=tk.EW)
        
        # الموديل
        ttk.Label(form_frame, text="الموديل:").grid(row=5, column=0, sticky=tk.W, pady=5)
        fields['model'] = ttk.Entry(form_frame, width=30)
        fields['model'].grid(row=5, column=1, pady=5, padx=10, sticky=tk.EW)
        
        # الرقم التسلسلي
        ttk.Label(form_frame, text="الرقم التسلسلي:").grid(row=6, column=0, sticky=tk.W, pady=5)
        fields['serial_number'] = ttk.Entry(form_frame, width=30)
        fields['serial_number'].grid(row=6, column=1, pady=5, padx=10, sticky=tk.EW)
        
        # تكلفة الشراء
        ttk.Label(form_frame, text="تكلفة الشراء:").grid(row=7, column=0, sticky=tk.W, pady=5)
        fields['purchase_cost'] = ttk.Entry(form_frame, width=30)
        fields['purchase_cost'].grid(row=7, column=1, pady=5, padx=10, sticky=tk.EW)
        
        # الحالة
        ttk.Label(form_frame, text="الحالة:").grid(row=8, column=0, sticky=tk.W, pady=5)
        fields['status'] = ttk.Combobox(form_frame, width=27, values=['active', 'maintenance', 'retired', 'lost'])
        fields['status'].grid(row=8, column=1, pady=5, padx=10, sticky=tk.EW)
        fields['status'].set('active')
        
        # الحالة الفنية
        ttk.Label(form_frame, text="الحالة الفنية:").grid(row=9, column=0, sticky=tk.W, pady=5)
        fields['condition'] = ttk.Combobox(form_frame, width=27, values=['excellent', 'good', 'fair', 'poor'])
        fields['condition'].grid(row=9, column=1, pady=5, padx=10, sticky=tk.EW)
        fields['condition'].set('good')
        
        # ملاحظات
        ttk.Label(form_frame, text="ملاحظات:").grid(row=10, column=0, sticky=tk.W, pady=5)
        fields['notes'] = tk.Text(form_frame, width=30, height=3)
        fields['notes'].grid(row=10, column=1, pady=5, padx=10, sticky=tk.EW)
        
        # أزرار الحفظ والإلغاء
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.grid(row=11, column=0, columnspan=2, pady=20)
        
        def save_asset():
            # التحقق من الحقول المطلوبة
            if not fields['asset_tag'].get() or not fields['name'].get():
                messagebox.showerror("خطأ", "يرجى ملء الحقول المطلوبة (رقم الأصل والاسم)")
                return
            
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # استخراج معرف الفئة
                category_id = None
                if fields['category'].get():
                    category_text = fields['category'].get()
                    if '(' in category_text:
                        category_id = int(category_text.split('(')[1].split(')')[0])
                
                # إدراج الأصل
                cursor.execute('''
                    INSERT INTO assets (asset_tag, name, description, category_id, brand, model, 
                                      serial_number, purchase_cost, status, condition, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    fields['asset_tag'].get(),
                    fields['name'].get(),
                    fields['description'].get('1.0', tk.END).strip(),
                    category_id,
                    fields['brand'].get() or None,
                    fields['model'].get() or None,
                    fields['serial_number'].get() or None,
                    float(fields['purchase_cost'].get()) if fields['purchase_cost'].get() else None,
                    fields['status'].get(),
                    fields['condition'].get(),
                    fields['notes'].get('1.0', tk.END).strip()
                ))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("نجح", "تم إضافة الأصل بنجاح")
                add_window.destroy()
                
                # تحديث قائمة الأصول إذا كانت مفتوحة
                if hasattr(self, 'assets_tree'):
                    self.load_assets_data()
                
            except sqlite3.IntegrityError:
                messagebox.showerror("خطأ", "رقم الأصل موجود مسبقاً")
            except ValueError:
                messagebox.showerror("خطأ", "يرجى إدخال قيمة صحيحة للتكلفة")
            except Exception as e:
                messagebox.showerror("خطأ", f"حدث خطأ: {str(e)}")
        
        ttk.Button(buttons_frame, text="حفظ", command=save_asset).pack(side=tk.LEFT, padx=10)
        ttk.Button(buttons_frame, text="إلغاء", command=add_window.destroy).pack(side=tk.LEFT, padx=10)
        
        # تركيز على أول حقل
        fields['asset_tag'].focus()
    
    def edit_selected_asset(self, event):
        """تعديل الأصل المحدد"""
        selection = self.assets_tree.selection()
        if not selection:
            return
        
        item = self.assets_tree.item(selection[0])
        asset_id = item['values'][0]
        
        messagebox.showinfo("تعديل الأصل", f"تعديل الأصل رقم {asset_id} - قيد التطوير")
    
    def search_assets(self):
        """البحث في الأصول"""
        search_term = simpledialog.askstring("البحث", "أدخل كلمة البحث:")
        if not search_term:
            return
        
        messagebox.showinfo("البحث", f"البحث عن: {search_term} - قيد التطوير")
    
    def show_maintenance(self):
        """عرض سجل الصيانة"""
        messagebox.showinfo("الصيانة", "سجل الصيانة - قيد التطوير")
    
    def add_maintenance(self):
        """إضافة صيانة جديدة"""
        messagebox.showinfo("إضافة صيانة", "إضافة صيانة جديدة - قيد التطوير")
    
    def assets_report(self):
        """تقرير الأصول"""
        messagebox.showinfo("التقارير", "تقرير الأصول - قيد التطوير")
    
    def maintenance_report(self):
        """تقرير الصيانة"""
        messagebox.showinfo("التقارير", "تقرير الصيانة - قيد التطوير")
    
    def start_web_server(self):
        """تشغيل خادم الويب"""
        if self.web_server_process and self.web_server_process.poll() is None:
            messagebox.showinfo("الخادم", "الخادم يعمل بالفعل")
            return
        
        try:
            # تشغيل الخادم في عملية منفصلة
            self.web_server_process = subprocess.Popen([
                sys.executable, 'fixed_app.py'
            ], cwd=os.path.dirname(os.path.abspath(__file__)))
            
            self.update_status("تم تشغيل خادم الويب")
            messagebox.showinfo("الخادم", "تم تشغيل خادم الويب على http://localhost:5000")
            
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في تشغيل الخادم: {str(e)}")
    
    def stop_web_server(self):
        """إيقاف خادم الويب"""
        if self.web_server_process and self.web_server_process.poll() is None:
            self.web_server_process.terminate()
            self.update_status("تم إيقاف خادم الويب")
            messagebox.showinfo("الخادم", "تم إيقاف خادم الويب")
        else:
            messagebox.showinfo("الخادم", "الخادم غير مُشغل")
    
    def open_in_browser(self):
        """فتح النظام في المتصفح"""
        webbrowser.open('http://localhost:5000')
    
    def backup_database(self):
        """نسخة احتياطية من قاعدة البيانات"""
        backup_path = filedialog.asksaveasfilename(
            title="حفظ النسخة الاحتياطية",
            defaultextension=".db",
            filetypes=[("قاعدة البيانات", "*.db"), ("جميع الملفات", "*.*")]
        )
        
        if backup_path:
            try:
                import shutil
                shutil.copy2(self.db_path, backup_path)
                messagebox.showinfo("نجح", f"تم إنشاء النسخة الاحتياطية في:\n{backup_path}")
            except Exception as e:
                messagebox.showerror("خطأ", f"فشل في إنشاء النسخة الاحتياطية: {str(e)}")
    
    def restore_database(self):
        """استعادة قاعدة البيانات"""
        backup_path = filedialog.askopenfilename(
            title="اختر النسخة الاحتياطية",
            filetypes=[("قاعدة البيانات", "*.db"), ("جميع الملفات", "*.*")]
        )
        
        if backup_path:
            result = messagebox.askyesno("تأكيد", "هل أنت متأكد من استعادة النسخة الاحتياطية؟\nسيتم استبدال البيانات الحالية.")
            if result:
                try:
                    import shutil
                    shutil.copy2(backup_path, self.db_path)
                    messagebox.showinfo("نجح", "تم استعادة النسخة الاحتياطية بنجاح")
                    # إعادة تحميل البيانات
                    if hasattr(self, 'assets_tree'):
                        self.load_assets_data()
                except Exception as e:
                    messagebox.showerror("خطأ", f"فشل في استعادة النسخة الاحتياطية: {str(e)}")
    
    def show_about(self):
        """حول البرنامج"""
        about_text = """
نظام إدارة الأصول التقنية
IT Asset Management System

الإصدار: 1.0
تاريخ الإصدار: 2025

نظام شامل لإدارة الأصول التقنية باللغة العربية
يتضمن إدارة الأصول والصيانة والتقارير

المطور: فريق التطوير
        """
        messagebox.showinfo("حول البرنامج", about_text)
    
    def show_help(self):
        """دليل المستخدم"""
        help_text = """
دليل الاستخدام السريع:

1. تسجيل الدخول:
   - اسم المستخدم: admin
   - كلمة المرور: admin123

2. إضافة أصل جديد:
   - اضغط على "إضافة أصل" من شريط الأدوات
   - املأ البيانات المطلوبة
   - اضغط "حفظ"

3. عرض الأصول:
   - اضغط على "الأصول" من شريط الأدوات
   - انقر نقراً مزدوجاً على أي أصل للتعديل

4. النسخ الاحتياطي:
   - من قائمة "ملف" اختر "نسخة احتياطية"

5. الخادم الويب:
   - اضغط على "الويب" لتشغيل النسخة الويب
   - افتح http://localhost:5000 في المتصفح
        """
        messagebox.showinfo("دليل المستخدم", help_text)
    
    def update_status(self, message):
        """تحديث شريط الحالة"""
        self.status_bar.config(text=f"{message} - {datetime.now().strftime('%H:%M:%S')}")
    
    def run(self):
        """تشغيل التطبيق"""
        # إعداد إغلاق التطبيق
        def on_closing():
            if self.web_server_process and self.web_server_process.poll() is None:
                result = messagebox.askyesno("إغلاق", "خادم الويب يعمل. هل تريد إيقافه وإغلاق التطبيق؟")
                if result:
                    self.web_server_process.terminate()
                    self.root.destroy()
            else:
                self.root.destroy()
        
        self.root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # تشغيل الحلقة الرئيسية
        self.root.mainloop()

def main():
    """الدالة الرئيسية"""
    print("🚀 تشغيل نسخة ديسك توب لنظام إدارة الأصول التقنية")
    print("   Desktop Version - IT Asset Management System")
    print("=" * 60)
    
    try:
        app = ITAssetManager()
        app.run()
    except Exception as e:
        print(f"❌ خطأ في تشغيل التطبيق: {e}")
        messagebox.showerror("خطأ", f"فشل في تشغيل التطبيق:\n{str(e)}")

if __name__ == '__main__':
    main()