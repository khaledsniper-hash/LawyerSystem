from django.urls import path
from django.contrib.auth import views as auth_views
from core import views

app_name = 'core'

urlpatterns = [
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Cases
    path('cases/', views.CaseListView.as_view(), name='cases'),
    path('cases/create/', views.CaseCreateView.as_view(), name='case_create'),
    path('cases/<int:pk>/', views.CaseDetailView.as_view(), name='case_detail'),
    path('cases/<int:pk>/edit/', views.CaseUpdateView.as_view(), name='case_update'),
    path('cases/<int:pk>/delete/', views.CaseDeleteView.as_view(), name='case_delete'),
    
    # Clients
    path('clients/', views.ClientListView.as_view(), name='clients'),
    path('clients/create/', views.ClientCreateView.as_view(), name='client_create'),
    path('clients/<int:pk>/', views.ClientDetailView.as_view(), name='client_detail'),
    path('clients/<int:pk>/edit/', views.ClientUpdateView.as_view(), name='client_update'),
    path('clients/<int:pk>/delete/', views.ClientDeleteView.as_view(), name='client_delete'),
    
    # Opponents
    path('opponents/', views.OpponentListView.as_view(), name='opponents'),
    path('opponents/create/', views.OpponentCreateView.as_view(), name='opponent_create'),
    path('opponents/<int:pk>/', views.OpponentDetailView.as_view(), name='opponent_detail'),
    path('opponents/<int:pk>/edit/', views.OpponentUpdateView.as_view(), name='opponent_update'),
    path('opponents/<int:pk>/delete/', views.OpponentDeleteView.as_view(), name='opponent_delete'),
    
    # Sessions
    path('sessions/', views.SessionListView.as_view(), name='sessions'),
    path('sessions/create/', views.SessionCreateView.as_view(), name='session_create'),
    path('sessions/<int:pk>/', views.SessionDetailView.as_view(), name='session_detail'),
    path('sessions/<int:pk>/edit/', views.SessionUpdateView.as_view(), name='session_update'),
    path('sessions/<int:pk>/delete/', views.SessionDeleteView.as_view(), name='session_delete'),
    
    # Documents
    path('documents/', views.DocumentListView.as_view(), name='documents'),
    path('documents/upload/', views.DocumentCreateView.as_view(), name='document_upload'),
    
    # Finance
    path('finance/', views.FinanceDashboardView.as_view(), name='finance'),
    path('fees/', views.FeeListView.as_view(), name='fees'),
    path('fees/create/', views.FeeCreateView.as_view(), name='fee_create'),
    path('expenses/', views.ExpenseListView.as_view(), name='expenses'),
    path('expenses/create/', views.ExpenseCreateView.as_view(), name='expense_create'),
    path('invoices/', views.InvoiceListView.as_view(), name='invoices'),
    path('invoices/create/', views.InvoiceCreateView.as_view(), name='invoice_create'),
    path('invoices/<int:pk>/', views.InvoiceDetailView.as_view(), name='invoice_detail'),
    path('invoices/<int:pk>/edit/', views.InvoiceUpdateView.as_view(), name='invoice_update'),
    path('invoices/<int:pk>/delete/', views.InvoiceDeleteView.as_view(), name='invoice_delete'),
    
    # Tasks
    path('tasks/', views.TaskListView.as_view(), name='tasks'),
    path('tasks/create/', views.TaskCreateView.as_view(), name='task_create'),
    path('tasks/<int:pk>/', views.TaskDetailView.as_view(), name='task_detail'),
    path('tasks/<int:pk>/edit/', views.TaskUpdateView.as_view(), name='task_update'),
    path('tasks/<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task_delete'),
    
    # Appointments
    path('appointments/', views.AppointmentListView.as_view(), name='appointments'),
    path('appointments/create/', views.AppointmentCreateView.as_view(), name='appointment_create'),
    path('appointments/<int:pk>/', views.AppointmentDetailView.as_view(), name='appointment_detail'),
    path('appointments/<int:pk>/edit/', views.AppointmentUpdateView.as_view(), name='appointment_update'),
    path('appointments/<int:pk>/delete/', views.AppointmentDeleteView.as_view(), name='appointment_delete'),
    path('calendar/', views.CalendarView.as_view(), name='calendar'),
    
    # Contracts
    path('contracts/', views.ContractListView.as_view(), name='contracts'),
    path('contracts/create/', views.ContractCreateView.as_view(), name='contract_create'),
    path('contracts/<int:pk>/', views.ContractDetailView.as_view(), name='contract_detail'),
    path('contracts/<int:pk>/edit/', views.ContractUpdateView.as_view(), name='contract_update'),
    path('contracts/<int:pk>/delete/', views.ContractDeleteView.as_view(), name='contract_delete'),
    
    # Power of Attorney
    path('power-of-attorney/', views.PowerOfAttorneyListView.as_view(), name='power_of_attorney'),
    path('power-of-attorney/create/', views.PowerOfAttorneyCreateView.as_view(), name='poa_create'),
    path('power-of-attorney/<int:pk>/', views.PowerOfAttorneyDetailView.as_view(), name='poa_detail'),
    path('power-of-attorney/<int:pk>/edit/', views.PowerOfAttorneyUpdateView.as_view(), name='poa_update'),
    path('power-of-attorney/<int:pk>/delete/', views.PowerOfAttorneyDeleteView.as_view(), name='poa_delete'),
    
    # Reports & Settings
    path('reports/', views.ReportsView.as_view(), name='reports'),
    path('settings/', views.SettingsView.as_view(), name='settings'),
]