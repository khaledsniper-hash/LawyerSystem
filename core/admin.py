"""
Admin configuration for Law Firm Management System.
All models registered with Arabic labels and full customization.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Count
from django.utils.html import format_html

from .models import (
    User,
    OfficeProfile,
    Client,
    Opponent,
    Case,
    Session,
    Document,
    Fee,
    Payment,
    Invoice,
    Expense,
    Consultation,
    Task,
    Appointment,
    Contract,
    PowerOfAttorney,
    Declaration,
    Notification,
    LookupData,
)


# ==================== 1. USERS & AUTH ====================

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """مستخدم النظام"""
    list_display = ('username', 'email', 'role', 'bar_number', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'bar_number')
    list_filter = ('role', 'is_active', 'is_staff')
    ordering = ('username',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('بيانات إضافية', {
            'fields': ('role', 'bar_number', 'specialization', 'profile_picture'),
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('بيانات إضافية', {
            'fields': ('role', 'bar_number', 'specialization', 'profile_picture'),
        }),
    )


@admin.register(OfficeProfile)
class OfficeProfileAdmin(admin.ModelAdmin):
    """ملف المكتب"""
    list_display = ('id', 'tax_id', 'phone', 'email', 'currency')
    search_fields = ('tax_id', 'phone', 'email', 'address')
    readonly_fields = ('logo_preview',)

    def logo_preview(self, obj):
        if obj and obj.logo:
            return format_html('<img src="{}" width="200" alt="شعار المكتب" />', obj.logo.url)
        return "—"

    logo_preview.short_description = 'معاينة الشعار'

    def has_add_permission(self, request):
        # Allow only one OfficeProfile (singleton-like)
        return not OfficeProfile.objects.exists()


# ==================== 2. CASES MODULE ====================

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """العملاء"""
    list_display = ('client_id', 'full_name', 'type', 'phone', 'email', 'status', 'case_count')
    search_fields = ('client_id', 'full_name', 'phone', 'email')
    list_filter = ('type', 'status')
    readonly_fields = ('client_id',)
    date_hierarchy = None

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_case_count=Count('cases'))

    @admin.display(description='عدد القضايا', ordering='_case_count')
    def case_count(self, obj):
        return getattr(obj, '_case_count', obj.cases.count())


@admin.register(Opponent)
class OpponentAdmin(admin.ModelAdmin):
    """الخصوم"""
    list_display = ('name', 'type', 'id_number', 'phone', 'opponent_lawyer')
    search_fields = ('name', 'id_number', 'phone', 'opponent_lawyer')
    list_filter = ('type',)


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    """القضايا"""
    list_display = (
        'case_number', 'subject', 'client', 'court', 'case_type',
        'status', 'priority', 'next_session_date'
    )
    search_fields = ('case_number', 'subject', 'court', 'case_type')
    list_filter = ('status', 'priority', 'position', 'case_type')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    filter_horizontal = ('opponents',)
    raw_id_fields = ('client',)


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    """الجلسات"""
    list_display = ('case', 'date', 'session_type', 'status')
    search_fields = ('case__case_number', 'session_type', 'minutes')
    list_filter = ('status', 'date')
    date_hierarchy = 'date'
    raw_id_fields = ('case',)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """المستندات"""
    list_display = ('doc_type', 'case', 'security_level', 'uploaded_at')
    list_filter = ('doc_type', 'security_level')
    readonly_fields = ('uploaded_at',)
    date_hierarchy = 'uploaded_at'
    raw_id_fields = ('case',)


# ==================== 3. FINANCE MODULE ====================

@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    """الأتعاب"""
    list_display = ('case', 'fee_type', 'agreed_amount', 'status')
    search_fields = ('case__case_number',)
    list_filter = ('fee_type', 'status')
    raw_id_fields = ('case',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """الدفعات"""
    list_display = ('fee', 'amount', 'date', 'payment_method')
    search_fields = ('fee__case__case_number', 'notes')
    list_filter = ('payment_method', 'date')
    date_hierarchy = 'date'
    raw_id_fields = ('fee',)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """الفواتير"""
    list_display = (
        'invoice_number', 'client', 'subtotal', 'tax_amount', 'total',
        'status', 'date'
    )
    search_fields = ('invoice_number', 'client__full_name', 'client__client_id')
    list_filter = ('status', 'date')
    readonly_fields = ('invoice_number', 'tax_amount', 'total')
    date_hierarchy = 'date'
    raw_id_fields = ('client',)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    """المصروفات"""
    list_display = ('description', 'category', 'amount', 'case', 'date')
    search_fields = ('description', 'case__case_number')
    list_filter = ('category', 'date')
    date_hierarchy = 'date'
    raw_id_fields = ('case',)


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    """الاستشارات"""
    list_display = ('title', 'client', 'date', 'amount_collected', 'status')
    search_fields = ('title', 'client__full_name', 'notes')
    list_filter = ('status', 'date')
    date_hierarchy = 'date'
    raw_id_fields = ('client',)


# ==================== 4. OPERATIONS MODULE ====================

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """المهام"""
    list_display = ('title', 'assigned_to', 'status', 'priority', 'due_date', 'case')
    search_fields = ('title', 'description', 'assigned_to__username')
    list_filter = ('status', 'priority')
    date_hierarchy = 'due_date'
    raw_id_fields = ('assigned_to', 'case')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """المواعيد"""
    list_display = ('type', 'client', 'location', 'datetime', 'status')
    search_fields = ('location', 'client__full_name')
    list_filter = ('type', 'status')
    date_hierarchy = 'datetime'
    raw_id_fields = ('client',)


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    """العقود"""
    list_display = (
        'contract_number', 'type', 'client', 'value',
        'start_date', 'end_date', 'status'
    )
    search_fields = ('contract_number', 'type', 'client__full_name')
    list_filter = ('status',)
    date_hierarchy = 'start_date'
    raw_id_fields = ('client',)


@admin.register(PowerOfAttorney)
class PowerOfAttorneyAdmin(admin.ModelAdmin):
    """التوكيلات"""
    list_display = ('client', 'type', 'issue_date', 'expiry_date', 'status')
    search_fields = ('client__full_name', 'issuer')
    list_filter = ('type', 'status')
    date_hierarchy = 'expiry_date'
    raw_id_fields = ('client',)


@admin.register(Declaration)
class DeclarationAdmin(admin.ModelAdmin):
    """الإقرارات"""
    list_display = ('declaration_number', 'type', 'client', 'date', 'status')
    search_fields = ('declaration_number', 'type', 'client__full_name')
    list_filter = ('status',)
    date_hierarchy = 'date'
    raw_id_fields = ('client',)


# ==================== 5. SYSTEM MODULE ====================

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """الإشعارات"""
    list_display = ('message', 'notification_type', 'target_user', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    raw_id_fields = ('target_user',)

    def has_add_permission(self, request):
        return True


@admin.register(LookupData)
class LookupDataAdmin(admin.ModelAdmin):
    """البيانات المرجعية"""
    list_display = ('category', 'name', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name',)
