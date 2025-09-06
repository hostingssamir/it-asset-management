#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from datetime import datetime, timedelta
import random

# إنشاء التطبيق
def create_app():
    app = Flask(__name__)
    app.secret_key = 'your-secret-key-here'
    
    # صفحة تسجيل الدخول
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            if username == 'admin' and password == 'admin123':
                session['logged_in'] = True
                session['username'] = username
                return redirect(url_for('dashboard'))
            else:
                flash('اسم المستخدم أو كلمة المرور غير صحيحة')
        
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
        
        cursor.execute("SELECT SUM(cost) FROM assets")
        total_cost = cursor.fetchone()[0] or 0
        
        # أحدث الأصول
        cursor.execute("SELECT tag, name, category, cost FROM assets ORDER BY created_at DESC LIMIT 5")
        recent_assets = cursor.fetchall()
        
        conn.close()
        
        return render_template_string(DASHBOARD_TEMPLATE, 
                                    total_assets=total_assets,
                                    active_assets=active_assets,
                                    total_cost=total_cost,
                                    recent_assets=recent_assets)
    
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
                
                flash(f'تم إضافة الأصل "{request.form["name"]}" بنجاح!')
                return redirect(url_for('add_asset'))
                
            except Exception as e:
                flash(f'خطأ في إضافة الأصل: {str(e)}')
        
        return render_template_string(ADD_ASSET_TEMPLATE)
    
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
    
    # صفحة الفواتير
    @app.route('/invoices')
    def invoices():
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        
        return render_template_string('<h1>صفحة الفواتير قيد التطوير</h1>')
    
    # صفحة التراخيص
    @app.route('/licenses')
    def licenses():
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        
        return render_template_string('<h1>صفحة التراخيص قيد التطوير</h1>')
    
    # صفحة الإشعارات
    @app.route('/notifications')
    def notifications():
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        
        return render_template_string('<h1>صفحة الإشعارات قيد التطوير</h1>')
    
    # صفحة الدعم الفني
    @app.route('/support')
    def support():
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        
        return render_template_string('<h1>صفحة الدعم الفني قيد التطوير</h1>')
    
    # صفحة التقارير
    @app.route('/reports')
    def reports():
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        
        return render_template_string('<h1>صفحة التقارير قيد التطوير</h1>')
    
    # تسجيل الخروج
    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('login'))
    
    return app

# قوالب HTML
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>تسجيل الدخول</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card mt-5">
                    <div class="card-header text-center">
                        <h3>🚀 نظام إدارة الأصول</h3>
                    </div>
                    <div class="card-body">
                        {% with messages = get_flashed_messages() %}
                            {% if messages %}
                                {% for message in messages %}
                                    <div class="alert alert-danger">{{ message }}</div>
                                {% endfor %}
                            {% endif %}
                        {% endwith %}
                        
                        <form method="POST">
                            <div class="mb-3">
                                <label class="form-label">اسم المستخدم</label>
                                <input type="text" class="form-control" name="username" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">كلمة المرور</label>
                                <input type="password" class="form-control" name="password" required>
                            </div>
                            <button type="submit" class="btn btn-primary w-100">تسجيل الدخول</button>
                        </form>
                        
                        <div class="mt-3 text-center">
                            <small class="text-muted">
                                المستخدم: admin | كلمة المرور: admin123
                            </small>
                        </div>
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
                    <li class="nav-item"><a class="nav-link text-white" href="/notifications">🔔 الإشعارات</a></li>
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
                                        <td><strong>{{ asset[0] }}</strong></td>
                                        <td>{{ asset[1] }}</td>
                                        <td><span class="badge bg-secondary">{{ asset[2] }}</span></td>
                                        <td>{{ "%.0f"|format(asset[3]) }} ريال</td>
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
                            <a href="/purchases" class="btn btn-outline-success">
                                <i class="fas fa-shopping-cart"></i> إدارة المشتريات
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
                    <li class="nav-item"><a class="nav-link text-white" href="/notifications">🔔 الإشعارات</a></li>
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
                                <th>القيمة</th>
                                <th>الحالة</th>
                                <th>الإجراءات</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for asset in assets %}
                            <tr>
                                <td><strong>{{ asset[1] }}</strong></td>
                                <td>{{ asset[2] }}</td>
                                <td><span class="badge bg-secondary">{{ asset[3] }}</span></td>
                                <td>{{ asset[4] }}</td>
                                <td>{{ "%.0f"|format(asset[7]) }} ريال</td>
                                <td>
                                    <span class="badge bg-{{ 'success' if asset[12] == 'نشط' else 'warning' }}">
                                        {{ asset[12] }}
                                    </span>
                                </td>
                                <td>
                                    <button class="btn btn-primary btn-sm me-1">
                                        <i class="fas fa-edit"></i>
                                    </button>
                                    <button class="btn btn-danger btn-sm">
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
                    <li class="nav-item"><a class="nav-link text-white" href="/notifications">🔔 الإشعارات</a></li>
                    <li class="nav-item"><a class="nav-link text-white" href="/logout">🚪 خروج</a></li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row justify-content-center">
            <div class="col-lg-8">
                <div class="card">
                    <div class="card-header">
                        <h3><i class="fas fa-plus text-primary"></i> إضافة أصل جديد</h3>
                    </div>
                    <div class="card-body">
                        {% with messages = get_flashed_messages() %}
                            {% if messages %}
                                {% for message in messages %}
                                    <div class="alert alert-success">{{ message }}</div>
                                {% endfor %}
                            {% endif %}
                        {% endwith %}
                        
                        <form method="POST">
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">رقم الأصل *</label>
                                    <input type="text" class="form-control" name="tag" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">اسم الأصل *</label>
                                    <input type="text" class="form-control" name="name" required>
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">الفئة *</label>
                                    <select class="form-control" name="category" required>
                                        <option value="">اختر الفئة</option>
                                        <option value="أجهزة الكمبيوتر">أجهزة الكمبيوتر</option>
                                        <option value="الطابعات">الطابعات</option>
                                        <option value="الشبكات">الشبكات</option>
                                        <option value="الخوادم">الخوادم</option>
                                        <option value="الهواتف">الهواتف</option>
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
                                    <label class="form-label">التكلفة (ريال)</label>
                                    <input type="number" step="0.01" class="form-control" name="cost">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">تاريخ الشراء</label>
                                    <input type="date" class="form-control" name="purchase_date">
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">انتهاء الضمان</label>
                                    <input type="date" class="form-control" name="warranty_end">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">الموقع</label>
                                    <input type="text" class="form-control" name="location">
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">مخصص لـ</label>
                                    <input type="text" class="form-control" name="assigned_to">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">الحالة</label>
                                    <select class="form-control" name="status">
                                        <option value="نشط">نشط</option>
                                        <option value="متوقف">متوقف</option>
                                        <option value="صيانة">صيانة</option>
                                    </select>
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">ملاحظات</label>
                                <textarea class="form-control" name="notes" rows="3"></textarea>
                            </div>
                            
                            <div class="d-flex justify-content-between">
                                <button type="submit" class="btn btn-primary">
                                    <i class="fas fa-save"></i> حفظ الأصل
                                </button>
                                <a href="/assets" class="btn btn-secondary">
                                    <i class="fas fa-arrow-right"></i> العودة للأصول
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

EMPLOYEES_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>إدارة الموظفين</title>
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
                        <a class="nav-link dropdown-toggle text-white" href="#" role="button" data-bs-toggle="dropdown">💼 الأصول</a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="/assets">📋 عرض الأصول</a></li>
                            <li><a class="dropdown-item" href="/add_asset">➕ إضافة أصل</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="/custody">📋 إدارة العهد</a></li>
                        </ul>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle text-white active" href="#" role="button" data-bs-toggle="dropdown">👥 الموظفين</a>
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
                    <li class="nav-item"><a class="nav-link text-white" href="/notifications">🔔 الإشعارات</a></li>
                    <li class="nav-item"><a class="nav-link text-white" href="/logout">🚪 خروج</a></li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="fas fa-users text-primary"></i> إدارة الموظفين</h2>
            <a href="/add_employee" class="btn btn-primary">
                <i class="fas fa-user-plus"></i> إضافة موظف جديد
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
                                <i class="fas fa-envelope me-1"></i>{{ employee[5] }}
                            </small>
                        </div>
                        
                        <div class="mb-2">
                            <small class="text-muted">
                                <i class="fas fa-phone me-1"></i>{{ employee[6] }}
                            </small>
                        </div>
                        
                        <div class="d-flex justify-content-between align-items-center mt-3">
                            <span class="badge bg-{{ 'success' if employee[8] == 'نشط' else 'warning' }}">
                                {{ employee[8] }}
                            </span>
                            <div>
                                <button class="btn btn-sm btn-outline-info">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-danger">
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

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
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
        body { background: #f8f9fa; }
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
                    <li class="nav-item"><a class="nav-link text-white" href="/notifications">🔔 الإشعارات</a></li>
                    <li class="nav-item"><a class="nav-link text-white" href="/logout">🚪 خروج</a></li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="fas fa-shopping-cart text-primary"></i> إدارة المشتريات</h2>
            <a href="/add_purchase" class="btn btn-primary">
                <i class="fas fa-plus"></i> إضافة مشترى جديد
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
                                <td><strong>{{ purchase[1] }}</strong></td>
                                <td>{{ purchase[2] }}</td>
                                <td>{{ purchase[4] }}</td>
                                <td><span class="badge bg-secondary">{{ purchase[6] }}</span></td>
                                <td>{{ purchase[7] }}</td>
                                <td>{{ "{:,.2f}".format(purchase[9]) }} {{ purchase[10] }}</td>
                                <td>
                                    <span class="badge bg-{{ 'success' if purchase[15] == 'مكتمل' else 'warning' if purchase[15] == 'قيد التوريد' else 'secondary' }}">
                                        {{ purchase[15] }}
                                    </span>
                                </td>
                                <td>{{ purchase[12] }}</td>
                                <td>
                                    <button class="btn btn-sm btn-outline-primary">
                                        <i class="fas fa-eye"></i>
                                    </button>
                                    <button class="btn btn-sm btn-outline-success">
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
</body>
</html>
'''

# تشغيل التطبيق
if __name__ == '__main__':
    print("=" * 70)
    print("🚀 نظام إدارة الأصول مع القوائم المحدثة")
    print("   Asset Management System with Updated Menus")
    print("=" * 70)
    
    print("✅ النظام جاهز!")
    print("🌐 الرابط: http://localhost:5000")
    print("👤 المستخدم: admin")
    print("🔑 كلمة المرور: admin123")
    print("📱 القوائم المنسدلة: تم تحديثها وتحسينها")
    print("🔧 للإيقاف: اضغط Ctrl+C")
    print("=" * 70)
    
    # تشغيل الخادم
    app = create_app()
    app.run(debug=False, host='0.0.0.0', port=5000)