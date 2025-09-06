#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام إدارة الأصول التقنية - نسخة الإنتاج
IT Asset Management System - Production Version
للنشر على الاستضافة السحابية
"""

import os
import sys
import logging
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template_string, request, redirect, url_for, flash, session

# إعداد المتغيرات
DATABASE_URL = os.environ.get('DATABASE_URL')
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
FLASK_ENV = os.environ.get('FLASK_ENV', 'development')

# إعداد قاعدة البيانات
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

def create_app():
    """إنشاء تطبيق Flask للإنتاج"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['DATABASE_URL'] = DATABASE_URL
    
    # إعداد السجلات
    if FLASK_ENV == 'production':
        logging.basicConfig(level=logging.INFO)
        app.logger.setLevel(logging.INFO)
    
    # إعداد قاعدة البيانات
    if DATABASE_URL:
        # استخدام PostgreSQL للإنتاج
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        def get_db():
            """الحصول على اتصال PostgreSQL"""
            conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
            return conn
        
        def init_db():
            """إنشاء الجداول في PostgreSQL"""
            conn = get_db()
            cursor = conn.cursor()
            
            try:
                # جدول المستخدمين
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(80) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        full_name VARCHAR(100) NOT NULL,
                        role VARCHAR(20) DEFAULT 'user',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # جدول الفئات
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS categories (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) UNIQUE NOT NULL,
                        description TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # جدول الأصول
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS assets (
                        id SERIAL PRIMARY KEY,
                        asset_tag VARCHAR(50) UNIQUE NOT NULL,
                        name VARCHAR(200) NOT NULL,
                        description TEXT,
                        category_id INTEGER REFERENCES categories(id),
                        brand VARCHAR(100),
                        model VARCHAR(100),
                        serial_number VARCHAR(100),
                        purchase_cost DECIMAL(10,2),
                        status VARCHAR(20) DEFAULT 'active',
                        condition_status VARCHAR(20) DEFAULT 'good',
                        notes TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # التحقق من وجود المستخدم الافتراضي
                cursor.execute('SELECT COUNT(*) FROM users WHERE username = %s', ('admin',))
                if cursor.fetchone()[0] == 0:
                    # إنشاء المستخدم الافتراضي
                    admin_password = generate_password_hash('admin123')
                    cursor.execute('''
                        INSERT INTO users (username, password_hash, full_name, role)
                        VALUES (%s, %s, %s, %s)
                    ''', ('admin', admin_password, 'مدير النظام', 'admin'))
                
                # التحقق من وجود الفئات
                cursor.execute('SELECT COUNT(*) FROM categories')
                if cursor.fetchone()[0] == 0:
                    # إنشاء الفئات الافتراضية
                    categories = [
                        ('أجهزة الكمبيوتر', 'أجهزة الكمبيوتر المكتبية والمحمولة'),
                        ('الخوادم', 'خوادم الشبكة وقواعد البيانات'),
                        ('معدات الشبكة', 'أجهزة التوجيه والتبديل'),
                        ('الطابعات', 'أجهزة الطباعة والمسح'),
                        ('الهواتف', 'الهواتف الثابتة والذكية')
                    ]
                    
                    for name, desc in categories:
                        cursor.execute('INSERT INTO categories (name, description) VALUES (%s, %s)', (name, desc))
                
                # التحقق من وجود الأصول التجريبية
                cursor.execute('SELECT COUNT(*) FROM assets')
                if cursor.fetchone()[0] == 0:
                    # إنشاء أصول تجريبية
                    sample_assets = [
                        ('PC001', 'جهاز كمبيوتر مكتبي', 'جهاز كمبيوتر للموظفين', 1, 'Dell', 'OptiPlex 7090', 'DL123456', 2500.00),
                        ('LP001', 'جهاز لابتوب', 'جهاز محمول للإدارة', 1, 'HP', 'EliteBook 840', 'HP789012', 3200.00),
                        ('PR001', 'طابعة ليزر', 'طابعة مكتبية', 4, 'Canon', 'LBP6030', 'CN345678', 800.00),
                        ('SW001', 'جهاز تبديل شبكة', 'سويتش 24 منفذ', 3, 'Cisco', 'SG250-24', 'CS901234', 1500.00),
                        ('SV001', 'خادم رئيسي', 'خادم قاعدة البيانات', 2, 'Dell', 'PowerEdge R740', 'DL567890', 8500.00)
                    ]
                    
                    for asset in sample_assets:
                        cursor.execute('''
                            INSERT INTO assets (asset_tag, name, description, category_id, brand, model, serial_number, purchase_cost)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ''', asset)
                
                conn.commit()
                app.logger.info("تم إنشاء قاعدة البيانات بنجاح")
                
            except Exception as e:
                conn.rollback()
                app.logger.error(f"خطأ في إنشاء قاعدة البيانات: {e}")
            finally:
                cursor.close()
                conn.close()
    
    else:
        # استخدام SQLite للتطوير المحلي
        import sqlite3
        
        def get_db():
            """الحصول على اتصال SQLite"""
            conn = sqlite3.connect('production_assets.db')
            conn.row_factory = sqlite3.Row
            return conn
        
        def init_db():
            """إنشاء الجداول في SQLite"""
            conn = get_db()
            cursor = conn.cursor()
            
            # نفس الجداول مع تعديل الصيغة لـ SQLite
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS assets (
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
            
            # إدراج البيانات الافتراضية إذا لم تكن موجودة
            if cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', ('admin',)).fetchone()[0] == 0:
                admin_password = generate_password_hash('admin123')
                cursor.execute('''
                    INSERT INTO users (username, password_hash, full_name, role)
                    VALUES (?, ?, ?, ?)
                ''', ('admin', admin_password, 'مدير النظام', 'admin'))
            
            conn.commit()
            conn.close()
    
    # تهيئة قاعدة البيانات
    with app.app_context():
        init_db()
    
    def login_required(f):
        """تحقق من تسجيل الدخول"""
        from functools import wraps
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    
    @app.route('/')
    def index():
        """الصفحة الرئيسية"""
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        conn = get_db()
        cursor = conn.cursor()
        
        # إحصائيات
        if DATABASE_URL:
            cursor.execute('SELECT COUNT(*) as count FROM assets')
            total_assets = cursor.fetchone()['count']
            cursor.execute('SELECT COUNT(*) as count FROM assets WHERE status = %s', ('active',))
            active_assets = cursor.fetchone()['count']
            cursor.execute('SELECT COUNT(*) as count FROM categories')
            categories_count = cursor.fetchone()['count']
            
            # الأصول الحديثة
            cursor.execute('''
                SELECT a.*, c.name as category_name 
                FROM assets a 
                LEFT JOIN categories c ON a.category_id = c.id 
                ORDER BY a.created_at DESC 
                LIMIT 5
            ''')
            recent_assets = cursor.fetchall()
        else:
            cursor.execute('SELECT COUNT(*) as count FROM assets')
            total_assets = cursor.fetchone()['count']
            cursor.execute('SELECT COUNT(*) as count FROM assets WHERE status = ?', ('active',))
            active_assets = cursor.fetchone()['count']
            cursor.execute('SELECT COUNT(*) as count FROM categories')
            categories_count = cursor.fetchone()['count']
            
            cursor.execute('''
                SELECT a.*, c.name as category_name 
                FROM assets a 
                LEFT JOIN categories c ON a.category_id = c.id 
                ORDER BY a.created_at DESC 
                LIMIT 5
            ''')
            recent_assets = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template_string(DASHBOARD_TEMPLATE, 
            total_assets=total_assets,
            active_assets=active_assets,
            categories_count=categories_count,
            recent_assets=recent_assets,
            user_name=session.get('user_name', 'المستخدم'))
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """تسجيل الدخول"""
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            conn = get_db()
            cursor = conn.cursor()
            
            if DATABASE_URL:
                cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
            else:
                cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if user and check_password_hash(user['password_hash'], password):
                session['user_id'] = user['id']
                session['user_name'] = user['full_name']
                session['role'] = user['role']
                flash('تم تسجيل الدخول بنجاح', 'success')
                return redirect(url_for('index'))
            else:
                flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
        
        return render_template_string(LOGIN_TEMPLATE)
    
    @app.route('/logout')
    def logout():
        """تسجيل الخروج"""
        session.clear()
        flash('تم تسجيل الخروج بنجاح', 'success')
        return redirect(url_for('login'))
    
    @app.route('/assets')
    @login_required
    def assets():
        """قائمة الأصول"""
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT a.*, c.name as category_name
            FROM assets a
            LEFT JOIN categories c ON a.category_id = c.id
            ORDER BY a.created_at DESC
        ''')
        assets = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template_string(ASSETS_TEMPLATE, 
            assets=assets,
            user_name=session.get('user_name', 'المستخدم'))
    
    @app.route('/add_asset', methods=['GET', 'POST'])
    @login_required
    def add_asset():
        """إضافة أصل جديد"""
        if request.method == 'POST':
            try:
                conn = get_db()
                cursor = conn.cursor()
                
                if DATABASE_URL:
                    cursor.execute('''
                        INSERT INTO assets (asset_tag, name, description, category_id, brand, model, 
                                          serial_number, purchase_cost, status, condition_status, notes)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                else:
                    cursor.execute('''
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
                cursor.close()
                conn.close()
                
                flash('تم إضافة الأصل بنجاح', 'success')
                return redirect(url_for('assets'))
                
            except Exception as e:
                flash(f'خطأ في إضافة الأصل: {str(e)}', 'error')
        
        # جلب الفئات
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM categories ORDER BY name')
        categories = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return render_template_string(ADD_ASSET_TEMPLATE, 
            categories=categories,
            user_name=session.get('user_name', 'المستخدم'))
    
    @app.route('/categories')
    @login_required
    def categories():
        """قائمة الفئات"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM categories ORDER BY name')
        categories = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return render_template_string(CATEGORIES_TEMPLATE, 
            categories=categories,
            user_name=session.get('user_name', 'المستخدم'))
    
    @app.route('/health')
    def health():
        """فحص صحة التطبيق"""
        return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}
    
    return app

# قوالب HTML (نفس القوالب من النسخة المبسطة)
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تسجيل الدخول - نظام إدارة الأصول</title>
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
        }
        .btn-primary { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            border: none; 
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-6 col-lg-4">
                <div class="login-card p-5">
                    <div class="text-center mb-4">
                        <i class="fas fa-laptop fa-3x text-primary mb-3"></i>
                        <h2>نظام إدارة الأصول</h2>
                        <p class="text-muted">النسخة السحابية</p>
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
                            <i class="fas fa-sign-in-alt"></i> تسجيل الدخول
                        </button>
                    </form>
                    
                    <div class="mt-4 p-3 bg-light rounded text-center">
                        <small>
                            <strong>بيانات تجريبية:</strong><br>
                            المستخدم: admin | كلمة المرور: admin123
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
    <title>لوحة التحكم - نظام إدارة الأصول</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; }
        .navbar-custom { background: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stats-card { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            border-radius: 15px; 
            transition: transform 0.3s ease;
        }
        .stats-card:hover { transform: translateY(-5px); }
        .card { border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 15px; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; }
        .cloud-badge { 
            background: linear-gradient(45deg, #00c6ff, #0072ff); 
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
            <a class="navbar-brand fw-bold" href="{{ url_for('index') }}">
                <i class="fas fa-cloud text-primary"></i> إدارة الأصول السحابية
                <span class="cloud-badge ms-2">☁️ Cloud</span>
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="{{ url_for('assets') }}">
                    <i class="fas fa-desktop"></i> الأصول
                </a>
                <a class="nav-link" href="{{ url_for('categories') }}">
                    <i class="fas fa-tags"></i> الفئات
                </a>
                <div class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
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
        <div class="alert alert-info">
            <i class="fas fa-cloud"></i> 
            <strong>النسخة السحابية:</strong> 
            نظام إدارة الأصول متاح الآن عبر الإنترنت مع قاعدة بيانات سحابية آمنة
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
                    <i class="fas fa-tags fa-3x mb-3"></i>
                    <h3>{{ categories_count }}</h3>
                    <p class="mb-0">الفئات</p>
                </div>
            </div>
        </div>

        <div class="row">
            <div class="col-lg-8 mb-4">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">الأصول المضافة حديثاً</h5>
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
                                        <th>الحالة</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for asset in recent_assets %}
                                    <tr>
                                        <td><strong class="text-primary">{{ asset.asset_tag }}</strong></td>
                                        <td>{{ asset.name }}</td>
                                        <td><span class="badge bg-secondary">{{ asset.category_name or 'غير محدد' }}</span></td>
                                        <td><span class="badge bg-success">{{ asset.status }}</span></td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                        {% else %}
                        <div class="text-center py-4">
                            <i class="fas fa-inbox fa-3x text-muted mb-3"></i>
                            <p class="text-muted">لا توجد أصول</p>
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
                        </div>
                    </div>
                </div>
                
                <div class="card mt-3">
                    <div class="card-header">
                        <h6 class="mb-0">معلومات النشر</h6>
                    </div>
                    <div class="card-body">
                        <small class="text-muted">
                            <i class="fas fa-server"></i> قاعدة بيانات سحابية<br>
                            <i class="fas fa-shield-alt"></i> اتصال آمن (SSL)<br>
                            <i class="fas fa-globe"></i> متاح عالمياً
                        </small>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

ASSETS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>قائمة الأصول - نظام إدارة الأصول</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; }
        .navbar-custom { background: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .card { border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 15px; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; }
        .cloud-badge { 
            background: linear-gradient(45deg, #00c6ff, #0072ff); 
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
            <a class="navbar-brand fw-bold" href="{{ url_for('index') }}">
                <i class="fas fa-cloud text-primary"></i> إدارة الأصول السحابية
                <span class="cloud-badge ms-2">☁️ Cloud</span>
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link active" href="{{ url_for('assets') }}">
                    <i class="fas fa-desktop"></i> الأصول
                </a>
                <a class="nav-link" href="{{ url_for('categories') }}">
                    <i class="fas fa-tags"></i> الفئات
                </a>
                <div class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
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
                <h5 class="mb-0">قائمة الأصول ({{ assets|length }})</h5>
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
                                    {{ "%.2f"|format(asset.purchase_cost) }} ريال
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

ADD_ASSET_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>إضافة أصل جديد - نظام إدارة الأصول</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; }
        .navbar-custom { background: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .card { border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 15px; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; }
        .cloud-badge { 
            background: linear-gradient(45deg, #00c6ff, #0072ff); 
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
            <a class="navbar-brand fw-bold" href="{{ url_for('index') }}">
                <i class="fas fa-cloud text-primary"></i> إدارة الأصول السحابية
                <span class="cloud-badge ms-2">☁️ Cloud</span>
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="{{ url_for('assets') }}">
                    <i class="fas fa-desktop"></i> الأصول
                </a>
                <a class="nav-link" href="{{ url_for('categories') }}">
                    <i class="fas fa-tags"></i> الفئات
                </a>
                <div class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
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
                                    <input type="text" class="form-control" name="asset_tag" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">اسم الأصل *</label>
                                    <input type="text" class="form-control" name="name" required>
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">الوصف</label>
                                <textarea class="form-control" name="description" rows="3"></textarea>
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
                                    <input type="text" class="form-control" name="brand">
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">الموديل</label>
                                    <input type="text" class="form-control" name="model">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">الرقم التسلسلي</label>
                                    <input type="text" class="form-control" name="serial_number">
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">تكلفة الشراء</label>
                                    <input type="number" step="0.01" class="form-control" name="purchase_cost">
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
                                <textarea class="form-control" name="notes" rows="3"></textarea>
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

CATEGORIES_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>الفئات - نظام إدارة الأصول</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; }
        .navbar-custom { background: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .card { border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 15px; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; }
        .cloud-badge { 
            background: linear-gradient(45deg, #00c6ff, #0072ff); 
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
            <a class="navbar-brand fw-bold" href="{{ url_for('index') }}">
                <i class="fas fa-cloud text-primary"></i> إدارة الأصول السحابية
                <span class="cloud-badge ms-2">☁️ Cloud</span>
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="{{ url_for('assets') }}">
                    <i class="fas fa-desktop"></i> الأصول
                </a>
                <a class="nav-link active" href="{{ url_for('categories') }}">
                    <i class="fas fa-tags"></i> الفئات
                </a>
                <div class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
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
                <h5 class="mb-0">فئات الأصول ({{ categories|length }})</h5>
            </div>
            <div class="card-body">
                <div class="row">
                    {% for category in categories %}
                    <div class="col-md-6 col-lg-4 mb-3">
                        <div class="card h-100">
                            <div class="card-body">
                                <h6 class="card-title">
                                    <i class="fas fa-tag text-primary"></i> {{ category.name }}
                                </h6>
                                <p class="card-text text-muted">{{ category.description or 'لا يوجد وصف' }}</p>
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

# إنشاء التطبيق
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=(FLASK_ENV != 'production'))