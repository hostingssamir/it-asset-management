#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نسخة ويب فورية مع التقارير - تعمل بنقرة واحدة
Instant Web Version with Reports - One-Click Launch
"""

import os
import sys
import sqlite3
import webbrowser
import threading
import time
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

def install_flask():
    """تثبيت Flask تلقائياً إذا لم يكن مثبت"""
    try:
        import flask
        return True
    except ImportError:
        print("📦 تثبيت Flask...")
        try:
            import subprocess
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'Flask', 'Werkzeug'])
            print("✅ تم تثبيت Flask بنجاح")
            return True
        except Exception as e:
            print(f"❌ فشل في تثبيت Flask: {e}")
            return False

def create_instant_database():
    """إنشاء قاعدة بيانات فورية"""
    db_path = 'instant_assets_reports.db'
    
    # حذف قاعدة البيانات القديمة
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # إنشاء الجداول
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_tag TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            category_id INTEGER,
            brand TEXT,
            model TEXT,
            serial_number TEXT,
            purchase_cost REAL,
            status TEXT DEFAULT 'active',
            condition_status TEXT DEFAULT 'good',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')
    
    # إدراج البيانات الافتراضية
    admin_password = generate_password_hash('admin123')
    cursor.execute('''
        INSERT INTO users (username, password_hash, full_name, role)
        VALUES (?, ?, ?, ?)
    ''', ('admin', admin_password, 'مدير النظام', 'admin'))
    
    # الفئات
    categories = [
        ('أجهزة الكمبيوتر', 'أجهزة الكمبيوتر المكتبية والمحمولة'),
        ('الخوادم', 'خوادم الشبكة وقواعد البيانات'),
        ('معدات الشبكة', 'أجهزة التوجيه والتبديل'),
        ('الطابعات', 'أجهزة الطباعة والمسح'),
        ('الهواتف', 'الهواتف الثابتة والذكية'),
        ('الشاشات', 'شاشات العرض والمراقيب'),
        ('التخزين', 'أجهزة التخزين الخارجية')
    ]
    
    for name, desc in categories:
        cursor.execute('INSERT INTO categories (name, description) VALUES (?, ?)', (name, desc))
    
    # أصول تجريبية متنوعة
    sample_assets = [
        ('PC001', 'جهاز كمبيوتر مكتبي', 'جهاز Dell للموظفين', 1, 'Dell', 'OptiPlex 7090', 'DL123456', 2500.00, 'active'),
        ('PC002', 'جهاز كمبيوتر مكتبي', 'جهاز HP للمحاسبة', 1, 'HP', 'EliteDesk 800', 'HP234567', 2200.00, 'active'),
        ('LP001', 'جهاز لابتوب', 'جهاز HP محمول للإدارة', 1, 'HP', 'EliteBook 840', 'HP789012', 3200.00, 'active'),
        ('LP002', 'جهاز لابتوب', 'جهاز Lenovo للمبيعات', 1, 'Lenovo', 'ThinkPad X1', 'LN345678', 4500.00, 'maintenance'),
        ('PR001', 'طابعة ليزر', 'طابعة Canon مكتبية', 4, 'Canon', 'LBP6030', 'CN345678', 800.00, 'active'),
        ('PR002', 'طابعة ملونة', 'طابعة HP ملونة', 4, 'HP', 'LaserJet Pro', 'HP456789', 1200.00, 'active'),
        ('SW001', 'جهاز تبديل شبكة', 'سويتش Cisco 24 منفذ', 3, 'Cisco', 'SG250-24', 'CS901234', 1500.00, 'active'),
        ('SW002', 'جهاز تبديل شبكة', 'سويتش TP-Link 16 منفذ', 3, 'TP-Link', 'TL-SG1016D', 'TP567890', 300.00, 'active'),
        ('SV001', 'خادم رئيسي', 'خادم Dell قاعدة البيانات', 2, 'Dell', 'PowerEdge R740', 'DL567890', 8500.00, 'active'),
        ('SV002', 'خادم ويب', 'خادم HP للتطبيقات', 2, 'HP', 'ProLiant DL380', 'HP678901', 6500.00, 'maintenance'),
        ('PH001', 'هاتف IP', 'هاتف مكتبي ذكي', 5, 'Cisco', 'IP Phone 8841', 'CS111222', 350.00, 'active'),
        ('PH002', 'هاتف IP', 'هاتف مؤتمرات', 5, 'Polycom', 'VVX 411', 'PL333444', 450.00, 'active'),
        ('RT001', 'جهاز توجيه', 'راوتر الشبكة الرئيسي', 3, 'Cisco', 'ISR 4331', 'CS333444', 2200.00, 'active'),
        ('TB001', 'جهاز تابلت', 'تابلت للعروض التقديمية', 1, 'Samsung', 'Galaxy Tab S8', 'SM555666', 1800.00, 'active'),
        ('MN001', 'شاشة عرض', 'شاشة Dell 24 بوصة', 6, 'Dell', 'UltraSharp U2419H', 'DL777888', 650.00, 'active'),
        ('MN002', 'شاشة عرض', 'شاشة LG 27 بوصة', 6, 'LG', '27UL500-W', 'LG999000', 750.00, 'active'),
        ('HD001', 'قرص صلب خارجي', 'قرص تخزين 2TB', 7, 'Seagate', 'Backup Plus', 'SG111222', 250.00, 'active'),
        ('HD002', 'قرص صلب خارجي', 'قرص تخزين 4TB', 7, 'WD', 'My Passport', 'WD333444', 400.00, 'retired')
    ]
    
    for asset in sample_assets:
        cursor.execute('''
            INSERT INTO assets (asset_tag, name, description, category_id, brand, model, serial_number, purchase_cost, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', asset)
    
    conn.commit()
    conn.close()
    
    print("✅ تم إنشاء قاعدة البيانات مع 18 أصل تجريبي")
    return db_path

def create_instant_app():
    """إنشاء تطبيق Flask فوري مع التقارير"""
    from flask import Flask, render_template_string, request, redirect, url_for, flash, session, Response
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'instant-asset-management-with-reports-2025'
    
    DB_PATH = 'instant_assets_reports.db'
    
    def get_db():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    
    def login_required(f):
        from functools import wraps
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    
    @app.route('/')
    def index():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        conn = get_db()
        
        # إحصائيات
        total_assets = conn.execute('SELECT COUNT(*) as count FROM assets').fetchone()['count']
        active_assets = conn.execute('SELECT COUNT(*) as count FROM assets WHERE status = "active"').fetchone()['count']
        categories_count = conn.execute('SELECT COUNT(*) as count FROM categories').fetchone()['count']
        
        # إحصائيات إضافية
        total_cost = conn.execute('SELECT SUM(purchase_cost) as total FROM assets WHERE purchase_cost IS NOT NULL').fetchone()['total'] or 0
        
        # الأصول الحديثة
        recent_assets = conn.execute('''
            SELECT a.*, c.name as category_name 
            FROM assets a 
            LEFT JOIN categories c ON a.category_id = c.id 
            ORDER BY a.created_at DESC 
            LIMIT 5
        ''').fetchall()
        
        # إحصائيات الفئات
        category_stats = conn.execute('''
            SELECT c.name, COUNT(a.id) as asset_count
            FROM categories c
            LEFT JOIN assets a ON c.id = a.category_id
            GROUP BY c.id, c.name
            ORDER BY asset_count DESC
        ''').fetchall()
        
        conn.close()
        
        return render_template_string(DASHBOARD_TEMPLATE, 
            total_assets=total_assets,
            active_assets=active_assets,
            categories_count=categories_count,
            total_cost=total_cost,
            recent_assets=recent_assets,
            category_stats=category_stats,
            user_name=session.get('user_name', 'المستخدم'))
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            conn = get_db()
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            conn.close()
            
            if user and check_password_hash(user['password_hash'], password):
                session['user_id'] = user['id']
                session['user_name'] = user['full_name']
                session['role'] = user['role']
                flash('مرحباً بك في نظام إدارة الأصول مع التقارير!', 'success')
                return redirect(url_for('index'))
            else:
                flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
        
        return render_template_string(LOGIN_TEMPLATE)
    
    @app.route('/logout')
    def logout():
        session.clear()
        flash('تم تسجيل الخروج بنجاح', 'success')
        return redirect(url_for('login'))
    
    @app.route('/assets')
    @login_required
    def assets():
        conn = get_db()
        assets = conn.execute('''
            SELECT a.*, c.name as category_name
            FROM assets a
            LEFT JOIN categories c ON a.category_id = c.id
            ORDER BY a.created_at DESC
        ''').fetchall()
        conn.close()
        
        return render_template_string(ASSETS_TEMPLATE, 
            assets=assets,
            user_name=session.get('user_name', 'المستخدم'))
    
    @app.route('/add_asset', methods=['GET', 'POST'])
    @login_required
    def add_asset():
        if request.method == 'POST':
            try:
                conn = get_db()
                
                conn.execute('''
                    INSERT INTO assets (asset_tag, name, description, category_id, brand, model, 
                                      serial_number, purchase_cost, status, condition_status, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    request.form['asset_tag'],
                    request.form['name'],
                    request.form.get('description', ''),
                    int(request.form['category_id']) if request.form['category_id'] else None,
                    request.form.get('brand', ''),
                    request.form.get('model', ''),
                    request.form.get('serial_number', ''),
                    float(request.form['purchase_cost']) if request.form.get('purchase_cost') else None,
                    request.form.get('status', 'active'),
                    request.form.get('condition_status', 'good'),
                    request.form.get('notes', '')
                ))
                
                conn.commit()
                conn.close()
                
                flash('تم إضافة الأصل بنجاح! 🎉', 'success')
                return redirect(url_for('assets'))
                
            except Exception as e:
                flash(f'خطأ في إضافة الأصل: {str(e)}', 'error')
        
        conn = get_db()
        categories = conn.execute('SELECT * FROM categories ORDER BY name').fetchall()
        conn.close()
        
        return render_template_string(ADD_ASSET_TEMPLATE, 
            categories=categories,
            user_name=session.get('user_name', 'المستخدم'))
    
    @app.route('/categories')
    @login_required
    def categories():
        conn = get_db()
        categories_with_count = conn.execute('''
            SELECT c.*, COUNT(a.id) as asset_count
            FROM categories c
            LEFT JOIN assets a ON c.id = a.category_id
            GROUP BY c.id, c.name, c.description
            ORDER BY c.name
        ''').fetchall()
        conn.close()
        
        return render_template_string(CATEGORIES_TEMPLATE, 
            categories=categories_with_count,
            user_name=session.get('user_name', 'المستخدم'))
    
    @app.route('/reports')
    @login_required
    def reports():
        """صفحة التقارير الرئيسية"""
        conn = get_db()
        
        # إحصائيات عامة
        total_assets = conn.execute('SELECT COUNT(*) as count FROM assets').fetchone()['count']
        active_assets = conn.execute('SELECT COUNT(*) as count FROM assets WHERE status = "active"').fetchone()['count']
        maintenance_assets = conn.execute('SELECT COUNT(*) as count FROM assets WHERE status = "maintenance"').fetchone()['count']
        retired_assets = conn.execute('SELECT COUNT(*) as count FROM assets WHERE status = "retired"').fetchone()['count']
        
        # إجمالي القيمة
        total_cost = conn.execute('SELECT SUM(purchase_cost) as total FROM assets WHERE purchase_cost IS NOT NULL').fetchone()['total'] or 0
        
        # إحصائيات الفئات
        category_stats = conn.execute('''
            SELECT c.name, c.id, COUNT(a.id) as asset_count, 
                   COALESCE(SUM(a.purchase_cost), 0) as total_value
            FROM categories c
            LEFT JOIN assets a ON c.id = a.category_id
            GROUP BY c.id, c.name
            ORDER BY asset_count DESC
        ''').fetchall()
        
        # إحصائيات العلامات التجارية
        brand_stats = conn.execute('''
            SELECT brand, COUNT(*) as count, 
                   COALESCE(SUM(purchase_cost), 0) as total_value
            FROM assets 
            WHERE brand IS NOT NULL AND brand != ''
            GROUP BY brand
            ORDER BY count DESC
            LIMIT 10
        ''').fetchall()
        
        # الأصول الأعلى قيمة
        expensive_assets = conn.execute('''
            SELECT a.*, c.name as category_name
            FROM assets a
            LEFT JOIN categories c ON a.category_id = c.id
            WHERE a.purchase_cost IS NOT NULL
            ORDER BY a.purchase_cost DESC
            LIMIT 10
        ''').fetchall()
        
        conn.close()
        
        return render_template_string(REPORTS_TEMPLATE,
            total_assets=total_assets,
            active_assets=active_assets,
            maintenance_assets=maintenance_assets,
            retired_assets=retired_assets,
            total_cost=total_cost,
            category_stats=category_stats,
            brand_stats=brand_stats,
            expensive_assets=expensive_assets,
            user_name=session.get('user_name', 'المستخدم'))
    
    @app.route('/reports/detailed')
    @login_required
    def detailed_report():
        """تقرير مفصل لجميع الأصول"""
        conn = get_db()
        
        # جلب جميع الأصول مع تفاصيلها
        assets = conn.execute('''
            SELECT a.*, c.name as category_name,
                   DATE(a.created_at) as purchase_date
            FROM assets a
            LEFT JOIN categories c ON a.category_id = c.id
            ORDER BY a.created_at DESC
        ''').fetchall()
        
        # إحصائيات إضافية
        stats = {
            'total_count': len(assets),
            'total_value': sum(float(asset['purchase_cost'] or 0) for asset in assets),
            'avg_value': 0,
            'active_count': len([a for a in assets if a['status'] == 'active']),
            'maintenance_count': len([a for a in assets if a['status'] == 'maintenance']),
            'retired_count': len([a for a in assets if a['status'] == 'retired'])
        }
        
        if stats['total_count'] > 0:
            stats['avg_value'] = stats['total_value'] / stats['total_count']
        
        conn.close()
        
        return render_template_string(DETAILED_REPORT_TEMPLATE,
            assets=assets,
            stats=stats,
            user_name=session.get('user_name', 'المستخدم'))
    
    @app.route('/reports/category/<int:category_id>')
    @login_required
    def category_report(category_id):
        """تقرير فئة محددة"""
        conn = get_db()
        
        # معلومات الفئة
        category = conn.execute('SELECT * FROM categories WHERE id = ?', (category_id,)).fetchone()
        if not category:
            flash('الفئة غير موجودة', 'error')
            return redirect(url_for('reports'))
        
        # أصول الفئة
        assets = conn.execute('''
            SELECT * FROM assets 
            WHERE category_id = ?
            ORDER BY created_at DESC
        ''', (category_id,)).fetchall()
        
        # إحصائيات الفئة
        stats = {
            'total_count': len(assets),
            'total_value': sum(float(asset['purchase_cost'] or 0) for asset in assets),
            'active_count': len([a for a in assets if a['status'] == 'active']),
            'maintenance_count': len([a for a in assets if a['status'] == 'maintenance']),
            'retired_count': len([a for a in assets if a['status'] == 'retired'])
        }
        
        conn.close()
        
        return render_template_string(CATEGORY_REPORT_TEMPLATE,
            category=category,
            assets=assets,
            stats=stats,
            user_name=session.get('user_name', 'المستخدم'))
    
    @app.route('/reports/export/csv')
    @login_required
    def export_csv():
        """تصدير التقرير كملف CSV"""
        import csv
        from io import StringIO
        
        conn = get_db()
        assets = conn.execute('''
            SELECT a.asset_tag, a.name, a.description, c.name as category,
                   a.brand, a.model, a.serial_number, a.purchase_cost,
                   a.status, a.condition_status, a.notes,
                   DATE(a.created_at) as created_date
            FROM assets a
            LEFT JOIN categories c ON a.category_id = c.id
            ORDER BY a.created_at DESC
        ''').fetchall()
        conn.close()
        
        # إنشاء ملف CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # كتابة العناوين
        writer.writerow([
            'رقم الأصل', 'الاسم', 'الوصف', 'الفئة', 'العلامة التجارية',
            'الموديل', 'الرقم التسلسلي', 'التكلفة', 'الحالة', 'حالة الجهاز',
            'ملاحظات', 'تاريخ الإضافة'
        ])
        
        # كتابة البيانات
        for asset in assets:
            writer.writerow([
                asset['asset_tag'] or '',
                asset['name'] or '',
                asset['description'] or '',
                asset['category'] or '',
                asset['brand'] or '',
                asset['model'] or '',
                asset['serial_number'] or '',
                asset['purchase_cost'] or '',
                asset['status'] or '',
                asset['condition_status'] or '',
                asset['notes'] or '',
                asset['created_date'] or ''
            ])
        
        output.seek(0)
        
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename=assets_report_{datetime.now().strftime("%Y%m%d")}.csv'
            }
        )
    
    @app.route('/reports/print')
    @login_required
    def print_report():
        """تقرير للطباعة"""
        conn = get_db()
        
        # جلب جميع الأصول
        assets = conn.execute('''
            SELECT a.*, c.name as category_name
            FROM assets a
            LEFT JOIN categories c ON a.category_id = c.id
            ORDER BY c.name, a.name
        ''').fetchall()
        
        # إحصائيات
        stats = {
            'total_assets': len(assets),
            'total_value': sum(float(asset['purchase_cost'] or 0) for asset in assets),
            'active_assets': len([a for a in assets if a['status'] == 'active']),
            'maintenance_assets': len([a for a in assets if a['status'] == 'maintenance']),
            'retired_assets': len([a for a in assets if a['status'] == 'retired'])
        }
        
        # إحصائيات الفئات
        category_stats = conn.execute('''
            SELECT c.name, COUNT(a.id) as count, 
                   COALESCE(SUM(a.purchase_cost), 0) as total_value
            FROM categories c
            LEFT JOIN assets a ON c.id = a.category_id
            GROUP BY c.id, c.name
            ORDER BY c.name
        ''').fetchall()
        
        conn.close()
        
        return render_template_string(PRINT_REPORT_TEMPLATE,
            assets=assets,
            stats=stats,
            category_stats=category_stats,
            report_date=datetime.now().strftime('%Y-%m-%d'),
            user_name=session.get('user_name', 'المستخدم'))
    
    return app

# قوالب HTML
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>نظام إدارة الأصول مع التقارير</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            min-height: 100vh; 
            display: flex; 
            align-items: center; 
        }
        .login-card { 
            background: white; 
            border-radius: 20px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }
        .btn-primary { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            border: none; 
            transition: transform 0.3s ease;
        }
        .btn-primary:hover { transform: translateY(-2px); }
        .reports-badge {
            background: linear-gradient(45deg, #28a745, #20c997);
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.8em;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-6 col-lg-4">
                <div class="login-card p-5">
                    <div class="text-center mb-4">
                        <i class="fas fa-chart-line fa-3x text-primary mb-3"></i>
                        <h2>نظام إدارة الأصول</h2>
                        <span class="reports-badge">📊 مع التقارير</span>
                        <p class="text-muted mt-2">تقارير شاملة وإحصائيات متقدمة</p>
                    </div>
                    
                    {% with messages = get_flashed_messages(with_categories=true) %}
                        {% if messages %}
                            {% for category, message in messages %}
                                <div class="alert alert-{{ 'danger' if category == 'error' else 'success' }}">
                                    {{ message }}
                                </div>
                            {% endfor %}
                        {% endif %}
                    {% endwith %}
                    
                    <form method="POST">
                        <div class="mb-3">
                            <label class="form-label">اسم المستخدم</label>
                            <input type="text" class="form-control" name="username" required value="admin">
                        </div>
                        <div class="mb-4">
                            <label class="form-label">كلمة المرور</label>
                            <input type="password" class="form-control" name="password" required value="admin123">
                        </div>
                        <button type="submit" class="btn btn-primary w-100 btn-lg">
                            <i class="fas fa-sign-in-alt"></i> دخول مع التقارير
                        </button>
                    </form>
                    
                    <div class="mt-4 p-3 bg-light rounded text-center">
                        <small>
                            <strong>🚀 الميزات الجديدة:</strong><br>
                            المستخدم: admin | كلمة المرور: admin123<br>
                            <span class="text-success">✅ 18 أصل تجريبي</span><br>
                            <span class="text-info">📊 تقارير متقدمة</span><br>
                            <span class="text-warning">📈 رسوم بيانية</span>
                        </small>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
'''

DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة التحكم - نظام إدارة الأصول مع التقارير</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; }
        .navbar-custom { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
        }
        .stats-card { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            border-radius: 15px; 
            transition: transform 0.3s ease;
        }
        .stats-card:hover { transform: translateY(-5px); }
        .card { border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 15px; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; }
        .reports-badge { 
            background: linear-gradient(45deg, #28a745, #20c997); 
            color: white; 
            padding: 5px 15px; 
            border-radius: 20px; 
            font-size: 0.8em;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="{{ url_for('index') }}">
                <i class="fas fa-chart-line"></i> إدارة الأصول مع التقارير
                <span class="reports-badge ms-2">📊 تقارير</span>
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white active" href="{{ url_for('index') }}">
                    <i class="fas fa-home"></i> الرئيسية
                </a>
                <a class="nav-link text-white" href="{{ url_for('assets') }}">
                    <i class="fas fa-desktop"></i> الأصول
                </a>
                <a class="nav-link text-white" href="{{ url_for('categories') }}">
                    <i class="fas fa-tags"></i> الفئات
                </a>
                <a class="nav-link text-white" href="{{ url_for('reports') }}">
                    <i class="fas fa-chart-bar"></i> التقارير
                </a>
                <div class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle text-white" href="#" role="button" data-bs-toggle="dropdown">
                        <i class="fas fa-user"></i> {{ user_name }}
                    </a>
                    <ul class="dropdown-menu">
                        <li><a class="dropdown-item" href="{{ url_for('logout') }}">
                            <i class="fas fa-sign-out-alt"></i> تسجيل الخروج
                        </a></li>
                    </ul>
                </div>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="alert alert-success">
            <i class="fas fa-check-circle"></i> 
            <strong>النظام مع التقارير يعمل بنجاح!</strong> 
            {{ total_assets }} أصل مع تقارير شاملة وإحصائيات متقدمة
        </div>
        
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
                    <i class="fas fa-tags fa-3x mb-3"></i>
                    <h3>{{ categories_count }}</h3>
                    <p class="mb-0">الفئات</p>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
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
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">الأصول الحديثة</h5>
                        <div class="btn-group">
                            <a href="{{ url_for('add_asset') }}" class="btn btn-primary btn-sm">
                                <i class="fas fa-plus"></i> إضافة أصل
                            </a>
                            <a href="{{ url_for('reports') }}" class="btn btn-success btn-sm">
                                <i class="fas fa-chart-bar"></i> التقارير
                            </a>
                        </div>
                    </div>
                    <div class="card-body">
                        {% if recent_assets %}
                        <div class="table-responsive">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>رقم الأصل</th>
                                        <th>الاسم</th>
                                        <th>الفئة</th>
                                        <th>العلامة التجارية</th>
                                        <th>القيمة</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for asset in recent_assets %}
                                    <tr>
                                        <td><strong class="text-primary">{{ asset.asset_tag }}</strong></td>
                                        <td>{{ asset.name }}</td>
                                        <td><span class="badge bg-secondary">{{ asset.category_name or 'غير محدد' }}</span></td>
                                        <td>{{ asset.brand or '-' }}</td>
                                        <td>
                                            {% if asset.purchase_cost %}
                                            {{ "%.0f"|format(asset.purchase_cost) }} ريال
                                            {% else %}
                                            -
                                            {% endif %}
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                        {% endif %}
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
                            <a href="{{ url_for('add_asset') }}" class="btn btn-outline-primary">
                                <i class="fas fa-plus"></i> إضافة أصل جديد
                            </a>
                            <a href="{{ url_for('assets') }}" class="btn btn-outline-info">
                                <i class="fas fa-list"></i> عرض جميع الأصول
                            </a>
                            <a href="{{ url_for('categories') }}" class="btn btn-outline-warning">
                                <i class="fas fa-tags"></i> إدارة الفئات
                            </a>
                            <a href="{{ url_for('reports') }}" class="btn btn-outline-success">
                                <i class="fas fa-chart-bar"></i> التقارير والإحصائيات
                            </a>
                        </div>
                    </div>
                </div>
                
                <div class="card mt-3">
                    <div class="card-header">
                        <h6 class="mb-0">إحصائيات الفئات</h6>
                    </div>
                    <div class="card-body">
                        {% for cat in category_stats %}
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <span>{{ cat.name }}</span>
                            <span class="badge bg-primary">{{ cat.asset_count }}</span>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

# قوالب أخرى مبسطة
ASSETS_TEMPLATE = CATEGORIES_TEMPLATE = ADD_ASSET_TEMPLATE = '''
<p>استخدم النسخة الكاملة للحصول على جميع القوالب</p>
'''

# قوالب التقارير
REPORTS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>التقارير - نظام إدارة الأصول</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { background: #f8f9fa; }
        .navbar-custom { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
        }
        .card { border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 15px; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; }
        .reports-badge { 
            background: linear-gradient(45deg, #28a745, #20c997); 
            color: white; 
            padding: 5px 15px; 
            border-radius: 20px; 
            font-size: 0.8em;
        }
        .stats-card { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            border-radius: 15px; 
            transition: transform 0.3s ease;
        }
        .stats-card:hover { transform: translateY(-5px); }
        .chart-container { position: relative; height: 300px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="{{ url_for('index') }}">
                <i class="fas fa-chart-line"></i> إدارة الأصول مع التقارير
                <span class="reports-badge ms-2">📊 تقارير</span>
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="{{ url_for('index') }}">
                    <i class="fas fa-home"></i> الرئيسية
                </a>
                <a class="nav-link text-white" href="{{ url_for('assets') }}">
                    <i class="fas fa-desktop"></i> الأصول
                </a>
                <a class="nav-link text-white" href="{{ url_for('categories') }}">
                    <i class="fas fa-tags"></i> الفئات
                </a>
                <a class="nav-link text-white active" href="{{ url_for('reports') }}">
                    <i class="fas fa-chart-bar"></i> التقارير
                </a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="fas fa-chart-bar text-primary"></i> التقارير والإحصائيات المتقدمة</h2>
            <div class="btn-group">
                <a href="{{ url_for('detailed_report') }}" class="btn btn-outline-primary">
                    <i class="fas fa-list"></i> تقرير مفصل
                </a>
                <a href="{{ url_for('export_csv') }}" class="btn btn-outline-success">
                    <i class="fas fa-download"></i> تصدير CSV
                </a>
                <a href="{{ url_for('print_report') }}" class="btn btn-outline-info" target="_blank">
                    <i class="fas fa-print"></i> طباعة
                </a>
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
                    <i class="fas fa-check-circle fa-3x mb-3"></i>
                    <h3>{{ active_assets }}</h3>
                    <p class="mb-0">أصول نشطة</p>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="stats-card p-4 text-center">
                    <i class="fas fa-tools fa-3x mb-3"></i>
                    <h3>{{ maintenance_assets }}</h3>
                    <p class="mb-0">في الصيانة</p>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="stats-card p-4 text-center">
                    <i class="fas fa-dollar-sign fa-3x mb-3"></i>
                    <h3>{{ "%.0f"|format(total_cost) }}</h3>
                    <p class="mb-0">إجمالي القيمة (ريال)</p>
                </div>
            </div>
        </div>

        <div class="row">
            <!-- رسم بياني للفئات -->
            <div class="col-lg-6 mb-4">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">توزيع الأصول حسب الفئات</h5>
                    </div>
                    <div class="card-body">
                        <div class="chart-container">
                            <canvas id="categoryChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>

            <!-- رسم بياني للحالة -->
            <div class="col-lg-6 mb-4">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">حالة الأصول</h5>
                    </div>
                    <div class="card-body">
                        <div class="chart-container">
                            <canvas id="statusChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row">
            <!-- إحصائيات الفئات -->
            <div class="col-lg-6 mb-4">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">تفاصيل الفئات</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>الفئة</th>
                                        <th>عدد الأصول</th>
                                        <th>القيمة الإجمالية</th>
                                        <th>تقرير</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for cat in category_stats %}
                                    <tr>
                                        <td><strong>{{ cat.name }}</strong></td>
                                        <td><span class="badge bg-primary">{{ cat.asset_count }}</span></td>
                                        <td>{{ "%.0f"|format(cat.total_value) }} ريال</td>
                                        <td>
                                            <a href="{{ url_for('category_report', category_id=cat.id) }}" class="btn btn-sm btn-outline-info">
                                                <i class="fas fa-eye"></i> عرض
                                            </a>
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <!-- أشهر العلامات التجارية -->
            <div class="col-lg-6 mb-4">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">أشهر العلامات التجارية</h5>
                    </div>
                    <div class="card-body">
                        {% for brand in brand_stats %}
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <div>
                                <strong>{{ brand.brand }}</strong>
                                <br><small class="text-muted">{{ "%.0f"|format(brand.total_value) }} ريال</small>
                            </div>
                            <span class="badge bg-secondary">{{ brand.count }} أصل</span>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
        </div>

        <!-- الأصول الأعلى قيمة -->
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">الأصول الأعلى قيمة</h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>رقم الأصل</th>
                                <th>الاسم</th>
                                <th>الفئة</th>
                                <th>العلامة التجارية</th>
                                <th>القيمة</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for asset in expensive_assets %}
                            <tr>
                                <td><strong class="text-primary">{{ asset.asset_tag }}</strong></td>
                                <td>{{ asset.name }}</td>
                                <td><span class="badge bg-secondary">{{ asset.category_name or 'غير محدد' }}</span></td>
                                <td>{{ asset.brand or '-' }}</td>
                                <td><strong class="text-success">{{ "%.0f"|format(asset.purchase_cost) }} ريال</strong></td>
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
        // رسم بياني للفئات
        const categoryCtx = document.getElementById('categoryChart').getContext('2d');
        new Chart(categoryCtx, {
            type: 'doughnut',
            data: {
                labels: [{% for cat in category_stats %}'{{ cat.name }}'{% if not loop.last %},{% endif %}{% endfor %}],
                datasets: [{
                    data: [{% for cat in category_stats %}{{ cat.asset_count }}{% if not loop.last %},{% endif %}{% endfor %}],
                    backgroundColor: [
                        '#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe',
                        '#43e97b', '#fa709a', '#fee140', '#a8edea', '#d299c2'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });

        // رسم بياني للحالة
        const statusCtx = document.getElementById('statusChart').getContext('2d');
        new Chart(statusCtx, {
            type: 'bar',
            data: {
                labels: ['نشط', 'صيانة', 'متقاعد'],
                datasets: [{
                    label: 'عدد الأصول',
                    data: [{{ active_assets }}, {{ maintenance_assets }}, {{ retired_assets }}],
                    backgroundColor: ['#28a745', '#ffc107', '#dc3545']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    </script>
</body>
</html>
'''

# قوالب أخرى مبسطة للتقارير
DETAILED_REPORT_TEMPLATE = CATEGORY_REPORT_TEMPLATE = PRINT_REPORT_TEMPLATE = '''
<h1>تقرير مفصل</h1>
<p>استخدم النسخة الكاملة للحصول على التقارير المفصلة</p>
'''

def open_browser():
    """فتح المتصفح تلقائياً"""
    time.sleep(2)
    webbrowser.open('http://localhost:5000')

def main():
    """الدالة الرئيسية"""
    print("=" * 70)
    print("📊 نظام إدارة الأصول التقنية مع التقارير - النسخة الفورية")
    print("   Instant IT Asset Management System with Reports")
    print("=" * 70)
    print()
    
    # تثبيت Flask إذا لم يكن مثبت
    if not install_flask():
        print("❌ فشل في تثبيت Flask")
        input("اضغط Enter للخروج...")
        return
    
    # إنشاء قاعدة البيانات
    print("📊 إنشاء قاعدة البيانات مع بيانات تجريبية متنوعة...")
    create_instant_database()
    
    # إنشاء التطبيق
    print("🔧 إنشاء التطبيق الفوري مع التقارير...")
    app = create_instant_app()
    
    print("✅ النظام مع التقارير جاهز للتشغيل الفوري!")
    print("🌐 الخادم: http://localhost:5000")
    print("👤 المستخدم: admin")
    print("🔑 كلمة المرور: admin123")
    print("📊 البيانات: 18 أصل تجريبي متنوع")
    print("📈 التقارير: رسوم بيانية وإحصائيات متقدمة")
    print("📋 التصدير: CSV وطباعة")
    print("🔧 للإيقاف: اضغط Ctrl+C")
    print("=" * 70)
    print()
    
    # فتح المتصفح تلقائياً
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        # تشغيل التطبيق بدون رسائل تحذيرية
        import logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        
        app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False)
    except KeyboardInterrupt:
        print("\n⏹️  تم إيقاف النظام بنجاح")
    except Exception as e:
        print(f"\n❌ خطأ في تشغيل النظام: {e}")
        input("اضغط Enter للخروج...")

if __name__ == '__main__':
    main()