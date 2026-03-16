from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.conf import settings
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
import shutil
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import logout

# استيراد الموديلات
    PowerOfAttorney, Notification, OfficeProfile, User, ClientAttachment,
    Consultation, Declaration,
)
from .forms import CaseForm, ClientForm


# ========================================
# Logout View
# ========================================
def logout_view(request):
    """تسجيل الخروج من النظام"""
    logout(request)
    return redirect('core:login')


# ========================================
# Dashboard View
# ========================================
class DashboardView(LoginRequiredMixin, ListView):
    model = Case
    template_name = 'core/dashboard.html'
    context_object_name = 'recent_cases'
    
    def get_queryset(self):
        return Case.objects.all().order_by('-created_at')[:5]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_cases'] = Case.objects.count()
        context['active_cases'] = Case.objects.filter(status='active').count()
        context['pending_cases'] = Case.objects.filter(status='pending').count()
        context['closed_cases'] = Case.objects.filter(status='closed').count()
        context['total_clients'] = Client.objects.count()
        context['today_sessions'] = Session.objects.filter(date=date.today()).count()
        context['pending_tasks'] = Task.objects.filter(status__in=['new', 'in_progress']).count()
        
        total_fees = Fee.objects.aggregate(total=Sum('agreed_amount'))['total'] or 0
        total_expenses = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0
        context['total_fees'] = total_fees
        context['total_expenses'] = total_expenses
        context['net_profit'] = total_fees - total_expenses
        
        context['clients'] = Client.objects.all().order_by('full_name')
        try:
            context['opponents'] = Opponent.objects.filter(is_active=True).order_by('name')
        except:
            context['opponents'] = Opponent.objects.all().order_by('name')
        context['current_year'] = timezone.now().year
        
        return context


# ========================================
# Cases Views
# ========================================
class CaseListView(LoginRequiredMixin, ListView):
    model = Case
    template_name = 'core/cases.html'
    context_object_name = 'cases'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = Case.objects.all().select_related('client').prefetch_related('opponents')
        
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        case_type = self.request.GET.get('case_type')
        if case_type:
            queryset = queryset.filter(case_type=case_type)
        
        court = self.request.GET.get('court')
        if court:
            queryset = queryset.filter(court=court)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(case_number__icontains=search) |
                Q(subject__icontains=search) |
                Q(client__full_name__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_cases'] = Case.objects.count()
        context['active_cases'] = Case.objects.filter(status='active').count()
        context['pending_cases'] = Case.objects.filter(status='pending').count()
        context['closed_cases'] = Case.objects.filter(status='closed').count()
        context['clients'] = Client.objects.all().order_by('full_name')
        
        try:
            context['opponents'] = Opponent.objects.filter(is_active=True).order_by('name')
        except:
            context['opponents'] = Opponent.objects.all().order_by('name')
        
        context['current_year'] = timezone.now().year
        context['form'] = CaseForm()
        
        return context


class CaseCreateView(LoginRequiredMixin, CreateView):
    model = Case
    form_class = CaseForm
    template_name = 'core/case_standalone_form.html'
    success_url = reverse_lazy('core:cases')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clients'] = Client.objects.all().order_by('full_name')
        
        try:
            context['opponents'] = Opponent.objects.filter(is_active=True).order_by('name')
        except:
            context['opponents'] = Opponent.objects.all().order_by('name')
        
        context['current_year'] = timezone.now().year
        return context
    
    def form_valid(self, form):
        self.object = form.save()
        
        files = self.request.FILES.getlist('attachments')
        for f in files:
            Document.objects.create(file=f, case=self.object, doc_type='other')
        
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': f'تم حفظ القضية رقم {self.object.case_number} بنجاح',
                'case_id': self.object.id,
            })
        
        messages.success(self.request, '✅ تم إضافة القضية بنجاح')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'errors': form.errors,
            }, status=400)
        
        messages.error(self.request, '❌ هناك أخطاء في النموذج')
        return super().form_invalid(form)


class CaseUpdateView(LoginRequiredMixin, UpdateView):
    model = Case
    form_class = CaseForm
    template_name = 'core/case_standalone_form.html'
    success_url = reverse_lazy('core:cases')
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.template.loader import render_to_string
            context = self.get_context_data()
            html = render_to_string('core/case_form.html', context, request=request)
            return JsonResponse({'html': html})
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clients'] = Client.objects.all().order_by('full_name')
        
        try:
            context['opponents'] = Opponent.objects.filter(is_active=True).order_by('name')
        except:
            context['opponents'] = Opponent.objects.all().order_by('name')
        
        context['current_year'] = timezone.now().year
        context['years_range'] = range(2000, 2100)
        
        return context
    
    def form_valid(self, form):
        self.object = form.save()
        
        files = self.request.FILES.getlist('attachments')
        for f in files:
            Document.objects.create(file=f, case=self.object, doc_type='other')
        
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': f'تم تحديث القضية رقم {self.object.case_number} بنجاح',
                'case_id': self.object.id,
            })
        
        messages.success(self.request, '✅ تم تحديث بيانات القضية بنجاح')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'errors': form.errors,
            }, status=400)
        
        messages.error(self.request, '❌ هناك أخطاء في النموذج')
        return super().form_invalid(form)


class CaseDeleteView(LoginRequiredMixin, DeleteView):
    model = Case
    template_name = 'core/case_confirm_delete.html'
    success_url = reverse_lazy('core:cases')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        return redirect(success_url)


# ========================================
# Clients Views
# ========================================
class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'core/clients.html'
    context_object_name = 'clients'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = Client.objects.all().annotate(case_count=Count('cases'))
        
        client_type = self.request.GET.get('type')
        if client_type:
            queryset = queryset.filter(type=client_type)
        
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search) |
                Q(phone__icontains=search) |
                Q(email__icontains=search) |
                Q(client_id__icontains=search) |
                Q(national_id__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            context = self.get_context_data()
            return render(request, 'core/includes/client_table_partial.html', context)
        
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_clients'] = Client.objects.count()
        context['individual_clients'] = Client.objects.filter(type='individual').count()
        context['company_clients'] = Client.objects.filter(type='company').count()
        context['active_clients'] = Client.objects.filter(status='active').count()
        return context


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'core/client_form.html'
    success_url = reverse_lazy('core:clients')
    
    def form_valid(self, form):
        self.object = form.save()
        
        files = self.request.FILES.getlist('attachments')
        for f in files:
            ClientAttachment.objects.create(client=self.object, file=f)
        
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': 'تم إضافة العميل بنجاح'})
        
        messages.success(self.request, 'تم إضافة العميل بنجاح')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'errors': form.errors})
        return super().form_invalid(form)


class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = 'core/client_detail.html'
    context_object_name = 'client'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client = self.get_object()
        context['cases'] = Case.objects.filter(client=client)
        context['contracts'] = Contract.objects.filter(client=client)
        context['invoices'] = Invoice.objects.filter(client=client)
        return context


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    fields = ['full_name', 'national_id', 'type', 'phone', 'email', 'status']
    template_name = 'core/client_form.html'
    success_url = reverse_lazy('core:clients')


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = 'core/client_confirm_delete.html'
    success_url = reverse_lazy('core:clients')


# ========================================
# Opponents Views
# ========================================
class OpponentListView(LoginRequiredMixin, ListView):
    model = Opponent
    template_name = 'core/opponents.html'
    context_object_name = 'opponents'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Opponent.objects.all().annotate(case_count=Count('cases'))
        
        opponent_type = self.request.GET.get('type')
        if opponent_type:
            queryset = queryset.filter(type=opponent_type)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(phone__icontains=search) |
                Q(id_number__icontains=search) |
                Q(opponent_lawyer__icontains=search)
            )
        
        return queryset.order_by('-id')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_opponents'] = Opponent.objects.count()
        context['individual_opponents'] = Opponent.objects.filter(type='individual').count()
        context['company_opponents'] = Opponent.objects.filter(type='company').count()
        context['government_opponents'] = Opponent.objects.filter(type='government').count()
        return context


class OpponentCreateView(LoginRequiredMixin, CreateView):
    model = Opponent
    fields = ['name', 'type', 'id_number', 'phone', 'opponent_lawyer']
    template_name = 'core/opponent_form.html'
    success_url = reverse_lazy('core:opponents')


class OpponentDetailView(LoginRequiredMixin, DetailView):
    model = Opponent
    template_name = 'core/opponent_detail.html'
    context_object_name = 'opponent'


class OpponentUpdateView(LoginRequiredMixin, UpdateView):
    model = Opponent
    fields = ['name', 'type', 'id_number', 'phone', 'opponent_lawyer']
    template_name = 'core/opponent_form.html'
    success_url = reverse_lazy('core:opponents')


class OpponentDeleteView(LoginRequiredMixin, DeleteView):
    model = Opponent
    template_name = 'core/opponent_confirm_delete.html'
    success_url = reverse_lazy('core:opponents')


# ========================================
# Sessions Views
# ========================================
class SessionListView(LoginRequiredMixin, ListView):
    model = Session
    template_name = 'core/sessions.html'
    context_object_name = 'sessions'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Session.objects.all().select_related('case', 'case__client')
        
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        session_type = self.request.GET.get('session_type')
        if session_type:
            queryset = queryset.filter(session_type=session_type)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(case__case_number__icontains=search) |
                Q(case__subject__icontains=search) |
                Q(court__icontains=search)
            )
        
        return queryset.order_by('date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_sessions'] = Session.objects.count()
        context['todays_sessions'] = Session.objects.filter(date=timezone.now().date()).count()
        context['upcoming_sessions'] = Session.objects.filter(
            date__gt=timezone.now().date(),
            status='scheduled'
        ).count()
        context['completed_sessions'] = Session.objects.filter(status='completed').count()
        return context


class SessionCreateView(LoginRequiredMixin, CreateView):
    model = Session
    fields = ['case', 'date', 'time', 'session_type', 'court', 'notes', 'status']
    template_name = 'core/session_form.html'
    success_url = reverse_lazy('core:sessions')


class SessionDetailView(LoginRequiredMixin, DetailView):
    model = Session
    template_name = 'core/session_detail.html'
    context_object_name = 'session'


class SessionUpdateView(LoginRequiredMixin, UpdateView):
    model = Session
    fields = ['case', 'date', 'time', 'session_type', 'court', 'notes', 'status']
    template_name = 'core/session_form.html'
    success_url = reverse_lazy('core:sessions')


class SessionDeleteView(LoginRequiredMixin, DeleteView):
    model = Session
    template_name = 'core/session_confirm_delete.html'
    success_url = reverse_lazy('core:sessions')


# ========================================
# Documents Views
# ========================================
class DocumentListView(LoginRequiredMixin, ListView):
    model = Document
    template_name = 'core/documents.html'
    context_object_name = 'documents'


class DocumentCreateView(LoginRequiredMixin, CreateView):
    model = Document
    fields = '__all__'
    template_name = 'core/document_form.html'
    success_url = reverse_lazy('core:documents')


# ========================================
# Finance Views
# ========================================
class FinanceDashboardView(LoginRequiredMixin, ListView):
    model = Fee
    template_name = 'core/finance.html'
    context_object_name = 'recent_fees'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Fee.objects.all().select_related('case', 'case__client')
        
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        fee_type = self.request.GET.get('fee_type')
        if fee_type:
            queryset = queryset.filter(fee_type=fee_type)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(case__case_number__icontains=search) |
                Q(case__subject__icontains=search) |
                Q(case__client__full_name__icontains=search)
            )
        
        return queryset.order_by('-id')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_fees'] = Fee.objects.aggregate(total=Sum('agreed_amount'))['total'] or 0
        context['total_collected'] = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0
        context['total_expenses'] = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0
        context['net_profit'] = context['total_collected'] - context['total_expenses']
        context['total_invoices'] = Invoice.objects.count()
        context['paid_invoices'] = Invoice.objects.filter(status='paid').count()
        context['pending_invoices'] = Invoice.objects.filter(status='pending').count()
        context['expenses_by_category'] = Expense.objects.values('category').annotate(
            total=Sum('amount')
        ).order_by('-total')[:5]
        return context


class FeeListView(LoginRequiredMixin, ListView):
    model = Fee
    template_name = 'core/fees.html'
    context_object_name = 'fees'
    paginate_by = 10


class ExpenseListView(LoginRequiredMixin, ListView):
    model = Expense
    template_name = 'core/expenses.html'
    context_object_name = 'expenses'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Expense.objects.all().select_related('case')
        
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        case_id = self.request.GET.get('case')
        if case_id:
            queryset = queryset.filter(case_id=case_id)
        
        start_date = self.request.GET.get('start_date')
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        
        end_date = self.request.GET.get('end_date')
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset.order_by('-date', '-id')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_expenses'] = Expense.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        context['month_expenses'] = Expense.objects.filter(
            date__month=timezone.now().month,
            date__year=timezone.now().year
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        context['case_expenses'] = Expense.objects.filter(case__isnull=False).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        context['admin_expenses'] = Expense.objects.filter(case__isnull=True).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        context['cases'] = Case.objects.all().order_by('-id')
        context['expense_categories'] = ExpenseCategory.choices
        return context


class FeeCreateView(LoginRequiredMixin, CreateView):
    model = Fee
    fields = ['case', 'fee_type', 'agreed_amount', 'status']
    template_name = 'core/fee_form.html'
    success_url = reverse_lazy('core:finance')


class ExpenseCreateView(LoginRequiredMixin, CreateView):
    model = Expense
    fields = ['description', 'category', 'amount', 'case']
    template_name = 'core/expense_form.html'
    success_url = reverse_lazy('core:finance')


# ========================================
# Tasks Views
# ========================================
class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'core/tasks.html'
    context_object_name = 'tasks'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Task.objects.all().select_related('case', 'assigned_to')
        
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        assigned_to = self.request.GET.get('assigned_to')
        if assigned_to:
            queryset = queryset.filter(assigned_to_id=assigned_to)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(case__case_number__icontains=search)
            )
        
        return queryset.order_by('-id')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_tasks'] = Task.objects.count()
        context['new_tasks'] = Task.objects.filter(status='new').count()
        context['in_progress_tasks'] = Task.objects.filter(status='in_progress').count()
        context['done_tasks'] = Task.objects.filter(status='done').count()
        context['overdue_tasks'] = Task.objects.filter(
            status__in=['new', 'in_progress'],
            due_date__lt=timezone.now().date()
        ).count()
        return context


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description', 'case', 'assigned_to', 'status', 'priority', 'due_date']
    template_name = 'core/task_form.html'
    success_url = reverse_lazy('core:tasks')


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'core/task_detail.html'
    context_object_name = 'task'


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description', 'case', 'assigned_to', 'status', 'priority', 'due_date']
    template_name = 'core/task_form.html'
    success_url = reverse_lazy('core:tasks')


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'core/task_confirm_delete.html'
    success_url = reverse_lazy('core:tasks')


# ========================================
# Invoices Views
# ========================================
class InvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = 'core/invoices.html'
    context_object_name = 'invoices'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Invoice.objects.all().select_related('client')
        
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(invoice_number__icontains=search) |
                Q(client__full_name__icontains=search)
            )
        
        return queryset.order_by('-id')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_invoices'] = Invoice.objects.count()
        context['paid_invoices'] = Invoice.objects.filter(status='paid').count()
        context['pending_invoices'] = Invoice.objects.filter(status='pending').count()
        context['cancelled_invoices'] = Invoice.objects.filter(status='cancelled').count()
        context['total_amount'] = Invoice.objects.filter(status='paid').aggregate(total=Sum('total'))['total'] or 0
        context['pending_amount'] = Invoice.objects.filter(status='pending').aggregate(total=Sum('total'))['total'] or 0
        return context


class InvoiceCreateView(LoginRequiredMixin, CreateView):
    model = Invoice
    fields = ['invoice_number', 'client', 'subtotal', 'tax_rate', 'status', 'notes']
    template_name = 'core/invoice_form.html'
    success_url = reverse_lazy('core:invoices')


class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    template_name = 'core/invoice_detail.html'
    context_object_name = 'invoice'


class InvoiceUpdateView(LoginRequiredMixin, UpdateView):
    model = Invoice
    fields = ['invoice_number', 'client', 'subtotal', 'tax_rate', 'status', 'notes']
    template_name = 'core/invoice_form.html'
    success_url = reverse_lazy('core:invoices')


class InvoiceDeleteView(LoginRequiredMixin, DeleteView):
    model = Invoice
    template_name = 'core/invoice_confirm_delete.html'
    success_url = reverse_lazy('core:invoices')


# ========================================
# Appointments Views
# ========================================
class AppointmentListView(LoginRequiredMixin, ListView):
    model = Appointment
    template_name = 'core/appointments.html'
    context_object_name = 'appointments'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Appointment.objects.all().select_related('client')
        
        apt_type = self.request.GET.get('type')
        if apt_type:
            queryset = queryset.filter(type=apt_type)
        
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(client__full_name__icontains=search) |
                Q(case__case_number__icontains=search) |
                Q(location__icontains=search)
            )
        
        return queryset.order_by('-datetime')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_appointments'] = Appointment.objects.count()
        context['today_appointments'] = Appointment.objects.filter(datetime__date=timezone.now().date()).count()
        context['upcoming_appointments'] = Appointment.objects.filter(
            datetime__gt=timezone.now(),
            status='scheduled'
        ).count()
        context['completed_appointments'] = Appointment.objects.filter(status='completed').count()
        return context


class AppointmentCreateView(LoginRequiredMixin, CreateView):
    model = Appointment
    fields = ['type', 'client', 'case', 'datetime', 'location', 'notes', 'status']
    template_name = 'core/appointment_form.html'
    success_url = reverse_lazy('core:appointments')


class AppointmentDetailView(LoginRequiredMixin, DetailView):
    model = Appointment
    template_name = 'core/appointment_detail.html'
    context_object_name = 'appointment'


class AppointmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Appointment
    fields = ['type', 'client', 'case', 'datetime', 'location', 'notes', 'status']
    template_name = 'core/appointment_form.html'
    success_url = reverse_lazy('core:appointments')


class AppointmentDeleteView(LoginRequiredMixin, DeleteView):
    model = Appointment
    template_name = 'core/appointment_confirm_delete.html'
    success_url = reverse_lazy('core:appointments')


class CalendarView(LoginRequiredMixin, TemplateView):
    template_name = 'core/calendar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['appointments'] = Appointment.objects.filter(
            datetime__month=timezone.now().month,
            datetime__year=timezone.now().year
        )
        context['sessions'] = Session.objects.filter(
            date__month=timezone.now().month,
            date__year=timezone.now().year
        )
        return context


# ========================================
# Contracts Views
# ========================================
class ContractListView(LoginRequiredMixin, ListView):
    model = Contract
    template_name = 'core/contracts.html'
    context_object_name = 'contracts'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Contract.objects.all().select_related('client')
        
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        contract_type = self.request.GET.get('type')
        if contract_type:
            queryset = queryset.filter(type=contract_type)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(contract_number__icontains=search) |
                Q(client__full_name__icontains=search)
            )
        
        return queryset.order_by('-id')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_contracts'] = Contract.objects.count()
        context['active_contracts'] = Contract.objects.filter(status='active').count()
        context['expired_contracts'] = Contract.objects.filter(status='expired').count()
        context['expiring_soon'] = Contract.objects.filter(
            status='active',
            end_date__lte=timezone.now().date() + timedelta(days=30)
        ).count()
        return context


class ContractCreateView(LoginRequiredMixin, CreateView):
    model = Contract
    fields = ['contract_number', 'client', 'type', 'value', 'start_date', 'end_date', 'status', 'notes']
    template_name = 'core/contract_form.html'
    success_url = reverse_lazy('core:contracts')


class ContractDetailView(LoginRequiredMixin, DetailView):
    model = Contract
    template_name = 'core/contract_detail.html'
    context_object_name = 'contract'


class ContractUpdateView(LoginRequiredMixin, UpdateView):
    model = Contract
    fields = ['contract_number', 'client', 'type', 'value', 'start_date', 'end_date', 'status', 'notes']
    template_name = 'core/contract_form.html'
    success_url = reverse_lazy('core:contracts')


class ContractDeleteView(LoginRequiredMixin, DeleteView):
    model = Contract
    template_name = 'core/contract_confirm_delete.html'
    success_url = reverse_lazy('core:contracts')


# ========================================
# Power of Attorney Views
# ========================================
class PowerOfAttorneyListView(LoginRequiredMixin, ListView):
    model = PowerOfAttorney
    template_name = 'core/power_of_attorney.html'
    context_object_name = 'poas'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = PowerOfAttorney.objects.all().select_related('client')
        
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(client__full_name__icontains=search) |
                Q(issuer__icontains=search)
            )
        
        return queryset.order_by('-id')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_poas'] = PowerOfAttorney.objects.count()
        context['active_poas'] = PowerOfAttorney.objects.filter(status='active').count()
        context['expired_poas'] = PowerOfAttorney.objects.filter(status='expired').count()
        return context


class PowerOfAttorneyCreateView(LoginRequiredMixin, CreateView):
    model = PowerOfAttorney
    fields = ['client', 'type', 'issue_date', 'expiry_date', 'issuer', 'status', 'notes']
    template_name = 'core/poa_form.html'
    success_url = reverse_lazy('core:power_of_attorney')


class PowerOfAttorneyDetailView(LoginRequiredMixin, DetailView):
    model = PowerOfAttorney
    template_name = 'core/poa_detail.html'
    context_object_name = 'poa'


class PowerOfAttorneyUpdateView(LoginRequiredMixin, UpdateView):
    model = PowerOfAttorney
    fields = ['client', 'type', 'issue_date', 'expiry_date', 'issuer', 'status', 'notes']
    template_name = 'core/poa_form.html'
    success_url = reverse_lazy('core:power_of_attorney')


class PowerOfAttorneyDeleteView(LoginRequiredMixin, DeleteView):
    model = PowerOfAttorney
    template_name = 'core/poa_confirm_delete.html'
    success_url = reverse_lazy('core:power_of_attorney')


# ========================================
# Consultations & Declarations Views
# ========================================
class ConsultationListView(LoginRequiredMixin, ListView):
    model = Consultation
    template_name = 'core/consultations.html'
    context_object_name = 'consultations'


class DeclarationListView(LoginRequiredMixin, ListView):
    model = Declaration
    template_name = 'core/declarations.html'
    context_object_name = 'declarations'


class DeclarationCreateView(LoginRequiredMixin, CreateView):
    model = Declaration
    fields = '__all__'
    template_name = 'core/declaration_form.html'
    success_url = reverse_lazy('core:declarations')


# ========================================
# Notifications Views
# ========================================
class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'core/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 20
    
    def get_queryset(self):
        return Notification.objects.all().order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unread_count'] = Notification.objects.filter(is_read=False).count()
        return context


# ========================================
# Reports Views
# ========================================
class ReportsView(LoginRequiredMixin, TemplateView):
    template_name = 'core/reports.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # إحصائيات القضايا
        context['total_cases'] = Case.objects.count()
        context['active_cases'] = Case.objects.filter(status='active').count()
        context['won_cases'] = Case.objects.filter(status='won').count()
        context['lost_cases'] = Case.objects.filter(status='lost').count()
        context['pending_cases'] = Case.objects.filter(status='pending').count()
        context['closed_cases'] = Case.objects.filter(status='closed').count()
        
        # إحصائيات العملاء
        context['total_clients'] = Client.objects.count()
        context['individual_clients'] = Client.objects.filter(type='individual').count()
        context['company_clients'] = Client.objects.filter(type='company').count()
        
        # إحصائيات مالية
        context['total_fees'] = Fee.objects.aggregate(total=Sum('agreed_amount'))['total'] or 0
        context['total_collected'] = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0
        context['total_expenses'] = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0
        context['net_profit'] = context['total_collected'] - context['total_expenses']
        
        # إحصائيات الفواتير
        context['total_invoices'] = Invoice.objects.count()
        context['paid_invoices'] = Invoice.objects.filter(status='paid').count()
        context['pending_invoices'] = Invoice.objects.filter(status='pending').count()
        
        # إحصائيات المهام
        context['total_tasks'] = Task.objects.count()
        context['completed_tasks'] = Task.objects.filter(status='done').count()
        context['pending_tasks'] = Task.objects.filter(status__in=['new', 'in_progress']).count()
        
        # إحصائيات المواعيد
        context['total_appointments'] = Appointment.objects.count()
        context['completed_appointments'] = Appointment.objects.filter(status='completed').count()
        context['upcoming_appointments'] = Appointment.objects.filter(
            datetime__gt=timezone.now(),
            status='scheduled'
        ).count()
        
        # إحصائيات العقود
        context['total_contracts'] = Contract.objects.count()
        context['active_contracts'] = Contract.objects.filter(status='active').count()
        context['expiring_contracts'] = Contract.objects.filter(
            status='active',
            end_date__lte=timezone.now().date() + timedelta(days=30)
        ).count()
        
        # القضايا حسب النوع
        context['cases_by_type'] = Case.objects.values('case_type').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        # المصروفات حسب الفئة
        context['expenses_by_category'] = Expense.objects.values('category').annotate(
            total=Sum('amount')
        ).order_by('-total')[:5]
        
        return context


# ========================================
# Settings Views
# ========================================
class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'core/settings.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        default_path = Path(settings.BASE_DIR) / 'media_files' / 'backups'
        context.update({
            'backup_default_path': default_path,
            'office_profile': OfficeProfile.objects.first(),
            'total_users': User.objects.count(),
            'total_cases': Case.objects.count(),
            'total_clients': Client.objects.count(),
            'total_invoices': Invoice.objects.count(),
            'total_tasks': Task.objects.count(),
        })
        return context
    
    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        backup_path = request.POST.get('backup_path') or ''
        target_dir = Path(backup_path) if backup_path else Path(settings.BASE_DIR) / 'media_files' / 'backups'
        target_dir.mkdir(parents=True, exist_ok=True)
        
        db_file = Path(settings.BASE_DIR) / 'db.sqlite3'
        
        if action == 'backup':
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            backup_file = target_dir / f'backup_{timestamp}.sqlite3'
            try:
                shutil.copy2(db_file, backup_file)
                messages.success(request, f'تم إنشاء النسخة الاحتياطية في: {backup_file}')
            except Exception as exc:
                messages.error(request, f'تعذر إنشاء النسخة الاحتياطية: {exc}')
        
        elif action == 'restore':
            upload = request.FILES.get('backup_file')
            if not upload:
                messages.error(request, 'يرجى اختيار ملف نسخة احتياطية للاستعادة.')
                return redirect('core:settings')
            
            restore_temp = target_dir / f'restore_{timezone.now().strftime("%Y%m%d_%H%M%S")}.sqlite3'
            try:
                with open(restore_temp, 'wb+') as dest:
                    for chunk in upload.chunks():
                        dest.write(chunk)
                shutil.copy2(restore_temp, db_file)
                messages.success(request, f'تم الاستعادة من النسخة: {restore_temp}')
            except Exception as exc:
                messages.error(request, f'تعذر الاستعادة: {exc}')
        
        return redirect('core:settings')