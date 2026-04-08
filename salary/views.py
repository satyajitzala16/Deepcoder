from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from decimal import Decimal
from functools import wraps

from .models import (
    Employee, Leave, Role, Technology, Admin,
    SalarySlip, Earning, Deduction, Company
)
from django.contrib.auth.models import User


# ==============================
# 🔐 AUTH DECORATORS
# ==============================
def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'admin_id' not in request.session:
            return redirect('/admin-login-page/')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_api_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'admin_id' not in request.session:
            return Response({"error": "Unauthorized"})
        return view_func(request, *args, **kwargs)
    return wrapper


# ==============================
# 🔥 FINANCIAL YEAR
# ==============================
def get_financial_year(month_str):

    month_name, year = month_str.split()
    year = int(year)

    months_map = {
        "April":4,"May":5,"June":6,"July":7,"August":8,"September":9,
        "October":10,"November":11,"December":12,
        "January":1,"February":2,"March":3
    }

    m = months_map[month_name]

    if m >= 4:
        return f"{year}-{year+1}"
    else:
        return f"{year-1}-{year}"


# ==============================
# 🔥 USED PAID LEAVES
# ==============================
def get_used_paid_leaves(emp, financial_year):

    leaves = Leave.objects.filter(employee=emp)

    total_paid = 0

    for l in leaves:
        fy = get_financial_year(l.month)
        if fy == financial_year:
            total_paid += float(l.paid_leaves)

    return total_paid


# ==============================
# 🧠 SALARY CALCULATION
# ==============================
def calculate_salary(emp, leave):

    working_days = Decimal('24')
    salary_per_day = emp.salary / working_days

    total = Decimal(str(leave.total_leaves)) if leave else Decimal('0')
    paid = Decimal(str(leave.paid_leaves)) if leave else Decimal('0')
    comp = Decimal(str(leave.comp_off_leaves)) if leave else Decimal('0')

    unpaid = total - (paid + comp)

    if unpaid < 0:
        unpaid = Decimal('0')

    cut = unpaid * salary_per_day
    final = emp.salary - cut

    return total, paid, unpaid, round(cut, 2), round(final, 2)


# ==============================
# 📊 SALARY LIST
# ==============================
@api_view(['GET'])
@admin_api_required
def employee_salary_list(request):

    month = request.GET.get("month")

    if not month:
        return Response({"error": "Month is required"})

    employees = Employee.objects.all()
    result = []

    for emp in employees:

        leave = Leave.objects.filter(employee=emp, month=month).first()

        total, paid, unpaid, cut, final = calculate_salary(emp, leave)

        tax = Decimal('200')  # 🔥 FIX: add tax

        final = final - tax   # 🔥 FINAL SALARY UPDATE

        basic = emp.salary * Decimal('0.45')
        hra = emp.salary * Decimal('0.18')
        conv = Decimal('1600')
        special = emp.salary * Decimal('0.25')

        total_earnings = basic + hra + conv + special

        company = Company.objects.first()

        if not company:
            company = Company.objects.create(
                name="Your Company",
                address="Default Address"
            )

        slip, created = SalarySlip.objects.update_or_create(
                employee=emp,
                month=month,
                defaults={
                    "company": company,
                    "pay_days": 30,
                    "total_earnings": total_earnings,
                    "total_deductions": cut + tax,   # 🔥 include tax
                    "net_pay": final
                }
            )
        # 🔥 Purana data delete (important)
        slip.earnings.all().delete()
        slip.deductions.all().delete()

        # 🔥 Earnings add
        Earning.objects.create(salary_slip=slip, name="Basic", amount=basic)
        Earning.objects.create(salary_slip=slip, name="HRA", amount=hra)
        Earning.objects.create(salary_slip=slip, name="Conveyance", amount=conv)
        Earning.objects.create(salary_slip=slip, name="Special Allowance", amount=special)

        # 🔥 Deduction
        if cut > 0:
            Deduction.objects.create(salary_slip=slip, name="Leave Deduction", amount=cut)

        # 🔥 ALWAYS ADD TAX
        Deduction.objects.create(salary_slip=slip, name="Professional Tax", amount=tax)

        result.append({
            "id": emp.id,   # 🔥 ADD THIS
            "name": emp.name,
            "email": emp.email,
            "salary": emp.salary,
            "month": month,
            "total_leaves": total,
            "paid_leaves": paid,
            "unpaid_leaves": unpaid,
            "cut_amount": cut,
            "tax": tax,   # 🔥 NEW FIELD
            "final_salary": final
        })

    return Response(result)


# ==============================
# 📅 ADD LEAVE (LIMIT + RESET)
# ==============================
@api_view(['POST'])
@admin_api_required
def add_leave(request):

    emp_id = request.data.get("employee_id")
    month = request.data.get("month")

    total = float(request.data.get("total_leaves", 0))
    paid = float(request.data.get("paid_leaves", 0))
    comp = float(request.data.get("comp_off_leaves", 0))

    if not emp_id or not month:
        return Response({"error": "employee_id and month required"})

    emp = get_object_or_404(Employee, id=emp_id)

    fy = get_financial_year(month)

    used_paid = get_used_paid_leaves(emp, fy)
    remaining = emp.yearly_paid_leaves - used_paid

    if paid > remaining:
        return Response({
            "error": f"Only {remaining} paid leaves left in {fy}"
        })

    Leave.objects.update_or_create(
        employee=emp,
        month=month,
        defaults={
            "total_leaves": total,
            "paid_leaves": paid,
            "comp_off_leaves": comp
        }
    )

    return Response({
        "message": f"Leave saved (Remaining Paid Leaves: {remaining - paid})"
    })


# ==============================
# ✏️ UPDATE LEAVE
# ==============================
@api_view(['PUT'])
@admin_api_required
def update_leave(request, id):

    leave = get_object_or_404(Leave, id=id)

    total = float(request.data.get("total_leaves", 0))
    paid = float(request.data.get("paid_leaves", 0))
    comp = float(request.data.get("comp_off_leaves", 0))

    emp = leave.employee
    fy = get_financial_year(leave.month)

    old_paid = float(leave.paid_leaves)

    used_paid = get_used_paid_leaves(emp, fy) - old_paid
    remaining = emp.yearly_paid_leaves - used_paid

    if paid > remaining:
        return Response({"error": f"Only {remaining} paid leaves left"})

    leave.total_leaves = total
    leave.paid_leaves = paid
    leave.comp_off_leaves = comp
    leave.save()

    return Response({"message": "Leave updated"})


# ==============================
# 📋 LEAVE LIST
# ==============================
@api_view(['GET'])
@admin_api_required
def leave_list(request):

    data = Leave.objects.select_related('employee').all()

    result = []

    for i in data:
        result.append({
            "id": i.id,
            "employee_id": i.employee.id,
            "employee_name": i.employee.name,
            "month": i.month,
            "total_leaves": i.total_leaves,
            "paid_leaves": i.paid_leaves,
            "comp_off_leaves": i.comp_off_leaves
        })

    return Response(result)


# ==============================
# 👨‍💼 EMPLOYEE CRUD
# ==============================
@api_view(['POST'])
@admin_api_required
def add_employee(request):

    name = request.data.get("name")
    email = request.data.get("email")
    password = request.data.get("password")
    salary = request.data.get("salary")

    if not name or not email or not password or not salary or not request.data.get("employee_id") or not request.data.get("date_of_joining"):
        return Response({"error": "All fields required"})

    role = Role.objects.get(id=request.data.get("role_id")) if request.data.get("role_id") else None

    emp = Employee.objects.create(
        employee_id=request.data.get("employee_id"),
        name=name,
        email=email,
        password=password,
        salary=salary,
        date_of_joining=request.data.get("date_of_joining"),
        role=role
    )

    if request.data.get("technology_ids"):
        emp.technologies.set(request.data.get("technology_ids"))

    return Response({"message": "Employee added"})


@api_view(['GET'])
@admin_api_required
def get_employees(request):

    employees = Employee.objects.select_related('role').prefetch_related('technologies')

    data = []

    for emp in employees:
        data.append({
            "id": emp.id,
            "employee_id": emp.employee_id,
            "name": emp.name,
            "email": emp.email,
            "salary": emp.salary,
            "password": emp.password,
            "date_of_joining": emp.date_of_joining,
            "yearly_paid_leaves": emp.yearly_paid_leaves,
            "role": emp.role.name if emp.role else "",
            "technologies": [t.name for t in emp.technologies.all()]
        })

    return Response(data)


@api_view(['PUT'])
@admin_api_required
def update_employee(request, id):

    emp = get_object_or_404(Employee, id=id)

    emp.employee_id = request.data.get("employee_id")
    emp.name = request.data.get("name")
    emp.email = request.data.get("email")
    emp.password = request.data.get("password")
    emp.salary = request.data.get("salary")
    emp.date_of_joining = request.data.get("date_of_joining")

    emp.save()

    return Response({"message": "Employee updated"})


@api_view(['DELETE'])
@admin_api_required
def delete_employee(request, id):

    emp = get_object_or_404(Employee, id=id)
    emp.delete()

    return Response({"message": "Employee deleted"})


# ==============================
# 🔹 ROLE API
# ==============================
@api_view(['GET'])
@admin_api_required
def get_roles(request):
    roles = Role.objects.all()
    data = [{"id": r.id, "name": r.name} for r in roles]
    return Response(data)


@api_view(['POST'])
@admin_api_required
def add_role(request):
    name = request.data.get("name")
    if not name:
        return Response({"error": "Role name required"})
    role, created = Role.objects.get_or_create(name=name)
    if not created:
        return Response({"error": "Role already exists"})
    return Response({"message": "Role added"})


@api_view(['PUT'])
@admin_api_required
def update_role(request, id):
    role = get_object_or_404(Role, id=id)
    name = request.data.get("name")
    if not name:
        return Response({"error": "Role name required"})
    role.name = name
    role.save()
    return Response({"message": "Role updated"})


@api_view(['DELETE'])
@admin_api_required
def delete_role(request, id):
    role = get_object_or_404(Role, id=id)
    role.delete()
    return Response({"message": "Role deleted"})


# ==============================
# TECHNOLOGY CRUD
# ==============================
@api_view(['POST'])
@admin_api_required
def add_technology(request):
    Technology.objects.create(name=request.data.get("name"))
    return Response({"message": "Technology added"})


@api_view(['GET'])
@admin_api_required
def get_technologies(request):
    techs = Technology.objects.all()
    data = [{"id":t.id,"name":t.name} for t in techs]
    return Response(data)


@api_view(['PUT'])
@admin_api_required
def update_technology(request, id):
    tech = get_object_or_404(Technology, id=id)
    tech.name = request.data.get("name")
    tech.save()
    return Response({"message":"Technology updated"})


@api_view(['DELETE'])
@admin_api_required
def delete_technology(request, id):
    tech = get_object_or_404(Technology, id=id)
    tech.delete()
    return Response({"message":"Technology deleted"})

import os
import calendar
from decimal import Decimal, ROUND_HALF_UP
from django.http import HttpResponse
from django.conf import settings

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

from .models import Employee, SalarySlip, Leave


def salary_slip_pdf(request, emp_id, month):
    emp = Employee.objects.get(id=emp_id)
    slip = SalarySlip.objects.get(employee=emp, month=month)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{emp.name}_{month}_salary.pdf"'

    c = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # ---------------------------
    # ✅ LOGO FIX
    # ---------------------------
    logo_path = os.path.join(settings.BASE_DIR, 'salary', 'static', 'salary', 'images', 'DeepcoderPdf.png')

    if os.path.exists(logo_path):
        c.drawImage(logo_path, 50, height-100, width=100, height=50, mask='auto')

    # ---------------------------
    # Company Info
    # ---------------------------
    c.setFont("Helvetica-Bold", 14)
    c.drawString(200, height-60, "Deepcoder Pvt Ltd")

    c.setFont("Helvetica", 10)
    c.drawString(200, height-75, "504, Jaihind HN Safal")
    c.drawString(200, height-90, "Nr. New York Tower -1")
    c.drawString(200, height-105, "S.G. Highway")
    c.drawString(200, height-120, "Ahmedabad - 380054")

    # ---------------------------
    # Title
    # ---------------------------
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height-150, f"Salary Pay Slip for: {month}")

    # ---------------------------
    # Employee Info
    # ---------------------------
    y = height - 170

    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Employee Name: {emp.name}")

    doj = emp.date_of_joining.strftime('%d-%b-%Y') if emp.date_of_joining else "N/A"
    c.drawString(300, y, f"DOJ: {doj}")

    month_name, year = month.split()
    month_number = list(calendar.month_name).index(month_name)
    year = int(year)
    total_days = calendar.monthrange(year, month_number)[1]

    y -= 15
    c.drawString(50, y, f"Employee ID: {emp.employee_id}")
    c.drawString(300, y, f"Pay Days: {slip.pay_days}/{total_days}")

    y -= 15
    c.drawString(50, y, f"Role: {emp.role.name if emp.role else 'N/A'}")

    # ---------------------------
    # Salary Calculation
    # ---------------------------
    total_salary = Decimal(emp.salary)

    basic = (total_salary * Decimal('0.45')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    special = (total_salary * Decimal('0.25')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    conveyance = (total_salary * Decimal('0.128')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    hra = (total_salary - (basic + special + conveyance)).quantize(Decimal('0.01'))

    professional_tax = Decimal('200.00')
    tds = Decimal('0.00')
    esic = Decimal('0.00')

    leaves_record = Leave.objects.filter(employee=emp, month=month).first()
    leaves_deduction = Decimal('0.00')

    if leaves_record:
        unpaid = leaves_record.total_leaves - leaves_record.paid_leaves
        per_day = total_salary / Decimal(total_days)
        leaves_deduction = (Decimal(unpaid) * per_day).quantize(Decimal('0.01'))

    # ---------------------------
    # ✅ TABLE DATA
    # ---------------------------
    table_data = [
        ["Earnings", "Amount", "Deductions", "Amount"],
        ["Basic", f"{basic}", "Professional Tax", f"{professional_tax}"],
        ["Special Allowance", f"{special}", "TDS", f"{tds}"],
        ["Conveyance", f"{conveyance}", "ESIC", f"{esic}"],
        ["HRA", f"{hra}", "Leaves Deduction", f"{leaves_deduction}"],
    ]

    total_earnings = basic + special + conveyance + hra
    total_deductions = professional_tax + tds + esic + leaves_deduction
    net_pay = total_earnings - total_deductions

    # Totals Row
    table_data.append([
        "Total Earnings", f"{total_earnings}",
        "Total Deductions", f"{total_deductions}"
    ])

    # ✅ FIXED Net Pay Row (NO SPAN ISSUE)
    table_data.append([
        "Net Pay", f"{net_pay}", "", ""
    ])

    # ---------------------------
    # 🔥 TABLE DESIGN
    # ---------------------------
    table = Table(table_data, colWidths=[140, 80, 140, 80])

    style = TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),

        # Header
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

        # Alignment
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),

        # Bold totals
        ('FONTNAME', (0, -2), (-1, -1), 'Helvetica-Bold'),

        # 🔥 Net Pay Highlight (FIXED)
        ('BACKGROUND', (0, -1), (1, -1), colors.lightgrey),
        ('ALIGN', (1, -1), (1, -1), 'RIGHT'),

        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
    ])

    table.setStyle(style)

    table.wrapOn(c, width, height)
    table.drawOn(c, 50, y - 200)

    # ---------------------------
    # Footer
    # ---------------------------
    c.setFont("Helvetica", 8)
    c.drawString(50, 100, "** This is a computer generated salary slip and does not require signature.")

    c.save()
    return response


# ==============================
# LOGIN
# ==============================
@api_view(['POST'])
def admin_login(request):
    try:
        admin = Admin.objects.get(email=request.data.get("email"), password=request.data.get("password"))
        request.session['admin_id'] = admin.id
        return Response({"status": "success"})
    except:
        return Response({"status": "error"})


@api_view(['POST'])
def employee_login(request):
    try:
        user = Employee.objects.get(email=request.data.get("email"), password=request.data.get("password"))
        request.session['employee_id'] = user.id
        return Response({"status": "success", "employee_id": user.id})
    except:
        return Response({"status": "error"})


def create_admin(request):
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser(
            username="admin",
            email="admin@gmail.com",
            password="admin123"
        )
        return JsonResponse({"message": "Admin created"})
    else:
        return JsonResponse({"message": "Admin already exists"})


# ==============================
# LOGOUT
# ==============================
def logout(request):
    request.session.flush()
    return redirect('admin_login_page')


# ==============================
# PAGES (PROTECTED)
# ==============================
def home(request): return render(request, "index.html")

def admin_page(request): return render(request, "admin_login.html")

@admin_required
def admin_dashboard(request): return render(request, "admin/admin_dashboard.html")

@admin_required
def admin_employee(request): return render(request, "admin/admin_employee.html")

@admin_required
def admin_leaves(request): return render(request, "admin/admin_leaves.html")

@admin_required
def admin_salary(request):return render(request, "admin/admin_salary.html")

@admin_required
def admin_role(request): return render(request, "admin/admin-role.html")

@admin_required
def admin_technology(request): return render(request, "admin/admin-technology.html")