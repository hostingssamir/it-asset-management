#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
وحدة الإدارة لنظام إدارة الأصول التقنية
Admin Module for IT Asset Management System
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from functools import wraps
from models import db, User, Category, Location, Supplier, Employee
from werkzeug.security import generate_password_hash
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """تحقق من صلاحيات المدير"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# إدارة المستخدمين
@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """صفحة إدارة المستخدمين"""
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    """إضافة مستخدم جديد"""
    if request.method == 'POST':
        # التحقق من عدم تكرار اسم المستخدم والبريد الإلكتروني
        existing_user = User.query.filter(
            (User.username == request.form['username']) | 
            (User.email == request.form['email'])
        ).first()
        
        if existing_user:
            flash('اسم المستخدم أو البريد الإلكتروني موجود مسبقاً', 'error')
            return render_template('admin/add_user.html')
        
        user = User(
            username=request.form['username'],
            email=request.form['email'],
            password_hash=generate_password_hash(request.form['password']),
            full_name=request.form['full_name'],
            role=request.form.get('role', 'user'),
            is_active=True
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('تم إضافة المستخدم بنجاح', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/add_user.html')

@admin_bp.route('/users/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    """تعديل مستخدم"""
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        user.full_name = request.form['full_name']
        user.role = request.form.get('role', 'user')
        user.is_active = 'is_active' in request.form
        
        # تحديث كلمة المرور إذا تم إدخالها
        if request.form.get('password'):
            user.password_hash = generate_password_hash(request.form['password'])
        
        db.session.commit()
        flash('تم تحديث المستخدم بنجاح', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/edit_user.html', user=user)

@admin_bp.route('/users/<int:id>/delete', methods=['DELETE'])
@login_required
@admin_required
def delete_user(id):
    """حذف مستخدم"""
    if id == current_user.id:
        return jsonify({'success': False, 'message': 'لا يمكنك حذف حسابك الخاص'})
    
    user = User.query.get_or_404(id)
    
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'success': True, 'message': 'تم حذف المستخدم بنجاح'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'حدث خطأ أثناء الحذف'})

@admin_bp.route('/users/<int:id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(id):
    """تغيير حالة المستخدم"""
    user = User.query.get_or_404(id)
    
    # منع تعطيل المستخدم الحالي
    if user.id == current_user.id:
        return jsonify({'success': False, 'message': 'لا يمكن تعطيل حسابك الخاص'})
    
    try:
        user.is_active = not user.is_active
        db.session.commit()
        status = 'تم تفعيل' if user.is_active else 'تم تعطيل'
        return jsonify({'success': True, 'message': f'{status} المستخدم بنجاح'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'حدث خطأ أثناء تغيير الحالة'})

# إدارة الفئات
@admin_bp.route('/categories')
@login_required
@admin_required
def categories():
    """صفحة إدارة الفئات"""
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@admin_bp.route('/categories/add', methods=['POST'])
@login_required
@admin_required
def add_category():
    """إضافة فئة جديدة"""
    category = Category(
        name=request.form['name'],
        description=request.form.get('description')
    )
    
    db.session.add(category)
    db.session.commit()
    
    flash('تم إضافة الفئة بنجاح', 'success')
    return redirect(url_for('admin.categories'))

@admin_bp.route('/categories/<int:id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_category(id):
    """تعديل فئة"""
    category = Category.query.get_or_404(id)
    category.name = request.form['name']
    category.description = request.form.get('description')
    
    db.session.commit()
    flash('تم تحديث الفئة بنجاح', 'success')
    return redirect(url_for('admin.categories'))

@admin_bp.route('/categories/<int:id>/delete', methods=['DELETE'])
@login_required
@admin_required
def delete_category(id):
    """حذف فئة"""
    category = Category.query.get_or_404(id)
    
    # التحقق من وجود أصول مرتبطة بهذه الفئة
    if category.assets:
        return jsonify({'success': False, 'message': 'لا يمكن حذف الفئة لوجود أصول مرتبطة بها'})
    
    try:
        db.session.delete(category)
        db.session.commit()
        return jsonify({'success': True, 'message': 'تم حذف الفئة بنجاح'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'حدث خطأ أثناء الحذف'})

# إدارة المواقع
@admin_bp.route('/locations')
@login_required
@admin_required
def locations():
    """صفحة إدارة المواقع"""
    locations = Location.query.all()
    return render_template('admin/locations.html', locations=locations)

@admin_bp.route('/locations/add', methods=['POST'])
@login_required
@admin_required
def add_location():
    """إضافة موقع جديد"""
    location = Location(
        name=request.form['name'],
        building=request.form.get('building'),
        floor=request.form.get('floor'),
        room=request.form.get('room'),
        description=request.form.get('description')
    )
    
    db.session.add(location)
    db.session.commit()
    
    flash('تم إضافة الموقع بنجاح', 'success')
    return redirect(url_for('admin.locations'))

@admin_bp.route('/locations/<int:id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_location(id):
    """تعديل موقع"""
    location = Location.query.get_or_404(id)
    location.name = request.form['name']
    location.building = request.form.get('building')
    location.floor = request.form.get('floor')
    location.room = request.form.get('room')
    location.description = request.form.get('description')
    
    db.session.commit()
    flash('تم تحديث الموقع بنجاح', 'success')
    return redirect(url_for('admin.locations'))

@admin_bp.route('/locations/<int:id>/delete', methods=['DELETE'])
@login_required
@admin_required
def delete_location(id):
    """حذف موقع"""
    location = Location.query.get_or_404(id)
    
    # التحقق من وجود أصول مرتبطة بهذا الموقع
    if location.assets:
        return jsonify({'success': False, 'message': 'لا يمكن حذف الموقع لوجود أصول مرتبطة به'})
    
    try:
        db.session.delete(location)
        db.session.commit()
        return jsonify({'success': True, 'message': 'تم حذف الموقع بنجاح'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'حدث خطأ أثناء الحذف'})

# إدارة الموردين
@admin_bp.route('/suppliers')
@login_required
@admin_required
def suppliers():
    """صفحة إدارة الموردين"""
    suppliers = Supplier.query.all()
    return render_template('admin/suppliers.html', suppliers=suppliers)

@admin_bp.route('/suppliers/add', methods=['POST'])
@login_required
@admin_required
def add_supplier():
    """إضافة مورد جديد"""
    supplier = Supplier(
        name=request.form['name'],
        contact_person=request.form.get('contact_person'),
        phone=request.form.get('phone'),
        email=request.form.get('email'),
        address=request.form.get('address')
    )
    
    db.session.add(supplier)
    db.session.commit()
    
    flash('تم إضافة المورد بنجاح', 'success')
    return redirect(url_for('admin.suppliers'))

@admin_bp.route('/suppliers/<int:id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_supplier(id):
    """تعديل مورد"""
    supplier = Supplier.query.get_or_404(id)
    supplier.name = request.form['name']
    supplier.contact_person = request.form.get('contact_person')
    supplier.phone = request.form.get('phone')
    supplier.email = request.form.get('email')
    supplier.address = request.form.get('address')
    
    db.session.commit()
    flash('تم تحديث المورد بنجاح', 'success')
    return redirect(url_for('admin.suppliers'))

@admin_bp.route('/suppliers/<int:id>/delete', methods=['DELETE'])
@login_required
@admin_required
def delete_supplier(id):
    """حذف مورد"""
    supplier = Supplier.query.get_or_404(id)
    
    # التحقق من وجود أصول مرتبطة بهذا المورد
    if supplier.assets:
        return jsonify({'success': False, 'message': 'لا يمكن حذف المورد لوجود أصول مرتبطة به'})
    
    try:
        db.session.delete(supplier)
        db.session.commit()
        return jsonify({'success': True, 'message': 'تم حذف المورد بنجاح'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'حدث خطأ أثناء الحذف'})

# إدارة الموظفين
@admin_bp.route('/employees')
@login_required
@admin_required
def employees():
    """صفحة إدارة الموظفين"""
    employees = Employee.query.all()
    return render_template('admin/employees.html', employees=employees)

@admin_bp.route('/employees/add', methods=['POST'])
@login_required
@admin_required
def add_employee():
    """إضافة موظف جديد"""
    # التحقق من عدم تكرار رقم الموظف
    existing_employee = Employee.query.filter_by(employee_id=request.form['employee_id']).first()
    if existing_employee:
        flash('رقم الموظف موجود مسبقاً', 'error')
        return redirect(url_for('admin.employees'))
    
    employee = Employee(
        employee_id=request.form['employee_id'],
        full_name=request.form['full_name'],
        department=request.form.get('department'),
        position=request.form.get('position'),
        email=request.form.get('email'),
        phone=request.form.get('phone')
    )
    
    db.session.add(employee)
    db.session.commit()
    
    flash('تم إضافة الموظف بنجاح', 'success')
    return redirect(url_for('admin.employees'))

@admin_bp.route('/employees/<int:id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_employee(id):
    """تعديل موظف"""
    employee = Employee.query.get_or_404(id)
    employee.employee_id = request.form['employee_id']
    employee.full_name = request.form['full_name']
    employee.department = request.form.get('department')
    employee.position = request.form.get('position')
    employee.email = request.form.get('email')
    employee.phone = request.form.get('phone')
    
    db.session.commit()
    flash('تم تحديث الموظف بنجاح', 'success')
    return redirect(url_for('admin.employees'))

@admin_bp.route('/employees/<int:id>/delete', methods=['DELETE'])
@login_required
@admin_required
def delete_employee(id):
    """حذف موظف"""
    employee = Employee.query.get_or_404(id)
    
    # التحقق من وجود أصول مخصصة لهذا الموظف
    if employee.assignments:
        return jsonify({'success': False, 'message': 'لا يمكن حذف الموظف لوجود أصول مخصصة له'})
    
    try:
        db.session.delete(employee)
        db.session.commit()
        return jsonify({'success': True, 'message': 'تم حذف الموظف بنجاح'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'حدث خطأ أثناء الحذف'})

# النسخ الاحتياطي
@admin_bp.route('/backup')
@login_required
@admin_required
def backup():
    """صفحة النسخ الاحتياطي"""
    return render_template('admin/backup.html')

@admin_bp.route('/backup/create', methods=['POST'])
@login_required
@admin_required
def create_backup():
    """إنشاء نسخة احتياطية"""
    try:
        from utils import backup_database
        import os
        
        # البحث عن ملف قاعدة البيانات
        possible_paths = [
            'instance/it_assets.db',
            'instance/database.db',
            'it_assets.db',
            'database.db'
        ]
        
        db_path = None
        for path in possible_paths:
            if os.path.exists(path):
                db_path = path
                break
        
        # إذا لم نجد الملف، ابحث في مجلد instance
        if not db_path and os.path.exists('instance'):
            for filename in os.listdir('instance'):
                if filename.endswith('.db'):
                    db_path = os.path.join('instance', filename)
                    break
        
        if not db_path:
            flash('لم يتم العثور على ملف قاعدة البيانات', 'error')
            return redirect(url_for('admin.backup'))
        
        backup_path = backup_database(db_path)
        
        if backup_path:
            flash(f'تم إنشاء النسخة الاحتياطية بنجاح: {os.path.basename(backup_path)}', 'success')
        else:
            flash('حدث خطأ أثناء إنشاء النسخة الاحتياطية', 'error')
    except Exception as e:
        flash(f'حدث خطأ: {str(e)}', 'error')
    
    return redirect(url_for('admin.backup'))

@admin_bp.route('/backup/list')
@login_required
@admin_required
def list_backups():
    """قائمة النسخ الاحتياطية"""
    try:
        import os
        from datetime import datetime
        
        backup_dir = 'backups'
        backups = []
        
        if os.path.exists(backup_dir):
            for filename in os.listdir(backup_dir):
                if filename.startswith('it_assets_backup_') and filename.endswith('.db'):
                    file_path = os.path.join(backup_dir, filename)
                    stat = os.stat(file_path)
                    
                    backups.append({
                        'filename': filename,
                        'size': stat.st_size,
                        'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat()
                    })
            
            # ترتيب حسب تاريخ الإنشاء (الأحدث أولاً)
            backups.sort(key=lambda x: x['created_at'], reverse=True)
        
        return jsonify({'success': True, 'backups': backups})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@admin_bp.route('/backup/download/<filename>')
@login_required
@admin_required
def download_backup(filename):
    """تحميل نسخة احتياطية"""
    try:
        import os
        from flask import send_file
        
        backup_dir = 'backups'
        file_path = os.path.join(backup_dir, filename)
        
        if not os.path.exists(file_path):
            flash('الملف غير موجود', 'error')
            return redirect(url_for('admin.backup'))
        
        # التحقق من أن الملف نسخة احتياطية صحيحة
        if not filename.startswith('it_assets_backup_') or not filename.endswith('.db'):
            flash('ملف غير صحيح', 'error')
            return redirect(url_for('admin.backup'))
        
        return send_file(file_path, as_attachment=True, download_name=filename)
    except Exception as e:
        flash(f'حدث خطأ: {str(e)}', 'error')
        return redirect(url_for('admin.backup'))

@admin_bp.route('/backup/delete/<filename>', methods=['DELETE'])
@login_required
@admin_required
def delete_backup(filename):
    """حذف نسخة احتياطية"""
    try:
        import os
        
        backup_dir = 'backups'
        file_path = os.path.join(backup_dir, filename)
        
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'message': 'الملف غير موجود'})
        
        # التحقق من أن الملف نسخة احتياطية صحيحة
        if not filename.startswith('it_assets_backup_') or not filename.endswith('.db'):
            return jsonify({'success': False, 'message': 'ملف غير صحيح'})
        
        os.remove(file_path)
        return jsonify({'success': True, 'message': 'تم حذف النسخة الاحتياطية بنجاح'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@admin_bp.route('/backup/clean', methods=['POST'])
@login_required
@admin_required
def clean_backups():
    """حذف النسخ الاحتياطية القديمة"""
    try:
        from utils import clean_old_backups
        import os
        
        backup_dir = 'backups'
        deleted_count = 0
        
        if os.path.exists(backup_dir):
            # عد الملفات قبل الحذف
            files_before = len([f for f in os.listdir(backup_dir) 
                              if f.startswith('it_assets_backup_') and f.endswith('.db')])
            
            clean_old_backups(backup_dir, keep_days=30)
            
            # عد الملفات بعد الحذف
            files_after = len([f for f in os.listdir(backup_dir) 
                             if f.startswith('it_assets_backup_') and f.endswith('.db')])
            
            deleted_count = files_before - files_after
        
        return jsonify({'success': True, 'deleted_count': deleted_count})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@admin_bp.route('/backup/restore/<filename>', methods=['POST'])
@login_required
@admin_required
def restore_backup(filename):
    """استعادة نسخة احتياطية"""
    try:
        import os
        import shutil
        from datetime import datetime
        
        backup_dir = 'backups'
        backup_file = os.path.join(backup_dir, filename)
        
        # التحقق من وجود ملف النسخة الاحتياطية
        if not os.path.exists(backup_file):
            return jsonify({'success': False, 'message': 'ملف النسخة الاحتياطية غير موجود'})
        
        # التحقق من صحة اسم الملف
        if not filename.startswith('it_assets_backup_') or not filename.endswith('.db'):
            return jsonify({'success': False, 'message': 'ملف غير صحيح'})
        
        # البحث عن ملف قاعدة البيانات الحالي
        possible_paths = [
            'instance/it_assets.db',
            'instance/database.db',
            'it_assets.db',
            'database.db'
        ]
        
        current_db_path = None
        for path in possible_paths:
            if os.path.exists(path):
                current_db_path = path
                break
        
        # إذا لم نجد الملف، ابحث في مجلد instance
        if not current_db_path and os.path.exists('instance'):
            for db_filename in os.listdir('instance'):
                if db_filename.endswith('.db'):
                    current_db_path = os.path.join('instance', db_filename)
                    break
        
        if not current_db_path:
            return jsonify({'success': False, 'message': 'لم يتم العثور على ملف قاعدة البيانات الحالي'})
        
        # إنشاء نسخة احتياطية من قاعدة البيانات الحالية قبل الاستعادة
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safety_backup = f"backups/safety_backup_before_restore_{timestamp}.db"
        
        # التأكد من وجود مجلد النسخ الاحتياطية
        if not os.path.exists('backups'):
            os.makedirs('backups')
        
        shutil.copy2(current_db_path, safety_backup)
        
        # استعادة النسخة الاحتياطية
        shutil.copy2(backup_file, current_db_path)
        
        return jsonify({
            'success': True, 
            'message': f'تم استعادة النسخة الاحتياطية بنجاح. تم حفظ نسخة أمان في: {os.path.basename(safety_backup)}'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'حدث خطأ أثناء الاستعادة: {str(e)}'})

@admin_bp.route('/backup/info')
@login_required
@admin_required
def backup_info():
    """معلومات النسخ الاحتياطي"""
    try:
        import os
        from datetime import datetime
        
        # البحث عن ملف قاعدة البيانات
        possible_paths = [
            'instance/it_assets.db',
            'instance/database.db', 
            'it_assets.db',
            'database.db'
        ]
        
        current_db_path = None
        current_db_size = 0
        
        for path in possible_paths:
            if os.path.exists(path):
                current_db_path = path
                current_db_size = os.path.getsize(path)
                break
        
        # إذا لم نجد الملف، ابحث في مجلد instance
        if not current_db_path and os.path.exists('instance'):
            for filename in os.listdir('instance'):
                if filename.endswith('.db'):
                    current_db_path = os.path.join('instance', filename)
                    current_db_size = os.path.getsize(current_db_path)
                    break
        
        # معلومات مجلد النسخ الاحتياطية
        backup_dir = 'backups'
        backup_count = 0
        total_backup_size = 0
        
        if os.path.exists(backup_dir):
            for filename in os.listdir(backup_dir):
                if filename.endswith('.db'):
                    backup_count += 1
                    total_backup_size += os.path.getsize(os.path.join(backup_dir, filename))
        
        return jsonify({
            'success': True,
            'current_db_path': current_db_path,
            'current_db_size': current_db_size,
            'backup_count': backup_count,
            'total_backup_size': total_backup_size,
            'backup_dir_exists': os.path.exists(backup_dir)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# إعدادات النظام
@admin_bp.route('/settings')
@login_required
@admin_required
def settings():
    """صفحة إعدادات النظام"""
    return render_template('admin/settings.html')

# إحصائيات النظام
@admin_bp.route('/stats')
@login_required
@admin_required
def stats():
    """إحصائيات النظام"""
    from app import Asset, MaintenanceRecord, AssetAssignment
    
    stats_data = {
        'total_users': User.query.count(),
        'total_assets': Asset.query.count(),
        'total_categories': Category.query.count(),
        'total_locations': Location.query.count(),
        'total_suppliers': Supplier.query.count(),
        'total_employees': Employee.query.count(),
        'total_maintenance': MaintenanceRecord.query.count(),
        'total_assignments': AssetAssignment.query.count(),
        'active_assets': Asset.query.filter_by(status='active').count(),
        'maintenance_assets': Asset.query.filter_by(status='maintenance').count(),
        'recent_assets': Asset.query.order_by(Asset.created_at.desc()).limit(5).all(),
        'recent_maintenance': MaintenanceRecord.query.order_by(MaintenanceRecord.created_at.desc()).limit(5).all()
    }
    
    return render_template('admin/stats.html', **stats_data)