#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نسخة ويب فورية - تعمل بنقرة واحدة
Instant Web Version - One-Click Launch
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
    db_path = 'instant_assets.db'
    
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
        ('الهواتف', 'الهواتف الثابتة والذكية')
    ]
    
    for name, desc in categories:
        cursor.execute('INSERT INTO categories (name, description) VALUES (?, ?)', (name, desc))
    
    # أصول تجريبية
    sample_assets = [
        ('PC001', 'جهاز كمبيوتر مكتبي', 'جهاز Dell للموظفين', 1, 'Dell', 'OptiPlex 7090', 'DL123456', 2500.00),
        ('LP001', 'جهاز لابتوب', 'جهاز HP محمول', 1, 'HP', 'EliteBook 840', 'HP789012', 3200.00),
        ('PR001', 'طابعة ليزر', 'طابعة Canon مكتبية', 4, 'Canon', 'LBP6030', 'CN345678', 800.00),
        ('SW001', 'جهاز تبديل شبكة', 'سويتش Cisco 24 منفذ', 3, 'Cisco', 'SG250-24', 'CS901234', 1500.00),
        ('SV001', 'خادم رئيسي', 'خادم Dell قاعدة البيانات', 2, 'Dell', 'PowerEdge R740', 'DL567890', 8500.00),
        ('PH001', 'هاتف IP', 'هاتف مكتبي ذكي', 5, 'Cisco', 'IP Phone 8841', 'CS111222', 350.00),
        ('RT001', 'جهاز توجيه', 'راوتر الشبكة الرئيسي', 3, 'Cisco', 'ISR 4331', 'CS333444', 2200.00),
        ('TB001', 'جهاز تابلت', 'تابلت للعروض التقديمية', 1, 'Samsung', 'Galaxy Tab S8', 'SM555666', 1800.00)
    ]
    
    for asset in sample_assets:
        cursor.execute('''
            INSERT INTO assets (asset_tag, name, description, category_id, brand, model, serial_number, purchase_cost)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', asset)
    
    conn.commit()
    conn.close()
    
    print("✅ تم إنشاء قاعدة البيانات مع 8 أصول تجريبية")
    return db_path

def create_instant_app():
    """إنشاء تطبيق Flask فوري"""
    from flask import Flask, render_template_string, request, redirect, url_for, flash, session
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'instant-asset-management-2025'
    
    DB_PATH = 'instant_assets.db'
    
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
        
        return render_template_string(INSTANT_DASHBOARD_TEMPLATE, 
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
                flash('مرحباً بك في نظام إدارة الأصول!', 'success')
                return redirect(url_for('index'))
            else:
                flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
        
        return render_template_string(INSTANT_LOGIN_TEMPLATE)
    
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
        
        return render_template_string(INSTANT_ASSETS_TEMPLATE, 
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
        
        return render_template_string(INSTANT_ADD_ASSET_TEMPLATE, 
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
        
        return render_template_string(INSTANT_CATEGORIES_TEMPLATE, 
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
            SELECT c.name, COUNT(a.id) as asset_count, 
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
        from flask import Response
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

# قوالب HTML محسنة
INSTANT_LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>نظام إدارة الأصول - النسخة الفورية</title>
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
        .instant-badge {
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
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
                        <i class="fas fa-rocket fa-3x text-primary mb-3"></i>
                        <h2>نظام إدارة الأصول</h2>
                        <span class="instant-badge">⚡ النسخة الفورية</span>
                        <p class="text-muted mt-2">جاهز للاستخدام فوراً!</p>
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
                            <i class="fas fa-sign-in-alt"></i> دخول فوري
                        </button>
                    </form>
                    
                    <div class="mt-4 p-3 bg-light rounded text-center">
                        <small>
                            <strong>🚀 جاهز للاستخدام:</strong><br>
                            المستخدم: admin | كلمة المرور: admin123<br>
                            <span class="text-success">✅ 8 أصول تجريبية جاهزة</span>
                        </small>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
'''

INSTANT_DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة التحكم - نظام إدارة الأصول الفوري</title>
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
        .instant-badge { 
            background: linear-gradient(45deg, #ff6b6b, #ee5a24); 
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
        .success-badge {
            background: linear-gradient(45deg, #00b894, #00cec9);
            color: white;
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 0.75em;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="{{ url_for('index') }}">
                <i class="fas fa-rocket"></i> إدارة الأصول الفورية
                <span class="instant-badge ms-2">⚡ فوري</span>
            </a>
            <div class="navbar-nav ms-auto">
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
            <strong>النظام يعمل بنجاح!</strong> 
            نسخة فورية مع {{ total_assets }} أصول جاهزة للإدارة
            <span class="success-badge ms-2">✅ جاهز</span>
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
                        <h5 class="mb-0">الأصول المتاحة ({{ recent_assets|length }})</h5>
                        <a href="{{ url_for('add_asset') }}" class="btn btn-primary btn-sm">
                            <i class="fas fa-plus"></i> إضافة أصل
                        </a>
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

INSTANT_ASSETS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>قائمة الأصول - النسخة الفورية</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; }
        .navbar-custom { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
        }
        .card { border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 15px; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; }
        .instant-badge { 
            background: linear-gradient(45deg, #ff6b6b, #ee5a24); 
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
                <i class="fas fa-rocket"></i> إدارة الأصول الفورية
                <span class="instant-badge ms-2">⚡ فوري</span>
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white active" href="{{ url_for('assets') }}">
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
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">قائمة الأصول ({{ assets|length }} أصل)</h5>
                <a href="{{ url_for('add_asset') }}" class="btn btn-primary">
                    <i class="fas fa-plus"></i> إضافة أصل جديد
                </a>
            </div>
            <div class="card-body">
                {% if assets %}
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>رقم الأصل</th>
                                <th>الاسم</th>
                                <th>الفئة</th>
                                <th>العلامة التجارية</th>
                                <th>الموديل</th>
                                <th>التكلفة</th>
                                <th>الحالة</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for asset in assets %}
                            <tr>
                                <td><strong class="text-primary">{{ asset.asset_tag }}</strong></td>
                                <td>
                                    <strong>{{ asset.name }}</strong>
                                    {% if asset.description %}
                                    <br><small class="text-muted">{{ asset.description }}</small>
                                    {% endif %}
                                </td>
                                <td><span class="badge bg-secondary">{{ asset.category_name or 'غير محدد' }}</span></td>
                                <td>{{ asset.brand or '-' }}</td>
                                <td>{{ asset.model or '-' }}</td>
                                <td>
                                    {% if asset.purchase_cost %}
                                    {{ "%.0f"|format(asset.purchase_cost) }} ريال
                                    {% else %}
                                    -
                                    {% endif %}
                                </td>
                                <td>
                                    <span class="badge bg-{{ 'success' if asset.status == 'active' else 'warning' }}">
                                        {{ 'نشط' if asset.status == 'active' else asset.status }}
                                    </span>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <div class="text-center py-5">
                    <i class="fas fa-inbox fa-3x text-muted mb-3"></i>
                    <h5 class="text-muted">لا توجد أصول</h5>
                    <p class="text-muted">ابدأ بإضافة أول أصل</p>
                    <a href="{{ url_for('add_asset') }}" class="btn btn-primary btn-lg">
                        <i class="fas fa-plus"></i> إضافة أول أصل
                    </a>
                </div>
                {% endif %}
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

INSTANT_ADD_ASSET_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>إضافة أصل جديد - النسخة الفورية</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; }
        .navbar-custom { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
        }
        .card { border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 15px; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; }
        .instant-badge { 
            background: linear-gradient(45deg, #ff6b6b, #ee5a24); 
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
                <i class="fas fa-rocket"></i> إدارة الأصول الفورية
                <span class="instant-badge ms-2">⚡ فوري</span>
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="{{ url_for('assets') }}">
                    <i class="fas fa-desktop"></i> الأصول
                </a>
                <a class="nav-link text-white" href="{{ url_for('categories') }}">
                    <i class="fas fa-tags"></i> الفئات
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
        <div class="row justify-content-center">
            <div class="col-lg-8">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">إضافة أصل جديد</h5>
                    </div>
                    <div class="card-body">
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
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">رقم الأصل *</label>
                                    <input type="text" class="form-control" name="asset_tag" required placeholder="مثال: PC009">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">اسم الأصل *</label>
                                    <input type="text" class="form-control" name="name" required placeholder="مثال: جهاز كمبيوتر جديد">
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">الوصف</label>
                                <textarea class="form-control" name="description" rows="3" placeholder="وصف مختصر للأصل..."></textarea>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">الفئة</label>
                                    <select class="form-select" name="category_id">
                                        <option value="">اختر الفئة</option>
                                        {% for category in categories %}
                                        <option value="{{ category.id }}">{{ category.name }}</option>
                                        {% endfor %}
                                    </select>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">العلامة التجارية</label>
                                    <input type="text" class="form-control" name="brand" placeholder="مثال: Dell, HP, Canon">
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">الموديل</label>
                                    <input type="text" class="form-control" name="model" placeholder="مثال: OptiPlex 7090">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">الرقم التسلسلي</label>
                                    <input type="text" class="form-control" name="serial_number" placeholder="الرقم التسلسلي للجهاز">
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">تكلفة الشراء (ريال)</label>
                                    <input type="number" step="0.01" class="form-control" name="purchase_cost" placeholder="0.00">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">الحالة</label>
                                    <select class="form-select" name="status">
                                        <option value="active">نشط</option>
                                        <option value="maintenance">صيانة</option>
                                        <option value="retired">متقاعد</option>
                                    </select>
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">ملاحظات</label>
                                <textarea class="form-control" name="notes" rows="3" placeholder="أي ملاحظات إضافية..."></textarea>
                            </div>
                            
                            <div class="d-flex gap-2">
                                <button type="submit" class="btn btn-primary">
                                    <i class="fas fa-save"></i> حفظ الأصل
                                </button>
                                <a href="{{ url_for('assets') }}" class="btn btn-secondary">
                                    <i class="fas fa-times"></i> إلغاء
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
        .instant-badge { 
            background: linear-gradient(45deg, #ff6b6b, #ee5a24); 
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
                <i class="fas fa-rocket"></i> إدارة الأصول الفورية
                <span class="instant-badge ms-2">⚡ فوري</span>
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="{{ url_for('assets') }}">
                    <i class="fas fa-desktop"></i> الأصول
                </a>
                <a class="nav-link text-white" href="{{ url_for('categories') }}">
                    <i class="fas fa-tags"></i> الفئات
                </a>
                <a class="nav-link text-white active" href="{{ url_for('reports') }}">
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
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="fas fa-chart-bar text-primary"></i> التقارير والإحصائيات</h2>
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
                                            <a href="{{ url_for('category_report', category_id=cat.name) }}" class="btn btn-sm btn-outline-info">
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

            <!-- أعلى العلامات التجارية -->
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

DETAILED_REPORT_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>التقرير المفصل - نظام إدارة الأصول</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; }
        .navbar-custom { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
        }
        .card { border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 15px; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; }
        .instant-badge { 
            background: linear-gradient(45deg, #ff6b6b, #ee5a24); 
            color: white; 
            padding: 5px 15px; 
            border-radius: 20px; 
            font-size: 0.8em;
        }
        .stats-summary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="{{ url_for('index') }}">
                <i class="fas fa-rocket"></i> إدارة الأصول الفورية
                <span class="instant-badge ms-2">⚡ فوري</span>
            </a>
            <div class="navbar-nav ms-auto">
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
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="fas fa-file-alt text-primary"></i> التقرير المفصل</h2>
            <div class="btn-group">
                <a href="{{ url_for('reports') }}" class="btn btn-outline-secondary">
                    <i class="fas fa-arrow-right"></i> العودة للتقارير
                </a>
                <a href="{{ url_for('export_csv') }}" class="btn btn-outline-success">
                    <i class="fas fa-download"></i> تصدير CSV
                </a>
                <a href="{{ url_for('print_report') }}" class="btn btn-outline-info" target="_blank">
                    <i class="fas fa-print"></i> طباعة
                </a>
            </div>
        </div>

        <!-- ملخص الإحصائيات -->
        <div class="stats-summary">
            <div class="row text-center">
                <div class="col-md-3">
                    <h3>{{ stats.total_count }}</h3>
                    <p class="mb-0">إجمالي الأصول</p>
                </div>
                <div class="col-md-3">
                    <h3>{{ "%.0f"|format(stats.total_value) }}</h3>
                    <p class="mb-0">إجمالي القيمة (ريال)</p>
                </div>
                <div class="col-md-3">
                    <h3>{{ "%.0f"|format(stats.avg_value) }}</h3>
                    <p class="mb-0">متوسط القيمة (ريال)</p>
                </div>
                <div class="col-md-3">
                    <h3>{{ stats.active_count }}</h3>
                    <p class="mb-0">أصول نشطة</p>
                </div>
            </div>
        </div>

        <!-- جدول الأصول المفصل -->
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">جميع الأصول ({{ assets|length }} أصل)</h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover table-striped">
                        <thead class="table-dark">
                            <tr>
                                <th>رقم الأصل</th>
                                <th>الاسم</th>
                                <th>الفئة</th>
                                <th>العلامة التجارية</th>
                                <th>الموديل</th>
                                <th>الرقم التسلسلي</th>
                                <th>التكلفة</th>
                                <th>الحالة</th>
                                <th>تاريخ الإضافة</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for asset in assets %}
                            <tr>
                                <td><strong class="text-primary">{{ asset.asset_tag }}</strong></td>
                                <td>
                                    <strong>{{ asset.name }}</strong>
                                    {% if asset.description %}
                                    <br><small class="text-muted">{{ asset.description }}</small>
                                    {% endif %}
                                </td>
                                <td>
                                    {% if asset.category_name %}
                                    <span class="badge bg-secondary">{{ asset.category_name }}</span>
                                    {% else %}
                                    <span class="badge bg-light text-dark">غير محدد</span>
                                    {% endif %}
                                </td>
                                <td>{{ asset.brand or '-' }}</td>
                                <td>{{ asset.model or '-' }}</td>
                                <td><small>{{ asset.serial_number or '-' }}</small></td>
                                <td>
                                    {% if asset.purchase_cost %}
                                    <strong class="text-success">{{ "%.0f"|format(asset.purchase_cost) }} ريال</strong>
                                    {% else %}
                                    <span class="text-muted">-</span>
                                    {% endif %}
                                </td>
                                <td>
                                    <span class="badge bg-{{ 'success' if asset.status == 'active' else 'warning' if asset.status == 'maintenance' else 'danger' }}">
                                        {{ 'نشط' if asset.status == 'active' else 'صيانة' if asset.status == 'maintenance' else 'متقاعد' }}
                                    </span>
                                </td>
                                <td><small>{{ asset.purchase_date or '-' }}</small></td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

CATEGORY_REPORT_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تقرير الفئة - {{ category.name }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; }
        .navbar-custom { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
        }
        .card { border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 15px; }
        .instant-badge { 
            background: linear-gradient(45deg, #ff6b6b, #ee5a24); 
            color: white; 
            padding: 5px 15px; 
            border-radius: 20px; 
            font-size: 0.8em;
        }
        .category-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="{{ url_for('index') }}">
                <i class="fas fa-rocket"></i> إدارة الأصول الفورية
                <span class="instant-badge ms-2">⚡ فوري</span>
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="{{ url_for('reports') }}">
                    <i class="fas fa-chart-bar"></i> التقارير
                </a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="category-header text-center">
            <h1><i class="fas fa-tag"></i> {{ category.name }}</h1>
            <p class="mb-0">{{ category.description or 'تقرير مفصل للفئة' }}</p>
        </div>

        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h3 class="text-primary">{{ stats.total_count }}</h3>
                        <p class="mb-0">إجمالي الأصول</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h3 class="text-success">{{ "%.0f"|format(stats.total_value) }}</h3>
                        <p class="mb-0">إجمالي القيمة (ريال)</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h3 class="text-info">{{ stats.active_count }}</h3>
                        <p class="mb-0">أصول نشطة</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h3 class="text-warning">{{ stats.maintenance_count }}</h3>
                        <p class="mb-0">في الصيانة</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">أصول الفئة</h5>
            </div>
            <div class="card-body">
                {% if assets %}
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>رقم الأصل</th>
                                <th>الاسم</th>
                                <th>العلامة التجارية</th>
                                <th>الموديل</th>
                                <th>التكلفة</th>
                                <th>الحالة</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for asset in assets %}
                            <tr>
                                <td><strong class="text-primary">{{ asset.asset_tag }}</strong></td>
                                <td>{{ asset.name }}</td>
                                <td>{{ asset.brand or '-' }}</td>
                                <td>{{ asset.model or '-' }}</td>
                                <td>
                                    {% if asset.purchase_cost %}
                                    {{ "%.0f"|format(asset.purchase_cost) }} ريال
                                    {% else %}
                                    -
                                    {% endif %}
                                </td>
                                <td>
                                    <span class="badge bg-{{ 'success' if asset.status == 'active' else 'warning' }}">
                                        {{ 'نشط' if asset.status == 'active' else asset.status }}
                                    </span>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <div class="text-center py-4">
                    <i class="fas fa-inbox fa-3x text-muted mb-3"></i>
                    <p class="text-muted">لا توجد أصول في هذه الفئة</p>
                </div>
                {% endif %}
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

PRINT_REPORT_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تقرير الأصول - للطباعة</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 20px;
            font-size: 12px;
        }
        .header { 
            text-align: center; 
            border-bottom: 2px solid #333; 
            padding-bottom: 20px; 
            margin-bottom: 30px;
        }
        .stats { 
            display: flex; 
            justify-content: space-around; 
            margin-bottom: 30px;
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
        }
        .stat-item { text-align: center; }
        .stat-item h3 { margin: 0; color: #007bff; }
        table { 
            width: 100%; 
            border-collapse: collapse; 
            margin-bottom: 30px;
        }
        th, td { 
            border: 1px solid #ddd; 
            padding: 8px; 
            text-align: right;
        }
        th { 
            background-color: #007bff; 
            color: white; 
            font-weight: bold;
        }
        tr:nth-child(even) { background-color: #f2f2f2; }
        .footer { 
            margin-top: 30px; 
            text-align: center; 
            font-size: 10px; 
            color: #666;
        }
        @media print {
            body { margin: 0; }
            .no-print { display: none; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>تقرير إدارة الأصول التقنية</h1>
        <p>تاريخ التقرير: {{ report_date }}</p>
        <p>المستخدم: {{ user_name }}</p>
    </div>

    <div class="stats">
        <div class="stat-item">
            <h3>{{ stats.total_assets }}</h3>
            <p>إجمالي الأصول</p>
        </div>
        <div class="stat-item">
            <h3>{{ "%.0f"|format(stats.total_value) }}</h3>
            <p>إجمالي القيمة (ريال)</p>
        </div>
        <div class="stat-item">
            <h3>{{ stats.active_assets }}</h3>
            <p>أصول نشطة</p>
        </div>
        <div class="stat-item">
            <h3>{{ stats.maintenance_assets }}</h3>
            <p>في الصيانة</p>
        </div>
    </div>

    <h2>إحصائيات الفئات</h2>
    <table>
        <thead>
            <tr>
                <th>الفئة</th>
                <th>عدد الأصول</th>
                <th>إجمالي القيمة (ريال)</th>
            </tr>
        </thead>
        <tbody>
            {% for cat in category_stats %}
            <tr>
                <td>{{ cat.name }}</td>
                <td>{{ cat.count }}</td>
                <td>{{ "%.0f"|format(cat.total_value) }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    <h2>جميع الأصول</h2>
    <table>
        <thead>
            <tr>
                <th>رقم الأصل</th>
                <th>الاسم</th>
                <th>الفئة</th>
                <th>العلامة التجارية</th>
                <th>الموديل</th>
                <th>التكلفة (ريال)</th>
                <th>الحالة</th>
            </tr>
        </thead>
        <tbody>
            {% for asset in assets %}
            <tr>
                <td>{{ asset.asset_tag }}</td>
                <td>{{ asset.name }}</td>
                <td>{{ asset.category_name or '-' }}</td>
                <td>{{ asset.brand or '-' }}</td>
                <td>{{ asset.model or '-' }}</td>
                <td>{{ "%.0f"|format(asset.purchase_cost) if asset.purchase_cost else '-' }}</td>
                <td>{{ 'نشط' if asset.status == 'active' else 'صيانة' if asset.status == 'maintenance' else 'متقاعد' }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    <div class="footer">
        <p>تم إنشاء هذا التقرير بواسطة نظام إدارة الأصول التقنية - النسخة الفورية</p>
        <p>{{ report_date }}</p>
    </div>

    <script>
        // طباعة تلقائية عند فتح الصفحة
        window.onload = function() {
            window.print();
        }
    </script>
</body>
</html>
'''

INSTANT_CATEGORIES_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>الفئات - النسخة الفورية</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; }
        .navbar-custom { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
        }
        .card { border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 15px; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; }
        .instant-badge { 
            background: linear-gradient(45deg, #ff6b6b, #ee5a24); 
            color: white; 
            padding: 5px 15px; 
            border-radius: 20px; 
            font-size: 0.8em;
        }
        .category-card {
            transition: transform 0.3s ease;
        }
        .category-card:hover {
            transform: translateY(-5px);
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="{{ url_for('index') }}">
                <i class="fas fa-rocket"></i> إدارة الأصول الفورية
                <span class="instant-badge ms-2">⚡ فوري</span>
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="{{ url_for('assets') }}">
                    <i class="fas fa-desktop"></i> الأصول
                </a>
                <a class="nav-link text-white active" href="{{ url_for('categories') }}">
                    <i class="fas fa-tags"></i> الفئات
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
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">فئات الأصول ({{ categories|length }} فئة)</h5>
            </div>
            <div class="card-body">
                <div class="row">
                    {% for category in categories %}
                    <div class="col-md-6 col-lg-4 mb-3">
                        <div class="card h-100 category-card">
                            <div class="card-body">
                                <h6 class="card-title">
                                    <i class="fas fa-tag text-primary"></i> {{ category.name }}
                                    <span class="badge bg-primary ms-2">{{ category.asset_count }}</span>
                                </h6>
                                <p class="card-text text-muted">{{ category.description or 'لا يوجد وصف' }}</p>
                                <small class="text-muted">
                                    <i class="fas fa-laptop"></i> {{ category.asset_count }} أصل
                                </small>
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

def open_browser():
    """فتح المتصفح تلقائياً"""
    time.sleep(2)
    webbrowser.open('http://localhost:5000')

def main():
    """الدالة الرئيسية"""
    print("=" * 70)
    print("🚀 نظام إدارة الأصول التقنية - النسخة الفورية")
    print("   Instant IT Asset Management System")
    print("=" * 70)
    print()
    
    # تثبيت Flask إذا لم يكن مثبت
    if not install_flask():
        print("❌ فشل في تثبيت Flask")
        input("اضغط Enter للخروج...")
        return
    
    # إنشاء قاعدة البيانات
    print("📊 إنشاء قاعدة البيانات مع بيانات تجريبية...")
    create_instant_database()
    
    # إنشاء التطبيق
    print("🔧 إنشاء التطبيق الفوري...")
    app = create_instant_app()
    
    print("✅ النظام جاهز للتشغيل الفوري!")
    print("🌐 الخادم: http://localhost:5000")
    print("👤 المستخدم: admin")
    print("🔑 كلمة المرور: admin123")
    print("📊 البيانات: 8 أصول تجريبية جاهزة")
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