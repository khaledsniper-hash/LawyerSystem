"""
Forms for the core app.
"""
from django import forms
from django.core.exceptions import ValidationError
from .models import Case, Client, Opponent


class CaseForm(forms.ModelForm):
    custom_opponent = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'أضف خصم جديد',
            'dir': 'rtl',
        }),
        label="خصم آخر (غير مسجل)"
    )
    
    class Meta:
        model = Case
        fields = [
            'case_number', 'case_year', 'subject', 'case_type',
            'client', 'opponents', 'court', 'status', 'priority',
            'position', 'next_session_date', 'notes',
        ]
        widgets = {
            'case_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1234/2024', 'dir': 'rtl'}),
            'case_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '2024', 'dir': 'rtl'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'موضوع القضية', 'dir': 'rtl'}),
            'case_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مدني، جنائي...', 'dir': 'rtl'}),
            'client': forms.Select(attrs={'class': 'form-select', 'dir': 'rtl'}),
            'opponents': forms.SelectMultiple(attrs={'class': 'form-select', 'dir': 'rtl'}),
            'court': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'المحكمة', 'dir': 'rtl'}),
            'status': forms.Select(attrs={'class': 'form-select', 'dir': 'rtl'}),
            'priority': forms.Select(attrs={'class': 'form-select', 'dir': 'rtl'}),
            'position': forms.Select(attrs={'class': 'form-select', 'dir': 'rtl'}),
            'next_session_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'dir': 'rtl'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'dir': 'rtl'}),
        }
        labels = {
            'case_number': 'رقم القضية',
            'case_year': 'السنة',
            'subject': 'موضوع القضية',
            'client': 'العميل',
            'opponents': 'الخصوم',
            'court': 'المحكمة',
            'case_type': 'نوع القضية',
            'status': 'الحالة',
            'priority': 'الأولوية',
            'position': 'موقف المكتب',
            'next_session_date': 'تاريخ الجلسة القادمة',
            'notes': 'ملاحظات',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.Textarea, forms.DateInput, forms.SelectMultiple)):
                field.widget.attrs.update({
                    'class': (field.widget.attrs.get('class', '') + ' text-end').strip(),
                    'dir': 'rtl',
                })
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({
                    'class': (field.widget.attrs.get('class', '') + ' text-end').strip(),
                    'dir': 'rtl',
                })
    
    def clean_case_number(self):
        case_number = self.cleaned_data.get('case_number')
        if case_number:
            instance = getattr(self, 'instance', None)
            qs = Case.objects.filter(case_number=case_number)
            if instance and instance.pk:
                qs = qs.exclude(pk=instance.pk)
            if qs.exists():
                raise ValidationError('رقم القضية مستخدم بالفعل')
        return case_number
    
    def save(self, commit=True):
        case = super().save(commit=commit)
        custom_opponent = self.cleaned_data.get('custom_opponent')
        if custom_opponent and commit:
            opponent, _ = Opponent.objects.get_or_create(name=custom_opponent)
            case.opponents.add(opponent)
        return case


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['full_name', 'national_id', 'phone', 'additional_phone', 'job', 'type', 'address', 'notes']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الاسم الكامل'}),
            'national_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '14 رقم'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'رقم الهاتف'}),
            'additional_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'رقم إضافي'}),
            'job': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الوظيفة'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if hasattr(field.widget, 'attrs'):
                field.widget.attrs.update({'dir': 'rtl'})
    
    def clean_national_id(self):
        national_id = self.cleaned_data.get('national_id')
        if national_id and len(national_id) != 14:
            raise ValidationError('الرقم القومي يجب أن يكون 14 رقماً')
        return national_id