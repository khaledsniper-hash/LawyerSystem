"""
Core models for Law Firm Management System.
All models use Arabic verbose_name and TextChoices for choice fields.
"""

import re
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


# --- Upload path helpers (media_files/ subfolders) ---

def document_upload_path(instance, filename):
    case_id = getattr(instance, 'case_id', None) or (instance.case.id if instance.case else None)
    if case_id:
        return f"documents/case_{case_id}/{filename}"
    return f"documents/{filename}"


def session_attachment_upload_path(instance, filename):
    case_id = getattr(instance, 'case_id', None) or (instance.case.id if instance.case else None)
    if case_id:
        return f"documents/sessions/case_{case_id}/{filename}"
    return f"documents/sessions/{filename}"


def contract_upload_path(instance, filename):
    return f"contracts/{filename}"


def poa_upload_path(instance, filename):
    return f"contracts/poa/{filename}"


def declaration_upload_path(instance, filename):
    return f"documents/declarations/{filename}"


def expense_receipt_upload_path(instance, filename):
    return f"documents/receipts/{filename}"


def logo_upload_path(instance, filename):
    return f"logos/{filename}"


def profile_picture_upload_path(instance, filename):
    return f"logos/profiles/{filename}"


# ==================== 1. USERS & AUTH ====================

class UserRole(models.TextChoices):
    ADMIN = 'admin', 'مدير النظام'
    LAWYER = 'lawyer', 'محامي'
    SECRETARY = 'secretary', 'سكرتير'
    ACCOUNTANT = 'accountant', 'محاسب'


class User(AbstractUser):
    """مستخدم النظام (مدير، محامي، سكرتير، محاسب)"""
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.LAWYER,
        verbose_name='الدور'
    )
    bar_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='رقم القيد'
    )
    specialization = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='التخصص'
    )
    profile_picture = models.ImageField(
        upload_to=profile_picture_upload_path,
        blank=True,
        null=True,
        verbose_name='صورة الملف الشخصي'
    )

    class Meta:
        verbose_name = 'مستخدم'
        verbose_name_plural = 'المستخدمون'
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.get_full_name() or self.username


class OfficeProfile(models.Model):
    """ملف المكتب (الشعار، البيانات الضريبية، الاتصال)"""
    logo = models.ImageField(
        upload_to=logo_upload_path,
        blank=True,
        null=True,
        verbose_name='شعار المكتب'
    )
    name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='اسم المكتب'
    )
    tax_id = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='الرقم الضريبي'
    )
    phone = models.CharField(
        max_length=30,
        blank=True,
        verbose_name='الهاتف'
    )
    email = models.EmailField(
        blank=True,
        verbose_name='البريد الإلكتروني'
    )
    address = models.TextField(
        blank=True,
        verbose_name='العنوان'
    )
    currency = models.CharField(
        max_length=10,
        default='EGP',
        verbose_name='العملة'
    )
    commercial_registration = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='السجل التجاري'
    )
    license_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='رقم الترخيص'
    )

    class Meta:
        verbose_name = 'ملف المكتب'
        verbose_name_plural = 'ملف المكتب'

    def __str__(self):
        return self.email or 'ملف المكتب'


# ==================== 2. CASES MODULE ====================

class ClientType(models.TextChoices):
    INDIVIDUAL = 'individual', 'فرد'
    COMPANY = 'company', 'شركة'


class ClientStatus(models.TextChoices):
    ACTIVE = 'active', 'نشط'
    INACTIVE = 'inactive', 'غير نشط'


class Client(models.Model):
    """العميل"""
    client_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        verbose_name='رقم العميل'
    )
    full_name = models.CharField(
        max_length=200,
        verbose_name='الاسم الكامل'
    )
    type = models.CharField(
        max_length=20,
        choices=ClientType.choices,
        default=ClientType.INDIVIDUAL,
        verbose_name='نوع العميل'
    )
    phone = models.CharField(
        max_length=30,
        blank=True,
        verbose_name='الهاتف'
    )
    additional_phone = models.CharField(
        max_length=30,
        blank=True,
        verbose_name='رقم إضافي'
    )
    email = models.EmailField(
        blank=True,
        verbose_name='البريد الإلكتروني'
    )
    national_id = models.CharField(
        max_length=14,
        blank=True,
        verbose_name='الرقم القومي'
    )
    job = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='الوظيفة'
    )
    address = models.TextField(
        blank=True,
        verbose_name='العنوان بالتفصيل'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='ملاحظات'
    )
    status = models.CharField(
        max_length=20,
        choices=ClientStatus.choices,
        default=ClientStatus.ACTIVE,
        verbose_name='الحالة'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ الإضافة"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاريخ التحديث"
    )

    class Meta:
        verbose_name = 'عميل'
        verbose_name_plural = 'العملاء'
        indexes = [
            models.Index(fields=['client_id']),
            models.Index(fields=['status']),
            models.Index(fields=['national_id']),
            models.Index(fields=['type']),
        ]

    def save(self, *args, **kwargs):
        if not self.client_id:
            last = Client.objects.order_by('-id').first()
            num = (last.id + 1) if last else 1
            self.client_id = f"CLT-{num:05d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.client_id} - {self.full_name}"


def client_attachment_path(instance, filename):
    return f'clients/{instance.client.client_id}/attachments/{filename}'


class ClientAttachment(models.Model):
    """مرفقات العميل"""
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name='العميل'
    )
    file = models.FileField(
        upload_to=client_attachment_path,
        verbose_name='الملف'
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الرفع'
    )

    class Meta:
        verbose_name = 'مرفق عميل'
        verbose_name_plural = 'مرفقات العميل'

    def __str__(self):
        return f"مرفق - {self.client.full_name}"


class OpponentType(models.TextChoices):
    INDIVIDUAL = 'individual', 'فرد'
    COMPANY = 'company', 'شركة'
    GOVERNMENT = 'government', 'جهة حكومية'
    ENTITY = 'entity', 'جهة أخرى'


class Opponent(models.Model):
    """الخصم"""
    name = models.CharField(
        max_length=200,
        verbose_name='الاسم'
    )
    type = models.CharField(
        max_length=20,
        choices=OpponentType.choices,
        default=OpponentType.INDIVIDUAL,
        verbose_name='نوع الخصم'
    )
    id_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='رقم الهوية'
    )
    phone = models.CharField(
        max_length=30,
        blank=True,
        verbose_name='الهاتف'
    )
    opponent_lawyer = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='محامي الخصم'
    )

    class Meta:
        verbose_name = 'خصم'
        verbose_name_plural = 'الخصوم'
        indexes = [models.Index(fields=['type'])]

    def __str__(self):
        return self.name


# ========================================
# CASE STATUS CHOICES - مصدر واحد للحقيقة
# ========================================

CASE_STATUS_CHOICES = [
    ('active', 'نشطة'),
    ('pending', 'معلقة'),
    ('won', 'مكسوبة'),
    ('closed', 'مغلقة'),
]

# ========================================
# CASE PRIORITY CHOICES
# ========================================

CASE_PRIORITY_CHOICES = [
    ('high', 'عاجل'),
    ('normal', 'عادي'),
    ('low', 'منخفض'),
]

# ========================================
# OFFICE POSITION CHOICES
# ========================================

OFFICE_POSITION_CHOICES = [
    ('plaintiff', 'مدعي'),
    ('defendant', 'مدعى عليه'),
]


class Case(models.Model):
    """القضية"""
    case_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='رقم القضية'
    )
    subject = models.CharField(
        max_length=500,
        verbose_name='موضوع القضية'
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='cases',
        verbose_name='العميل'
    )
    opponents = models.ManyToManyField(
        Opponent,
        blank=True,
        related_name='cases',
        verbose_name='الخصوم'
    )
    court = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='المحكمة'
    )
    case_type = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='نوع القضية'
    )
    status = models.CharField(
        max_length=20,
        choices=CASE_STATUS_CHOICES,
        default='active',
        verbose_name="حالة القضية"
    )
    
    priority = models.CharField(
        max_length=20,
        choices=CASE_PRIORITY_CHOICES,
        default='normal',
        verbose_name="الأولوية"
    )
    
    position = models.CharField(
        max_length=20,
        choices=OFFICE_POSITION_CHOICES,
        blank=True,
        verbose_name="موقف المكتب"
    )
    next_session_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='تاريخ الجلسة القادمة'
    )
    case_year = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='سنة القضية'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='ملاحظات'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الإنشاء'
    )

    class Meta:
        verbose_name = 'قضية'
        verbose_name_plural = 'القضايا'
        indexes = [
            models.Index(fields=['case_number']),
            models.Index(fields=['status']),
            models.Index(fields=['next_session_date']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.case_number} - {self.subject}"


class SessionStatus(models.TextChoices):
    SCHEDULED = 'scheduled', 'مجدولة'
    COMPLETED = 'completed', 'منتهية'
    POSTPONED = 'postponed', 'مؤجلة'


class Session(models.Model):
    """جلسة قضائية"""
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name='sessions',
        verbose_name='القضية'
    )
    date = models.DateField(
        verbose_name='التاريخ'
    )
    session_type = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='نوع الجلسة'
    )
    minutes = models.TextField(
        blank=True,
        verbose_name='محضر الجلسة'
    )
    attachments = models.FileField(
        upload_to=session_attachment_upload_path,
        blank=True,
        null=True,
        verbose_name='مرفقات'
    )
    status = models.CharField(
        max_length=20,
        choices=SessionStatus.choices,
        default=SessionStatus.SCHEDULED,
        verbose_name='الحالة'
    )

    class Meta:
        verbose_name = 'جلسة'
        verbose_name_plural = 'الجلسات'
        indexes = [
            models.Index(fields=['case']),
            models.Index(fields=['date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.case.case_number} - {self.date}"


class DocumentType(models.TextChoices):
    CONTRACT = 'contract', 'عقد'
    COURT_DOC = 'court_doc', 'مستند محكمة'
    EVIDENCE = 'evidence', 'دليل'
    CORRESPONDENCE = 'correspondence', 'مراسلات'
    ID = 'id', 'هوية/وثيقة'
    OTHER = 'other', 'أخرى'


class SecurityLevel(models.TextChoices):
    NORMAL = 'normal', 'عادي'
    CONFIDENTIAL = 'confidential', 'سري'


class Document(models.Model):
    """مستند مرتبط بقضية"""
    file = models.FileField(
        upload_to=document_upload_path,
        verbose_name='الملف'
    )
    doc_type = models.CharField(
        max_length=20,
        choices=DocumentType.choices,
        default=DocumentType.OTHER,
        verbose_name='نوع المستند'
    )
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='القضية'
    )
    security_level = models.CharField(
        max_length=20,
        choices=SecurityLevel.choices,
        default=SecurityLevel.NORMAL,
        verbose_name='مستوى السرية'
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الرفع'
    )

    class Meta:
        verbose_name = 'مستند'
        verbose_name_plural = 'المستندات'
        indexes = [
            models.Index(fields=['case']),
            models.Index(fields=['doc_type']),
            models.Index(fields=['uploaded_at']),
        ]

    def __str__(self):
        return f"{self.get_doc_type_display()} - {self.case.case_number}"


# ==================== 3. FINANCE MODULE ====================

class FeeType(models.TextChoices):
    FIXED = 'fixed', 'مبلغ ثابت'
    HOURLY = 'hourly', 'بالساعة'


class FeeStatus(models.TextChoices):
    PENDING = 'pending', 'معلق'
    PAID = 'paid', 'مدفوع'
    PARTIAL = 'partial', 'مدفوع جزئياً'


class Fee(models.Model):
    """أتعاب القضية"""
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name='fees',
        verbose_name='القضية'
    )
    fee_type = models.CharField(
        max_length=20,
        choices=FeeType.choices,
        default=FeeType.FIXED,
        verbose_name='نوع الأتعاب'
    )
    agreed_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0'),
        verbose_name='المبلغ المتفق عليه'
    )
    status = models.CharField(
        max_length=20,
        choices=FeeStatus.choices,
        default=FeeStatus.PENDING,
        verbose_name='الحالة'
    )

    class Meta:
        verbose_name = 'أتعاب'
        verbose_name_plural = 'الأتعاب'
        indexes = [
            models.Index(fields=['case']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.case.case_number} - {self.agreed_amount} {self.get_status_display()}"


class PaymentMethod(models.TextChoices):
    CASH = 'cash', 'نقدي'
    TRANSFER = 'transfer', 'تحويل'
    CHECK = 'check', 'شيك'


class Payment(models.Model):
    """دفعة مقابل أتعاب"""
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='المبلغ'
    )
    date = models.DateField(
        verbose_name='التاريخ'
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CASH,
        verbose_name='طريقة الدفع'
    )
    fee = models.ForeignKey(
        Fee,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='الأتعاب'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='ملاحظات'
    )

    class Meta:
        verbose_name = 'دفعة'
        verbose_name_plural = 'الدفعات'
        indexes = [
            models.Index(fields=['fee']),
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f"{self.amount} - {self.date}"


class InvoiceStatus(models.TextChoices):
    PAID = 'paid', 'مدفوع'
    PENDING = 'pending', 'معلق'
    CANCELLED = 'cancelled', 'ملغي'


class Invoice(models.Model):
    """فاتورة"""
    invoice_number = models.CharField(
        max_length=30,
        unique=True,
        editable=False,
        verbose_name='رقم الفاتورة'
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='invoices',
        verbose_name='العميل'
    )
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0'),
        verbose_name='المجموع الفرعي'
    )
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('15'),
        verbose_name='نسبة الضريبة %'
    )
    tax_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0'),
        editable=False,
        verbose_name='مبلغ الضريبة'
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0'),
        editable=False,
        verbose_name='الإجمالي'
    )
    status = models.CharField(
        max_length=20,
        choices=InvoiceStatus.choices,
        default=InvoiceStatus.PENDING,
        verbose_name='الحالة'
    )
    date = models.DateField(
        verbose_name='التاريخ'
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='تاريخ الاستحقاق'
    )

    class Meta:
        verbose_name = 'فاتورة'
        verbose_name_plural = 'الفواتير'
        indexes = [
            models.Index(fields=['invoice_number']),
            models.Index(fields=['client']),
            models.Index(fields=['status']),
            models.Index(fields=['date']),
        ]

    def save(self, *args, **kwargs):
        self.tax_amount = (self.subtotal * self.tax_rate / Decimal('100')).quantize(Decimal('0.01'))
        self.total = self.subtotal + self.tax_amount
        if not self.invoice_number:
            from datetime import date
            year = date.today().year
            last = Invoice.objects.filter(invoice_number__startswith=f"INV-{year}-").order_by('-id').first()
            if last:
                match = re.search(rf'INV-{year}-(\d+)', last.invoice_number)
                num = int(match.group(1)) + 1 if match else 1
            else:
                num = 1
            self.invoice_number = f"INV-{year}-{num:03d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice_number} - {self.client.full_name}"


class ExpenseCategory(models.TextChoices):
    COURT_FEES = 'court_fees', 'رسوم محكمة'
    TRANSPORT = 'transport', 'نقل'
    DOCUMENTS = 'documents', 'مستندات'
    UTILITIES = 'utilities', 'مرافق'
    OTHER = 'other', 'أخرى'


class Expense(models.Model):
    """مصروف"""
    description = models.CharField(
        max_length=500,
        verbose_name='الوصف'
    )
    category = models.CharField(
        max_length=30,
        choices=ExpenseCategory.choices,
        default=ExpenseCategory.OTHER,
        verbose_name='الفئة'
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='المبلغ'
    )
    case = models.ForeignKey(
        Case,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenses',
        verbose_name='القضية'
    )
    receipt = models.FileField(
        upload_to=expense_receipt_upload_path,
        blank=True,
        null=True,
        verbose_name='إيصال'
    )
    date = models.DateField(
        verbose_name='التاريخ'
    )

    class Meta:
        verbose_name = 'مصروف'
        verbose_name_plural = 'المصروفات'
        indexes = [
            models.Index(fields=['case']),
            models.Index(fields=['category']),
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f"{self.description} - {self.amount}"


class ConsultationStatus(models.TextChoices):
    NEW = 'new', 'جديد'
    COMPLETED = 'completed', 'منتهي'


class Consultation(models.Model):
    """استشارة"""
    title = models.CharField(
        max_length=200,
        verbose_name='العنوان'
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='consultations',
        verbose_name='العميل'
    )
    date = models.DateField(
        verbose_name='التاريخ'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='ملاحظات/توثيق الكلام'
    )
    amount_collected = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0'),
        verbose_name='المبلغ المحصل'
    )
    status = models.CharField(
        max_length=20,
        choices=ConsultationStatus.choices,
        default=ConsultationStatus.NEW,
        verbose_name='الحالة'
    )

    class Meta:
        verbose_name = 'استشارة'
        verbose_name_plural = 'الاستشارات'
        indexes = [
            models.Index(fields=['client']),
            models.Index(fields=['date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.title} - {self.client.full_name}"


# ==================== 4. OPERATIONS MODULE ====================

class TaskStatus(models.TextChoices):
    NEW = 'new', 'جديد'
    IN_PROGRESS = 'in_progress', 'قيد التنفيذ'
    REVIEW = 'review', 'مراجعة'
    DONE = 'done', 'منتهي'


class TaskPriority(models.TextChoices):
    URGENT = 'urgent', 'عاجل'
    HIGH = 'high', 'عالي'
    NORMAL = 'normal', 'عادي'
    LOW = 'low', 'منخفض'


class Task(models.Model):
    """مهمة"""
    title = models.CharField(
        max_length=200,
        verbose_name='العنوان'
    )
    description = models.TextField(
        blank=True,
        verbose_name='الوصف'
    )
    status = models.CharField(
        max_length=20,
        choices=TaskStatus.choices,
        default=TaskStatus.NEW,
        verbose_name='الحالة'
    )
    priority = models.CharField(
        max_length=20,
        choices=TaskPriority.choices,
        default=TaskPriority.NORMAL,
        verbose_name='الأولوية'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
        verbose_name='المكلف'
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='تاريخ الاستحقاق'
    )
    case = models.ForeignKey(
        Case,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
        verbose_name='القضية'
    )

    class Meta:
        verbose_name = 'مهمة'
        verbose_name_plural = 'المهام'
        indexes = [
            models.Index(fields=['assigned_to']),
            models.Index(fields=['status']),
            models.Index(fields=['due_date']),
            models.Index(fields=['case']),
        ]

    def __str__(self):
        return self.title


class AppointmentType(models.TextChoices):
    MEETING = 'meeting', 'اجتماع'
    CALL = 'call', 'مكالمة'
    CONSULTATION = 'consultation', 'استشارة'
    COURT_VISIT = 'court_visit', 'زيارة محكمة'
    SIGNING = 'signing', 'توقيع'


class AppointmentStatus(models.TextChoices):
    SCHEDULED = 'scheduled', 'مجدول'
    COMPLETED = 'completed', 'منتهي'
    CANCELLED = 'cancelled', 'ملغي'


class Appointment(models.Model):
    """موعد"""
    type = models.CharField(
        max_length=30,
        choices=AppointmentType.choices,
        default=AppointmentType.MEETING,
        verbose_name='النوع'
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='appointments',
        verbose_name='العميل'
    )
    location = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='المكان'
    )
    datetime = models.DateTimeField(
        verbose_name='التاريخ والوقت'
    )
    status = models.CharField(
        max_length=20,
        choices=AppointmentStatus.choices,
        default=AppointmentStatus.SCHEDULED,
        verbose_name='الحالة'
    )
    case = models.ForeignKey(
        'Case',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='appointments',
        verbose_name="القضية"
    )
    class Meta:
        verbose_name = 'موعد'
        verbose_name_plural = 'المواعيد'
        indexes = [
            models.Index(fields=['client']),
            models.Index(fields=['datetime']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.get_type_display()} - {self.datetime}"


class ContractStatus(models.TextChoices):
    DRAFT = 'draft', 'مسودة'
    PENDING_SIGNATURE = 'pending_signature', 'بانتظار التوقيع'
    ACTIVE = 'active', 'نشط'
    EXPIRED = 'expired', 'منتهي'


class Contract(models.Model):
    """عقد"""
    contract_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='رقم العقد'
    )
    type = models.CharField(
        max_length=100,
        verbose_name='نوع العقد'
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='contracts',
        verbose_name='العميل'
    )
    value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0'),
        verbose_name='القيمة'
    )
    start_date = models.DateField(
        verbose_name='تاريخ البدء'
    )
    end_date = models.DateField(
        verbose_name='تاريخ الانتهاء'
    )
    status = models.CharField(
        max_length=30,
        choices=ContractStatus.choices,
        default=ContractStatus.DRAFT,
        verbose_name='الحالة'
    )
    file = models.FileField(
        upload_to=contract_upload_path,
        blank=True,
        null=True,
        verbose_name='الملف'
    )

    class Meta:
        verbose_name = 'عقد'
        verbose_name_plural = 'العقود'
        indexes = [
            models.Index(fields=['contract_number']),
            models.Index(fields=['client']),
            models.Index(fields=['status']),
            models.Index(fields=['end_date']),
        ]

    def __str__(self):
        return f"{self.contract_number} - {self.client.full_name}"

    @property
    def is_expiring_soon(self):
        from django.utils import timezone
        import datetime
        if not self.end_date:
            return False
        days_left = (self.end_date - timezone.now().date()).days
        return 0 <= days_left <= 30 and self.status == 'active'


class PowerOfAttorneyType(models.TextChoices):
    GENERAL = 'general', 'عام'
    SPECIAL = 'special', 'خاص'
    JUDICIAL = 'judicial', 'قضائي'
    REAL_ESTATE = 'real_estate', 'عقاري'


class PowerOfAttorneyStatus(models.TextChoices):
    ACTIVE = 'active', 'نشط'
    EXPIRING_SOON = 'expiring_soon', 'قارب على الانتهاء'
    EXPIRED = 'expired', 'منتهي'


class PowerOfAttorney(models.Model):
    """وكالة"""
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='powers_of_attorney',
        verbose_name='العميل'
    )
    type = models.CharField(
        max_length=30,
        choices=PowerOfAttorneyType.choices,
        default=PowerOfAttorneyType.SPECIAL,
        verbose_name='نوع الوكالة'
    )
    issue_date = models.DateField(
        verbose_name='تاريخ الإصدار'
    )
    expiry_date = models.DateField(
        verbose_name='تاريخ الانتهاء'
    )
    issuer = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='الجهة المصدرة'
    )
    file = models.FileField(
        upload_to=poa_upload_path,
        blank=True,
        null=True,
        verbose_name='الملف'
    )
    status = models.CharField(
        max_length=20,
        choices=PowerOfAttorneyStatus.choices,
        default=PowerOfAttorneyStatus.ACTIVE,
        verbose_name='الحالة'
    )

    class Meta:
        verbose_name = 'وكالة'
        verbose_name_plural = 'التوكيلات'
        indexes = [
            models.Index(fields=['client']),
            models.Index(fields=['expiry_date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.get_type_display()} - {self.client.full_name}"


class DeclarationStatus(models.TextChoices):
    DRAFT = 'draft', 'مسودة'
    FINAL = 'final', 'نهائي'
    SIGNED = 'signed', 'موقع'


class Declaration(models.Model):
    """إقرار"""
    declaration_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='رقم الإقرار'
    )
    type = models.CharField(
        max_length=200,
        verbose_name='نوع الإقرار'
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='declarations',
        verbose_name='العميل'
    )
    date = models.DateField(
        verbose_name='التاريخ'
    )
    status = models.CharField(
        max_length=20,
        choices=DeclarationStatus.choices,
        default=DeclarationStatus.DRAFT,
        verbose_name='الحالة'
    )
    file = models.FileField(
        upload_to=declaration_upload_path,
        blank=True,
        null=True,
        verbose_name='الملف'
    )

    class Meta:
        verbose_name = 'إقرار'
        verbose_name_plural = 'الإقرارات'
        indexes = [
            models.Index(fields=['declaration_number']),
            models.Index(fields=['client']),
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f"{self.declaration_number} - {self.type}"


# ==================== 5. SYSTEM MODULE ====================

class NotificationType(models.TextChoices):
    SESSION = 'session', 'جلسة'
    PAYMENT = 'payment', 'دفعة'
    TASK = 'task', 'مهمة'
    CASE = 'case', 'قضية'
    CONTRACT = 'contract', 'عقد'


class Notification(models.Model):
    """إشعار"""
    message = models.TextField(
        verbose_name='الرسالة'
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.CASE,
        verbose_name='نوع الإشعار'
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name='تمت القراءة'
    )
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='المستخدم المستهدف'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الإنشاء'
    )

    class Meta:
        verbose_name = 'إشعار'
        verbose_name_plural = 'الإشعارات'
        indexes = [
            models.Index(fields=['target_user']),
            models.Index(fields=['is_read']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.message[:50] + '...' if len(self.message) > 50 else self.message


class LookupCategory(models.TextChoices):
    COURTS = 'courts', 'المحاكم'
    CASE_TYPES = 'case_types', 'أنواع القضايا'
    EXPENSE_CATEGORIES = 'expense_categories', 'فئات المصروفات'


class LookupData(models.Model):
    """بيانات مرجعية (محاكم، أنواع قضايا، فئات مصروفات)"""
    category = models.CharField(
        max_length=30,
        choices=LookupCategory.choices,
        verbose_name='الفئة'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='الاسم'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='نشط'
    )

    class Meta:
        verbose_name = 'بيانات مرجعية'
        verbose_name_plural = 'البيانات المرجعية'
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
        ]
        unique_together = [['category', 'name']]

    def __str__(self):
        return f"{self.get_category_display()} - {self.name}"
