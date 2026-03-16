# دليل تشغيل مشروع "ميزان العدالة" محلياً

هذا المستند يوضح جميع المتطلبات والخطوات اللازمة لتشغيل المشروع على أي جهاز محلي.

## 1. المتطلبات البرمجية (System Requirements)

*   **Python**: الإصدار 3.10 أو أحدث.
*   **Redis**: مطلوب كـ Broker لـ Celery (للتعامل مع المهام الخلفية والإشعارات).
    *   *على ويندوز، يمكنك استخدامه عبر [Memurai](https://www.memurai.com/) أو WSL.*
*   **Database**: يتم استخدام **SQLite** بشكل افتراضي للتطوير، ولا يتطلب تثبيت إضافي. (يُنصح بـ **PostgreSQL** للإنتاج).

## 2. متطلبات لغة Python (Libraries)

يجب تثبيت المكتبات التالية داخل بيئة افتراضية (Virtual Environment):

pip install -r requirements.txt
أو
pip install django pillow celery django-celery-beat redis


*توضيح للمكتبات:*
*   **Django**: إطار العمل الأساسي.
*   **Pillow**: ضروري للتعامل مع الصور (مثل صور البروفايل وشعار المكتب).
*   **Celery & django-celery-beat**: لإدارة المهام المجدولة (مثل تنبيهات الجلسات).
*   **Redis**: للربط بين Django و Celery.

## 3. خطوات التشغيل لأول مرة

افتح الـ Terminal في مجلد المشروع وقم بتنفيذ الخطوات التالية:

### أ. إنشاء البيئة الافتراضية (اختياري ولكن ينصح به)

python -m venv venv
.\venv\Scripts\activate

### ب. تهيئة قاعدة البيانات
python manage.py migrate

### ج. إنشاء حساب مدير النظام
python manage.py createsuperuser

### د. تشغيل خادم التطوير
python manage.py runserver

---

## 4. تشغيل المهام الخلفية (Celery)
إذا كان المشروع يحتوي على إشعارات تلقائية أو مهام مجدولة، يجب تشغيل Celery (تأكد من تشغيل خادم Redis أولاً):

1.  **تشغيل الـ Worker:**
    
    celery -A lawyer_system worker -l info
    
2.  **تشغيل الـ Beat (للمهام المجدولة):**
    
    celery -A lawyer_system beat -l info
    

---

## 5. هيكل المجلدات الهام
يجب التأكد من وجود المجلدات التالية لضمان عمل حفظ الملفات بشكل صحيح:
*   `static/`: للملفات الثابتة (CSS, JS, Images).
*   `media_files/`: لحفظ المستندات المرفوعة، الفواتير، والنسخ الاحتياطية.

---
**ملاحظة:** تم استنتاج هذه المتطلبات بناءً على تحليل ملفات الإعدادات ([settings.py](file:///d:/VSCode/LawyerSystem/lawyer_system/settings.py)) ونماذج البيانات ([models.py](file:///d:/VSCode/LawyerSystem/core/models.py)) ووثيقة المواصفات ([SPECIFICATION.md](file:///d:/VSCode/LawyerSystem/SPECIFICATION.md)).
تثبيت المتطلبات
