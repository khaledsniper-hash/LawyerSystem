# core/management/commands/seed_data.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import (
    User, Client, Opponent, Case, Session, Document,
    Fee, Payment, Invoice, Expense, Consultation,
    Task, Appointment, Contract, PowerOfAttorney, Declaration,
    Notification, OfficeProfile
)


class Command(BaseCommand):
    help = 'تعبئة قاعدة البيانات ببيانات تجريبية'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('=== بدء تعبئة البيانات التجريبية ==='))
        
        self.get_or_createadmin_user()
        self.get_or_createoffice_profile()
        clients = self.get_or_createclients()
        opponents = self.get_or_createopponents()
        cases = self.get_or_createcases(clients, opponents)
        self.get_or_createsessions(cases)
        self.get_or_createtasks(cases)
        self.get_or_createappointments(clients)
        self.get_or_createfees_and_payments(cases)
        self.get_or_createinvoices(clients)
        self.get_or_createexpenses(cases)
        self.get_or_createcontracts_and_poa(clients)
        self.get_or_createdocuments(cases)
        self.get_or_createnotifications()
        
        self.stdout.write(self.style.SUCCESS('=== اكتملت تعبئة البيانات بنجاح! ==='))

    def get_or_createadmin_user(self):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@mezan.com',
                password='admin123',
                first_name='مدير',
                last_name='النظام',
                role='admin',
                bar_number='12345',
                specialization='جميع التخصصات'
            )
            self.stdout.write(self.style.SUCCESS('✓ تم إنشاء حساب المدير: admin / admin123'))
        else:
            self.stdout.write(self.style.WARNING('⚠ حساب المدير موجود مسبقاً'))

    def get_or_createoffice_profile(self):
        if not OfficeProfile.objects.exists():
            OfficeProfile.objects.create(
                tax_id='310000000000003',
                phone='0223456789',
                email='info@mezan-eg.com',
                commercial_registration='1010000000',
                license_number='12345',
                currency='EGP',
                address='جمهورية مصر العربية - القاهرة'
            )
            self.stdout.write(self.style.SUCCESS('✓ تم إنشاء بيانات المكتب (مصر)'))
        else:
            self.stdout.write(self.style.WARNING('⚠ بيانات المكتب موجودة مسبقاً'))

    def get_or_createclients(self):
        clients_data = [
            {'client_id': 'CLT-00001', 'full_name': 'شركة الفجر للتجارة', 'type': 'company', 'phone': '01001111111', 'email': 'info@alfajr.com'},
            {'client_id': 'CLT-00002', 'full_name': 'عبدالله محمد العتيبي', 'type': 'individual', 'phone': '01002222222', 'email': 'abdullah@gmail.com'},
            {'client_id': 'CLT-00003', 'full_name': 'مؤسسة النور للمقاولات', 'type': 'company', 'phone': '01003333333', 'email': 'noor@construction.com'},
            {'client_id': 'CLT-00004', 'full_name': 'فهد سعود الشمري', 'type': 'individual', 'phone': '01004444444', 'email': 'fahad.sh@outlook.com'},
            {'client_id': 'CLT-00005', 'full_name': 'سارة أحمد القحطاني', 'type': 'individual', 'phone': '01005555555', 'email': 'sara@gmail.com'},
            {'client_id': 'CLT-00006', 'full_name': 'خالد عبدالرحمن الدوسري', 'type': 'individual', 'phone': '01006666666', 'email': 'khaled@gmail.com'},
            {'client_id': 'CLT-00007', 'full_name': 'شركة الأمل العقارية', 'type': 'company', 'phone': '01007777777', 'email': 'amal@realestate.com'},
            {'client_id': 'CLT-00008', 'full_name': 'شركة البناء الحديث', 'type': 'company', 'phone': '01008888888', 'email': 'building@construction.com'},
            {'client_id': 'CLT-00009', 'full_name': 'نورة محمد السبيعي', 'type': 'individual', 'phone': '01009999999', 'email': 'nora@gmail.com'},
            {'client_id': 'CLT-00010', 'full_name': 'مصنع الخليج للبلاستيك', 'type': 'company', 'phone': '01001010101', 'email': 'gulf@plastic.com'},
            {'client_id': 'CLT-00021', 'full_name': 'محمد رجب', 'type': 'individual', 'phone': '01006890323', 'email': ''},
            {'client_id': 'CLT-00022', 'full_name': 'محمد احمد', 'type': 'individual', 'phone': '01068905698', 'email': ''},
            {'client_id': 'CLT-00023', 'full_name': 'عاطف عبد الوهاب', 'type': 'individual', 'phone': '01251852458', 'email': ''},
            {'client_id': 'CLT-00025', 'full_name': 'محمد عاطف سليم', 'type': 'individual', 'phone': '01067504078', 'email': ''},
            {'client_id': 'CLT-00026', 'full_name': 'أحمد العتيبي', 'type': 'individual', 'phone': '01254', 'email': 'admin@app.com'},
            {'client_id': 'CLT-00027', 'full_name': 'محمد سلامه عطا', 'type': 'individual', 'phone': '01005560930', 'email': 'aliqenawy10@gmail.com'},
        ]
        
        clients = []
        for data in clients_data:
            client, created = Client.objects.get_or_create(
                client_id=data['client_id'],
                defaults={
                    'full_name': data['full_name'],
                    'type': data['type'],
                    'phone': data['phone'],
                    'email': data['email'],
                    'status': 'active'
                }
            )
            if created:
                clients.append(client)
        
        self.stdout.write(self.style.SUCCESS(f'✓ تم إنشاء {len(clients)} عملاء'))
        return clients

    def get_or_createopponents(self):
        opponents_data = [
            {'name': 'شركة السعيد', 'type': 'company', 'id_number': '-', 'phone': '01652482668', 'opponent_lawyer': 'ادهم'},
            {'name': 'مؤسسة المنارة للمقاولات', 'type': 'entity', 'id_number': '1234567', 'phone': '011474753', 'opponent_lawyer': 'فهد'},
        ]
        
        opponents = []
        for data in opponents_data:
            opponent, created = Opponent.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            if created:
                opponents.append(opponent)
        
        self.stdout.write(self.style.SUCCESS(f'✓ تم إنشاء {len(opponents)} خصوم'))
        return opponents

    def get_or_createcases(self, clients, opponents):
        cases_data = [
            {'case_number': '8555', 'subject': 'علاوات', 'client': 'CLT-00025', 'court': 'محكمة الإسكندرية الابتدائية', 'case_type': 'عمالي', 'status': 'pending', 'priority': 'normal'},
            {'case_number': '25530', 'subject': 'قضية جنائية', 'client': 'CLT-00001', 'court': 'محكمة استئناف القاهرة', 'case_type': 'جنائي', 'status': 'active', 'priority': 'normal'},
            {'case_number': '123/5687', 'subject': 'دعوة ضد شركة عقارية', 'client': 'CLT-00002', 'court': 'المحكمة الدستورية العليا', 'case_type': 'تجاري', 'status': 'active', 'priority': 'normal'},
            {'case_number': '123/456', 'subject': 'دعوة ضد مواطن', 'client': 'CLT-00001', 'court': 'المحكمة الاقتصادية', 'case_type': 'أحوال شخصية', 'status': 'active', 'priority': 'normal'},
            {'case_number': '12345', 'subject': 'مطالبة بمبلغ 500,000 جنيه', 'client': 'CLT-00001', 'court': 'محكمة جنوب القاهرة الابتدائية', 'case_type': 'مدني', 'status': 'active', 'priority': 'high'},
            {'case_number': '23456', 'subject': 'اعتراض على قرار رفض تمويل', 'client': 'CLT-00002', 'court': 'محكمة الإسكندرية الابتدائية', 'case_type': 'أحوال شخصية', 'status': 'active', 'priority': 'normal'},
            {'case_number': '34567', 'subject': 'دعوى نفقة وحضانة', 'client': 'CLT-00005', 'court': 'محكمة الجيزة الابتدائية', 'case_type': 'أحوال شخصية', 'status': 'active', 'priority': 'urgent'},
            {'case_number': '45678', 'subject': 'دعوى جنائية - تزوير', 'client': 'CLT-00006', 'court': 'محكمة شمال القاهرة الابتدائية', 'case_type': 'جنائي', 'status': 'pending', 'priority': 'urgent'},
            {'case_number': '56789', 'subject': 'دعوى فصل تعسفي', 'client': 'CLT-00003', 'court': 'محكمة استئناف القاهرة', 'case_type': 'عمالي', 'status': 'active', 'priority': 'normal'},
            {'case_number': '67890', 'subject': 'نزاع على ملكية عقار', 'client': 'CLT-00007', 'court': 'محكمة جنوب القاهرة الابتدائية', 'case_type': 'مدني', 'status': 'active', 'priority': 'high'},
            {'case_number': '78901', 'subject': 'مطالبة بمستحقات مقاولة', 'client': 'CLT-00008', 'court': 'المحكمة الدستورية العليا', 'case_type': 'مدني', 'status': 'active', 'priority': 'normal'},
            {'case_number': '89012', 'subject': 'نزاع تجاري على عقد', 'client': 'CLT-00001', 'court': 'محكمة القضاء الإداري', 'case_type': 'تجاري', 'status': 'pending', 'priority': 'low'},
            {'case_number': '90123', 'subject': 'تنفيذ حكم 200,000 جنيه', 'client': 'CLT-00001', 'court': 'محكمة استئناف الإسكندرية', 'case_type': 'تنفيذ', 'status': 'active', 'priority': 'high'},
            {'case_number': '11111', 'subject': 'دعوى طلاق وحقوق', 'client': 'CLT-00009', 'court': 'محكمة الجيزة الابتدائية', 'case_type': 'أحوال شخصية', 'status': 'closed', 'priority': 'normal'},
            {'case_number': '22222', 'subject': 'مطالبة بأجور متأخرة', 'client': 'CLT-00010', 'court': 'محكمة استئناف القاهرة', 'case_type': 'عمالي', 'status': 'won', 'priority': 'low'},
        ]
        
        cases = []
        for data in cases_data:
            client = Client.objects.get(client_id=data.pop('client'))
            case, created = Case.objects.get_or_create(
                case_number=data['case_number'],
                defaults={
                    **data,
                    'client': client,
                    'position': 'plaintiff',
                    'created_at': timezone.now() - timedelta(days=30)
                }
            )
            if created:
                cases.append(case)
        
        self.stdout.write(self.style.SUCCESS(f'✓ تم إنشاء {len(cases)} قضايا'))
        return cases

    def get_or_createsessions(self, cases):
        sessions_data = [
            {'case': '8555', 'date': timezone.now() + timedelta(days=1), 'session_type': 'جلسة عادية', 'status': 'scheduled'},
            {'case': '12345', 'date': timezone.now() + timedelta(days=3), 'session_type': 'جلسة استماع', 'status': 'scheduled'},
            {'case': '34567', 'date': timezone.now() + timedelta(days=5), 'session_type': 'جلسة عاجلة', 'status': 'scheduled'},
        ]
        
        count = 0
        for data in sessions_data:
            case = Case.objects.get(case_number=data.pop('case'))
            Session.objects.get_or_create(
                case=case,
                date=data['date'],
                defaults=data
            )
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ تم إنشاء {count} جلسات'))

    def get_or_createtasks(self, cases):
        tasks_data = [
            {'title': 'مراجعة مستندات القضية 8555', 'status': 'new', 'priority': 'high'},
            {'title': 'إعداد مذكرة دفاع', 'status': 'in_progress', 'priority': 'urgent'},
            {'title': 'التواصل مع الشهود', 'status': 'new', 'priority': 'normal'},
            {'title': 'مراجعة العقد', 'status': 'done', 'priority': 'normal'},
        ]
        
        count = 0
        for data in tasks_data:
            Task.objects.create(
                assigned_to=User.objects.first(),
                due_date=timezone.now() + timedelta(days=7),
                **data
            )
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ تم إنشاء {count} مهام'))

    def get_or_createappointments(self, clients):
        appointments_data = [
            {'type': 'meeting', 'client': 'CLT-00001', 'location': 'المكتب'},
            {'type': 'consultation', 'client': 'CLT-00002', 'location': 'المكتب'},
            {'type': 'call', 'client': 'CLT-00005', 'location': 'هاتفي'},
        ]
        
        count = 0
        for data in appointments_data:
            client = Client.objects.get(client_id=data.pop('client'))
            Appointment.objects.create(
                status='scheduled',
                datetime=timezone.now() + timedelta(days=1),
                client=client,
                **data
            )
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ تم إنشاء {count} مواعيد'))

    def get_or_createfees_and_payments(self, cases):
        fees_data = [
            {'case': '8555', 'fee_type': 'fixed', 'agreed_amount': 15000, 'status': 'partial'},
            {'case': '12345', 'fee_type': 'fixed', 'agreed_amount': 50000, 'status': 'partial'},
            {'case': '34567', 'fee_type': 'fixed', 'agreed_amount': 25000, 'status': 'paid'},
            {'case': '45678', 'fee_type': 'fixed', 'agreed_amount': 35000, 'status': 'pending'},
            {'case': '67890', 'fee_type': 'hourly', 'agreed_amount': 40000, 'status': 'partial'},
        ]
        
        count = 0
        for data in fees_data:
            case = Case.objects.get(case_number=data.pop('case'))
            fee = Fee.objects.create(case=case, **data)
            Payment.objects.create(
                fee=fee,
                amount=data['agreed_amount'] * 0.3,
                payment_method='transfer',
                date=timezone.now()
            )
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ تم إنشاء {count} أتعاب ودفعات'))

    def get_or_createinvoices(self, clients):
        """إنشاء الفواتير"""
        invoices_data = [
            {'client': 'CLT-00001', 'subtotal': 15000, 'tax_rate': 14, 'status': 'paid'},
            {'client': 'CLT-00002', 'subtotal': 10000, 'tax_rate': 14, 'status': 'pending'},
        ]
        
        count = 0
        for i, data in enumerate(invoices_data, 1):
            client = Client.objects.get(client_id=data.pop('client'))
            invoice, created = Invoice.objects.get_or_create(
                invoice_number=f'INV-2026-{i:03d}',
                defaults={
                    'client': client,
                    'date': timezone.now(),
                    **data
                }
            )
            if created:
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ تم إنشاء {count} فواتير'))

    def get_or_createexpenses(self, cases):
        """إنشاء المصروفات"""
        expenses_data = [
            {'description': 'رسوم محكمة', 'category': 'court_fees', 'amount': 500, 'case_number': '8555'},
            {'description': 'مواصلات', 'category': 'transport', 'amount': 200},
            {'description': 'طباعة مستندات', 'category': 'documents', 'amount': 150, 'case_number': '12345'},
            {'description': 'أتعاب خبير', 'category': 'other', 'amount': 3000, 'case_number': '34567'},
            {'description': 'إيجار المكتب', 'category': 'utilities', 'amount': 2000},
        ]
        
        count = 0
        for data in expenses_data:
            case_obj = None
            case_number = data.pop('case_number', None)
            if case_number:
                case_obj = Case.objects.get(case_number=case_number)
            Expense.objects.create(
                date=timezone.now(),
                case=case_obj,
                **data
            )
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ تم إنشاء {count} مصروفات'))

    def get_or_createcontracts_and_poa(self, clients):
        contracts_data = [
            {'client': 'CLT-00001', 'type': 'توكيل عام', 'value': 2500, 'status': 'active'},
            {'client': 'CLT-00002', 'type': 'عقد استشارة', 'value': 2500, 'status': 'active'},
        ]
        
        for i, data in enumerate(contracts_data, 1):
            client = Client.objects.get(client_id=data.pop('client'))
            Contract.objects.create(
                contract_number=f'CNT-2026-{i:03d}',
                start_date=timezone.now().date(),
                end_date=(timezone.now() + timedelta(days=365)).date(),
                client=client,
                **data
            )
        
        PowerOfAttorney.objects.create(
            client=Client.objects.get(client_id='CLT-00001'),
            type='general',
            issue_date=timezone.now().date(),
            expiry_date=(timezone.now() + timedelta(days=365)).date(),
            issuer='المحكمة العامة',
            status='active'
        )
        
        self.stdout.write(self.style.SUCCESS('✓ تم إنشاء العقود والتوكيلات'))

    def get_or_createdocuments(self, cases):
        count = 0
        for case in cases[:5]:
            Document.objects.create(
                case=case,
                doc_type='contract',
                security_level='normal',
                uploaded_at=timezone.now()
            )
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ تم إنشاء {count} سجلات مستندات'))

    def get_or_createnotifications(self):
        user = User.objects.first()
        
        notifications_data = [
            {'message': 'جلسة قادمة للقضية 8555 غداً', 'notification_type': 'session'},
            {'message': 'فاتورة جديدة بانتظار السداد', 'notification_type': 'payment'},
            {'message': 'مهمة جديدة مكلفة بها', 'notification_type': 'task'},
            {'message': 'عقد ينتهي خلال 30 يوم', 'notification_type': 'contract'},
        ]
        
        for data in notifications_data:
            Notification.objects.create(
                target_user=user,
                is_read=False,
                **data
            )
        
        self.stdout.write(self.style.SUCCESS(f'✓ تم إنشاء {len(notifications_data)} إشعارات'))