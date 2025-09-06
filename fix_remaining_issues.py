#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
إصلاح المشاكل المتبقية في النظام
Fix remaining issues in the system
"""

# إضافة الكود المفقود لإصلاح المشاكل المتبقية

# 1. إصلاح مشكلة العهد
CUSTODY_FIX = '''
@app.route('/custody')
def custody():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    custodies = Custody.query.all()
    content = \'\'\'
    <div class="table-responsive">
        <table class="table table-hover">
            <thead>
                <tr>
                    <th>اسم الموظف</th>
                    <th>رقم الموظف</th>
                    <th>نوع العهدة</th>
                    <th>الرقم التسلسلي</th>
                    <th>تاريخ الاستلام</th>
                    <th>القيمة المقدرة</th>
                    <th>الحالة</th>
                    <th>الإجراءات</th>
                </tr>
            </thead>
            <tbody>
    \'\'\'
    
    for custody in custodies:
        content += f\'\'\'
                <tr>
                    <td>{custody.employee_name}</td>
                    <td>{custody.employee_id}</td>
                    <td>{custody.custody_type}</td>
                    <td>{custody.serial_number}</td>
                    <td>{custody.received_date.strftime('%Y-%m-%d') if custody.received_date else ''}</td>
                    <td>{"{:,.0f}".format(custody.estimated_value) if custody.estimated_value else '-'} ريال</td>
                    <td>
                        <span class="badge bg-{'success' if custody.status == 'نشط' else 'warning'}">
                            {custody.status}
                        </span>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary me-1">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
        \'\'\'
    
    if not custodies:
        content += '<tr><td colspan="8" class="text-center text-muted">لا توجد عهد مسجلة</td></tr>'
    
    content += \'\'\'
            </tbody>
        </table>
    </div>
    \'\'\'
    
    return render_template_string(create_page_template(
        "إدارة العهد", 
        "fa-handshake", 
        content, 
        "إضافة عهدة جديدة", 
        "/add_custody"
    ))
'''

# 2. إصلاح مشكلة الإدارات
DEPARTMENTS_FIX = '''
@app.route('/departments')
def departments():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    departments = Department.query.all()
    content = \'\'\'
    <div class="table-responsive">
        <table class="table table-hover">
            <thead>
                <tr>
                    <th>اسم الإدارة</th>
                    <th>رمز الإدارة</th>
                    <th>مدير الإدارة</th>
                    <th>الموقع</th>
                    <th>الحالة</th>
                    <th>الإجراءات</th>
                </tr>
            </thead>
            <tbody>
    \'\'\'
    
    for department in departments:
        content += f\'\'\'
                <tr>
                    <td>{department.department_name}</td>
                    <td>{department.department_code}</td>
                    <td>{department.manager_name or '-'}</td>
                    <td>{department.location or '-'}</td>
                    <td>
                        <span class="badge bg-{'success' if department.status == 'نشط' else 'warning'}">
                            {department.status}
                        </span>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary me-1">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
        \'\'\'
    
    if not departments:
        content += '<tr><td colspan="6" class="text-center text-muted">لا توجد إدارات مسجلة</td></tr>'
    
    content += \'\'\'
            </tbody>
        </table>
    </div>
    \'\'\'
    
    return render_template_string(create_page_template(
        "الإدارات", 
        "fa-building", 
        content, 
        "إضافة إدارة جديدة", 
        "/add_department"
    ))
'''

# 3. إصلاح مشكلة الفواتير
INVOICES_FIX = '''
@app.route('/invoices')
def invoices():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    invoices = Invoice.query.all()
    content = \'\'\'
    <div class="table-responsive">
        <table class="table table-hover">
            <thead>
                <tr>
                    <th>رقم الفاتورة</th>
                    <th>تاريخ الفاتورة</th>
                    <th>اسم المورد</th>
                    <th>المبلغ الإجمالي</th>
                    <th>حالة الدفع</th>
                    <th>تاريخ الاستحقاق</th>
                    <th>الإجراءات</th>
                </tr>
            </thead>
            <tbody>
    \'\'\'
    
    for invoice in invoices:
        content += f\'\'\'
                <tr>
                    <td>{invoice.invoice_number}</td>
                    <td>{invoice.invoice_date.strftime('%Y-%m-%d') if invoice.invoice_date else ''}</td>
                    <td>{invoice.supplier_name}</td>
                    <td>{"{:,.0f}".format(invoice.total_amount)} ريال</td>
                    <td>
                        <span class="badge bg-{'success' if invoice.payment_status == 'مدفوع' else 'warning' if invoice.payment_status == 'مدفوع جزئياً' else 'danger'}">
                            {invoice.payment_status}
                        </span>
                    </td>
                    <td>{invoice.due_date.strftime('%Y-%m-%d') if invoice.due_date else '-'}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary me-1">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
        \'\'\'
    
    if not invoices:
        content += '<tr><td colspan="7" class="text-center text-muted">لا توجد فواتير مسجلة</td></tr>'
    
    content += \'\'\'
            </tbody>
        </table>
    </div>
    \'\'\'
    
    return render_template_string(create_page_template(
        "إدارة الفواتير", 
        "fa-file-invoice", 
        content, 
        "إنشاء فاتورة جديدة", 
        "/create_invoice"
    ))
'''

# 4. إصلاح مشكلة التراخيص
LICENSES_FIX = '''
@app.route('/licenses')
def licenses():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    licenses = License.query.all()
    content = \'\'\'
    <div class="table-responsive">
        <table class="table table-hover">
            <thead>
                <tr>
                    <th>اسم البرنامج</th>
                    <th>نوع الترخيص</th>
                    <th>عدد المستخدمين</th>
                    <th>تاريخ الشراء</th>
                    <th>تاريخ انتهاء الصلاحية</th>
                    <th>التكلفة</th>
                    <th>الحالة</th>
                    <th>الإجراءات</th>
                </tr>
            </thead>
            <tbody>
    \'\'\'
    
    for license in licenses:
        content += f\'\'\'
                <tr>
                    <td>{license.software_name}</td>
                    <td>{license.license_type}</td>
                    <td>{license.user_count}</td>
                    <td>{license.purchase_date.strftime('%Y-%m-%d') if license.purchase_date else ''}</td>
                    <td>{license.expiry_date.strftime('%Y-%m-%d') if license.expiry_date else '-'}</td>
                    <td>{"{:,.0f}".format(license.cost) if license.cost else '-'} ريال</td>
                    <td>
                        <span class="badge bg-{'success' if license.status == 'نشط' else 'warning'}">
                            {license.status}
                        </span>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary me-1">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
        \'\'\'
    
    if not licenses:
        content += '<tr><td colspan="8" class="text-center text-muted">لا توجد تراخيص مسجلة</td></tr>'
    
    content += \'\'\'
            </tbody>
        </table>
    </div>
    \'\'\'
    
    return render_template_string(create_page_template(
        "إدارة التراخيص", 
        "fa-key", 
        content, 
        "إضافة ترخيص جديد", 
        "/add_license"
    ))
'''

# 5. إصلاح مشكلة الدعم الفني
SUPPORT_FIX = '''
@app.route('/support')
def support():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    tickets = SupportTicket.query.all()
    content = \'\'\'
    <div class="table-responsive">
        <table class="table table-hover">
            <thead>
                <tr>
                    <th>رقم التذكرة</th>
                    <th>اسم مقدم الطلب</th>
                    <th>نوع المشكلة</th>
                    <th>الأولوية</th>
                    <th>العنوان</th>
                    <th>الحالة</th>
                    <th>تاريخ الإنشاء</th>
                    <th>الإجراءات</th>
                </tr>
            </thead>
            <tbody>
    \'\'\'
    
    for ticket in tickets:
        content += f\'\'\'
                <tr>
                    <td>{ticket.ticket_number}</td>
                    <td>{ticket.requester_name}</td>
                    <td>{ticket.issue_type}</td>
                    <td>
                        <span class="badge bg-{'danger' if ticket.priority == 'عالية' else 'warning' if ticket.priority == 'متوسطة' else 'info'}">
                            {ticket.priority}
                        </span>
                    </td>
                    <td>{ticket.title}</td>
                    <td>
                        <span class="badge bg-{'success' if ticket.status == 'مغلق' else 'primary' if ticket.status == 'قيد المعالجة' else 'warning'}">
                            {ticket.status}
                        </span>
                    </td>
                    <td>{ticket.created_at.strftime('%Y-%m-%d %H:%M') if ticket.created_at else ''}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary me-1">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-success">
                            <i class="fas fa-check"></i>
                        </button>
                    </td>
                </tr>
        \'\'\'
    
    if not tickets:
        content += '<tr><td colspan="8" class="text-center text-muted">لا توجد تذاكر دعم فني</td></tr>'
    
    content += \'\'\'
            </tbody>
        </table>
    </div>
    \'\'\'
    
    return render_template_string(create_page_template(
        "الدعم الفني", 
        "fa-headset", 
        content, 
        "إنشاء تذكرة جديدة", 
        "/create_ticket"
    ))
'''

print("تم إنشاء ملف إصلاح المشاكل المتبقية")
print("يحتوي على الكود المطلوب لإصلاح:")
print("1. مشكلة العهد")
print("2. مشكلة الإدارات") 
print("3. مشكلة الفواتير")
print("4. مشكلة التراخيص")
print("5. مشكلة الدعم الفني")