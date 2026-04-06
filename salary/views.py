from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from decimal import Decimal

from .models import Employee, Leave, SalaryRecord, Role, Technology, Admin


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

    # 🔥 comp_off = NO salary cut
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
def employee_salary_list(request):

    month = request.GET.get("month")

    if not month:
        return Response({"error": "Month is required"})

    employees = Employee.objects.all()
    result = []

    for emp in employees:

        leave = Leave.objects.filter(employee=emp, month=month).first()

        total, paid, unpaid, cut, final = calculate_salary(emp, leave)

        SalaryRecord.objects.update_or_create(
            employee=emp,
            month=month,
            defaults={
                "total_leaves": total,
                "paid_leaves": paid,
                "unpaid_leaves": unpaid,
                "cut_amount": cut,
                "final_salary": final
            }
        )

        result.append({
            "name": emp.name,
            "email": emp.email,
            "salary": emp.salary,
            "month": month,
            "total_leaves": total,
            "paid_leaves": paid,
            "unpaid_leaves": unpaid,
            "cut_amount": cut,
            "final_salary": final
        })

    return Response(result)


# ==============================
# 📅 ADD LEAVE (LIMIT + RESET)
# ==============================
@api_view(['POST'])
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
def add_employee(request):

    name = request.data.get("name")
    email = request.data.get("email")
    password = request.data.get("password")
    salary = request.data.get("salary")

    if not name or not email or not password or not salary:
        return Response({"error": "All fields required"})

    role = Role.objects.get(id=request.data.get("role_id")) if request.data.get("role_id") else None

    emp = Employee.objects.create(
        name=name,
        email=email,
        password=password,
        salary=salary,
        role=role
    )

    if request.data.get("technology_ids"):
        emp.technologies.set(request.data.get("technology_ids"))

    return Response({"message": "Employee added"})


# 📋 Get Employees
@api_view(['GET'])
def get_employees(request):

    employees = Employee.objects.select_related('role').prefetch_related('technologies')

    data = []

    for emp in employees:
        data.append({
            "id": emp.id,
            "name": emp.name,
            "email": emp.email,
            "salary": emp.salary,
            "password": emp.password,
            "yearly_paid_leaves": emp.yearly_paid_leaves,
            "role": emp.role.name if emp.role else "",
            "technologies": [t.name for t in emp.technologies.all()]
        })

    return Response(data)


@api_view(['PUT'])
def update_employee(request, id):

    emp = get_object_or_404(Employee, id=id)

    emp.name = request.data.get("name")
    emp.email = request.data.get("email")
    emp.password = request.data.get("password")
    emp.salary = request.data.get("salary")

    emp.save()

    return Response({"message": "Employee updated"})


@api_view(['DELETE'])
def delete_employee(request, id):

    emp = get_object_or_404(Employee, id=id)
    emp.delete()

    return Response({"message": "Employee deleted"})


# ==============================
# 🔹 ROLE API
# ==============================
@api_view(['GET'])
def get_roles(request):
    roles = Role.objects.all()
    data = [{"id": r.id, "name": r.name} for r in roles]
    return Response(data)


@api_view(['POST'])
def add_role(request):
    name = request.data.get("name")
    if not name:
        return Response({"error": "Role name required"})
    role, created = Role.objects.get_or_create(name=name)
    if not created:
        return Response({"error": "Role already exists"})
    return Response({"message": "Role added"})


@api_view(['PUT'])
def update_role(request, id):
    role = get_object_or_404(Role, id=id)
    name = request.data.get("name")
    if not name:
        return Response({"error": "Role name required"})
    role.name = name
    role.save()
    return Response({"message": "Role updated"})


@api_view(['DELETE'])
def delete_role(request, id):
    role = get_object_or_404(Role, id=id)
    role.delete()
    return Response({"message": "Role deleted"})


# ==============================
# TECHNOLOGY CRUD
# ==============================
@api_view(['POST'])
def add_technology(request):
    Technology.objects.create(name=request.data.get("name"))
    return Response({"message": "Technology added"})

@api_view(['GET'])
def get_technologies(request):
    techs = Technology.objects.all()
    data = [{"id":t.id,"name":t.name} for t in techs]
    return Response(data)

@api_view(['PUT'])
def update_technology(request, id):
    tech = get_object_or_404(Technology, id=id)
    tech.name = request.data.get("name")
    tech.save()
    return Response({"message":"Technology updated"})

@api_view(['DELETE'])
def delete_technology(request, id):
    tech = get_object_or_404(Technology, id=id)
    tech.delete()
    return Response({"message":"Technology deleted"})


# ==============================
# LOGIN
# ==============================
@api_view(['POST'])
def admin_login(request):
    try:
        Admin.objects.get(email=request.data.get("email"), password=request.data.get("password"))
        return Response({"status": "success"})
    except:
        return Response({"status": "error"})


@api_view(['POST'])
def employee_login(request):
    try:
        user = Employee.objects.get(email=request.data.get("email"), password=request.data.get("password"))
        return Response({"status": "success", "employee_id": user.id})
    except:
        return Response({"status": "error"})
    
from django.contrib.auth.models import User

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
# PAGES
# ==============================
def home(request): return render(request, "index.html")
def admin_page(request): return render(request, "admin_login.html")
def admin_dashboard(request): return render(request, "admin/admin_dashboard.html")
def admin_employee(request): return render(request, "admin/admin_employee.html")
def admin_leaves(request): return render(request, "admin/admin_leaves.html")
def admin_salary(request): return render(request, "admin/admin_salary_record.html")
def admin_role(request): return render(request, "admin/admin-role.html")
def admin_technology(request): return render(request, "admin/admin-technology.html")