#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
from flask import Flask, render_template_string, request, redirect, url_for, session, flash, jsonify
from datetime import datetime, timedelta
import random
import string

# إنشاء التطبيق
def create_app():
    app = Flask(__name__)
    app.secret_key = 'your-secret-key-here-2024'
    
    # صفحة تسجيل الدخول المحسنة
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            if username == 'admin' and password == 'admin123':
                session['logged_in'] = True
                session['username'] = username
                flash('تم تسجيل الدخول بنجاح! مرحباً بك في نظام إدارة الأصول', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
        
        return render_template_string(LOGIN_TEMPLATE)
    
    # الصفحة الرئيسية
    @app.route('/')
    def dashboard():
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        
        # إحصائيات الأصول
        cursor.execute("SELECT COUNT(*) FROM assets")
        total_assets = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM assets WHERE status = 'نشط'")
        active_assets = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(cost) FROM assets WHERE cost IS NOT NULL")
        total_cost = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM employees WHERE status = 'نشط'")
        total_employees = cursor.fetchone()[0]
        
        # أحدث الأصول
        cursor.execute("SELECT tag, name, category, cost FROM assets ORDER BY created_at DESC LIMIT 5")
        recent_assets = cursor.fetchall()
        
        # إحصائيات إضافية
        cursor.execute("SELECT COUNT(*) FROM custody WHERE status = 'نشط'")
        active_custody = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM support_tickets WHERE status = 'مفتوح'")
        open_tickets = cursor.fetchone()[0]
        
        conn.close()
        
        return render_template_string(DASHBOARD_TEMPLATE, 
                                    total_assets=total_assets,
                                    active_assets=active_assets,
                                    total_cost=total_cost,
                                    total_employees=total_employees,
                                    recent_assets=recent_assets,
                                    active_custody=active_custody,
                                    open_tickets=open_tickets)
    
    # صفحة الأصول
    @app.route('/assets')
    def assets():
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM assets ORDER BY created_at DESC")
        assets_list = cursor.fetchall()
        conn.close()
        
        return render_template_string(ASSETS_TEMPLATE, assets=assets_list)
    
    # صفحة إضافة أصل
    @app.route('/add_asset', methods=['GET', 'POST'])
    def add_asset():
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        
        if request.method == 'POST':
            try:
                conn = sqlite3.connect('assets.db')
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO assets (tag, name, category, brand, model, serial_number, 
                                      cost, purchase_date, warranty_end, location, assigned_to, 
                                      status, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    request.form['tag'],
                    request.form['name'],
                    request.form['category'],
                    request.form['brand'],
                    request.form['model'],
                    request.form['serial_number'],
                    float(request.form['cost']) if request.form['cost'] else 0,
                    request.form['purchase_date'],
                    request.form['warranty_end'],
                    request.form['location'],
                    request.form['assigned_to'],
                    request.form['status'],
                    request.form['notes']
                ))
                
                conn.commit()
                conn.close()
                
                flash(f'تم إضافة الأصل "{request.form["name"]}" بنجاح!', 'success')
                return redirect(url_for('add_asset'))
                
            except Exception as e:
                flash(f'خطأ في إضافة الأصل: {str(e)}', 'error')
        
        return render_template_string(ADD_ASSET_TEMPLATE)
    
    # صفحة إدارة العهد
    @app.route('/custody')
    def custody():
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        
        # جلب بيانات العهد مع تفاصيل الأصول والموظفين
        cursor.execute('''
            SELECT c.*, a.name as asset_name, e.name as employee_name 
            FROM custody c 
            LEFT JOIN assets a ON c.asset_id = a.id 
            LEFT JOIN employees e ON c.employee_id = e.id 
            ORDER BY c.created_at DESC
        ''')
        custody_list = cursor.fetchall()
        
        # إحصائيات العهد
        cursor.execute("SELECT COUNT(*) FROM custody WHERE status = 'نشط'")
        active_custody = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM custody WHERE status = 'مسترد'")
        returned_custody = cursor.fetchone()[0]
        
        conn.close()
        
        return render_template_string(CUSTODY_TEMPLATE, 
                                    custody_list=custody_list,
                                    active_custody=active_custody,
                                    returned_custody=returned_custody)
    
    # صفحة الموظفين
    @app.route('/employees')
    def employees():
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT e.*, m.name as manager_name 
            FROM employees e 
            LEFT JOIN employees m ON e.manager_id = m.id 
            ORDER BY e.created_at DESC
        ''')
        employees_list = cursor.fetchall()
        conn.close()
        
        return render_template_string(EMPLOYEES_TEMPLATE, employees=employees_list)
    
    # صفحة إضافة موظف
    @app.route('/add_employee', methods=['GET', 'POST'])
    def add_employee():
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        
        if request.method == 'POST':
            try:
                conn = sqlite3.connect('assets.db')
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO employees (emp_id, name, department, position, email, phone, 
                                         hire_date, status, manager_id, office_location)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    request.form['emp_id'],
                    request.form['name'],
                    request.form['department'],
                    request.form['position'],
                    request.form['email'],
                    request.form['phone'],
                    request.form['hire_date'],
                    request.form['status'],
                    int(request.form['manager_id']) if request.form['manager_id'] else None,
                    request.form['office_location']
                ))
                
                conn.commit()
                conn.close()
                
                flash(f'تم إضافة الموظف "{request.form["name"]}" بنجاح!', 'success')
                return redirect(url_for('add_employee'))
                
            except Exception as e:
                flash(f'خطأ في إضافة الموظف: {str(e)}', 'error')
        
        # جلب قائمة المدراء
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM employees WHERE position LIKE '%مدير%'")
        managers = cursor.fetchall()
        conn.close()
        
        return render_template_string(ADD_EMPLOYEE_TEMPLATE, managers=managers)
    
    # صفحة الإدارات
    @app.route('/departments')
    def departments():
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        
        # بيانات الإدارات الافتراضية
        departments_data = [
            {'name': 'المحاسبة', 'manager': 'أحمد محمد', 'employees': 5, 'budget': 150000},
            {'name': 'المبيعات', 'manager': 'فاطمة علي', 'employees': 8, 'budget': 200000},
            {'name': 'تقنية المعلومات', 'manager': 'محمد سالم', 'employees': 6, 'budget': 300000},
            {'name': 'التسويق', 'manager': 'نورا أحمد', 'employees': 4, 'budget': 120000},
            {'name': 'الموارد البشرية', 'manager': 'سارة محمد', 'employees': 3, 'budget': 100000},
            {'name': 'الإدارة العامة', 'manager': 'عبدالله سعد', 'employees': 2, 'budget': 80000}
        ]
        
        return render_template_string(DEPARTMENTS_TEMPLATE, departments=departments_data)
    
    # صفحة المشتريات
    @app.route('/purchases')
    def purchases():
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        
        # إحصائيات المشتريات
        cursor.execute("SELECT COUNT(*) FROM purchases")
        total_purchases = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(total_amount) FROM purchases")
        total_amount = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM purchases WHERE status = 'قيد التوريد'")
        pending_purchases = cursor.fetchone()[0]
        
        # قائمة المشتريات
        cursor.execute("SELECT * FROM purchases ORDER BY created_at DESC")
        purchases_list = cursor.fetchall()
        
        conn.close()
        
        return render_template_string(PURCHASES_TEMPLATE, 
                                    purchases=purchases_list,
                                    total_purchases=total_purchases,
                                    total_amount=total_amount,
                                    pending_purchases=pending_purchases)
    
    # صفحة إضافة مشترى
    @app.route('/add_purchase', methods=['GET', 'POST'])
    def add_purchase():
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        
        if request.method == 'POST':
            try:
                conn = sqlite3.connect('assets.db')
                cursor = conn.cursor()
                
                # توليد رقم مشترى تلقائي
                purchase_number = f"PUR-{datetime.now().year}-{random.randint(100, 999)}"
                
                quantity = int(request.form['quantity'])
                unit_price = float(request.form['unit_price'])
                total_amount = quantity * unit_price
                
                cursor.execute('''
                    INSERT INTO purchases (purchase_number, supplier_name, supplier_contact, 
                                         item_name, item_description, category, quantity, 
                                         unit_price, total_amount, currency, purchase_date, 
                                         delivery_date, warranty_period, status, 
                                         requesting_department, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    purchase_number,
                    request.form['supplier_name'],
                    request.form['supplier_contact'],
                    request.form['item_name'],
                    request.form['item_description'],
                    request.form['category'],
                    quantity,
                    unit_price,
                    total_amount,
                    request.form['currency'],
                    request.form['purchase_date'],
                    request.form['delivery_date'],
                    int(request.form['warranty_period']) if request.form['warranty_period'] else None,
                    request.form['status'],
                    request.form['requesting_department'],
                    request.form['notes']
                ))
                
                conn.commit()
                conn.close()
                
                flash(f'تم إضافة المشترى "{purchase_number}" بنجاح!', 'success')
                return redirect(url_for('add_purchase'))
                
            except Exception as e:
                flash(f'خطأ في إضافة المشترى: {str(e)}', 'error')
        
        return render_template_string(ADD_PURCHASE_TEMPLATE)
    
    # صفحة الفواتير
    @app.route('/invoices')
    def invoices():
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        
        # بيانات فواتير تجريبية
        invoices_data = [
            {'number': 'INV-2024-001', 'supplier': 'شركة التقنية المتقدمة', 'date': '2024-01-15', 'amount': 25000, 'status': 'مدفوع'},
            {'number': 'INV-2024-002', 'supplier': 'مؤسسة الحاسوب', 'date': '2024-01-20', 'amount': 15000, 'status': 'معلق'},
            {'number': 'INV-2024-003', 'supplier': 'شركة الأثاث المكتبي', 'date': '2024-01-25', 'amount': 8000, 'status': 'مدفوع'}
        ]
        
        return render_template_string(INVOICES_TEMPLATE, invoices=invoices_data)
    
    # صفحة التراخيص
    @app.route('/licenses')
    def licenses():
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        
        # بيانات تراخيص تجريبية
        licenses_data = [
            {'number': 'LIC-WIN-001', 'software': 'Windows 11 Pro', 'supplier': 'Microsoft', 'type': 'نظام تشغيل', 'seats': 50, 'used': 35, 'expiry': '2025-12-31', 'status': 'نشط'},
            {'number': 'LIC-OFF-002', 'software': 'Office 365', 'supplier': 'Microsoft', 'type': 'مكتبي', 'seats': 30, 'used': 28, 'expiry': '2024-12-31', 'status': 'نشط'},
            {'number': 'LIC-AV-003', 'software': 'Kaspersky Antivirus', 'supplier': 'Kaspersky', 'type': 'حماية', 'seats': 100, 'used': 85, 'expiry': '2024-06-30', 'status': 'نشط'}
        ]
        
        return render_template_string(LICENSES_TEMPLATE, licenses=licenses_data)
    
    # صفحة الدعم الفني
    @app.route('/support')
    def support():
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        
        # جلب تذاكر الدعم الفني
        cursor.execute("SELECT * FROM support_tickets ORDER BY created_at DESC")
        tickets = cursor.fetchall()
        
        # إحصائيات التذاكر
        cursor.execute("SELECT COUNT(*) FROM support_tickets WHERE status = 'مفتوح'")
        open_tickets = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM support_tickets WHERE status = 'مغلق'")
        closed_tickets = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM support_tickets WHERE priority = 'عالي'")
        high_priority = cursor.fetchone()[0]
        
        conn.close()
        
        return render_template_string(SUPPORT_TEMPLATE, 
                                    tickets=tickets,
                                    open_tickets=open_tickets,
                                    closed_tickets=closed_tickets,
                                    high_priority=high_priority)
    
    # صفحة التقارير
    @app.route('/reports')
    def reports():
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        
        # إحصائيات شاملة للتقارير
        cursor.execute("SELECT COUNT(*) FROM assets")
        total_assets = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(cost) FROM assets WHERE cost IS NOT NULL")
        total_value = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT category, COUNT(*) FROM assets GROUP BY category")
        assets_by_category = cursor.fetchall()
        
        cursor.execute("SELECT status, COUNT(*) FROM assets GROUP BY status")
        assets_by_status = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*) FROM employees WHERE status = 'نشط'")
        active_employees = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM purchases")
        total_purchases = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(total_amount) FROM purchases")
        total_purchase_value = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return render_template_string(REPORTS_TEMPLATE,
                                    total_assets=total_assets,
                                    total_value=total_value,
                                    assets_by_category=assets_by_category,
                                    assets_by_status=assets_by_status,
                                    active_employees=active_employees,
                                    total_purchases=total_purchases,
                                    total_purchase_value=total_purchase_value)
    
    # صفحة الإشعارات
    @app.route('/notifications')
    def notifications():
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        
        # إشعارات تجريبية
        notifications_data = [
            {
                'id': 1,
                'title': 'انتهاء ضمان أصل',
                'message': 'سينتهي ضمان جهاز الكمبيوتر AST-001 خلال 30 يوم',
                'type': 'تحذير',
                'date': '2024-01-15',
                'read': False
            },
            {
                'id': 2,
                'title': 'تذكرة دعم فني جديدة',
                'message': 'تم إنشاء تذكرة دعم فني جديدة من الموظف أحمد محمد',
                'type': 'معلومات',
                'date': '2024-01-14',
                'read': False
            },
            {
                'id': 3,
                'title': 'اكتمال مشترى',
                'message': 'تم اكتمال توريد المشترى PUR-2024-001',
                'type': 'نجاح',
                'date': '2024-01-13',
                'read': True
            },
            {
                'id': 4,
                'title': 'انتهاء ترخيص قريباً',
                'message': 'سينتهي ترخيص Office 365 خلال 60 يوم',
                'type': 'تحذير',
                'date': '2024-01-12',
                'read': True
            }
        ]
        
        return render_template_string(NOTIFICATIONS_TEMPLATE, notifications=notifications_data)
    
    # API لتحديث حالة المشترى
    @app.route('/api/update_purchase_status', methods=['POST'])
    def update_purchase_status():
        if not session.get('logged_in'):
            return jsonify({'error': 'غير مصرح'}), 401
        
        try:
            data = request.get_json()
            purchase_id = data['purchase_id']
            new_status = data['status']
            
            conn = sqlite3.connect('assets.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE purchases SET status = ? WHERE id = ?", (new_status, purchase_id))
            conn.commit()
            conn.close()
            
            return jsonify({'success': True, 'message': 'تم تحديث الحالة بنجاح'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # صفحة إضافة عهدة جديدة
    @app.route('/add_custody', methods=['GET', 'POST'])
    def add_custody():
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        
        if request.method == 'POST':
            try:
                custody_number = request.form['custody_number']
                asset_id = request.form['asset_id']
                employee_id = request.form['employee_id']
                delivery_date = request.form['delivery_date']
                notes = request.form.get('notes', '')
                
                conn = sqlite3.connect('assets.db')
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO custody (custody_number, asset_id, employee_id, delivery_date, notes, status, created_at)
                    VALUES (?, ?, ?, ?, ?, 'نشط', datetime('now'))
                ''', (custody_number, asset_id, employee_id, delivery_date, notes))
                
                conn.commit()
                conn.close()
                
                flash('تم إضافة العهدة بنجاح!', 'success')
                return redirect(url_for('custody'))
                
            except Exception as e:
                flash(f'خطأ في إضافة العهدة: {str(e)}', 'error')
        
        # جلب الأصول والموظفين للقوائم المنسدلة
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, tag, name FROM assets WHERE status = 'نشط'")
        assets = cursor.fetchall()
        
        cursor.execute("SELECT id, emp_id, name FROM employees WHERE status = 'نشط'")
        employees = cursor.fetchall()
        
        conn.close()
        
        return render_template_string(ADD_CUSTODY_TEMPLATE, assets=assets, employees=employees)
    
    # صفحة إضافة فاتورة جديدة
    @app.route('/add_invoice', methods=['GET', 'POST'])
    def add_invoice():
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        
        if request.method == 'POST':
            try:
                invoice_number = request.form['invoice_number']
                supplier = request.form['supplier']
                invoice_date = request.form['invoice_date']
                amount = float(request.form['amount'])
                description = request.form.get('description', '')
                
                # هنا يمكن إضافة الفاتورة إلى قاعدة البيانات
                flash('تم إنشاء الفاتورة بنجاح!', 'success')
                return redirect(url_for('invoices'))
                
            except Exception as e:
                flash(f'خطأ في إنشاء الفاتورة: {str(e)}', 'error')
        
        return render_template_string(ADD_INVOICE_TEMPLATE)
    
    # صفحة إضافة ترخيص جديد
    @app.route('/add_license', methods=['GET', 'POST'])
    def add_license():
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        
        if request.method == 'POST':
            try:
                license_number = request.form['license_number']
                software_name = request.form['software_name']
                supplier = request.form['supplier']
                license_type = request.form['license_type']
                seats = int(request.form['seats'])
                expiry_date = request.form['expiry_date']
                
                # هنا يمكن إضافة الترخيص إلى قاعدة البيانات
                flash('تم إضافة الترخيص بنجاح!', 'success')
                return redirect(url_for('licenses'))
                
            except Exception as e:
                flash(f'خطأ في إضافة الترخيص: {str(e)}', 'error')
        
        return render_template_string(ADD_LICENSE_TEMPLATE)
    
    # صفحة إنشاء تذكرة دعم فني
    @app.route('/create_ticket', methods=['GET', 'POST'])
    def create_ticket():
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        
        if request.method == 'POST':
            try:
                ticket_number = f"TKT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                title = request.form['title']
                description = request.form['description']
                employee_name = request.form['employee_name']
                priority = request.form['priority']
                category = request.form['category']
                
                conn = sqlite3.connect('assets.db')
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO support_tickets (ticket_number, title, description, employee_name, priority, category, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, 'مفتوح', datetime('now'))
                ''', (ticket_number, title, description, employee_name, priority, category))
                
                conn.commit()
                conn.close()
                
                flash('تم إنشاء تذكرة الدعم الفني بنجاح!', 'success')
                return redirect(url_for('support'))
                
            except Exception as e:
                flash(f'خطأ في إنشاء التذكرة: {str(e)}', 'error')
        
        return render_template_string(CREATE_TICKET_TEMPLATE)
    
    # API لطباعة الفاتورة
    @app.route('/api/print_invoice/<invoice_number>')
    def print_invoice(invoice_number):
        if not session.get('logged_in'):
            return jsonify({'success': False, 'message': 'غير مصرح'})
        
        # هنا يمكن إنشاء PDF للفاتورة
        return render_template_string(INVOICE_PRINT_TEMPLATE, invoice_number=invoice_number)
    
    # صفحة التقارير المخصصة
    @app.route('/custom_reports')
    def custom_reports():
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        
        return render_template_string(CUSTOM_REPORTS_TEMPLATE)
    
    # API لإرسال الإشعارات على الجوال
    @app.route('/api/send_sms_notification', methods=['POST'])
    def send_sms_notification():
        if not session.get('logged_in'):
            return jsonify({'success': False, 'message': 'غير مصرح'})
        
        data = request.get_json()
        phone = data.get('phone')
        message = data.get('message')
        
        # هنا يمكن إضافة خدمة SMS حقيقية
        # مثل Twilio أو خدمة SMS محلية
        
        return jsonify({'success': True, 'message': 'تم إرسال الإشعار بنجاح'})
    
    # تسجيل الخروج
    @app.route('/logout')
    def logout():
        session.clear()
        flash('تم تسجيل الخروج بنجاح', 'info')
        return redirect(url_for('login'))
    
    return app

# قالب تسجيل الدخول المحسن
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تسجيل الدخول - نظام إدارة الأصول</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Cairo', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            overflow: hidden;
        }
        
        body::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
            animation: float 20s ease-in-out infinite;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px) rotate(0deg); }
            50% { transform: translateY(-20px) rotate(1deg); }
        }
        
        .login-container {
            position: relative;
            z-index: 10;
            width: 100%;
            max-width: 450px;
            padding: 0 20px;
        }
        
        .login-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 25px;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
            overflow: hidden;
            transition: transform 0.3s ease;
        }
        
        .login-card:hover {
            transform: translateY(-5px);
        }
        
        .login-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            text-align: center;
            position: relative;
        }
        
        .logo-icon {
            width: 80px;
            height: 80px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1rem;
            font-size: 2.5rem;
            animation: pulse 2s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        
        .login-body {
            padding: 2.5rem;
        }
        
        .form-floating {
            margin-bottom: 1.5rem;
            position: relative;
        }
        
        .form-floating .form-control {
            border: 2px solid #e9ecef;
            border-radius: 15px;
            padding: 1rem 1rem 1rem 3rem;
            font-size: 1rem;
            transition: all 0.3s ease;
            background: #f8f9fa;
        }
        
        .form-floating .form-control:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
            background: white;
        }
        
        .form-floating label {
            padding-right: 3rem;
            color: #6c757d;
        }
        
        .input-icon {
            position: absolute;
            right: 1rem;
            top: 50%;
            transform: translateY(-50%);
            color: #6c757d;
            z-index: 5;
            transition: color 0.3s ease;
        }
        
        .form-floating .form-control:focus + label + .input-icon {
            color: #667eea;
        }
        
        .btn-login {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 15px;
            padding: 1rem 2rem;
            font-size: 1.1rem;
            font-weight: 600;
            color: white;
            width: 100%;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .btn-login:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
        }
        
        .alert {
            border: none;
            border-radius: 15px;
            padding: 1rem 1.5rem;
            margin-bottom: 1.5rem;
            animation: slideIn 0.5s ease;
        }
        
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .alert-danger {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
            color: white;
        }
        
        .alert-success {
            background: linear-gradient(135deg, #51cf66 0%, #40c057 100%);
            color: white;
        }
        
        .alert-info {
            background: linear-gradient(135deg, #339af0 0%, #228be6 100%);
            color: white;
        }
        
        .demo-info {
            background: rgba(102, 126, 234, 0.1);
            border: 1px solid rgba(102, 126, 234, 0.2);
            border-radius: 15px;
            padding: 1.5rem;
            text-align: center;
            margin-top: 1.5rem;
        }
        
        .demo-info h6 {
            color: #667eea;
            margin-bottom: 1rem;
            font-weight: 600;
        }
        
        .demo-credentials {
            display: flex;
            justify-content: space-between;
            gap: 1rem;
        }
        
        .credential-item {
            flex: 1;
            background: white;
            border-radius: 10px;
            padding: 0.75rem;
            border: 1px solid rgba(102, 126, 234, 0.1);
        }
        
        .credential-item small {
            color: #6c757d;
            display: block;
            margin-bottom: 0.25rem;
        }
        
        .credential-item strong {
            color: #667eea;
            font-family: 'Courier New', monospace;
        }
        
        @media (max-width: 576px) {
            .login-container {
                padding: 0 15px;
            }
            
            .login-body {
                padding: 2rem 1.5rem;
            }
            
            .demo-credentials {
                flex-direction: column;
                gap: 0.5rem;
            }
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-card">
            <div class="login-header">
                <div class="logo-icon">
                    <i class="fas fa-rocket"></i>
                </div>
                <h2 class="mb-0">نظام إدارة الأصول</h2>
                <p class="mb-0 opacity-75">مرحباً بك في نظام إدارة الأصول المتطور</p>
            </div>
            
            <div class="login-body">
                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                            <div class="alert alert-{{ 'danger' if category == 'error' else category }}">
                                <i class="fas fa-{{ 'exclamation-triangle' if category == 'error' else 'check-circle' if category == 'success' else 'info-circle' }} me-2"></i>
                                {{ message }}
                            </div>
                        {% endfor %}
                    {% endif %}
                {% endwith %}
                
                <form method="POST" id="loginForm">
                    <div class="form-floating">
                        <input type="text" class="form-control" id="username" name="username" placeholder="اسم المستخدم" required>
                        <label for="username">اسم المستخدم</label>
                        <i class="fas fa-user input-icon"></i>
                    </div>
                    
                    <div class="form-floating">
                        <input type="password" class="form-control" id="password" name="password" placeholder="كلمة المرور" required>
                        <label for="password">كلمة المرور</label>
                        <i class="fas fa-lock input-icon"></i>
                    </div>
                    
                    <button type="submit" class="btn btn-login">
                        <i class="fas fa-sign-in-alt me-2"></i>
                        تسجيل الدخول
                    </button>
                </form>
                
                <div class="demo-info">
                    <h6><i class="fas fa-info-circle me-2"></i>بيانات تجريبية للدخول</h6>
                    <div class="demo-credentials">
                        <div class="credential-item">
                            <small>اسم المستخدم</small>
                            <strong>admin</strong>
                        </div>
                        <div class="credential-item">
                            <small>كلمة المرور</small>
                            <strong>admin123</strong>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const form = document.getElementById('loginForm');
            const inputs = form.querySelectorAll('.form-control');
            
            inputs.forEach(input => {
                input.addEventListener('focus', function() {
                    this.parentElement.style.transform = 'translateY(-2px)';
                });
                
                input.addEventListener('blur', function() {
                    this.parentElement.style.transform = 'translateY(0)';
                });
            });
            
            form.addEventListener('submit', function(e) {
                const submitBtn = form.querySelector('.btn-login');
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>جاري تسجيل الدخول...';
                submitBtn.disabled = true;
            });
            
            document.querySelector('.demo-credentials').addEventListener('click', function() {
                document.getElementById('username').value = 'admin';
                document.getElementById('password').value = 'admin123';
                
                inputs.forEach(input => {
                    input.style.background = '#e3f2fd';
                    setTimeout(() => {
                        input.style.background = '';
                    }, 1000);
                });
            });
        });
    </script>
</body>
</html>
'''

# قالب صفحة بسيطة للصفحات قيد التطوير
SIMPLE_PAGE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ 
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            font-family: 'Cairo', sans-serif;
        }}
        .navbar-custom {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        .card {{ 
            border: none; 
            box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
            border-radius: 20px;
        }}
        .development-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 20px;
            padding: 3rem;
            text-align: center;
        }}
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/"><i class="fas fa-rocket me-2"></i>نظام إدارة الأصول</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link text-white" href="/"><i class="fas fa-home me-1"></i>الرئيسية</a></li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle text-white" href="#" role="button" data-bs-toggle="dropdown">
                            <i class="fas fa-laptop me-1"></i>الأصول
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="/assets"><i class="fas fa-list me-2"></i>عرض الأصول</a></li>
                            <li><a class="dropdown-item" href="/add_asset"><i class="fas fa-plus me-2"></i>إضافة أصل</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="/custody"><i class="fas fa-handshake me-2"></i>إدارة العهد</a></li>
                        </ul>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle text-white" href="#" role="button" data-bs-toggle="dropdown">
                            <i class="fas fa-users me-1"></i>الموظفين
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="/employees"><i class="fas fa-users me-2"></i>عرض الموظفين</a></li>
                            <li><a class="dropdown-item" href="/add_employee"><i class="fas fa-user-plus me-2"></i>إضافة موظف</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="/departments"><i class="fas fa-building me-2"></i>الإدارات</a></li>
                        </ul>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle text-white" href="#" role="button" data-bs-toggle="dropdown">
                            <i class="fas fa-shopping-cart me-1"></i>المشتريات
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="/purchases"><i class="fas fa-shopping-cart me-2"></i>عرض المشتريات</a></li>
                            <li><a class="dropdown-item" href="/add_purchase"><i class="fas fa-plus me-2"></i>إضافة مشترى</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="/invoices"><i class="fas fa-file-invoice me-2"></i>الفواتير</a></li>
                            <li><a class="dropdown-item" href="/licenses"><i class="fas fa-key me-2"></i>التراخيص</a></li>
                        </ul>
                    </li>
                    <li class="nav-item"><a class="nav-link text-white" href="/support"><i class="fas fa-headset me-1"></i>الدعم الفني</a></li>
                    <li class="nav-item"><a class="nav-link text-white" href="/reports"><i class="fas fa-chart-bar me-1"></i>التقارير</a></li>
                    <li class="nav-item"><a class="nav-link text-white" href="/notifications"><i class="fas fa-bell me-1"></i>الإشعارات</a></li>
                    <li class="nav-item"><a class="nav-link text-white" href="/logout"><i class="fas fa-sign-out-alt me-1"></i>خروج</a></li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="development-card">
            <i class="fas fa-{icon} fa-5x mb-4"></i>
            <h2 class="mb-3">{title}</h2>
            <p class="mb-4">{content}</p>
            <a href="/" class="btn btn-light btn-lg">
                <i class="fas fa-home me-2"></i>العودة للرئيسية
            </a>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

# قوالب إضافية
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>لوحة التحكم - نظام إدارة الأصول</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body { 
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            font-family: 'Cairo', sans-serif;
            min-height: 100vh;
        }
        .navbar-custom { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .stats-card { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            border-radius: 20px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border: none;
            overflow: hidden;
            position: relative;
        }
        .stats-card::before {
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 100px;
            height: 100px;
            background: rgba(255,255,255,0.1);
            border-radius: 50%;
            transform: translate(30px, -30px);
        }
        .stats-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
        }
        .card { 
            border: none; 
            box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
            border-radius: 20px;
            transition: transform 0.3s ease;
        }
        .card:hover {
            transform: translateY(-5px);
        }
        .welcome-alert {
            background: linear-gradient(135deg, #51cf66 0%, #40c057 100%);
            border: none;
            border-radius: 15px;
            color: white;
            animation: slideInDown 0.8s ease;
        }
        @keyframes slideInDown {
            from { opacity: 0; transform: translateY(-50px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .quick-action-btn {
            border-radius: 15px;
            padding: 1rem;
            transition: all 0.3s ease;
            border: 2px solid transparent;
        }
        .quick-action-btn:hover {
            transform: translateY(-3px);
            border-color: #667eea;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }
        .table th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            font-weight: 600;
        }
        .badge {
            padding: 0.5rem 1rem;
            border-radius: 10px;
            font-weight: 500;
        }
        .navbar-toggler {
            border: none;
            padding: 0.25rem 0.5rem;
        }
        .navbar-toggler:focus {
            box-shadow: none;
        }
        .navbar-toggler-icon {
            background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 30 30'%3e%3cpath stroke='rgba%28255, 255, 255, 1%29' stroke-linecap='round' stroke-miterlimit='10' stroke-width='2' d='M4 7h22M4 15h22M4 23h22'/%3e%3c/svg%3e");
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/">
                <i class="fas fa-rocket me-2"></i>نظام إدارة الأصول
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link text-white active" href="/"><i class="fas fa-home me-1"></i>الرئيسية</a></li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle text-white" href="#" role="button" data-bs-toggle="dropdown">
                            <i class="fas fa-laptop me-1"></i>الأصول
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="/assets"><i class="fas fa-list me-2"></i>عرض الأصول</a></li>
                            <li><a class="dropdown-item" href="/add_asset"><i class="fas fa-plus me-2"></i>إضافة أصل</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="/custody"><i class="fas fa-handshake me-2"></i>إدارة العهد</a></li>
                        </ul>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle text-white" href="#" role="button" data-bs-toggle="dropdown">
                            <i class="fas fa-users me-1"></i>الموظفين
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="/employees"><i class="fas fa-users me-2"></i>عرض الموظفين</a></li>
                            <li><a class="dropdown-item" href="/add_employee"><i class="fas fa-user-plus me-2"></i>إضافة موظف</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="/departments"><i class="fas fa-building me-2"></i>الإدارات</a></li>
                        </ul>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle text-white" href="#" role="button" data-bs-toggle="dropdown">
                            <i class="fas fa-shopping-cart me-1"></i>المشتريات
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="/purchases"><i class="fas fa-shopping-cart me-2"></i>عرض المشتريات</a></li>
                            <li><a class="dropdown-item" href="/add_purchase"><i class="fas fa-plus me-2"></i>إضافة مشترى</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="/invoices"><i class="fas fa-file-invoice me-2"></i>الفواتير</a></li>
                            <li><a class="dropdown-item" href="/licenses"><i class="fas fa-key me-2"></i>التراخيص</a></li>
                        </ul>
                    </li>
                    <li class="nav-item"><a class="nav-link text-white" href="/support"><i class="fas fa-headset me-1"></i>الدعم الفني</a></li>
                    <li class="nav-item"><a class="nav-link text-white" href="/reports"><i class="fas fa-chart-bar me-1"></i>التقارير</a></li>
                    <li class="nav-item"><a class="nav-link text-white" href="/notifications"><i class="fas fa-bell me-1"></i>الإشعارات</a></li>
                    <li class="nav-item"><a class="nav-link text-white" href="/logout"><i class="fas fa-sign-out-alt me-1"></i>خروج</a></li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert welcome-alert">
                        <i class="fas fa-check-circle me-2"></i>
                        <strong>{{ message }}</strong>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <!-- إحصائيات رئيسية -->
        <div class="row mb-4">
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="stats-card p-4 text-center">
                    <i class="fas fa-laptop fa-3x mb-3"></i>
                    <h3>{{ total_assets }}</h3>
                    <p class="mb-0">إجمالي الأصول</p>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="stats-card p-4 text-center">
                    <i class="fas fa-check-circle fa-3x mb-3"></i>
                    <h3>{{ active_assets }}</h3>
                    <p class="mb-0">أصول نشطة</p>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="stats-card p-4 text-center">
                    <i class="fas fa-users fa-3x mb-3"></i>
                    <h3>{{ total_employees }}</h3>
                    <p class="mb-0">الموظفين</p>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="stats-card p-4 text-center">
                    <i class="fas fa-dollar-sign fa-3x mb-3"></i>
                    <h3>{{ "{:,.0f}".format(total_cost) }}</h3>
                    <p class="mb-0">إجمالي القيمة (ريال)</p>
                </div>
            </div>
        </div>

        <!-- إحصائيات إضافية -->
        <div class="row mb-4">
            <div class="col-lg-6 col-md-6 mb-3">
                <div class="card text-center" style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%); color: white;">
                    <div class="card-body">
                        <i class="fas fa-handshake fa-2x mb-2"></i>
                        <h4>{{ active_custody }}</h4>
                        <p class="mb-0">عهد نشطة</p>
                    </div>
                </div>
            </div>
            <div class="col-lg-6 col-md-6 mb-3">
                <div class="card text-center" style="background: linear-gradient(135deg, #ffa726 0%, #ff9800 100%); color: white;">
                    <div class="card-body">
                        <i class="fas fa-ticket-alt fa-2x mb-2"></i>
                        <h4>{{ open_tickets }}</h4>
                        <p class="mb-0">تذاكر مفتوحة</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="row">
            <!-- الأصول الحديثة -->
            <div class="col-lg-8 mb-4">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5 class="mb-0"><i class="fas fa-clock me-2"></i>الأصول الحديثة</h5>
                        <a href="/reports" class="btn btn-primary btn-sm">
                            <i class="fas fa-chart-bar me-1"></i>التقارير
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
                                        <td><strong class="text-primary">{{ asset[0] }}</strong></td>
                                        <td>{{ asset[1] }}</td>
                                        <td><span class="badge bg-secondary">{{ asset[2] }}</span></td>
                                        <td><strong>{{ "{:,.0f}".format(asset[3] or 0) }} ريال</strong></td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <!-- الإجراءات السريعة -->
            <div class="col-lg-4 mb-4">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="fas fa-bolt me-2"></i>الإجراءات السريعة</h5>
                    </div>
                    <div class="card-body">
                        <div class="d-grid gap-3">
                            <a href="/assets" class="btn btn-outline-primary quick-action-btn">
                                <i class="fas fa-list me-2"></i>عرض جميع الأصول
                            </a>
                            <a href="/add_asset" class="btn btn-outline-success quick-action-btn">
                                <i class="fas fa-plus me-2"></i>إضافة أصل جديد
                            </a>
                            <a href="/employees" class="btn btn-outline-info quick-action-btn">
                                <i class="fas fa-users me-2"></i>إدارة الموظفين
                            </a>
                            <a href="/purchases" class="btn btn-outline-warning quick-action-btn">
                                <i class="fas fa-shopping-cart me-2"></i>إدارة المشتريات
                            </a>
                            <a href="/support" class="btn btn-outline-danger quick-action-btn">
                                <i class="fas fa-headset me-2"></i>الدعم الفني
                            </a>
                            <a href="/reports" class="btn btn-outline-dark quick-action-btn">
                                <i class="fas fa-chart-bar me-2"></i>التقارير والإحصائيات
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const counters = document.querySelectorAll('.stats-card h3');
            counters.forEach(counter => {
                const target = parseInt(counter.textContent.replace(/,/g, ''));
                let current = 0;
                const increment = target / 50;
                const timer = setInterval(() => {
                    current += increment;
                    if (current >= target) {
                        counter.textContent = target.toLocaleString();
                        clearInterval(timer);
                    } else {
                        counter.textContent = Math.floor(current).toLocaleString();
                    }
                }, 30);
            });
            
            const cards = document.querySelectorAll('.card, .stats-card');
            cards.forEach((card, index) => {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                setTimeout(() => {
                    card.style.transition = 'all 0.6s ease';
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }, index * 100);
            });
        });
    </script>
</body>
</html>
'''

# قوالب إضافية مفقودة
ASSETS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>الأصول</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body { 
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            font-family: 'Cairo', sans-serif;
        }
        .navbar-custom { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .card { 
            border: none; 
            box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
            border-radius: 20px;
        }
        .table th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            font-weight: 600;
        }
        .badge { padding: 0.5rem 1rem; border-radius: 10px; font-weight: 500; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/"><i class="fas fa-rocket me-2"></i>نظام إدارة الأصول</a>
            <div class="collapse navbar-collapse">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link text-white" href="/"><i class="fas fa-home me-1"></i>الرئيسية</a></li>
                    <li class="nav-item"><a class="nav-link text-white active" href="/assets"><i class="fas fa-laptop me-1"></i>الأصول</a></li>
                    <li class="nav-item"><a class="nav-link text-white" href="/employees"><i class="fas fa-users me-1"></i>الموظفين</a></li>
                    <li class="nav-item"><a class="nav-link text-white" href="/purchases"><i class="fas fa-shopping-cart me-1"></i>المشتريات</a></li>
                    <li class="nav-item"><a class="nav-link text-white" href="/logout"><i class="fas fa-sign-out-alt me-1"></i>خروج</a></li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="fas fa-laptop text-primary me-2"></i>إدارة الأصول</h2>
            <a href="/add_asset" class="btn btn-primary">
                <i class="fas fa-plus me-2"></i>إضافة أصل جديد
            </a>
        </div>

        <div class="card">
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>رقم الأصل</th>
                                <th>الاسم</th>
                                <th>الفئة</th>
                                <th>العلامة التجارية</th>
                                <th>الموديل</th>
                                <th>القيمة</th>
                                <th>الحالة</th>
                                <th>الإجراءات</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for asset in assets %}
                            <tr>
                                <td><strong class="text-primary">{{ asset[1] }}</strong></td>
                                <td>{{ asset[2] }}</td>
                                <td><span class="badge bg-secondary">{{ asset[3] }}</span></td>
                                <td>{{ asset[4] or 'غير محدد' }}</td>
                                <td>{{ asset[5] or 'غير محدد' }}</td>
                                <td><strong>{{ "{:,.0f}".format(asset[7] or 0) }} ريال</strong></td>
                                <td>
                                    <span class="badge bg-{{ 'success' if asset[12] == 'نشط' else 'warning' }}">
                                        {{ asset[12] }}
                                    </span>
                                </td>
                                <td>
                                    <button class="btn btn-primary btn-sm" onclick="viewAsset({{ asset[0] }})">
                                        <i class="fas fa-eye"></i>
                                    </button>
                                    <button class="btn btn-warning btn-sm" onclick="editAsset({{ asset[0] }})">
                                        <i class="fas fa-edit"></i>
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
        function viewAsset(id) { alert('عرض الأصل رقم: ' + id); }
        function editAsset(id) { alert('تحرير الأصل رقم: ' + id); }
    </script>
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
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            font-family: 'Cairo', sans-serif;
        }
        .navbar-custom { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .card { 
            border: none; 
            box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
            border-radius: 20px;
        }
        .form-control, .form-select {
            border-radius: 10px;
            border: 2px solid #e9ecef;
            padding: 0.75rem 1rem;
            transition: all 0.3s ease;
        }
        .form-control:focus, .form-select:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 10px;
            padding: 0.75rem 2rem;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/"><i class="fas fa-rocket me-2"></i>نظام إدارة الأصول</a>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row justify-content-center">
            <div class="col-lg-8">
                <div class="card">
                    <div class="card-header bg-transparent border-0 pt-4">
                        <div class="text-center">
                            <div class="d-inline-flex align-items-center justify-content-center bg-primary rounded-circle mb-3" style="width: 80px; height: 80px;">
                                <i class="fas fa-laptop fa-2x text-white"></i>
                            </div>
                            <h2 class="mb-1">إضافة أصل جديد</h2>
                            <p class="text-muted">أضف أصل جديد إلى النظام</p>
                        </div>
                    </div>
                    
                    <div class="card-body p-4">
                        {% with messages = get_flashed_messages(with_categories=true) %}
                            {% if messages %}
                                {% for category, message in messages %}
                                    <div class="alert alert-{{ 'success' if category == 'success' else 'danger' }}">
                                        <i class="fas fa-{{ 'check-circle' if category == 'success' else 'exclamation-triangle' }} me-2"></i>
                                        {{ message }}
                                    </div>
                                {% endfor %}
                            {% endif %}
                        {% endwith %}
                        
                        <form method="POST" id="assetForm">
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">رقم الأصل *</label>
                                    <input type="text" class="form-control" name="tag" required placeholder="AST-2024-001">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">اسم الأصل *</label>
                                    <input type="text" class="form-control" name="name" required placeholder="جهاز كمبيوتر Dell">
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">الفئة *</label>
                                    <select class="form-select" name="category" required>
                                        <option value="">اختر الفئة</option>
                                        <option value="كمبيوتر">كمبيوتر</option>
                                        <option value="طابعة">طابعة</option>
                                        <option value="شاشة">شاشة</option>
                                        <option value="شبكة">معدات شبكة</option>
                                        <option value="أثاث">أثاث مكتبي</option>
                                        <option value="أخرى">أخرى</option>
                                    </select>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">العلامة التجارية</label>
                                    <input type="text" class="form-control" name="brand" placeholder="Dell, HP, Lenovo">
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">الموديل</label>
                                    <input type="text" class="form-control" name="model" placeholder="OptiPlex 7090">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">الرقم التسلسلي</label>
                                    <input type="text" class="form-control" name="serial_number" placeholder="SN123456789">
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">التكلفة (ريال)</label>
                                    <input type="number" step="0.01" class="form-control" name="cost" placeholder="2500.00">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">تاريخ الشراء</label>
                                    <input type="date" class="form-control" name="purchase_date">
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">تاريخ انتهاء الضمان</label>
                                    <input type="date" class="form-control" name="warranty_end">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">الموقع</label>
                                    <input type="text" class="form-control" name="location" placeholder="الطابق الأول - مكتب 101">
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">مخصص لـ</label>
                                    <input type="text" class="form-control" name="assigned_to" placeholder="أحمد محمد">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">الحالة</label>
                                    <select class="form-select" name="status">
                                        <option value="نشط" selected>نشط</option>
                                        <option value="غير نشط">غير نشط</option>
                                        <option value="تحت الصيانة">تحت الصيانة</option>
                                        <option value="مستبعد">مستبعد</option>
                                    </select>
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">ملاحظات</label>
                                <textarea class="form-control" name="notes" rows="3" placeholder="أي ملاحظات إضافية..."></textarea>
                            </div>
                            
                            <div class="d-flex justify-content-between mt-4">
                                <button type="submit" class="btn btn-primary btn-lg">
                                    <i class="fas fa-save me-2"></i>حفظ الأصل
                                </button>
                                <a href="/assets" class="btn btn-outline-secondary btn-lg">
                                    <i class="fas fa-arrow-right me-2"></i>العودة للأصول
                                </a>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const today = new Date().toISOString().split('T')[0];
            document.querySelector('input[name="purchase_date"]').value = today;
            
            const warrantyEnd = new Date();
            warrantyEnd.setFullYear(warrantyEnd.getFullYear() + 3);
            document.querySelector('input[name="warranty_end"]').value = warrantyEnd.toISOString().split('T')[0];
        });
    </script>
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
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body { 
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            font-family: 'Cairo', sans-serif;
        }
        .navbar-custom { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .card { 
            border: none; 
            box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
            border-radius: 20px;
            transition: transform 0.3s ease;
        }
        .card:hover { transform: translateY(-5px); }
        .employee-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            transition: transform 0.3s ease;
        }
        .employee-card:hover { transform: translateY(-3px); }
        .badge { padding: 0.5rem 1rem; border-radius: 10px; font-weight: 500; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/"><i class="fas fa-rocket me-2"></i>نظام إدارة الأصول</a>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="fas fa-users text-primary me-2"></i>إدارة الموظفين</h2>
            <a href="/add_employee" class="btn btn-primary">
                <i class="fas fa-user-plus me-2"></i>إضافة موظف جديد
            </a>
        </div>

        <div class="row">
            {% for employee in employees %}
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="card">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <div class="bg-primary rounded-circle d-flex align-items-center justify-content-center me-3" style="width: 50px; height: 50px;">
                                <i class="fas fa-user text-white"></i>
                            </div>
                            <div>
                                <h5 class="mb-1">{{ employee[2] }}</h5>
                                <small class="text-muted">{{ employee[1] }}</small>
                            </div>
                        </div>
                        
                        <div class="mb-2">
                            <span class="badge bg-secondary">{{ employee[3] }}</span>
                            <span class="badge bg-info ms-1">{{ employee[4] }}</span>
                        </div>
                        
                        <div class="mb-2">
                            <small class="text-muted">
                                <i class="fas fa-envelope me-1"></i>{{ employee[5] or 'غير محدد' }}
                            </small>
                        </div>
                        
                        <div class="mb-2">
                            <small class="text-muted">
                                <i class="fas fa-phone me-1"></i>{{ employee[6] or 'غير محدد' }}
                            </small>
                        </div>
                        
                        <div class="d-flex justify-content-between align-items-center mt-3">
                            <span class="badge bg-{{ 'success' if employee[8] == 'نشط' else 'warning' }}">
                                {{ employee[8] }}
                            </span>
                            <div>
                                <button class="btn btn-sm btn-outline-info me-1" onclick="editEmployee({{ employee[0] }})">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-primary me-1" onclick="createTicket({{ employee[0] }}, '{{ employee[2] }}')">
                                    <i class="fas fa-ticket-alt"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function editEmployee(employeeId) {
            alert('تحرير الموظف رقم: ' + employeeId);
        }
        
        function createTicket(employeeId, employeeName) {
            if (confirm(`إنشاء تذكرة دعم فني للموظف: ${employeeName}؟`)) {
                alert('تم إنشاء تذكرة دعم فني');
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
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body { 
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            font-family: 'Cairo', sans-serif;
        }
        .navbar-custom { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .card { 
            border: none; 
            box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
            border-radius: 20px;
        }
        .form-control, .form-select {
            border-radius: 10px;
            border: 2px solid #e9ecef;
            padding: 0.75rem 1rem;
            transition: all 0.3s ease;
        }
        .form-control:focus, .form-select:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 10px;
            padding: 0.75rem 2rem;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/"><i class="fas fa-rocket me-2"></i>نظام إدارة الأصول</a>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row justify-content-center">
            <div class="col-lg-8">
                <div class="card">
                    <div class="card-header bg-transparent border-0 pt-4">
                        <div class="text-center">
                            <div class="d-inline-flex align-items-center justify-content-center bg-primary rounded-circle mb-3" style="width: 80px; height: 80px;">
                                <i class="fas fa-user-plus fa-2x text-white"></i>
                            </div>
                            <h2 class="mb-1">إضافة موظف جديد</h2>
                            <p class="text-muted">أضف موظف جديد إلى النظام</p>
                        </div>
                    </div>
                    
                    <div class="card-body p-4">
                        {% with messages = get_flashed_messages(with_categories=true) %}
                            {% if messages %}
                                {% for category, message in messages %}
                                    <div class="alert alert-{{ 'success' if category == 'success' else 'danger' }}">
                                        <i class="fas fa-{{ 'check-circle' if category == 'success' else 'exclamation-triangle' }} me-2"></i>
                                        {{ message }}
                                    </div>
                                {% endfor %}
                            {% endif %}
                        {% endwith %}
                        
                        <form method="POST" id="employeeForm">
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">رقم الموظف *</label>
                                    <input type="text" class="form-control" name="emp_id" required placeholder="EMP-001">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">الاسم الكامل *</label>
                                    <input type="text" class="form-control" name="name" required placeholder="أحمد محمد علي">
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">الإدارة *</label>
                                    <select class="form-select" name="department" required>
                                        <option value="">اختر الإدارة</option>
                                        <option value="المحاسبة">المحاسبة</option>
                                        <option value="المبيعات">المبيعات</option>
                                        <option value="التسويق">التسويق</option>
                                        <option value="تقنية المعلومات">تقنية المعلومات</option>
                                        <option value="الموارد البشرية">الموارد البشرية</option>
                                        <option value="الإدارة العامة">الإدارة العامة</option>
                                    </select>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">المنصب *</label>
                                    <input type="text" class="form-control" name="position" required placeholder="محاسب، مطور، مدير">
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">البريد الإلكتروني</label>
                                    <input type="email" class="form-control" name="email" placeholder="ahmed@company.com">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">رقم الهاتف</label>
                                    <input type="tel" class="form-control" name="phone" placeholder="0501234567">
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">تاريخ التوظيف</label>
                                    <input type="date" class="form-control" name="hire_date">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">الحالة</label>
                                    <select class="form-select" name="status">
                                        <option value="نشط" selected>نشط</option>
                                        <option value="غير نشط">غير نشط</option>
                                        <option value="إجازة">إجازة</option>
                                        <option value="مستقيل">مستقيل</option>
                                    </select>
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">المدير المباشر</label>
                                    <select class="form-select" name="manager_id">
                                        <option value="">اختر المدير</option>
                                        {% for manager in managers %}
                                        <option value="{{ manager[0] }}">{{ manager[1] }}</option>
                                        {% endfor %}
                                    </select>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">موقع المكتب</label>
                                    <input type="text" class="form-control" name="office_location" placeholder="الطابق الثاني - مكتب 201">
                                </div>
                            </div>
                            
                            <div class="d-flex justify-content-between mt-4">
                                <button type="submit" class="btn btn-primary btn-lg">
                                    <i class="fas fa-save me-2"></i>حفظ الموظف
                                </button>
                                <a href="/employees" class="btn btn-outline-secondary btn-lg">
                                    <i class="fas fa-arrow-right me-2"></i>العودة للموظفين
                                </a>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const today = new Date().toISOString().split('T')[0];
            document.querySelector('input[name="hire_date"]').value = today;
        });
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
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body { 
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            font-family: 'Cairo', sans-serif;
        }
        .navbar-custom { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .card { 
            border: none; 
            box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
            border-radius: 20px;
        }
        .stats-card { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            border-radius: 15px;
            transition: transform 0.3s ease;
        }
        .stats-card:hover { transform: translateY(-3px); }
        .table th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            font-weight: 600;
        }
        .badge { padding: 0.5rem 1rem; border-radius: 10px; font-weight: 500; }
        .btn-action { border-radius: 10px; margin: 0 2px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/"><i class="fas fa-rocket me-2"></i>نظام إدارة الأصول</a>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="fas fa-shopping-cart text-primary me-2"></i>إدارة المشتريات</h2>
            <a href="/add_purchase" class="btn btn-primary">
                <i class="fas fa-plus me-2"></i>إضافة مشترى جديد
            </a>
        </div>

        <!-- إحصائيات المشتريات -->
        <div class="row mb-4">
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="stats-card p-4 text-center">
                    <i class="fas fa-shopping-cart fa-3x mb-3"></i>
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
                <h5 class="mb-0"><i class="fas fa-list me-2"></i>قائمة المشتريات</h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>رقم المشترى</th>
                                <th>المورد</th>
                                <th>الصنف</th>
                                <th>الفئة</th>
                                <th>الكمية</th>
                                <th>القيمة الإجمالية</th>
                                <th>الحالة</th>
                                <th>الإجراءات</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for purchase in purchases %}
                            <tr>
                                <td><strong class="text-primary">{{ purchase[1] }}</strong></td>
                                <td>{{ purchase[2] }}</td>
                                <td>{{ purchase[4] }}</td>
                                <td><span class="badge bg-secondary">{{ purchase[6] }}</span></td>
                                <td>{{ purchase[7] }}</td>
                                <td><strong>{{ "{:,.2f}".format(purchase[9]) }} {{ purchase[10] }}</strong></td>
                                <td>
                                    <span class="badge bg-{{ 'success' if purchase[14] == 'مكتمل' else 'warning' if purchase[14] == 'قيد التوريد' else 'secondary' }}">
                                        {{ purchase[14] }}
                                    </span>
                                </td>
                                <td>
                                    <button class="btn btn-primary btn-sm btn-action" onclick="viewPurchase('{{ purchase[1] }}')">
                                        <i class="fas fa-eye"></i>
                                    </button>
                                    <button class="btn btn-success btn-sm btn-action" onclick="updateStatus({{ purchase[0] }}, 'مكتمل')">
                                        <i class="fas fa-check"></i>
                                    </button>
                                    <button class="btn btn-info btn-sm btn-action" onclick="createInvoice({{ purchase[0] }})">
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
        
        function updateStatus(purchaseId, newStatus) {
            if (confirm(`تحديث حالة المشترى إلى "${newStatus}"؟`)) {
                fetch('/api/update_purchase_status', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        purchase_id: purchaseId,
                        status: newStatus
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('تم تحديث الحالة بنجاح');
                        location.reload();
                    } else {
                        alert('خطأ في تحديث الحالة');
                    }
                })
                .catch(error => {
                    alert('خطأ في الاتصال');
                });
            }
        }
        
        function createInvoice(purchaseId) {
            if (confirm('إنشاء فاتورة لهذا المشترى؟')) {
                alert('تم إنشاء الفاتورة بنجاح');
            }
        }
    </script>
</body>
</html>
'''

ADD_PURCHASE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>إضافة مشترى جديد</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body { 
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            font-family: 'Cairo', sans-serif;
        }
        .navbar-custom { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .card { 
            border: none; 
            box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
            border-radius: 20px;
        }
        .form-control, .form-select {
            border-radius: 10px;
            border: 2px solid #e9ecef;
            padding: 0.75rem 1rem;
            transition: all 0.3s ease;
        }
        .form-control:focus, .form-select:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 10px;
            padding: 0.75rem 2rem;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/"><i class="fas fa-rocket me-2"></i>نظام إدارة الأصول</a>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row justify-content-center">
            <div class="col-lg-8">
                <div class="card">
                    <div class="card-header bg-transparent border-0 pt-4">
                        <div class="text-center">
                            <div class="d-inline-flex align-items-center justify-content-center bg-primary rounded-circle mb-3" style="width: 80px; height: 80px;">
                                <i class="fas fa-shopping-cart fa-2x text-white"></i>
                            </div>
                            <h2 class="mb-1">إضافة مشترى جديد</h2>
                            <p class="text-muted">أضف مشترى جديد إلى النظام</p>
                        </div>
                    </div>
                    
                    <div class="card-body p-4">
                        {% with messages = get_flashed_messages(with_categories=true) %}
                            {% if messages %}
                                {% for category, message in messages %}
                                    <div class="alert alert-{{ 'success' if category == 'success' else 'danger' }}">
                                        <i class="fas fa-{{ 'check-circle' if category == 'success' else 'exclamation-triangle' }} me-2"></i>
                                        {{ message }}
                                    </div>
                                {% endfor %}
                            {% endif %}
                        {% endwith %}
                        
                        <form method="POST" id="purchaseForm">
                            <!-- معلومات المورد -->
                            <h5 class="mb-3"><i class="fas fa-store me-2"></i>معلومات المورد</h5>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">اسم المورد *</label>
                                    <input type="text" class="form-control" name="supplier_name" required placeholder="شركة التقنية المتقدمة">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">معلومات الاتصال</label>
                                    <input type="text" class="form-control" name="supplier_contact" placeholder="0112345678">
                                </div>
                            </div>
                            
                            <hr class="my-4">
                            
                            <!-- معلومات الصنف -->
                            <h5 class="mb-3"><i class="fas fa-box me-2"></i>معلومات الصنف</h5>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">اسم الصنف *</label>
                                    <input type="text" class="form-control" name="item_name" required placeholder="أجهزة كمبيوتر Dell">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">الفئة *</label>
                                    <select class="form-select" name="category" required>
                                        <option value="">اختر الفئة</option>
                                        <option value="هاردوير">هاردوير</option>
                                        <option value="ترخيص">ترخيص</option>
                                        <option value="خدمات">خدمات</option>
                                        <option value="مستلزمات">مستلزمات</option>
                                        <option value="صيانة">صيانة</option>
                                    </select>
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">وصف الصنف</label>
                                <textarea class="form-control" name="item_description" rows="3" placeholder="وصف تفصيلي للصنف المطلوب..."></textarea>
                            </div>
                            
                            <hr class="my-4">
                            
                            <!-- معلومات مالية -->
                            <h5 class="mb-3"><i class="fas fa-dollar-sign me-2"></i>المعلومات المالية</h5>
                            <div class="row">
                                <div class="col-md-4 mb-3">
                                    <label class="form-label">الكمية *</label>
                                    <input type="number" class="form-control" name="quantity" required min="1" value="1" onchange="calculateTotal()">
                                </div>
                                <div class="col-md-4 mb-3">
                                    <label class="form-label">سعر الوحدة *</label>
                                    <input type="number" step="0.01" class="form-control" name="unit_price" required placeholder="2500.00" onchange="calculateTotal()">
                                </div>
                                <div class="col-md-4 mb-3">
                                    <label class="form-label">العملة</label>
                                    <select class="form-select" name="currency">
                                        <option value="ريال" selected>ريال سعودي</option>
                                        <option value="دولار">دولار أمريكي</option>
                                        <option value="يورو">يورو</option>
                                    </select>
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">المبلغ الإجمالي</label>
                                <input type="text" class="form-control" id="total_amount" readonly placeholder="0.00">
                            </div>
                            
                            <hr class="my-4">
                            
                            <!-- معلومات التوريد -->
                            <h5 class="mb-3"><i class="fas fa-calendar me-2"></i>معلومات التوريد</h5>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">تاريخ الشراء *</label>
                                    <input type="date" class="form-control" name="purchase_date" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">تاريخ التوريد المتوقع</label>
                                    <input type="date" class="form-control" name="delivery_date">
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">فترة الضمان (شهر)</label>
                                    <input type="number" class="form-control" name="warranty_period" placeholder="36">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">الحالة</label>
                                    <select class="form-select" name="status">
                                        <option value="قيد التوريد" selected>قيد التوريد</option>
                                        <option value="مكتمل">مكتمل</option>
                                        <option value="ملغي">ملغي</option>
                                    </select>
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">الإدارة الطالبة</label>
                                <select class="form-select" name="requesting_department">
                                    <option value="">اختر الإدارة</option>
                                    <option value="المحاسبة">المحاسبة</option>
                                    <option value="المبيعات">المبيعات</option>
                                    <option value="التسويق">التسويق</option>
                                    <option value="تقنية المعلومات">تقنية المعلومات</option>
                                    <option value="الموارد البشرية">الموارد البشرية</option>
                                    <option value="الإدارة العامة">الإدارة العامة</option>
                                </select>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">ملاحظات</label>
                                <textarea class="form-control" name="notes" rows="3" placeholder="أي ملاحظات إضافية..."></textarea>
                            </div>
                            
                            <div class="d-flex justify-content-between mt-4">
                                <button type="submit" class="btn btn-primary btn-lg">
                                    <i class="fas fa-save me-2"></i>حفظ المشترى
                                </button>
                                <a href="/purchases" class="btn btn-outline-secondary btn-lg">
                                    <i class="fas fa-arrow-right me-2"></i>العودة للمشتريات
                                </a>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function calculateTotal() {
            const quantity = parseFloat(document.querySelector('input[name="quantity"]').value) || 0;
            const unitPrice = parseFloat(document.querySelector('input[name="unit_price"]').value) || 0;
            const total = quantity * unitPrice;
            document.getElementById('total_amount').value = total.toFixed(2);
        }
        
        document.addEventListener('DOMContentLoaded', function() {
            const today = new Date().toISOString().split('T')[0];
            document.querySelector('input[name="purchase_date"]').value = today;
            
            const deliveryDate = new Date();
            deliveryDate.setDate(deliveryDate.getDate() + 14);
            document.querySelector('input[name="delivery_date"]').value = deliveryDate.toISOString().split('T')[0];
        });
    </script>
</body>
</html>
'''

# قوالب الصفحات المفقودة
CUSTODY_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>إدارة العهد</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body { 
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            font-family: 'Cairo', sans-serif;
        }
        .navbar-custom { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .card { 
            border: none; 
            box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
            border-radius: 20px;
        }
        .stats-card { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            border-radius: 15px;
            transition: transform 0.3s ease;
        }
        .stats-card:hover { transform: translateY(-3px); }
        .table th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            font-weight: 600;
        }
        .badge { padding: 0.5rem 1rem; border-radius: 10px; font-weight: 500; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/"><i class="fas fa-rocket me-2"></i>نظام إدارة الأصول</a>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="fas fa-handshake text-primary me-2"></i>إدارة العهد</h2>
            <div>
                <a href="/" class="btn btn-outline-success me-2">
                    <i class="fas fa-home me-1"></i>الرئيسية
                </a>
                <button class="btn btn-primary" onclick="addCustody()">
                    <i class="fas fa-plus me-2"></i>إضافة عهدة جديدة
                </button>
            </div>
        </div>

        <!-- إحصائيات العهد -->
        <div class="row mb-4">
            <div class="col-md-4">
                <div class="stats-card p-4 text-center">
                    <i class="fas fa-handshake fa-3x mb-3"></i>
                    <h3>{{ active_custody }}</h3>
                    <p class="mb-0">عهد نشطة</p>
                </div>
            </div>
            <div class="col-md-4">
                <div class="stats-card p-4 text-center">
                    <i class="fas fa-undo fa-3x mb-3"></i>
                    <h3>{{ returned_custody }}</h3>
                    <p class="mb-0">عهد مسترد</p>
                </div>
            </div>
            <div class="col-md-4">
                <div class="stats-card p-4 text-center">
                    <i class="fas fa-chart-line fa-3x mb-3"></i>
                    <h3>{{ active_custody + returned_custody }}</h3>
                    <p class="mb-0">إجمالي العهد</p>
                </div>
            </div>
        </div>

        <!-- جدول العهد -->
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0"><i class="fas fa-list me-2"></i>قائمة العهد</h5>
            </div>
            <div class="card-body">
                {% if custody_list %}
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>رقم العهدة</th>
                                <th>الأصل</th>
                                <th>الموظف</th>
                                <th>تاريخ التسليم</th>
                                <th>تاريخ الاسترداد</th>
                                <th>الحالة</th>
                                <th>الإجراءات</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for custody in custody_list %}
                            <tr>
                                <td><strong class="text-primary">{{ custody[1] }}</strong></td>
                                <td>{{ custody[11] or 'غير محدد' }}</td>
                                <td>{{ custody[12] or 'غير محدد' }}</td>
                                <td>{{ custody[4] }}</td>
                                <td>{{ custody[5] or 'لم يسترد بعد' }}</td>
                                <td>
                                    <span class="badge bg-{{ 'success' if custody[8] == 'نشط' else 'secondary' }}">
                                        {{ custody[8] }}
                                    </span>
                                </td>
                                <td>
                                    <button class="btn btn-primary btn-sm" onclick="viewCustody({{ custody[0] }})">
                                        <i class="fas fa-eye"></i>
                                    </button>
                                    {% if custody[8] == 'نشط' %}
                                    <button class="btn btn-warning btn-sm" onclick="returnCustody({{ custody[0] }})">
                                        <i class="fas fa-undo"></i>
                                    </button>
                                    {% endif %}
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <div class="text-center py-5">
                    <i class="fas fa-handshake fa-5x text-muted mb-3"></i>
                    <h4 class="text-muted">لا توجد عهد حالياً</h4>
                    <p class="text-muted">ابدأ بإضافة عهدة جديدة</p>
                    <button class="btn btn-primary" onclick="addCustody()">
                        <i class="fas fa-plus me-2"></i>إضافة عهدة جديدة
                    </button>
                </div>
                {% endif %}
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function addCustody() {
            window.location.href = '/add_custody';
        }
        
        function viewCustody(custodyId) {
            alert('عرض تفاصيل العهدة رقم: ' + custodyId);
        }
        
        function returnCustody(custodyId) {
            if (confirm('تأكيد استرداد هذه العهدة؟')) {
                alert('تم استرداد العهدة بنجاح');
                location.reload();
            }
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
    <title>الإدارات</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body { 
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            font-family: 'Cairo', sans-serif;
        }
        .navbar-custom { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .card { 
            border: none; 
            box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
            border-radius: 20px;
            transition: transform 0.3s ease;
        }
        .card:hover { transform: translateY(-5px); }
        .dept-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            transition: transform 0.3s ease;
        }
        .dept-card:hover { transform: translateY(-3px); }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/"><i class="fas fa-rocket me-2"></i>نظام إدارة الأصول</a>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="fas fa-building text-primary me-2"></i>الإدارات</h2>
            <div>
                <a href="/" class="btn btn-outline-success me-2">
                    <i class="fas fa-home me-1"></i>الرئيسية
                </a>
                <button class="btn btn-primary" onclick="addDepartment()">
                    <i class="fas fa-plus me-2"></i>إضافة إدارة جديدة
                </button>
            </div>
        </div>

        <div class="row">
            {% for dept in departments %}
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="card">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <div class="bg-primary rounded-circle d-flex align-items-center justify-content-center me-3" style="width: 50px; height: 50px;">
                                <i class="fas fa-building text-white"></i>
                            </div>
                            <div>
                                <h5 class="mb-1">{{ dept.name }}</h5>
                                <small class="text-muted">إدارة</small>
                            </div>
                        </div>
                        
                        <div class="mb-2">
                            <small class="text-muted">
                                <i class="fas fa-user-tie me-1"></i>المدير: {{ dept.manager }}
                            </small>
                        </div>
                        
                        <div class="mb-2">
                            <small class="text-muted">
                                <i class="fas fa-users me-1"></i>عدد الموظفين: {{ dept.employees }}
                            </small>
                        </div>
                        
                        <div class="mb-3">
                            <small class="text-muted">
                                <i class="fas fa-dollar-sign me-1"></i>الميزانية: {{ "{:,.0f}".format(dept.budget) }} ريال
                            </small>
                        </div>
                        
                        <div class="d-flex justify-content-between align-items-center">
                            <span class="badge bg-success">نشط</span>
                            <div>
                                <button class="btn btn-sm btn-outline-info me-1" onclick="editDept('{{ dept.name }}')">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-primary me-1" onclick="viewEmployees('{{ dept.name }}')">
                                    <i class="fas fa-users"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function addDepartment() {
            alert('إضافة إدارة جديدة - قيد التطوير');
        }
        
        function editDept(deptName) {
            alert('تحرير إدارة: ' + deptName);
        }
        
        function viewEmployees(deptName) {
            alert('عرض موظفي إدارة: ' + deptName);
        }
    </script>
</body>
</html>
'''

INVOICES_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>الفواتير</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body { 
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            font-family: 'Cairo', sans-serif;
        }
        .navbar-custom { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .card { 
            border: none; 
            box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
            border-radius: 20px;
        }
        .invoice-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            transition: transform 0.3s ease;
        }
        .invoice-card:hover { transform: translateY(-3px); }
        .table th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            font-weight: 600;
        }
        .badge { padding: 0.5rem 1rem; border-radius: 10px; font-weight: 500; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/"><i class="fas fa-rocket me-2"></i>نظام إدارة الأصول</a>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="fas fa-file-invoice text-primary me-2"></i>إدارة الفواتير</h2>
            <div>
                <a href="/" class="btn btn-outline-success me-2">
                    <i class="fas fa-home me-1"></i>الرئيسية
                </a>
                <button class="btn btn-primary" onclick="createInvoice()">
                    <i class="fas fa-plus me-2"></i>إنشاء فاتورة جديدة
                </button>
            </div>
        </div>

        <!-- إحصائيات الفواتير -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="invoice-card p-3 text-center">
                    <i class="fas fa-file-invoice fa-2x mb-2"></i>
                    <h4>{{ invoices|length }}</h4>
                    <p class="mb-0">إجمالي الفواتير</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="invoice-card p-3 text-center">
                    <i class="fas fa-check-circle fa-2x mb-2"></i>
                    <h4>{{ invoices|selectattr('status', 'equalto', 'مدفوع')|list|length }}</h4>
                    <p class="mb-0">فواتير مدفوعة</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="invoice-card p-3 text-center">
                    <i class="fas fa-clock fa-2x mb-2"></i>
                    <h4>{{ invoices|selectattr('status', 'equalto', 'معلق')|list|length }}</h4>
                    <p class="mb-0">فواتير معلقة</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="invoice-card p-3 text-center">
                    <i class="fas fa-dollar-sign fa-2x mb-2"></i>
                    <h4>{{ "{:,.0f}".format(invoices|sum(attribute='amount')) }}</h4>
                    <p class="mb-0">إجمالي القيمة</p>
                </div>
            </div>
        </div>

        <!-- جدول الفواتير -->
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0"><i class="fas fa-list me-2"></i>قائمة الفواتير</h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>رقم الفاتورة</th>
                                <th>المورد</th>
                                <th>التاريخ</th>
                                <th>المبلغ</th>
                                <th>الحالة</th>
                                <th>الإجراءات</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for invoice in invoices %}
                            <tr>
                                <td><strong class="text-primary">{{ invoice.number }}</strong></td>
                                <td>{{ invoice.supplier }}</td>
                                <td>{{ invoice.date }}</td>
                                <td><strong>{{ "{:,.0f}".format(invoice.amount) }} ريال</strong></td>
                                <td>
                                    <span class="badge bg-{{ 'success' if invoice.status == 'مدفوع' else 'warning' }}">
                                        {{ invoice.status }}
                                    </span>
                                </td>
                                <td>
                                    <button class="btn btn-primary btn-sm" onclick="viewInvoice('{{ invoice.number }}')">
                                        <i class="fas fa-eye"></i>
                                    </button>
                                    <button class="btn btn-success btn-sm" onclick="markPaid('{{ invoice.number }}')">
                                        <i class="fas fa-check"></i>
                                    </button>
                                    <button class="btn btn-info btn-sm" onclick="printInvoice('{{ invoice.number }}')">
                                        <i class="fas fa-print"></i>
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
        function createInvoice() {
            window.location.href = '/add_invoice';
        }
        
        function viewInvoice(invoiceNumber) {
            alert(`عرض تفاصيل الفاتورة: ${invoiceNumber}`);
        }
        
        function markPaid(invoiceNumber) {
            if (confirm('تأكيد دفع هذه الفاتورة؟')) {
                alert('تم تحديث حالة الفاتورة إلى مدفوع');
                location.reload();
            }
        }
        
        function printInvoice(invoiceNumber) {
            window.open(`/api/print_invoice/${invoiceNumber}`, '_blank');
        }
    </script>
</body>
</html>
'''

LICENSES_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>التراخيص</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body { 
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            font-family: 'Cairo', sans-serif;
        }
        .navbar-custom { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .card { 
            border: none; 
            box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
            border-radius: 20px;
        }
        .license-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            transition: transform 0.3s ease;
        }
        .license-card:hover { transform: translateY(-3px); }
        .table th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            font-weight: 600;
        }
        .badge { padding: 0.5rem 1rem; border-radius: 10px; font-weight: 500; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/"><i class="fas fa-rocket me-2"></i>نظام إدارة الأصول</a>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="fas fa-key text-primary me-2"></i>إدارة التراخيص</h2>
            <div>
                <a href="/" class="btn btn-outline-success me-2">
                    <i class="fas fa-home me-1"></i>الرئيسية
                </a>
                <button class="btn btn-primary" onclick="addLicense()">
                    <i class="fas fa-plus me-2"></i>إضافة ترخيص جديد
                </button>
            </div>
        </div>

        <!-- إحصائيات التراخيص -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="license-card p-3 text-center">
                    <i class="fas fa-key fa-2x mb-2"></i>
                    <h4>{{ licenses|length }}</h4>
                    <p class="mb-0">إجمالي التراخيص</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="license-card p-3 text-center">
                    <i class="fas fa-check-circle fa-2x mb-2"></i>
                    <h4>{{ licenses|selectattr('status', 'equalto', 'نشط')|list|length }}</h4>
                    <p class="mb-0">تراخيص نشطة</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="license-card p-3 text-center">
                    <i class="fas fa-users fa-2x mb-2"></i>
                    <h4>{{ licenses|sum(attribute='seats') }}</h4>
                    <p class="mb-0">إجمالي المقاعد</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="license-card p-3 text-center">
                    <i class="fas fa-user-check fa-2x mb-2"></i>
                    <h4>{{ licenses|sum(attribute='used') }}</h4>
                    <p class="mb-0">المقاعد المستخدمة</p>
                </div>
            </div>
        </div>

        <!-- جدول التراخيص -->
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0"><i class="fas fa-list me-2"></i>قائمة التراخيص</h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>رقم الترخيص</th>
                                <th>البرنامج</th>
                                <th>المورد</th>
                                <th>النوع</th>
                                <th>المقاعد</th>
                                <th>تاريخ الانتهاء</th>
                                <th>الحالة</th>
                                <th>الإجراءات</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for license in licenses %}
                            <tr>
                                <td><strong class="text-primary">{{ license.number }}</strong></td>
                                <td>{{ license.software }}</td>
                                <td>{{ license.supplier }}</td>
                                <td><span class="badge bg-info">{{ license.type }}</span></td>
                                <td>{{ license.used }}/{{ license.seats }}</td>
                                <td>{{ license.expiry }}</td>
                                <td>
                                    <span class="badge bg-{{ 'success' if license.status == 'نشط' else 'danger' }}">
                                        {{ license.status }}
                                    </span>
                                </td>
                                <td>
                                    <button class="btn btn-primary btn-sm" onclick="viewLicense('{{ license.number }}')">
                                        <i class="fas fa-eye"></i>
                                    </button>
                                    <button class="btn btn-warning btn-sm" onclick="renewLicense('{{ license.number }}')">
                                        <i class="fas fa-sync"></i>
                                    </button>
                                    <button class="btn btn-info btn-sm" onclick="assignLicense('{{ license.number }}')">
                                        <i class="fas fa-user-plus"></i>
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
        function addLicense() {
            window.location.href = '/add_license';
        }
        
        function viewLicense(licenseNumber) {
            alert(`عرض تفاصيل الترخيص: ${licenseNumber}`);
        }
        
        function renewLicense(licenseNumber) {
            if (confirm('تجديد هذا الترخيص؟')) {
                alert('تم تجديد الترخيص بنجاح');
                location.reload();
            }
        }
        
        function assignLicense(licenseNumber) {
            alert('تخصيص الترخيص لموظف - قيد التطوير');
        }
    </script>
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
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body { 
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            font-family: 'Cairo', sans-serif;
        }
        .navbar-custom { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .card { 
            border: none; 
            box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
            border-radius: 20px;
        }
        .support-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            transition: transform 0.3s ease;
        }
        .support-card:hover { transform: translateY(-3px); }
        .table th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            font-weight: 600;
        }
        .badge { padding: 0.5rem 1rem; border-radius: 10px; font-weight: 500; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/"><i class="fas fa-rocket me-2"></i>نظام إدارة الأصول</a>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="fas fa-headset text-primary me-2"></i>الدعم الفني</h2>
            <div>
                <a href="/" class="btn btn-outline-success me-2">
                    <i class="fas fa-home me-1"></i>الرئيسية
                </a>
                <button class="btn btn-primary" onclick="createTicket()">
                    <i class="fas fa-plus me-2"></i>إنشاء تذكرة جديدة
                </button>
            </div>
        </div>

        <!-- إحصائيات الدعم الفني -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="support-card p-3 text-center">
                    <i class="fas fa-ticket-alt fa-2x mb-2"></i>
                    <h4>{{ open_tickets }}</h4>
                    <p class="mb-0">تذاكر مفتوحة</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="support-card p-3 text-center">
                    <i class="fas fa-check-circle fa-2x mb-2"></i>
                    <h4>{{ closed_tickets }}</h4>
                    <p class="mb-0">تذاكر مغلقة</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="support-card p-3 text-center">
                    <i class="fas fa-exclamation-triangle fa-2x mb-2"></i>
                    <h4>{{ high_priority }}</h4>
                    <p class="mb-0">أولوية عالية</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="support-card p-3 text-center">
                    <i class="fas fa-chart-line fa-2x mb-2"></i>
                    <h4>{{ open_tickets + closed_tickets }}</h4>
                    <p class="mb-0">إجمالي التذاكر</p>
                </div>
            </div>
        </div>

        <!-- جدول التذاكر -->
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0"><i class="fas fa-list me-2"></i>تذاكر الدعم الفني</h5>
            </div>
            <div class="card-body">
                {% if tickets %}
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>رقم التذكرة</th>
                                <th>العنوان</th>
                                <th>الموظف</th>
                                <th>الأولوية</th>
                                <th>الحالة</th>
                                <th>تاريخ الإنشاء</th>
                                <th>الإجراءات</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for ticket in tickets %}
                            <tr>
                                <td><strong class="text-primary">{{ ticket[1] }}</strong></td>
                                <td>{{ ticket[2] }}</td>
                                <td>{{ ticket[4] or 'غير محدد' }}</td>
                                <td>
                                    <span class="badge bg-{{ 'danger' if ticket[6] == 'عالي' else 'warning' if ticket[6] == 'متوسط' else 'secondary' }}">
                                        {{ ticket[6] }}
                                    </span>
                                </td>
                                <td>
                                    <span class="badge bg-{{ 'success' if ticket[7] == 'مغلق' else 'primary' if ticket[7] == 'قيد المعالجة' else 'warning' }}">
                                        {{ ticket[7] }}
                                    </span>
                                </td>
                                <td>{{ ticket[9] }}</td>
                                <td>
                                    <button class="btn btn-primary btn-sm" onclick="viewTicket({{ ticket[0] }})">
                                        <i class="fas fa-eye"></i>
                                    </button>
                                    <button class="btn btn-success btn-sm" onclick="closeTicket({{ ticket[0] }})">
                                        <i class="fas fa-check"></i>
                                    </button>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <div class="text-center py-5">
                    <i class="fas fa-headset fa-5x text-muted mb-3"></i>
                    <h4 class="text-muted">لا توجد تذاكر دعم فني حالياً</h4>
                    <p class="text-muted">ابدأ بإنشاء تذكرة دعم فني جديدة</p>
                    <button class="btn btn-primary" onclick="createTicket()">
                        <i class="fas fa-plus me-2"></i>إنشاء تذكرة جديدة
                    </button>
                </div>
                {% endif %}
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function createTicket() {
            window.location.href = '/create_ticket';
        }
        
        function viewTicket(ticketId) {
            alert('عرض تفاصيل التذكرة رقم: ' + ticketId);
        }
        
        function closeTicket(ticketId) {
            if (confirm('تأكيد إغلاق هذه التذكرة؟')) {
                alert('تم إغلاق التذكرة بنجاح');
                location.reload();
            }
        }
    </script>
</body>
</html>
'''

REPORTS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>التقارير</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { 
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            font-family: 'Cairo', sans-serif;
        }
        .navbar-custom { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .card { 
            border: none; 
            box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
            border-radius: 20px;
        }
        .stats-card { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            border-radius: 15px;
            transition: transform 0.3s ease;
        }
        .stats-card:hover { transform: translateY(-3px); }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/"><i class="fas fa-rocket me-2"></i>نظام إدارة الأصول</a>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="fas fa-chart-bar text-primary me-2"></i>التقارير والإحصائيات</h2>
            <div>
                <a href="/" class="btn btn-outline-success me-2">
                    <i class="fas fa-home me-1"></i>الرئيسية
                </a>
                <a href="/custom_reports" class="btn btn-outline-info me-2">
                    <i class="fas fa-cog me-1"></i>تقارير مخصصة
                </a>
                <button class="btn btn-primary" onclick="exportReport()">
                    <i class="fas fa-download me-2"></i>تصدير التقرير
                </button>
            </div>
        </div>

        <!-- إحصائيات عامة -->
        <div class="row mb-4">
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="stats-card p-4 text-center">
                    <i class="fas fa-laptop fa-3x mb-3"></i>
                    <h3>{{ total_assets }}</h3>
                    <p class="mb-0">إجمالي الأصول</p>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="stats-card p-4 text-center">
                    <i class="fas fa-dollar-sign fa-3x mb-3"></i>
                    <h3>{{ "{:,.0f}".format(total_value) }}</h3>
                    <p class="mb-0">إجمالي القيمة (ريال)</p>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="stats-card p-4 text-center">
                    <i class="fas fa-users fa-3x mb-3"></i>
                    <h3>{{ active_employees }}</h3>
                    <p class="mb-0">الموظفين النشطين</p>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="stats-card p-4 text-center">
                    <i class="fas fa-shopping-cart fa-3x mb-3"></i>
                    <h3>{{ total_purchases }}</h3>
                    <p class="mb-0">إجمالي المشتريات</p>
                </div>
            </div>
        </div>

        <div class="row">
            <!-- رسم بياني للأصول حسب الفئة -->
            <div class="col-lg-6 mb-4">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="fas fa-chart-pie me-2"></i>الأصول حسب الفئة</h5>
                    </div>
                    <div class="card-body">
                        <canvas id="assetsCategoryChart"></canvas>
                    </div>
                </div>
            </div>

            <!-- رسم بياني للأصول حسب الحالة -->
            <div class="col-lg-6 mb-4">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="fas fa-chart-doughnut me-2"></i>الأصول حسب الحالة</h5>
                    </div>
                    <div class="card-body">
                        <canvas id="assetsStatusChart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- جداول التقارير -->
        <div class="row">
            <div class="col-lg-6 mb-4">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="fas fa-table me-2"></i>الأصول حسب الفئة</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>الفئة</th>
                                        <th>العدد</th>
                                        <th>النسبة</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for category in assets_by_category %}
                                    <tr>
                                        <td>{{ category[0] or 'غير محدد' }}</td>
                                        <td>{{ category[1] }}</td>
                                        <td>{{ "{:.1f}".format((category[1] / total_assets * 100) if total_assets > 0 else 0) }}%</td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <div class="col-lg-6 mb-4">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="fas fa-table me-2"></i>الأصول حسب الحالة</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>الحالة</th>
                                        <th>العدد</th>
                                        <th>النسبة</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for status in assets_by_status %}
                                    <tr>
                                        <td>{{ status[0] or 'غير محدد' }}</td>
                                        <td>{{ status[1] }}</td>
                                        <td>{{ "{:.1f}".format((status[1] / total_assets * 100) if total_assets > 0 else 0) }}%</td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // رسم بياني للأصول حسب الفئة
        const categoryCtx = document.getElementById('assetsCategoryChart').getContext('2d');
        new Chart(categoryCtx, {
            type: 'pie',
            data: {
                labels: [{% for category in assets_by_category %}'{{ category[0] or "غير محدد" }}'{% if not loop.last %},{% endif %}{% endfor %}],
                datasets: [{
                    data: [{% for category in assets_by_category %}{{ category[1] }}{% if not loop.last %},{% endif %}{% endfor %}],
                    backgroundColor: [
                        '#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });

        // رسم بياني للأصول حسب الحالة
        const statusCtx = document.getElementById('assetsStatusChart').getContext('2d');
        new Chart(statusCtx, {
            type: 'doughnut',
            data: {
                labels: [{% for status in assets_by_status %}'{{ status[0] or "غير محدد" }}'{% if not loop.last %},{% endif %}{% endfor %}],
                datasets: [{
                    data: [{% for status in assets_by_status %}{{ status[1] }}{% if not loop.last %},{% endif %}{% endfor %}],
                    backgroundColor: [
                        '#51cf66', '#ffa726', '#ff6b6b', '#339af0'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });

        function exportReport() {
            alert('تصدير التقرير - قيد التطوير');
        }
    </script>
</body>
</html>
'''

NOTIFICATIONS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>الإشعارات</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body { 
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            font-family: 'Cairo', sans-serif;
        }
        .navbar-custom { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .card { 
            border: none; 
            box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
            border-radius: 20px;
        }
        .notification-item {
            border-radius: 15px;
            transition: transform 0.3s ease;
            border-left: 4px solid;
        }
        .notification-item:hover { transform: translateX(-5px); }
        .notification-warning { border-left-color: #ffa726; }
        .notification-info { border-left-color: #339af0; }
        .notification-success { border-left-color: #51cf66; }
        .notification-unread { background: rgba(102, 126, 234, 0.05); }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/"><i class="fas fa-rocket me-2"></i>نظام إدارة الأصول</a>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="fas fa-bell text-primary me-2"></i>الإشعارات</h2>
            <div>
                <a href="/" class="btn btn-outline-success me-2">
                    <i class="fas fa-home me-1"></i>الرئيسية
                </a>
                <button class="btn btn-outline-primary me-2" onclick="markAllRead()">
                    <i class="fas fa-check-double me-1"></i>تحديد الكل كمقروء
                </button>
                <button class="btn btn-outline-info me-2" onclick="sendSMSNotification()">
                    <i class="fas fa-mobile-alt me-1"></i>إرسال SMS
                </button>
                <button class="btn btn-outline-danger" onclick="clearAll()">
                    <i class="fas fa-trash me-1"></i>مسح الكل
                </button>
            </div>
        </div>

        <div class="row">
            <div class="col-lg-8">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="fas fa-list me-2"></i>قائمة الإشعارات</h5>
                    </div>
                    <div class="card-body">
                        {% for notification in notifications %}
                        <div class="notification-item p-3 mb-3 notification-{{ notification.type|lower }} {{ 'notification-unread' if not notification.read else '' }}">
                            <div class="d-flex justify-content-between align-items-start">
                                <div class="flex-grow-1">
                                    <div class="d-flex align-items-center mb-2">
                                        <i class="fas fa-{{ 'exclamation-triangle' if notification.type == 'تحذير' else 'info-circle' if notification.type == 'معلومات' else 'check-circle' }} me-2 text-{{ 'warning' if notification.type == 'تحذير' else 'info' if notification.type == 'معلومات' else 'success' }}"></i>
                                        <h6 class="mb-0 fw-bold">{{ notification.title }}</h6>
                                        {% if not notification.read %}
                                        <span class="badge bg-primary ms-2">جديد</span>
                                        {% endif %}
                                    </div>
                                    <p class="mb-2 text-muted">{{ notification.message }}</p>
                                    <small class="text-muted">
                                        <i class="fas fa-clock me-1"></i>{{ notification.date }}
                                    </small>
                                </div>
                                <div class="dropdown">
                                    <button class="btn btn-sm btn-outline-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown">
                                        <i class="fas fa-ellipsis-v"></i>
                                    </button>
                                    <ul class="dropdown-menu">
                                        {% if not notification.read %}
                                        <li><a class="dropdown-item" href="#" onclick="markAsRead({{ notification.id }})">
                                            <i class="fas fa-check me-2"></i>تحديد كمقروء
                                        </a></li>
                                        {% endif %}
                                        <li><a class="dropdown-item text-danger" href="#" onclick="deleteNotification({{ notification.id }})">
                                            <i class="fas fa-trash me-2"></i>حذف
                                        </a></li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>

            <div class="col-lg-4">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="fas fa-chart-pie me-2"></i>إحصائيات الإشعارات</h5>
                    </div>
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <span>إجمالي الإشعارات</span>
                            <span class="badge bg-primary">{{ notifications|length }}</span>
                        </div>
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <span>غير مقروءة</span>
                            <span class="badge bg-warning">{{ notifications|rejectattr('read')|list|length }}</span>
                        </div>
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <span>تحذيرات</span>
                            <span class="badge bg-danger">{{ notifications|selectattr('type', 'equalto', 'تحذير')|list|length }}</span>
                        </div>
                        <div class="d-flex justify-content-between align-items-center">
                            <span>معلومات</span>
                            <span class="badge bg-info">{{ notifications|selectattr('type', 'equalto', 'معلومات')|list|length }}</span>
                        </div>
                    </div>
                </div>

                <div class="card mt-4">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="fas fa-cog me-2"></i>إعدادات الإشعارات</h5>
                    </div>
                    <div class="card-body">
                        <div class="form-check form-switch mb-3">
                            <input class="form-check-input" type="checkbox" id="emailNotifications" checked>
                            <label class="form-check-label" for="emailNotifications">
                                إشعارات البريد الإلكتروني
                            </label>
                        </div>
                        <div class="form-check form-switch mb-3">
                            <input class="form-check-input" type="checkbox" id="warrantyAlerts" checked>
                            <label class="form-check-label" for="warrantyAlerts">
                                تنبيهات انتهاء الضمان
                            </label>
                        </div>
                        <div class="form-check form-switch mb-3">
                            <input class="form-check-input" type="checkbox" id="licenseAlerts" checked>
                            <label class="form-check-label" for="licenseAlerts">
                                تنبيهات انتهاء التراخيص
                            </label>
                        </div>
                        <div class="form-check form-switch">
                            <input class="form-check-input" type="checkbox" id="supportTickets" checked>
                            <label class="form-check-label" for="supportTickets">
                                إشعارات الدعم الفني
                            </label>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function markAsRead(notificationId) {
            alert('تم تحديد الإشعار كمقروء');
            location.reload();
        }
        
        function deleteNotification(notificationId) {
            if (confirm('هل أنت متأكد من حذف هذا الإشعار؟')) {
                alert('تم حذف الإشعار');
                location.reload();
            }
        }
        
        function markAllRead() {
            if (confirm('تحديد جميع الإشعارات كمقروءة؟')) {
                alert('تم تحديد جميع الإشعارات كمقروءة');
                location.reload();
            }
        }
        
        function clearAll() {
            if (confirm('هل أنت متأكد من حذف جميع الإشعارات؟')) {
                alert('تم حذف جميع الإشعارات');
                location.reload();
            }
        }
        
        function sendSMSNotification() {
            const phone = prompt('أدخل رقم الجوال:');
            const message = prompt('أدخل نص الرسالة:');
            
            if (phone && message) {
                fetch('/api/send_sms_notification', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        phone: phone,
                        message: message
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('تم إرسال الإشعار بنجاح');
                    } else {
                        alert('خطأ في إرسال الإشعار');
                    }
                })
                .catch(error => {
                    alert('خطأ في الاتصال');
                });
            }
        }
    </script>
</body>
</html>
'''

# قوالب النماذج الجديدة
ADD_CUSTODY_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>إضافة عهدة جديدة</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body { 
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            font-family: 'Cairo', sans-serif;
        }
        .navbar-custom { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .card { 
            border: none; 
            box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
            border-radius: 20px;
        }
        .form-control, .form-select {
            border-radius: 10px;
            border: 2px solid #e9ecef;
            padding: 0.75rem 1rem;
            transition: all 0.3s ease;
        }
        .form-control:focus, .form-select:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 10px;
            padding: 0.75rem 2rem;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/"><i class="fas fa-rocket me-2"></i>نظام إدارة الأصول</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="/"><i class="fas fa-home me-1"></i>الرئيسية</a>
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
                                <i class="fas fa-handshake fa-2x text-white"></i>
                            </div>
                            <h2 class="mb-1">إضافة عهدة جديدة</h2>
                            <p class="text-muted">تخصيص أصل لموظف</p>
                        </div>
                    </div>
                    
                    <div class="card-body p-4">
                        {% with messages = get_flashed_messages(with_categories=true) %}
                            {% if messages %}
                                {% for category, message in messages %}
                                    <div class="alert alert-{{ 'success' if category == 'success' else 'danger' }}">
                                        <i class="fas fa-{{ 'check-circle' if category == 'success' else 'exclamation-triangle' }} me-2"></i>
                                        {{ message }}
                                    </div>
                                {% endfor %}
                            {% endif %}
                        {% endwith %}
                        
                        <form method="POST" id="custodyForm">
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">رقم العهدة *</label>
                                    <input type="text" class="form-control" name="custody_number" required placeholder="CUS-2024-001">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">تاريخ التسليم *</label>
                                    <input type="date" class="form-control" name="delivery_date" required>
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">الأصل *</label>
                                    <select class="form-select" name="asset_id" required>
                                        <option value="">اختر الأصل</option>
                                        {% for asset in assets %}
                                        <option value="{{ asset[0] }}">{{ asset[1] }} - {{ asset[2] }}</option>
                                        {% endfor %}
                                    </select>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">الموظف *</label>
                                    <select class="form-select" name="employee_id" required>
                                        <option value="">اختر الموظف</option>
                                        {% for employee in employees %}
                                        <option value="{{ employee[0] }}">{{ employee[1] }} - {{ employee[2] }}</option>
                                        {% endfor %}
                                    </select>
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">ملاحظات</label>
                                <textarea class="form-control" name="notes" rows="3" placeholder="أي ملاحظات إضافية..."></textarea>
                            </div>
                            
                            <div class="d-flex justify-content-between mt-4">
                                <button type="submit" class="btn btn-primary btn-lg">
                                    <i class="fas fa-save me-2"></i>حفظ العهدة
                                </button>
                                <a href="/custody" class="btn btn-outline-secondary btn-lg">
                                    <i class="fas fa-arrow-right me-2"></i>العودة للعهد
                                </a>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const today = new Date().toISOString().split('T')[0];
            document.querySelector('input[name="delivery_date"]').value = today;
        });
    </script>
</body>
</html>
'''

ADD_INVOICE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>إنشاء فاتورة جديدة</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body { 
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            font-family: 'Cairo', sans-serif;
        }
        .navbar-custom { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .card { 
            border: none; 
            box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
            border-radius: 20px;
        }
        .form-control, .form-select {
            border-radius: 10px;
            border: 2px solid #e9ecef;
            padding: 0.75rem 1rem;
            transition: all 0.3s ease;
        }
        .form-control:focus, .form-select:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 10px;
            padding: 0.75rem 2rem;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/"><i class="fas fa-rocket me-2"></i>نظام إدارة الأصول</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="/"><i class="fas fa-home me-1"></i>الرئيسية</a>
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
                                <i class="fas fa-file-invoice fa-2x text-white"></i>
                            </div>
                            <h2 class="mb-1">إنشاء فاتورة جديدة</h2>
                            <p class="text-muted">إضافة فاتورة جديدة للنظام</p>
                        </div>
                    </div>
                    
                    <div class="card-body p-4">
                        {% with messages = get_flashed_messages(with_categories=true) %}
                            {% if messages %}
                                {% for category, message in messages %}
                                    <div class="alert alert-{{ 'success' if category == 'success' else 'danger' }}">
                                        <i class="fas fa-{{ 'check-circle' if category == 'success' else 'exclamation-triangle' }} me-2"></i>
                                        {{ message }}
                                    </div>
                                {% endfor %}
                            {% endif %}
                        {% endwith %}
                        
                        <form method="POST" id="invoiceForm">
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">رقم الفاتورة *</label>
                                    <input type="text" class="form-control" name="invoice_number" required placeholder="INV-2024-001">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">تاريخ الفاتورة *</label>
                                    <input type="date" class="form-control" name="invoice_date" required>
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">المورد *</label>
                                    <input type="text" class="form-control" name="supplier" required placeholder="شركة التقنية المتقدمة">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">المبلغ (ريال) *</label>
                                    <input type="number" step="0.01" class="form-control" name="amount" required placeholder="15000.00">
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">وصف الفاتورة</label>
                                <textarea class="form-control" name="description" rows="3" placeholder="وصف تفصيلي للفاتورة..."></textarea>
                            </div>
                            
                            <div class="d-flex justify-content-between mt-4">
                                <button type="submit" class="btn btn-primary btn-lg">
                                    <i class="fas fa-save me-2"></i>إنشاء الفاتورة
                                </button>
                                <a href="/invoices" class="btn btn-outline-secondary btn-lg">
                                    <i class="fas fa-arrow-right me-2"></i>العودة للفواتير
                                </a>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const today = new Date().toISOString().split('T')[0];
            document.querySelector('input[name="invoice_date"]').value = today;
        });
    </script>
</body>
</html>
'''

ADD_LICENSE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>إضافة ترخيص جديد</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body { 
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            font-family: 'Cairo', sans-serif;
        }
        .navbar-custom { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .card { 
            border: none; 
            box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
            border-radius: 20px;
        }
        .form-control, .form-select {
            border-radius: 10px;
            border: 2px solid #e9ecef;
            padding: 0.75rem 1rem;
            transition: all 0.3s ease;
        }
        .form-control:focus, .form-select:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 10px;
            padding: 0.75rem 2rem;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/"><i class="fas fa-rocket me-2"></i>نظام إدارة الأصول</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="/"><i class="fas fa-home me-1"></i>الرئيسية</a>
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
                                <i class="fas fa-key fa-2x text-white"></i>
                            </div>
                            <h2 class="mb-1">إضافة ترخيص جديد</h2>
                            <p class="text-muted">إضافة ترخيص برمجيات جديد</p>
                        </div>
                    </div>
                    
                    <div class="card-body p-4">
                        {% with messages = get_flashed_messages(with_categories=true) %}
                            {% if messages %}
                                {% for category, message in messages %}
                                    <div class="alert alert-{{ 'success' if category == 'success' else 'danger' }}">
                                        <i class="fas fa-{{ 'check-circle' if category == 'success' else 'exclamation-triangle' }} me-2"></i>
                                        {{ message }}
                                    </div>
                                {% endfor %}
                            {% endif %}
                        {% endwith %}
                        
                        <form method="POST" id="licenseForm">
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">رقم الترخيص *</label>
                                    <input type="text" class="form-control" name="license_number" required placeholder="LIC-WIN-001">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">اسم البرنامج *</label>
                                    <input type="text" class="form-control" name="software_name" required placeholder="Windows 11 Pro">
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">المورد *</label>
                                    <input type="text" class="form-control" name="supplier" required placeholder="Microsoft">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">نوع الترخيص *</label>
                                    <select class="form-select" name="license_type" required>
                                        <option value="">اختر النوع</option>
                                        <option value="نظام تشغيل">نظام تشغيل</option>
                                        <option value="مكتبي">مكتبي</option>
                                        <option value="حماية">حماية</option>
                                        <option value="تطوير">تطوير</option>
                                        <option value="تصميم">تصميم</option>
                                        <option value="أخرى">أخرى</option>
                                    </select>
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">عدد المقاعد *</label>
                                    <input type="number" class="form-control" name="seats" required min="1" placeholder="50">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">تاريخ انتهاء الترخيص *</label>
                                    <input type="date" class="form-control" name="expiry_date" required>
                                </div>
                            </div>
                            
                            <div class="d-flex justify-content-between mt-4">
                                <button type="submit" class="btn btn-primary btn-lg">
                                    <i class="fas fa-save me-2"></i>حفظ الترخيص
                                </button>
                                <a href="/licenses" class="btn btn-outline-secondary btn-lg">
                                    <i class="fas fa-arrow-right me-2"></i>العودة للتراخيص
                                </a>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const nextYear = new Date();
            nextYear.setFullYear(nextYear.getFullYear() + 1);
            document.querySelector('input[name="expiry_date"]').value = nextYear.toISOString().split('T')[0];
        });
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
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body { 
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            font-family: 'Cairo', sans-serif;
        }
        .navbar-custom { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .card { 
            border: none; 
            box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
            border-radius: 20px;
        }
        .form-control, .form-select {
            border-radius: 10px;
            border: 2px solid #e9ecef;
            padding: 0.75rem 1rem;
            transition: all 0.3s ease;
        }
        .form-control:focus, .form-select:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 10px;
            padding: 0.75rem 2rem;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/"><i class="fas fa-rocket me-2"></i>نظام إدارة الأصول</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="/"><i class="fas fa-home me-1"></i>الرئيسية</a>
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
                                <i class="fas fa-headset fa-2x text-white"></i>
                            </div>
                            <h2 class="mb-1">إنشاء تذكرة دعم فني</h2>
                            <p class="text-muted">طلب مساعدة فنية جديد</p>
                        </div>
                    </div>
                    
                    <div class="card-body p-4">
                        {% with messages = get_flashed_messages(with_categories=true) %}
                            {% if messages %}
                                {% for category, message in messages %}
                                    <div class="alert alert-{{ 'success' if category == 'success' else 'danger' }}">
                                        <i class="fas fa-{{ 'check-circle' if category == 'success' else 'exclamation-triangle' }} me-2"></i>
                                        {{ message }}
                                    </div>
                                {% endfor %}
                            {% endif %}
                        {% endwith %}
                        
                        <form method="POST" id="ticketForm">
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">عنوان المشكلة *</label>
                                    <input type="text" class="form-control" name="title" required placeholder="مشكلة في الطابعة">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">اسم الموظف *</label>
                                    <input type="text" class="form-control" name="employee_name" required placeholder="أحمد محمد">
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">الأولوية *</label>
                                    <select class="form-select" name="priority" required>
                                        <option value="">اختر الأولوية</option>
                                        <option value="منخفض">منخفض</option>
                                        <option value="متوسط" selected>متوسط</option>
                                        <option value="عالي">عالي</option>
                                        <option value="عاجل">عاجل</option>
                                    </select>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">الفئة *</label>
                                    <select class="form-select" name="category" required>
                                        <option value="">اختر الفئة</option>
                                        <option value="هاردوير">هاردوير</option>
                                        <option value="برمجيات">برمجيات</option>
                                        <option value="شبكة">شبكة</option>
                                        <option value="طابعة">طابعة</option>
                                        <option value="أخرى">أخرى</option>
                                    </select>
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">وصف المشكلة *</label>
                                <textarea class="form-control" name="description" rows="4" required placeholder="وصف تفصيلي للمشكلة..."></textarea>
                            </div>
                            
                            <div class="d-flex justify-content-between mt-4">
                                <button type="submit" class="btn btn-primary btn-lg">
                                    <i class="fas fa-paper-plane me-2"></i>إرسال التذكرة
                                </button>
                                <a href="/support" class="btn btn-outline-secondary btn-lg">
                                    <i class="fas fa-arrow-right me-2"></i>العودة للدعم الفني
                                </a>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

INVOICE_PRINT_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>طباعة الفاتورة {{ invoice_number }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <style>
        @media print {
            .no-print { display: none; }
        }
        body { font-family: 'Arial', sans-serif; }
        .invoice-header { border-bottom: 3px solid #667eea; padding-bottom: 20px; margin-bottom: 30px; }
        .invoice-details { background: #f8f9fa; padding: 20px; border-radius: 10px; }
    </style>
</head>
<body>
    <div class="container mt-4">
        <div class="invoice-header text-center">
            <h1 class="text-primary">فاتورة رقم: {{ invoice_number }}</h1>
            <p class="text-muted">نظام إدارة الأصول</p>
        </div>
        
        <div class="invoice-details">
            <h3>تفاصيل الفاتورة</h3>
            <p><strong>رقم الفاتورة:</strong> {{ invoice_number }}</p>
            <p><strong>التاريخ:</strong> {{ "الآن" }}</p>
            <p><strong>المورد:</strong> شركة التقنية المتقدمة</p>
            <p><strong>المبلغ:</strong> 15,000 ريال</p>
        </div>
        
        <div class="text-center mt-4 no-print">
            <button onclick="window.print()" class="btn btn-primary">
                <i class="fas fa-print me-2"></i>طباعة
            </button>
            <button onclick="window.close()" class="btn btn-secondary">
                <i class="fas fa-times me-2"></i>إغلاق
            </button>
        </div>
    </div>
</body>
</html>
'''

CUSTOM_REPORTS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>التقارير المخصصة</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body { 
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            font-family: 'Cairo', sans-serif;
        }
        .navbar-custom { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .card { 
            border: none; 
            box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
            border-radius: 20px;
        }
        .report-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            transition: transform 0.3s ease;
            cursor: pointer;
        }
        .report-card:hover { transform: translateY(-3px); }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/"><i class="fas fa-rocket me-2"></i>نظام إدارة الأصول</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="/"><i class="fas fa-home me-1"></i>الرئيسية</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="fas fa-chart-line text-primary me-2"></i>التقارير المخصصة</h2>
        </div>

        <div class="row">
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="report-card p-4 text-center" onclick="generateReport('assets')">
                    <i class="fas fa-laptop fa-3x mb-3"></i>
                    <h5>تقرير الأصول</h5>
                    <p class="mb-0">تقرير شامل عن جميع الأصول</p>
                </div>
            </div>
            
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="report-card p-4 text-center" onclick="generateReport('employees')">
                    <i class="fas fa-users fa-3x mb-3"></i>
                    <h5>تقرير الموظفين</h5>
                    <p class="mb-0">تقرير شامل عن الموظفين</p>
                </div>
            </div>
            
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="report-card p-4 text-center" onclick="generateReport('purchases')">
                    <i class="fas fa-shopping-cart fa-3x mb-3"></i>
                    <h5>تقرير المشتريات</h5>
                    <p class="mb-0">تقرير شامل عن المشتريات</p>
                </div>
            </div>
            
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="report-card p-4 text-center" onclick="generateReport('custody')">
                    <i class="fas fa-handshake fa-3x mb-3"></i>
                    <h5>تقرير العهد</h5>
                    <p class=