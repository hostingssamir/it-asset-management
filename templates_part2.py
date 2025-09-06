# قوالب HTML للنظام الكامل - الجزء الثاني

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
        // تأثيرات تفاعلية
        document.addEventListener('DOMContentLoaded', function() {
            // تأثير العد التصاعدي للأرقام
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
            
            // تأثير الظهور التدريجي للبطاقات
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
            transition: transform 0.3s ease;
        }
        .card:hover { transform: translateY(-5px); }
        .table th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            font-weight: 600;
        }
        .badge { padding: 0.5rem 1rem; border-radius: 10px; font-weight: 500; }
        .btn-action { border-radius: 10px; margin: 0 2px; }
        .custody-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            margin-bottom: 1rem;
            transition: transform 0.3s ease;
        }
        .custody-card:hover { transform: translateY(-3px); }
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
                        <a class="nav-link dropdown-toggle text-white active" href="#" role="button" data-bs-toggle="dropdown">
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
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="fas fa-handshake text-primary me-2"></i>إدارة العهد</h2>
            <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addCustodyModal">
                <i class="fas fa-plus me-2"></i>إضافة عهدة جديدة
            </button>
        </div>

        <!-- إحصائيات العهد -->
        <div class="row mb-4">
            <div class="col-md-4">
                <div class="custody-card p-3 text-center">
                    <i class="fas fa-handshake fa-2x mb-2"></i>
                    <h4>{{ custody_list|length }}</h4>
                    <p class="mb-0">إجمالي العهد</p>
                </div>
            </div>
            <div class="col-md-4">
                <div class="custody-card p-3 text-center">
                    <i class="fas fa-check-circle fa-2x mb-2"></i>
                    <h4>{{ custody_list|selectattr('10', 'equalto', 'نشط')|list|length }}</h4>
                    <p class="mb-0">عهد نشطة</p>
                </div>
            </div>
            <div class="col-md-4">
                <div class="custody-card p-3 text-center">
                    <i class="fas fa-undo fa-2x mb-2"></i>
                    <h4>{{ custody_list|selectattr('10', 'equalto', 'مرتجع')|list|length }}</h4>
                    <p class="mb-0">عهد مرتجعة</p>
                </div>
            </div>
        </div>

        <!-- جدول العهد -->
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0"><i class="fas fa-list me-2"></i>قائمة العهد</h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>رقم الأصل</th>
                                <th>اسم الأصل</th>
                                <th>الموظف</th>
                                <th>رقم الموظف</th>
                                <th>تاريخ التسليم</th>
                                <th>تاريخ الإرجاع</th>
                                <th>الحالة</th>
                                <th>الإجراءات</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for custody in custody_list %}
                            <tr>
                                <td><strong class="text-primary">{{ custody[11] }}</strong></td>
                                <td>{{ custody[12] }}</td>
                                <td>{{ custody[13] }}</td>
                                <td><span class="badge bg-info">{{ custody[14] }}</span></td>
                                <td>{{ custody[3] }}</td>
                                <td>{{ custody[4] or 'لم يُرجع بعد' }}</td>
                                <td>
                                    <span class="badge bg-{{ 'success' if custody[10] == 'نشط' else 'secondary' }}">
                                        {{ custody[10] }}
                                    </span>
                                </td>
                                <td>
                                    {% if custody[10] == 'نشط' %}
                                    <button class="btn btn-warning btn-sm btn-action" onclick="returnCustody({{ custody[0] }})">
                                        <i class="fas fa-undo"></i> إرجاع
                                    </button>
                                    {% endif %}
                                    <button class="btn btn-info btn-sm btn-action" onclick="viewCustody({{ custody[0] }})">
                                        <i class="fas fa-eye"></i>
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

    <!-- Modal إضافة عهدة -->
    <div class="modal fade" id="addCustodyModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">إضافة عهدة جديدة</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="custodyForm">
                        <div class="mb-3">
                            <label class="form-label">الأصل</label>
                            <select class="form-control" name="asset_id" required>
                                <option value="">اختر الأصل</option>
                                <!-- سيتم ملؤها بـ JavaScript -->
                            </select>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">الموظف</label>
                            <select class="form-control" name="employee_id" required>
                                <option value="">اختر الموظف</option>
                                <!-- سيتم ملؤها بـ JavaScript -->
                            </select>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">تاريخ التسليم</label>
                            <input type="date" class="form-control" name="assigned_date" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">ملاحظات</label>
                            <textarea class="form-control" name="notes" rows="3"></textarea>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إلغاء</button>
                    <button type="button" class="btn btn-primary" onclick="saveCustody()">حفظ العهدة</button>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function returnCustody(custodyId) {
            if (confirm('هل أنت متأكد من إرجاع هذه العهدة؟')) {
                // هنا يمكن إضافة كود الإرجاع
                alert('تم إرجاع العهدة بنجاح');
                location.reload();
            }
        }
        
        function viewCustody(custodyId) {
            alert('عرض تفاصيل العهدة رقم: ' + custodyId);
        }
        
        function saveCustody() {
            alert('تم حفظ العهدة بنجاح');
            document.getElementById('custodyForm').reset();
            bootstrap.Modal.getInstance(document.getElementById('addCustodyModal')).hide();
        }
        
        // تعيين تاريخ اليوم كافتراضي
        document.addEventListener('DOMContentLoaded', function() {
            const today = new Date().toISOString().split('T')[0];
            document.querySelector('input[name="assigned_date"]').value = today;
        });
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
        .quick-fill {
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            border-radius: 15px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }
        .quick-fill-btn {
            background: #2196f3;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            margin: 0.25rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .quick-fill-btn:hover {
            background: #1976d2;
            transform: scale(1.05);
        }
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
                        <a class="nav-link dropdown-toggle text-white active" href="#" role="button" data-bs-toggle="dropdown">
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
                        
                        <!-- ملء سريع -->
                        <div class="quick-fill">
                            <h6 class="mb-3"><i class="fas fa-magic me-2"></i>ملء سريع - أمثلة:</h6>
                            <button type="button" class="quick-fill-btn" onclick="fillExample('manager')">مدير</button>
                            <button type="button" class="quick-fill-btn" onclick="fillExample('accountant')">محاسب</button>
                            <button type="button" class="quick-fill-btn" onclick="fillExample('developer')">مطور</button>
                            <button type="button" class="quick-fill-btn" onclick="fillExample('designer')">مصمم</button>
                            <button type="button" class="quick-fill-btn" onclick="fillExample('sales')">مبيعات</button>
                        </div>
                        
                        <form method="POST" id="employeeForm">
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label"><i class="fas fa-id-card me-2"></i>رقم الموظف *</label>
                                    <input type="text" class="form-control" name="emp_id" required placeholder="EMP001">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label"><i class="fas fa-user me-2"></i>اسم الموظف *</label>
                                    <input type="text" class="form-control" name="name" required placeholder="أحمد محمد علي">
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label"><i class="fas fa-building me-2"></i>الإدارة *</label>
                                    <select class="form-select" name="department" required>
                                        <option value="">اختر الإدارة</option>
                                        <option value="المحاسبة">المحاسبة</option>
                                        <option value="المبيعات">المبيعات</option>
                                        <option value="التسويق">التسويق</option>
                                        <option value="تقنية المعلومات">تقنية المعلومات</option>
                                        <option value="الموارد البشرية">الموارد البشرية</option>
                                        <option value="الإدارة العامة">الإدارة العامة</option>
                                        <option value="خدمة العملاء">خدمة العملاء</option>
                                    </select>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label"><i class="fas fa-briefcase me-2"></i>المنصب *</label>
                                    <input type="text" class="form-control" name="position" required placeholder="محاسب أول">
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label"><i class="fas fa-envelope me-2"></i>البريد الإلكتروني</label>
                                    <input type="email" class="form-control" name="email" placeholder="ahmed@company.com">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label"><i class="fas fa-phone me-2"></i>رقم الهاتف</label>
                                    <input type="tel" class="form-control" name="phone" placeholder="0501234567">
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label"><i class="fas fa-calendar me-2"></i>تاريخ التوظيف *</label>
                                    <input type="date" class="form-control" name="hire_date" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label"><i class="fas fa-toggle-on me-2"></i>الحالة *</label>
                                    <select class="form-select" name="status" required>
                                        <option value="">اختر الحالة</option>
                                        <option value="نشط" selected>نشط</option>
                                        <option value="إجازة">إجازة</option>
                                        <option value="متوقف">متوقف</option>
                                    </select>
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label"><i class="fas fa-user-tie me-2"></i>المدير المباشر</label>
                                    <select class="form-select" name="manager_id">
                                        <option value="">لا يوجد</option>
                                        {% for manager in managers %}
                                        <option value="{{ manager[0] }}">{{ manager[1] }}</option>
                                        {% endfor %}
                                    </select>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label"><i class="fas fa-map-marker-alt me-2"></i>موقع المكتب</label>
                                    <input type="text" class="form-control" name="office_location" placeholder="الطابق الأول - مكتب 101">
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
        // أمثلة للملء السريع
        const examples = {
            manager: {
                emp_id: 'MGR' + String(Math.floor(Math.random() * 900) + 100),
                name: 'خالد أحمد المدير',
                department: 'الإدارة العامة',
                position: 'مدير عام',
                email: 'khalid.manager@company.com',
                phone: '0509876543'
            },
            accountant: {
                emp_id: 'ACC' + String(Math.floor(Math.random() * 900) + 100),
                name: 'فاطمة سعد المحاسبة',
                department: 'المحاسبة',
                position: 'محاسب أول',
                email: 'fatima.acc@company.com',
                phone: '0501234567'
            },
            developer: {
                emp_id: 'DEV' + String(Math.floor(Math.random() * 900) + 100),
                name: 'أحمد محمد المطور',
                department: 'تقنية المعلومات',
                position: 'مطور برمجيات',
                email: 'ahmed.dev@company.com',
                phone: '0507654321'
            },
            designer: {
                emp_id: 'DES' + String(Math.floor(Math.random() * 900) + 100),
                name: 'سارة علي المصممة',
                department: 'التسويق',
                position: 'مصممة جرافيك',
                email: 'sara.design@company.com',
                phone: '0502468135'
            },
            sales: {
                emp_id: 'SAL' + String(Math.floor(Math.random() * 900) + 100),
                name: 'محمد حسن المبيعات',
                department: 'المبيعات',
                position: 'مندوب مبيعات',
                email: 'mohammed.sales@company.com',
                phone: '0508642097'
            }
        };
        
        function fillExample(type) {
            const example = examples[type];
            if (example) {
                document.querySelector('input[name="emp_id"]').value = example.emp_id;
                document.querySelector('input[name="name"]').value = example.name;
                document.querySelector('select[name="department"]').value = example.department;
                document.querySelector('input[name="position"]').value = example.position;
                document.querySelector('input[name="email"]').value = example.email;
                document.querySelector('input[name="phone"]').value = example.phone;
            }
        }
        
        // تعيين تاريخ اليوم كافتراضي
        document.addEventListener('DOMContentLoaded', function() {
            const today = new Date().toISOString().split('T')[0];
            document.querySelector('input[name="hire_date"]').value = today;
            
            // تأثيرات التفاعل
            document.querySelectorAll('.form-control, .form-select').forEach(input => {
                input.addEventListener('focus', function() {
                    this.style.transform = 'translateY(-2px)';
                    this.style.boxShadow = '0 8px 25px rgba(102, 126, 234, 0.15)';
                });
                
                input.addEventListener('blur', function() {
                    this.style.transform = 'translateY(0)';
                    this.style.boxShadow = '';
                });
            });
            
            // تأكيد الإرسال
            document.getElementById('employeeForm').addEventListener('submit', function(e) {
                const name = document.querySelector('input[name="name"]').value;
                const empId = document.querySelector('input[name="emp_id"]').value;
                
                if (!confirm(`هل أنت متأكد من إضافة الموظف "${name}" برقم "${empId}"؟`)) {
                    e.preventDefault();
                }
            });
        });
    </script>
</body>
</html>
'''