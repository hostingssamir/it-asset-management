
    // إضافة أزرار العودة للرئيسية في جميع الصفحات
    document.addEventListener('DOMContentLoaded', function() {
        // البحث عن العناوين الرئيسية
        const headers = document.querySelectorAll('h2');
        
        headers.forEach(header => {
            const parent = header.parentElement;
            if (parent && parent.classList.contains('d-flex')) {
                // التحقق من وجود زر العودة
                const homeButton = parent.querySelector('a[href="/"]');
                if (!homeButton) {
                    // إنشاء زر العودة
                    const homeBtn = document.createElement('a');
                    homeBtn.href = '/';
                    homeBtn.className = 'btn btn-outline-success me-2';
                    homeBtn.innerHTML = '<i class="fas fa-home me-1"></i>الرئيسية';
                    
                    // إضافة الزر
                    const buttonContainer = parent.querySelector('div') || parent;
                    buttonContainer.insertBefore(homeBtn, buttonContainer.firstChild);
                }
            }
        });
    });
    