from django.contrib import admin
from .models import Admin, Employee, Leave ,SalaryRecord , Role ,Technology


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


# 💰 Salary Record Admin
@admin.register(SalaryRecord)
class SalaryRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'month', 'final_salary')
    search_fields = ('employee__name', 'month')
    list_filter = ('employee', 'month')
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