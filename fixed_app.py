#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام إدارة الأصول التقنية - إصدار محدث
IT Asset Management System - Fixed Version
"""

import os
import sys
import sqlite3
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash

def create_database():
    """إنشاء قاعدة البيانات يدوياً"""
    db_path = 'it_assets_fixed.db'
    
    # حذف قاعدة البيانات القديمة إذا كانت موجودة
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # إنشاء جدول المستخدمين
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
    
    # إنشاء جدول الفئات
    cursor.execute('''
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) UNIQUE NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # إنشاء جدول المواقع
    cursor.execute('''
        CREATE TABLE locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            building VARCHAR(100),
            floor VARCHAR(50),
            room VARCHAR(50),
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # إنشاء جدول الموردين
    cursor.execute('''
        CREATE TABLE suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(200) NOT NULL,
            contact_person VARCHAR(100),
            phone VARCHAR(20),
            email VARCHAR(120),
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # إنشاء جدول الموظفين
    cursor.execute('''
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id VARCHAR(50) UNIQUE NOT NULL,
            full_name VARCHAR(100) NOT NULL,
            department VARCHAR(100),
            position VARCHAR(100),
            email VARCHAR(120),
            phone VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # إنشاء جدول الأصول
    cursor.execute('''
        CREATE TABLE assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_tag VARCHAR(50) UNIQUE NOT NULL,
            name VARCHAR(200) NOT NULL,
            description TEXT,
            category_id INTEGER,
            location_id INTEGER,
            supplier_id INTEGER,
            brand VARCHAR(100),
            model VARCHAR(100),
            serial_number VARCHAR(100),
            specifications TEXT,
            purchase_date DATE,
            purchase_cost DECIMAL(10,2),
            warranty_expiry DATE,
            status VARCHAR(20) DEFAULT 'active',
            condition VARCHAR(20) DEFAULT 'good',
            image_path VARCHAR(255),
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id),
            FOREIGN KEY (location_id) REFERENCES locations (id),
            FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
        )
    ''')
    
    # إنشاء جدول سجل الصيانة
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
            next_maintenance DATE,
            notes TEXT,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (asset_id) REFERENCES assets (id),
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')
    
    # إنشاء جدول تخصيص الأصول
    cursor.execute('''
        CREATE TABLE asset_assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_id INTEGER NOT NULL,
            employee_id INTEGER NOT NULL,
            assigned_date DATE NOT NULL,
            return_date DATE,
            notes TEXT,
            assigned_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (asset_id) REFERENCES assets (id),
            FOREIGN KEY (employee_id) REFERENCES employees (id),
            FOREIGN KEY (assigned_by) REFERENCES users (id)
        )
    ''')
    
    # إدراج البيانات الافتراضية
    
    # المستخدم الافتراضي
    admin_password = generate_password_hash('admin123')
    cursor.execute('''
        INSERT INTO users (username, email, password_hash, full_name, role)
        VALUES (?, ?, ?, ?, ?)
    ''', ('admin', 'admin@company.com', admin_password, 'مدير النظام', 'admin'))
    
    # الفئات الافتراضية
    categories = [
        ('أجهزة الكمبيوتر', 'أجهزة الكمبيوتر المكتبية والمحمولة'),
        ('الخوادم', 'خوادم الشبكة وقواعد البيانات'),
        ('معدات الشبكة', 'أجهزة التوجيه والتبديل والشبكات'),
        ('الطابعات والماسحات', 'أجهزة الطباعة والمسح الضوئي'),
        ('الهواتف', 'الهواتف الثابتة والذكية'),
        ('الشاشات والعرض', 'شاشات الكمبيوتر وأجهزة العرض'),
        ('أجهزة التخزين', 'أقراص صلبة خارجية ووحدات التخزين'),
        ('معدات الأمان', 'كاميرات المراقبة وأنظمة الأمان')
    ]
    
    for name, desc in categories:
        cursor.execute('INSERT INTO categories (name, description) VALUES (?, ?)', (name, desc))
    
    # المواقع الافتراضية
    locations = [
        ('المبنى الرئيسي - الطابق الأول', 'المبنى الرئيسي', 'الأول', None),
        ('المبنى الرئيسي - الطابق الثاني', 'المبنى الرئيسي', 'الثاني', None),
        ('قسم تقنية المعلومات', 'المبنى الرئيسي', 'الثالث', '301'),
        ('قاعة الاجتماعات الكبرى', 'المبنى الرئيسي', 'الأول', '105'),
        ('المستودع', 'المبنى الفرعي', 'الأرضي', None)
    ]
    
    for name, building, floor, room in locations:
        cursor.execute('INSERT INTO locations (name, building, floor, room) VALUES (?, ?, ?, ?)', 
                      (name, building, floor, room))
    
    # الموردين الافتراضيين
    suppliers = [
        ('شركة التقنية المتقدمة', 'أحمد محمد', '0112345678', 'info@advanced-tech.com'),
        ('مؤسسة الحاسوب الحديث', 'فاطمة علي', '0123456789', 'sales@modern-pc.com'),
        ('شركة الشبكات المتطورة', 'محمد خالد', '0134567890', 'support@advanced-networks.com')
    ]
    
    for name, contact, phone, email in suppliers:
        cursor.execute('INSERT INTO suppliers (name, contact_person, phone, email) VALUES (?, ?, ?, ?)', 
                      (name, contact, phone, email))
    
    conn.commit()
    conn.close()
    
    print("✅ تم إنشاء قاعدة البيانات بنجاح")
    return db_path

def create_simple_flask_app():
    """إنشاء تطبيق Flask مبسط"""
    try:
        from flask import Flask, render_template_string, request, redirect, url_for, flash, session, jsonify
        import sqlite3
        from functools import wraps
        
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'dev-secret-key-2025'
        
        DB_PATH = 'it_assets_fixed.db'
        
        def get_db_connection():
            """الحصول على اتصال قاعدة البيانات"""
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            return conn
        
        def login_required(f):
            """تحقق من تسجيل الدخول"""
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if 'user_id' not in session:
                    return redirect(url_for('login'))
                return f(*args, **kwargs)
            return decorated_function
        
        def get_current_user():
            """الحصول على المستخدم الحالي"""
            if 'user_id' in session:
                conn = get_db_connection()
                user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
                conn.close()
                return user
            return None
        
        @app.route('/')
        def index():
            """الصفحة الرئيسية"""
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            conn = get_db_connection()
            
            # إحصائيات
            total_assets = conn.execute('SELECT COUNT(*) as count FROM assets').fetchone()['count']
            active_assets = conn.execute('SELECT COUNT(*) as count FROM assets WHERE status = "active"').fetchone()['count']
            maintenance_assets = conn.execute('SELECT COUNT(*) as count FROM assets WHERE status = "maintenance"').fetchone()['count']
            total_maintenance = conn.execute('SELECT COUNT(*) as count FROM maintenance_records').fetchone()['count']
            
            # الأصول الحديثة
            recent_assets = conn.execute('''
                SELECT a.*, c.name as category_name 
                FROM assets a 
                LEFT JOIN categories c ON a.category_id = c.id 
                ORDER BY a.created_at DESC 
                LIMIT 5
            ''').fetchall()
            
            # الصيانة المستحقة
            overdue_maintenance = conn.execute('''
                SELECT a.name, a.asset_tag, m.next_maintenance
                FROM assets a
                JOIN maintenance_records m ON a.id = m.asset_id
                WHERE m.next_maintenance < date('now') AND m.status != 'completed'
                ORDER BY m.next_maintenance
                LIMIT 5
            ''').fetchall()
            
            conn.close()
            
            user = get_current_user()
            
            return render_template_string('''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>نظام إدارة الأصول التقنية</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: #f8f9fa;
        }
        .header { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            padding: 2rem 0; 
            margin-bottom: 2rem;
        }
        .stats-card { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            border-radius: 15px; 
            padding: 20px; 
            margin-bottom: 20px; 
            transition: transform 0.3s ease;
        }
        .stats-card:hover {
            transform: translateY(-5px);
        }
        .card {
            border: none;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-radius: 15px;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
        }
        .navbar-custom {
            background: #fff;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 1rem 0;
        }
    </style>
</head>
<body>
    <!-- شريط التنقل -->
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold" href="{{ url_for('index') }}">
                <i class="fas fa-laptop text-primary"></i> إدارة الأصول
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="{{ url_for('assets') }}">
                    <i class="fas fa-desktop"></i> الأصول
                </a>
                <a class="nav-link" href="{{ url_for('maintenance') }}">
                    <i class="fas fa-tools"></i> الصيانة
                </a>
                <a class="nav-link" href="{{ url_for('reports') }}">
                    <i class="fas fa-chart-bar"></i> التقارير
                </a>
                <div class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                        <i class="fas fa-user"></i> {{ user.full_name }}
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

    <div class="container">
        <!-- الإحصائيات -->
        <div class="row mb-4">
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="stats-card text-center">
                    <i class="fas fa-laptop fa-3x mb-3"></i>
                    <h3>{{ total_assets }}</h3>
                    <p>إجمالي الأصول</p>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="stats-card text-center">
                    <i class="fas fa-check-circle fa-3x mb-3"></i>
                    <h3>{{ active_assets }}</h3>
                    <p>أصول نشطة</p>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="stats-card text-center">
                    <i class="fas fa-tools fa-3x mb-3"></i>
                    <h3>{{ maintenance_assets }}</h3>
                    <p>قيد الصيانة</p>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="stats-card text-center">
                    <i class="fas fa-wrench fa-3x mb-3"></i>
                    <h3>{{ total_maintenance }}</h3>
                    <p>عمليات الصيانة</p>
                </div>
            </div>
        </div>

        <div class="row">
            <!-- الأصول الحديثة -->
            <div class="col-lg-8 mb-4">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">
                            <i class="fas fa-plus-circle text-primary"></i> الأصول المضافة حديثاً
                        </h5>
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
                                        <th>تاريخ الإضافة</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for asset in recent_assets %}
                                    <tr>
                                        <td><strong class="text-primary">{{ asset.asset_tag }}</strong></td>
                                        <td>{{ asset.name }}</td>
                                        <td>
                                            <span class="badge bg-secondary">{{ asset.category_name or 'غير محدد' }}</span>
                                        </td>
                                        <td>
                                            <span class="badge bg-{{ 'success' if asset.status == 'active' else 'warning' }}">
                                                {% if asset.status == 'active' %}نشط
                                                {% elif asset.status == 'maintenance' %}صيانة
                                                {% elif asset.status == 'retired' %}متقاعد
                                                {% else %}{{ asset.status }}{% endif %}
                                            </span>
                                        </td>
                                        <td>{{ asset.created_at[:10] }}</td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                        {% else %}
                        <div class="text-center py-4">
                            <i class="fas fa-inbox fa-3x text-muted mb-3"></i>
                            <p class="text-muted">لا توجد أصول مضافة بعد</p>
                            <a href="{{ url_for('add_asset') }}" class="btn btn-primary">
                                <i class="fas fa-plus"></i> إضافة أول أصل
                            </a>
                        </div>
                        {% endif %}
                    </div>
                </div>
            </div>

            <!-- الصيانة المستحقة -->
            <div class="col-lg-4 mb-4">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">
                            <i class="fas fa-exclamation-triangle text-warning"></i> الصيانة المستحقة
                        </h5>
                    </div>
                    <div class="card-body">
                        {% if overdue_maintenance %}
                        {% for item in overdue_maintenance %}
                        <div class="d-flex justify-content-between align-items-center mb-3 p-2 bg-light rounded">
                            <div>
                                <strong>{{ item.name }}</strong>
                                <br><small class="text-muted">{{ item.asset_tag }}</small>
                            </div>
                            <span class="badge bg-danger">{{ item.next_maintenance }}</span>
                        </div>
                        {% endfor %}
                        {% else %}
                        <div class="text-center py-4">
                            <i class="fas fa-check-circle fa-3x text-success mb-3"></i>
                            <p class="text-muted">لا توجد صيانة مستحقة</p>
                        </div>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>

        <!-- الإجراءات السريعة -->
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">
                            <i class="fas fa-bolt text-warning"></i> الإجراءات السريعة
                        </h5>
                    </div>
                    <div class="card-body">
                        <div class="row text-center">
                            <div class="col-md-3 mb-3">
                                <a href="{{ url_for('add_asset') }}" class="btn btn-outline-primary btn-lg w-100">
                                    <i class="fas fa-plus fa-2x mb-2"></i>
                                    <br>إضافة أصل جديد
                                </a>
                            </div>
                            <div class="col-md-3 mb-3">
                                <a href="{{ url_for('assets') }}" class="btn btn-outline-info btn-lg w-100">
                                    <i class="fas fa-search fa-2x mb-2"></i>
                                    <br>البحث في الأصول
                                </a>
                            </div>
                            <div class="col-md-3 mb-3">
                                <a href="{{ url_for('add_maintenance') }}" class="btn btn-outline-warning btn-lg w-100">
                                    <i class="fas fa-calendar-plus fa-2x mb-2"></i>
                                    <br>جدولة صيانة
                                </a>
                            </div>
                            <div class="col-md-3 mb-3">
                                <a href="{{ url_for('reports') }}" class="btn btn-outline-success btn-lg w-100">
                                    <i class="fas fa-chart-bar fa-2x mb-2"></i>
                                    <br>إنشاء تقرير
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
            ''', user=user, total_assets=total_assets, active_assets=active_assets, 
                maintenance_assets=maintenance_assets, total_maintenance=total_maintenance,
                recent_assets=recent_assets, overdue_maintenance=overdue_maintenance)
        
        @app.route('/login', methods=['GET', 'POST'])
        def login():
            """تسجيل الدخول"""
            if request.method == 'POST':
                username = request.form['username']
                password = request.form['password']
                
                conn = get_db_connection()
                user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
                conn.close()
                
                if user and check_password_hash(user['password_hash'], password):
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    session['full_name'] = user['full_name']
                    session['role'] = user['role']
                    flash('تم تسجيل الدخول بنجاح', 'success')
                    return redirect(url_for('index'))
                else:
                    flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
            
            return render_template_string('''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تسجيل الدخول - نظام إدارة الأصول التقنية</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            min-height: 100vh; 
            display: flex; 
            align-items: center; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .login-card { 
            background: white; 
            border-radius: 20px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .login-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            text-align: center;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            padding: 12px;
        }
        .form-control {
            border-radius: 10px;
            padding: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-6 col-lg-5">
                <div class="login-card">
                    <div class="login-header">
                        <i class="fas fa-laptop fa-3x mb-3"></i>
                        <h2>نظام إدارة الأصول التقنية</h2>
                        <p class="mb-0">يرجى تسجيل الدخول للمتابعة</p>
                    </div>
                    
                    <div class="p-4">
                        {% with messages = get_flashed_messages(with_categories=true) %}
                            {% if messages %}
                                {% for category, message in messages %}
                                    <div class="alert alert-{{ 'danger' if category == 'error' else 'success' }} alert-dismissible fade show">
                                        {{ message }}
                                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                                    </div>
                                {% endfor %}
                            {% endif %}
                        {% endwith %}
                        
                        <form method="POST">
                            <div class="mb-3">
                                <label class="form-label">
                                    <i class="fas fa-user text-primary"></i> اسم المستخدم
                                </label>
                                <input type="text" class="form-control" name="username" required 
                                       placeholder="أدخل اسم المستخدم">
                            </div>
                            <div class="mb-4">
                                <label class="form-label">
                                    <i class="fas fa-lock text-primary"></i> كلمة المرور
                                </label>
                                <input type="password" class="form-control" name="password" required 
                                       placeholder="أدخل كلمة المرور">
                            </div>
                            <button type="submit" class="btn btn-primary w-100 btn-lg">
                                <i class="fas fa-sign-in-alt"></i> تسجيل الدخول
                            </button>
                        </form>
                        
                        <div class="mt-4 p-3 bg-light rounded">
                            <h6 class="text-primary">
                                <i class="fas fa-info-circle"></i> بيانات تسجيل الدخول الافتراضية:
                            </h6>
                            <div class="row">
                                <div class="col-6">
                                    <small><strong>اسم المستخدم:</strong></small>
                                    <br><code class="text-primary">admin</code>
                                </div>
                                <div class="col-6">
                                    <small><strong>كلمة المرور:</strong></small>
                                    <br><code class="text-primary">admin123</code>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
            ''')
        
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
            conn = get_db_connection()
            assets = conn.execute('''
                SELECT a.*, c.name as category_name, l.name as location_name, s.name as supplier_name
                FROM assets a
                LEFT JOIN categories c ON a.category_id = c.id
                LEFT JOIN locations l ON a.location_id = l.id
                LEFT JOIN suppliers s ON a.supplier_id = s.id
                ORDER BY a.created_at DESC
            ''').fetchall()
            conn.close()
            
            user = get_current_user()
            
            return render_template_string('''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>قائمة الأصول - نظام إدارة الأصول التقنية</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f8f9fa; }
        .navbar-custom { background: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .card { border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 15px; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; }
        .page-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem 0; margin-bottom: 2rem; }
    </style>
</head>
<body>
    <!-- شريط التنقل -->
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold" href="{{ url_for('index') }}">
                <i class="fas fa-laptop text-primary"></i> إدارة الأصول
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link active" href="{{ url_for('assets') }}">
                    <i class="fas fa-desktop"></i> الأصول
                </a>
                <a class="nav-link" href="{{ url_for('maintenance') }}">
                    <i class="fas fa-tools"></i> الصيانة
                </a>
                <a class="nav-link" href="{{ url_for('reports') }}">
                    <i class="fas fa-chart-bar"></i> التقارير
                </a>
                <div class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                        <i class="fas fa-user"></i> {{ user.full_name }}
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

    <!-- رأس الصفحة -->
    <div class="page-header text-center">
        <div class="container">
            <h1><i class="fas fa-desktop"></i> قائمة الأصول</h1>
            <p class="mb-0">إدارة وتتبع جميع الأصول التقنية</p>
        </div>
    </div>

    <div class="container">
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">
                    <i class="fas fa-list"></i> جميع الأصول ({{ assets|length }})
                </h5>
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
                                <th>الموقع</th>
                                <th>المورد</th>
                                <th>الحالة</th>
                                <th>تاريخ الإضافة</th>
                                <th>الإجراءات</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for asset in assets %}
                            <tr>
                                <td><strong class="text-primary">{{ asset.asset_tag }}</strong></td>
                                <td>
                                    <strong>{{ asset.name }}</strong>
                                    {% if asset.brand or asset.model %}
                                    <br><small class="text-muted">{{ asset.brand }} {{ asset.model }}</small>
                                    {% endif %}
                                </td>
                                <td>
                                    <span class="badge bg-secondary">{{ asset.category_name or 'غير محدد' }}</span>
                                </td>
                                <td>{{ asset.location_name or 'غير محدد' }}</td>
                                <td>{{ asset.supplier_name or 'غير محدد' }}</td>
                                <td>
                                    <span class="badge bg-{{ 'success' if asset.status == 'active' else 'warning' if asset.status == 'maintenance' else 'secondary' }}">
                                        {% if asset.status == 'active' %}نشط
                                        {% elif asset.status == 'maintenance' %}صيانة
                                        {% elif asset.status == 'retired' %}متقاعد
                                        {% else %}{{ asset.status }}{% endif %}
                                    </span>
                                </td>
                                <td>{{ asset.created_at[:10] }}</td>
                                <td>
                                    <div class="btn-group" role="group">
                                        <a href="{{ url_for('view_asset', id=asset.id) }}" class="btn btn-sm btn-outline-primary" title="عرض">
                                            <i class="fas fa-eye"></i>
                                        </a>
                                        <a href="{{ url_for('edit_asset', id=asset.id) }}" class="btn btn-sm btn-outline-warning" title="تعديل">
                                            <i class="fas fa-edit"></i>
                                        </a>
                                        <a href="{{ url_for('asset_qr', id=asset.id) }}" class="btn btn-sm btn-outline-info" title="QR Code">
                                            <i class="fas fa-qrcode"></i>
                                        </a>
                                    </div>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <div class="text-center py-5">
                    <i class="fas fa-inbox fa-3x text-muted mb-3"></i>
                    <h5 class="text-muted">لا توجد أصول مضافة بعد</h5>
                    <p class="text-muted">ابدأ بإضافة أول أصل في النظام</p>
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
            ''', assets=assets, user=user)
        
        # باقي الصفحات (مبسطة)
        @app.route('/add_asset')
        @login_required
        def add_asset():
            return render_template_string('<h1>صفحة إضافة أصل - قيد التطوير</h1><a href="{{ url_for(\'index\') }}">العودة للرئيسية</a>')
        
        @app.route('/view_asset/<int:id>')
        @login_required
        def view_asset(id):
            return render_template_string('<h1>صفحة عرض الأصل - قيد التطوير</h1><a href="{{ url_for(\'assets\') }}">العودة للأصول</a>')
        
        @app.route('/edit_asset/<int:id>')
        @login_required
        def edit_asset(id):
            return render_template_string('<h1>صفحة تعديل الأصل - قيد التطوير</h1><a href="{{ url_for(\'assets\') }}">العودة للأصول</a>')
        
        @app.route('/asset_qr/<int:id>')
        @login_required
        def asset_qr(id):
            return render_template_string('<h1>QR Code - قيد التطوير</h1><a href="{{ url_for(\'assets\') }}">العودة للأصول</a>')
        
        @app.route('/maintenance')
        @login_required
        def maintenance():
            return render_template_string('<h1>صفحة الصيانة - قيد التطوير</h1><a href="{{ url_for(\'index\') }}">العودة للرئيسية</a>')
        
        @app.route('/add_maintenance')
        @login_required
        def add_maintenance():
            return render_template_string('<h1>صفحة إضافة صيانة - قيد التطوير</h1><a href="{{ url_for(\'index\') }}">العودة للرئيسية</a>')
        
        @app.route('/reports')
        @login_required
        def reports():
            return render_template_string('<h1>صفحة التقارير - قيد التطوير</h1><a href="{{ url_for(\'index\') }}">العودة للرئيسية</a>')
        
        return app
        
    except ImportError as e:
        print(f"❌ خطأ في استيراد المكتبات: {e}")
        return None

def main():
    """الدالة الرئيسية"""
    print("=" * 70)
    print("🚀 نظام إدارة الأصول التقنية - الإصدار المحدث")
    print("   IT Asset Management System - Fixed Version")
    print("=" * 70)
    print()
    
    # إنشاء قاعدة البيانات
    print("📊 إنشاء قاعدة البيانات...")
    db_path = create_database()
    
    # إنشاء التطبيق
    print("🔧 إنشاء التطبيق...")
    app = create_simple_flask_app()
    
    if not app:
        print("❌ فشل في إنشاء التطبيق")
        return
    
    print("✅ النظام جاهز للتشغيل!")
    print("🌐 الخادم: http://localhost:5000")
    print("👤 المستخدم: admin")
    print("🔑 كلمة المرور: admin123")
    print("🔧 للإيقاف: اضغط Ctrl+C")
    print("=" * 70)
    print()
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n⏹️  تم إيقاف النظام بنجاح")
    except Exception as e:
        print(f"\n❌ خطأ في تشغيل النظام: {e}")

if __name__ == '__main__':
    main()