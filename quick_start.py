#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تشغيل سريع لنظام إدارة الأصول التقنية
Quick Start for IT Asset Management System
"""

import os
import sys

def print_banner():
    """طباعة شعار النظام"""
    print("=" * 70)
    print("🚀 نظام إدارة الأصول التقنية")
    print("   IT Asset Management System")
    print("=" * 70)
    print("⏰ جاري التشغيل...")
    print("🌐 الخادم: http://localhost:5000")
    print("👤 المستخدم الافتراضي: admin")
    print("🔑 كلمة المرور الافتراضية: admin123")
    print("=" * 70)
    print()

def check_and_install_basic_requirements():
    """التحقق من المكتبات الأساسية وتثبيتها"""
    required_packages = [
        'flask',
        'flask_sqlalchemy', 
        'flask_login'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"⚠️  المكتبات المفقودة: {', '.join(missing_packages)}")
        print("🔧 جاري تثبيت المكتبات الأساسية...")
        
        try:
            import subprocess
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "Flask", "Flask-SQLAlchemy", "Flask-Login"
            ])
            print("✅ تم تثبيت المكتبات الأساسية")
        except:
            print("❌ فشل في تثبيت المكتبات")
            print("يرجى تثبيتها يدوياً: pip install Flask Flask-SQLAlchemy Flask-Login")
            return False
    
    return True

def create_minimal_app():
    """إنشاء تطبيق مبسط"""
    try:
        from flask import Flask, render_template_string, request, redirect, url_for, flash
        from flask_sqlalchemy import SQLAlchemy
        from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
        from werkzeug.security import generate_password_hash, check_password_hash
        from datetime import datetime
        
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///it_assets_simple.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        db = SQLAlchemy(app)
        login_manager = LoginManager()
        login_manager.init_app(app)
        login_manager.login_view = 'login'
        
        # نماذج مبسطة
        class User(UserMixin, db.Model):
            id = db.Column(db.Integer, primary_key=True)
            username = db.Column(db.String(80), unique=True, nullable=False)
            password_hash = db.Column(db.String(120), nullable=False)
            full_name = db.Column(db.String(100), nullable=False)
            role = db.Column(db.String(20), default='user')
        
        class Asset(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            asset_tag = db.Column(db.String(50), unique=True, nullable=False)
            name = db.Column(db.String(200), nullable=False)
            description = db.Column(db.Text)
            status = db.Column(db.String(20), default='active')
            created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))
        
        # الصفحات
        @app.route('/')
        def index():
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            
            assets = Asset.query.all()
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
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem 0; }
        .stats-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px; padding: 20px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="header text-center">
        <h1><i class="fas fa-laptop"></i> نظام إدارة الأصول التقنية</h1>
        <p>مرحباً {{ current_user.full_name }} | <a href="{{ url_for('logout') }}" class="text-white">تسجيل الخروج</a></p>
    </div>
    
    <div class="container mt-4">
        <div class="row">
            <div class="col-md-6">
                <div class="stats-card text-center">
                    <h3>{{ assets|length }}</h3>
                    <p>إجمالي الأصول</p>
                </div>
            </div>
            <div class="col-md-6">
                <div class="stats-card text-center">
                    <h3>{{ assets|selectattr('status', 'equalto', 'active')|list|length }}</h3>
                    <p>أصول نشطة</p>
                </div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header d-flex justify-content-between">
                <h5>قائمة الأصول</h5>
                <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addAssetModal">
                    <i class="fas fa-plus"></i> إضافة أصل
                </button>
            </div>
            <div class="card-body">
                {% if assets %}
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>رقم الأصل</th>
                            <th>الاسم</th>
                            <th>الوصف</th>
                            <th>الحالة</th>
                            <th>تاريخ الإضافة</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for asset in assets %}
                        <tr>
                            <td><strong>{{ asset.asset_tag }}</strong></td>
                            <td>{{ asset.name }}</td>
                            <td>{{ asset.description or 'لا يوجد وصف' }}</td>
                            <td>
                                <span class="badge bg-{{ 'success' if asset.status == 'active' else 'warning' }}">
                                    {{ 'نشط' if asset.status == 'active' else asset.status }}
                                </span>
                            </td>
                            <td>{{ asset.created_at.strftime('%Y-%m-%d') }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% else %}
                <div class="text-center py-4">
                    <i class="fas fa-inbox fa-3x text-muted mb-3"></i>
                    <p class="text-muted">لا توجد أصول مضافة بعد</p>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
    
    <!-- Modal إضافة أصل -->
    <div class="modal fade" id="addAssetModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">إضافة أصل جديد</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <form method="POST" action="{{ url_for('add_asset') }}">
                    <div class="modal-body">
                        <div class="mb-3">
                            <label class="form-label">رقم الأصل</label>
                            <input type="text" class="form-control" name="asset_tag" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">اسم الأصل</label>
                            <input type="text" class="form-control" name="name" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">الوصف</label>
                            <textarea class="form-control" name="description" rows="3"></textarea>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">الحالة</label>
                            <select class="form-select" name="status">
                                <option value="active">نشط</option>
                                <option value="maintenance">صيانة</option>
                                <option value="retired">متقاعد</option>
                            </select>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إلغاء</button>
                        <button type="submit" class="btn btn-primary">حفظ</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
            ''', assets=assets)
        
        @app.route('/login', methods=['GET', 'POST'])
        def login():
            if request.method == 'POST':
                username = request.form['username']
                password = request.form['password']
                user = User.query.filter_by(username=username).first()
                
                if user and check_password_hash(user.password_hash, password):
                    login_user(user)
                    return redirect(url_for('index'))
                else:
                    flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
            
            return render_template_string('''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تسجيل الدخول</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; }
        .login-card { background: white; border-radius: 15px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="login-card p-5">
                    <div class="text-center mb-4">
                        <h2>نظام إدارة الأصول التقنية</h2>
                        <p class="text-muted">يرجى تسجيل الدخول للمتابعة</p>
                    </div>
                    
                    {% with messages = get_flashed_messages(with_categories=true) %}
                        {% if messages %}
                            {% for category, message in messages %}
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
                    
                    <div class="mt-4 p-3 bg-light rounded">
                        <small>
                            <strong>بيانات تسجيل الدخول الافتراضية:</strong><br>
                            اسم المستخدم: <code>admin</code><br>
                            كلمة المرور: <code>admin123</code>
                        </small>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
            ''')
        
        @app.route('/logout')
        @login_required
        def logout():
            logout_user()
            return redirect(url_for('login'))
        
        @app.route('/add_asset', methods=['POST'])
        @login_required
        def add_asset():
            asset = Asset(
                asset_tag=request.form['asset_tag'],
                name=request.form['name'],
                description=request.form.get('description'),
                status=request.form.get('status', 'active')
            )
            
            db.session.add(asset)
            db.session.commit()
            
            flash('تم إضافة الأصل بنجاح', 'success')
            return redirect(url_for('index'))
        
        # إنشاء الجداول والبيانات الافتراضية
        with app.app_context():
            db.create_all()
            
            if not User.query.first():
                admin = User(
                    username='admin',
                    password_hash=generate_password_hash('admin123'),
                    full_name='مدير النظام',
                    role='admin'
                )
                db.session.add(admin)
                db.session.commit()
                print("✅ تم إنشاء المستخدم الافتراضي")
        
        return app
        
    except ImportError as e:
        print(f"❌ خطأ في استيراد المكتبات: {e}")
        return None
    except Exception as e:
        print(f"❌ خطأ في إنشاء التطبيق: {e}")
        return None

def main():
    """الدالة الرئيسية"""
    print_banner()
    
    # التحقق من المكتبات الأساسية
    if not check_and_install_basic_requirements():
        print("❌ لا يمكن تشغيل النظام بدون المكتبات الأساسية")
        return
    
    # إنشاء التطبيق
    app = create_minimal_app()
    if not app:
        print("❌ فشل في إنشاء التطبيق")
        return
    
    print("✅ النظام جاهز للتشغيل!")
    print("🔧 للإيقاف: اضغط Ctrl+C")
    print()
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n⏹️  تم إيقاف النظام بنجاح")
    except Exception as e:
        print(f"\n❌ خطأ في تشغيل النظام: {e}")

if __name__ == '__main__':
    main()