from django.contrib import admin
from .models import Admin, Deduction, Employee, Leave  , Role ,Technology , Company , SalarySlip


# 👨‍💼 Employee Admin
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'salary')
    search_fields = ('name',)
    ordering = ('id',)


# 📅 Leave Admin
@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'total_leaves', 'paid_leaves')
    search_fields = ('employee__name',)
    list_filter = ('employee',)
    ordering = ('id',)


# 🏢 Company Admin
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('id',)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('id',)

@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('id',)

@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    list_display = ('id', 'email')
    search_fields = ('email',)
    ordering = ('id',)

# @admin.register(SalarySlip)
# class SalarySlipAdmin(admin.ModelAdmin):
#     list_display = ('id', 'employee', 'month', 'year', 'total_leaves', 'paid_leaves', 'deductions', 'net_salary')
#     search_fields = ('employee__name',)
#     list_filter = ('employee', 'month', 'year')
#     ordering = ('id',)

@admin.register(Deduction)
class DeductionAdmin(admin.ModelAdmin):
    list_display = ('id', 'salary_slip', 'name', 'amount')
    search_fields = ('salary_slip__employee__name', 'name')
    list_filter = ('salary_slip__employee',)
    ordering = ('id',)