Master Specification Document: "Mizan Al_ِِAdala" System
Law Firm Management System - Technical Specification (English Version)
1. Project Overview

    Project Name: Mizan Al_ِِAdala (Mizan Al_ِِAdala).
    Description: A comprehensive web-based SaaS platform for managing law firms. It covers the entire lifecycle of a case from client intake to case closure, including financial management, task management, HR, contracts, and intelligent reporting.
    Vision: Not just an archive, but a business management system focusing on organization, security, financial accuracy, and workflow automation.
    Language: Arabic (Full RTL Interface Support).
    Recommended Stack: Python Django (for security and data management), PostgreSQL (Production) / SQLite (Dev), Bootstrap 5 (RTL) + Chart.js.
    File Storage: All system files (backups, uploads, exports) must be stored locally within a specific directory structure inside the project path.

2. Technology Stack

    Backend: Python 3.10+ , Django 4.2+ (LTS).
    Database: PostgreSQL (Preferred) or SQLite.
    Frontend: Django Templates, Bootstrap 5 (RTL Version), jQuery (for legacy compatibility if needed), Chart.js.
    File Handling: Django FileField / ImageField configured to save within the project's media/ directory.
    Task Queue: Celery + Redis (for scheduled notifications and backups).
    PDF Generation: WeasyPrint or ReportLab for invoices and contracts.

3. Database Schema (Models)
Build the following models with precise relationships:
A. Core & Authentication

    User: Extend AbstractUser. Fields: BarNumber, Specialization, ProfilePicture, IsActive.
    Role: (Admin, Lawyer, Secretary, Accountant).
    Client: FullName, Type (Individual/Company), Phone, Email, Status (Active/Inactive), ClientID (Unique, e.g., CLT-00027).
    Opponent: Name, Type (Individual/Company/Gov), IDNumber, Phone, OpponentLawyer.

B. Cases Module

    Case: CaseNumber (Unique), Subject, Client (FK), Opponents (M2M), Court (Choice), CaseType (Choice), Status (New/Active/Pending/Won/Lost/Closed), Priority (Urgent/High/Normal/Low), NextSessionDate, CreatedAt.
    Session: Case (FK), Date, Type, Minutes/Notes (Rich Text), Attachments. (Video Insight: Detailed session minutes are crucial).
    Document: File, Type, Case (FK), SecurityLevel (Normal/Confidential), UploadedAt.

C. Finance Module

    Fee: Case (FK), Type (Fixed/Hourly), AgreedAmount, Status.
    Payment: Amount, Date, Method, Fee (FK).
    Expense: Description, Category, Amount, Case (FK Optional), ReceiptImage, Date.
    Invoice: InvoiceNumber (e.g., INV-2026-001), Client (FK), Subtotal, TaxRate, Total, Status (Paid/Pending), Date.
    Consultation: (Video Insight: Specific system for consultations) Title, Client, Date, Notes (Documenting words), AmountCollected, Status.

D. Operations & Tasks

    Task: Title, Description, Status (Kanban: New/In Progress/Review/Done), Priority, AssignedTo (User FK), DueDate, Case (FK Optional). (Video Insight: Task distribution to employees).
    Appointment: Type (Meeting/Call/Visit), Client, Location, Time, Status.
    Contract: Number, Type, Client, Value, StartDate, EndDate, Status (Draft/Active/Expired), File.
    PowerOfAttorney: Client, Type, StartDate, EndDate, Status, File. (Video Insight: Renewal alerts).
    Declaration: Number, Type (e.g., Fee Receipt Acknowledgement), Client, Date, Status (Draft/Final).

E. System & Settings

    OfficeProfile: Logo, TaxID, Phone, Email, Address, Currency.
    Notification: Message, Type (Session/Finance/Task/Renewal), IsRead, TargetUser.
    LookupData: Dynamic lists for Courts, Case Types, Expense Categories.

4. File Management System (Critical Requirement)
The system must handle all file storage locally within the project directory structure. Do not use external cloud storage unless configured later.

    Base Path: All files must be saved relative to BASE_DIR (Django Project Root).
    Configuration: Configure MEDIA_ROOT in settings.py to point to a folder named media_files inside the project directory.
    Directory Structure:

/project_root/
├── MAIN.py
├── media_files/          <-- MAIN STORAGE FOLDER
│   ├── documents/        <-- Case documents, PDFs, Images
│   ├── contracts/        <-- Contract files
│   ├── invoices/         <-- Generated PDF Invoices
│   ├── backups/          <-- Database backups (SQL/Dump)
│   ├── exports/          <-- Excel/CSV reports
│   └── logos/            <-- Office logo
├── static/
└── templates/

    Functionality:
        Uploads: When uploading a document/contract, save it to media_files/documents/ or media_files/contracts/ organized by Year/Month or Case ID.
        Backups: A management command or view must generate a database dump and save it to media_files/backups/ with a timestamp.
        Exports: Reports exported to Excel/PDF must be saved temporarily in media_files/exports/ and provided as a download link.
        Security: Ensure direct access to sensitive files (like backups/) is restricted via .htaccess or Django views permissions.

5. Functional Requirements
1. Dashboard

    Live Stats: Active Cases, Today's Sessions, Pending Tasks, New Consultations.
    Charts: Case Distribution (Pie), Income vs. Expenses (Bar).
    Today's Table: Sessions and Appointments scheduled for today.
    Recent Activity: Last 5 updated cases.
    Quick Actions: Add Case, Add Client, Add Session, Add Task.

2. Case & Session Management

    Lifecycle: Track case from "New" to "Closed".
    Session Minutes: Rich text field to record detailed minutes for every session.
    Alerts: Auto-notification 24 hours before a session.
    Linking: Link documents, fees, and tasks to the specific case.

3. Finance & Consultations

    Consultations: Treat consultations as financial products (Track content + Fees).
    Tax: Auto-calculate tax in invoices based on OfficeSettings.
    Payment Tracking: Show (Agreed - Paid - Remaining) via Progress Bar.
    Expenses: Categorize expenses (Admin, Case, Utilities) and report on them.

4. Tasks & Employees

    Assignment: Tasks must be assigned to specific users (Lawyers/Staff).
    Kanban Board: Drag & Drop tasks between columns (New, In Progress, Done).
    Performance: Manager view to track employee completion rates.

5. Contracts & POA (Power of Attorney)

    Renewal Alerts: Smart notification system alerts 30 days before contracts/POA expire.
    Auto-Status: Change status to "Expired" automatically if end date passes.

6. Reports & Analytics

    Tools: Use Chart.js for visualizations.
    Types: Case Status, Financial Performance, Lawyer Performance.
    Export: Export reports to Excel/PDF (saved in media_files/exports/).

7. Security & Roles

    Permissions:
        Admin: Full Access.
        Lawyer: Access to assigned cases/tasks.
        Secretary: Clients & Appointments.
        Accountant: Finance Module Only.
    Data Protection: Login required for all pages. Password hashing enabled.

6. UI/UX Requirements

    Direction: RTL (Right-to-Left) is mandatory for Arabic support.
    Theme: Clean white background, vibrant Blue and Purple accents (as per video description).
    Responsiveness: Fully responsive on Mobile, Tablet, and Desktop.
    Sidebar: Fixed sidebar with main sections (Cases, Finance, HR, Tasks, Contracts, Reports, Settings).
    Forms: Clear validation, required fields marked, date pickers for sessions/appointments.

7. Business Logic & Automation

    Contract/POA Status: Auto-update to "Expired" if EndDate < Today.
    Invoice Status: Auto-update to "Paid" if TotalPaid >= TotalAmount.
    Net Profit: Auto-calculate in Finance Dashboard (Total Fees Collected - Total Expenses).
    Notifications: Generate notifications for:
        Upcoming Sessions.
        Pending Payments.
        Contract/POA Expiry.
        Task Assignments.

8. Implementation Steps for AI Developer

    Project Setup:
        Initialize Django Project.
        Configure settings.py (Language='ar', Timezone='UTC', MEDIA_ROOT pointing to BASE_DIR / 'media_files').
        Install dependencies (django, pillow, reportlab, django-celery-beat).
    Models Development:
        Write models.py for all entities listed in Section 3.
        Implement save() methods for auto-calculations (e.g., Invoice Total).
        Run migrations.
    Admin Panel:
        Register models in admin.py.
        Customize list displays, filters, and search fields.
    Templates (Frontend):
        Create base.html with RTL Bootstrap 5 CDN.
        Convert the provided 18 HTML files into Django Templates (dashboard.html, cases.html, etc.).
        Replace static data with Django Template Tags ({{ variable }}, {% for %}).
    Views & Logic:
        Create views.py for CRUD operations.
        Implement File Upload handling (ensure files save to media_files/).
        Implement Dashboard Statistics logic.
    File Management & Backups:
        Create a custom Management Command python manage.py backup_db that dumps the DB to media_files/backups/.
        Ensure all FileField uploads respect the directory structure.
    Charts & Reports:
        Integrate Chart.js in templates.
        Pass context data from views to render charts dynamically.
    Seed Data:
        Create a seed_data.py script to populate the DB with dummy data matching the HTML examples (Clients like "Mohammad Salama", Cases like "8555 - Allowances").
    Testing:
        Verify RTL layout.
        Verify File Uploads save to the correct local folder.
        Verify Permissions (Login required).

9. Developer Notes

    Session Minutes: Ensure the "Session Minutes" field is prominent in the Case Detail view.
    Consultations: Do not treat consultations as simple appointments; they have financial value and content documentation.
    Renewal Alerts: Use Django Signals or Celery Beat to check expiration dates daily.
    Performance: Use select_related and prefetch_related in queries to avoid N+1 problems.
    Code Quality: Follow PEP 8, comment complex logic in English or Arabic.
    Local Storage: Remember, all files must stay within the project folder structure under media_files/. Do not configure external S3 unless explicitly requested later.
