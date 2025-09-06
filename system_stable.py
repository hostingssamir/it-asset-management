#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
نظام إدارة الأصول الاحترافي - نسخة مستقرة
Professional Asset Management System - Stable Version
"""

from flask import Flask, render_template_string, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os

# إنشاء التطبيق
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///asset_management_stable.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# إنشاء قاعدة البيانات
db = SQLAlchemy(app)

# نماذج قاعدة البيانات
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    serial_number = db.Column(db.String(100), unique=True, nullable=False)
    purchase_date = db.Column(db.Date, nullable=False)
    purchase_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='نشط')
    location = db.Column(db.String(100))
    assigned_to = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    supplier = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    purchase_date = db.Column(db.Date, nullable=False)
    invoice_file = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='مكتمل')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Custody(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_name = db.Column(db.String(100), nullable=False)
    employee_id = db.Column(db.String(20), nullable=False)
    custody_type = db.Column(db.String(50), nullable=False)
    serial_number = db.Column(db.String(100), nullable=False)
    received_date = db.Column(db.Date, nullable=False)
    estimated_value = db.Column(db.Float)
    barcode = db.Column(db.String(50), unique=True, nullable=True)
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='نشط')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    invoice_date = db.Column(db.Date, nullable=False)
    supplier_name = db.Column(db.String(100), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    payment_status = db.Column(db.String(20), nullable=False)
    due_date = db.Column(db.Date)
    invoice_file = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# قالب تسجيل الدخول
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
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: 'Cairo', sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: center;
        }
        .login-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 25px;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .login-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            text-align: center;
            border-radius: 25px 25px 0 0;
        }
        .btn-login {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 15px;
            padding: 1rem 2rem;
            font-size: 1.2rem;
            font-weight: 600;
            color: white;
            transition: all 0.3s ease;
        }
        .btn-login:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
            color: white;
        }
        .form-control {
            border-radius: 15px;
            border: 2px solid #e9ecef;
            padding: 1rem 1.5rem;
            font-size: 1.1rem;
        }
        .form-control:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-lg-5 col-md-7">
                <div class="login-card">
                    <div class="login-header">
                        <div style="font-size: 4rem; margin-bottom: 1rem;">
                            <i class="fas fa-building"></i>
                        </div>
                        <h2 class="mb-0">نظام إدارة الأصول</h2>
                        <p class="mb-0 mt-2">مرحباً بك في النظام الاحترافي</p>
                    </div>
                    
                    <div class="card-body p-5">
                        {% with messages = get_flashed_messages() %}
                            {% if messages %}
                                {% for message in messages %}
                                    <div class="alert alert-danger">{{ message }}</div>
                                {% endfor %}
                            {% endif %}
                        {% endwith %}
                        
                        <form method="POST">
                            <div class="mb-3">
                                <input type="text" class="form-control" name="username" 
                                       placeholder="اسم المستخدم" required>
                            </div>
                            
                            <div class="mb-3">
                                <input type="password" class="form-control" name="password" 
                                       placeholder="كلمة المرور" required>
                            </div>
                            
                            <button type="submit" class="btn btn-login w-100 mb-3">
                                <i class="fas fa-sign-in-alt me-2"></i>
                                دخول النظام
                            </button>
                        </form>
                        
                        <div class="text-center text-muted">
                            <small>
                                <i class="fas fa-shield-alt me-1"></i>
                                نظام آمن ومحمي
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

# قالب الصفحة الرئيسية
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة التحكم - نظام إدارة الأصول</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Cairo', sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }
        .navbar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }
        .welcome-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 20px;
            padding: 3rem;
            margin-bottom: 3rem;
            box-shadow: 0 15px 35px rgba(102, 126, 234, 0.3);
        }
        .module-card {
            background: white;
            border-radius: 20px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            border: none;
            text-align: center;
        }
        .module-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
        }
        .module-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .btn-module {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 15px;
            padding: 0.8rem 2rem;
            color: white;
            font-weight: 600;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }
        .btn-module:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
            color: white;
        }
        .stats-card {
            background: white;
            border-radius: 15px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
            transition: all 0.3s ease;
        }
        .stats-card:hover {
            transform: translateY(-5px);
        }
        .stats-number {
            font-size: 2.5rem;
            font-weight: 700;
            color: #667eea;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/dashboard">
                <i class="fas fa-building me-2"></i>
                نظام إدارة الأصول
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="/logout">
                    <i class="fas fa-sign-out-alt me-1"></i>
                    خروج
                </a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        <div class="welcome-card">
            <div class="row align-items-center">
                <div class="col-md-8">
                    <h1 class="mb-3">
                        <i class="fas fa-hand-wave me-2"></i>
                        مرحباً بك، {{ username }}
                    </h1>
                    <p class="lead mb-0">
                        مرحباً بك في نظام إدارة الأصول الاحترافي. يمكنك من هنا إدارة جميع أصول الشركة بكفاءة عالية.
                    </p>
                </div>
                <div class="col-md-4 text-center">
                    <i class="fas fa-chart-line" style="font-size: 5rem; opacity: 0.3;"></i>
                </div>
            </div>
        </div>
        
        <!-- إحصائيات سريعة -->
        <div class="row mb-4">
            <div class="col-md-3 mb-3">
                <div class="stats-card">
                    <i class="fas fa-laptop text-primary" style="font-size: 2rem;"></i>
                    <div class="stats-number">{{ total_assets }}</div>
                    <div class="stats-label">إجمالي الأصول</div>
                </div>
            </div>
            <div class="col-md-3 mb-3">
                <div class="stats-card">
                    <i class="fas fa-shopping-cart text-success" style="font-size: 2rem;"></i>
                    <div class="stats-number">{{ total_purchases }}</div>
                    <div class="stats-label">المشتريات</div>
                </div>
            </div>
            <div class="col-md-3 mb-3">
                <div class="stats-card">
                    <i class="fas fa-handshake text-warning" style="font-size: 2rem;"></i>
                    <div class="stats-number">{{ total_custodies }}</div>
                    <div class="stats-label">العهد</div>
                </div>
            </div>
            <div class="col-md-3 mb-3">
                <div class="stats-card">
                    <i class="fas fa-file-invoice text-info" style="font-size: 2rem;"></i>
                    <div class="stats-number">{{ total_invoices }}</div>
                    <div class="stats-label">الفواتير</div>
                </div>
            </div>
        </div>
        
        <!-- وحدات النظام -->
        <div class="row">
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="module-card">
                    <div class="module-icon">
                        <i class="fas fa-laptop"></i>
                    </div>
                    <h5>إدارة الأصول</h5>
                    <p>إدارة شاملة لجميع أصول الشركة مع تتبع الحالة والموقع</p>
                    <a href="/assets" class="btn-module">
                        <i class="fas fa-arrow-left me-2"></i>دخول
                    </a>
                </div>
            </div>
            
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="module-card">
                    <div class="module-icon">
                        <i class="fas fa-shopping-cart"></i>
                    </div>
                    <h5>إدارة المشتريات</h5>
                    <p>تتبع المشتريات والموردين مع إرفاق الفواتير</p>
                    <a href="/purchases" class="btn-module">
                        <i class="fas fa-arrow-left me-2"></i>دخول
                    </a>
                </div>
            </div>
            
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="module-card">
                    <div class="module-icon">
                        <i class="fas fa-handshake"></i>
                    </div>
                    <h5>إدارة العهد</h5>
                    <p>إدارة عهد الموظفين مع طباعة الباركود</p>
                    <a href="/custody" class="btn-module">
                        <i class="fas fa-arrow-left me-2"></i>دخول
                    </a>
                </div>
            </div>
            
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="module-card">
                    <div class="module-icon">
                        <i class="fas fa-file-invoice"></i>
                    </div>
                    <h5>إدارة الفواتير</h5>
                    <p>إدارة الفواتير والمدفوعات مع إرفاق الملفات</p>
                    <a href="/invoices" class="btn-module">
                        <i class="fas fa-arrow-left me-2"></i>دخول
                    </a>
                </div>
            </div>
            
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="module-card">
                    <div class="module-icon">
                        <i class="fas fa-chart-bar"></i>
                    </div>
                    <h5>التقارير</h5>
                    <p>تقارير شاملة وإحصائيات تفصيلية</p>
                    <a href="/reports" class="btn-module">
                        <i class="fas fa-arrow-left me-2"></i>دخول
                    </a>
                </div>
            </div>
            
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="module-card">
                    <div class="module-icon">
                        <i class="fas fa-cog"></i>
                    </div>
                    <h5>الإعدادات</h5>
                    <p>إعدادات النظام والمستخدمين</p>
                    <a href="/settings" class="btn-module">
                        <i class="fas fa-arrow-left me-2"></i>دخول
                    </a>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

# صفحة تسجيل الدخول
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('تم تسجيل الدخول بنجاح!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
    
    return render_template_string(LOGIN_TEMPLATE)

# الصفحة الرئيسية
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # حساب الإحصائيات
    total_assets = Asset.query.count()
    total_purchases = Purchase.query.count()
    total_custodies = Custody.query.count()
    total_invoices = Invoice.query.count()
    
    return render_template_string(DASHBOARD_TEMPLATE, 
        username=session.get('username', 'المستخدم'),
        total_assets=total_assets,
        total_purchases=total_purchases,
        total_custodies=total_custodies,
        total_invoices=total_invoices
    )

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# صفحات بسيطة للوحدات الأخرى
@app.route('/assets')
def assets():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return "<h1>صفحة إدارة الأصول</h1><a href='/dashboard'>العودة للرئيسية</a>"

@app.route('/purchases')
def purchases():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return "<h1>صفحة إدارة المشتريات</h1><a href='/dashboard'>العودة للرئيسية</a>"

@app.route('/custody')
def custody():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return "<h1>صفحة إدارة العهد</h1><a href='/dashboard'>العودة للرئيسية</a>"

@app.route('/invoices')
def invoices():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return "<h1>صفحة إدارة الفواتير</h1><a href='/dashboard'>العودة للرئيسية</a>"

@app.route('/reports')
def reports():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return "<h1>صفحة التقارير</h1><a href='/dashboard'>العودة للرئيسية</a>"

@app.route('/settings')
def settings():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return "<h1>صفحة الإعدادات</h1><a href='/dashboard'>العودة للرئيسية</a>"

# تهيئة قاعدة البيانات
def init_db():
    with app.app_context():
        db.create_all()
        
        # إضافة مستخدم افتراضي
        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin', email='admin@company.com')
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()

if __name__ == '__main__':
    init_db()
    print("=" * 70)
    print("🚀 نظام إدارة الأصول الاحترافي - النسخة المستقرة")
    print("   Professional Asset Management System - Stable Version")
    print("=" * 70)
    print("✅ النظام جاهز!")
    print("🌐 الرابط: http://localhost:5001")
    print("👤 المستخدم: admin")
    print("🔑 كلمة المرور: admin123")
    print("🎨 التصميم: احترافي ومستقر")
    print("📱 متجاوب: يعمل على جميع الأجهزة")
    print("🔧 للإيقاف: اضغط Ctrl+C")
    print("=" * 70)
    app.run(host='0.0.0.0', port=5001, debug=False)