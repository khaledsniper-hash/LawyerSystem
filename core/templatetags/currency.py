# core/templatetags/currency.py

from django import template
from django.conf import settings

register = template.Library()

@register.filter
def currency(value):
    """
    تنسيق القيمة مع رمز العملة
    مثال: 660000 → 660,000.00 ج.م
    """
    try:
        # تنسيق الرقم مع فاصل آلاف (فاصلة) وفاصل عشري (نقطة)
        return f"{float(value):,.2f} {getattr(settings, 'CURRENCY_SYMBOL', 'ج.م')}"
    except (ValueError, TypeError):
        return f"{value} {getattr(settings, 'CURRENCY_SYMBOL', 'ج.م')}"

@register.filter
def currency_name(value):
    """
    تنسيق القيمة مع اسم العملة الكامل
    مثال: 660000 → 660,000.00 جنيه مصري
    """
    try:
        return f"{float(value):,.2f} {getattr(settings, 'CURRENCY_NAME', 'جنيه مصري')}"
    except (ValueError, TypeError):
        return f"{value} {getattr(settings, 'CURRENCY_NAME', 'جنيه مصري')}"

@register.filter
def currency_short(value):
    """
    تنسيق مختصر بدون خانات عشرية
    مثال: 660000 → 660,000 ج.م
    """
    try:
        return f"{int(float(value)):,} {getattr(settings, 'CURRENCY_SYMBOL', 'ج.م')}"
    except (ValueError, TypeError):
        return f"{value} {getattr(settings, 'CURRENCY_SYMBOL', 'ج.م')}"

@register.filter
def currency_egypt(value):
    """
    تنسيق مصري (فاصلة للعشرية، نقطة للآلاف)
    مثال: 660000 → 660.000,00 ج.م
    """
    try:
        # تنسيق دولي أولاً
        formatted = f"{float(value):,.2f}"
        # عكس الفواصل للتنسيق المصري
        formatted = formatted.replace(',', 'TEMP').replace('.', ',').replace('TEMP', '.')
        return f"{formatted} {getattr(settings, 'CURRENCY_SYMBOL', 'ج.م')}"
    except (ValueError, TypeError):
        return f"{value} {getattr(settings, 'CURRENCY_SYMBOL', 'ج.م')}"