from . import views
from django.urls import path

urlpatterns = [
    path('', views.home),
    path('admin-login-page/', views.admin_page),
    path('admin-dashboard/', views.admin_dashboard),
    path('admin-employee/', views.admin_employee),
    path('admin-leaves/', views.admin_leaves),
    path('admin-salary/', views.admin_salary),
    path('admin-role/', views.admin_role, name="admin-role"),
    path('admin-technology/', views.admin_technology, name="admin-technology"),
    path('logout/', views.logout, name='logout'),


    path('employee-login/', views.employee_login),
    path('admin-login/', views.admin_login),

    path('employee-salary/', views.employee_salary_list),
    path('add-employee/', views.add_employee),
    path('employees/', views.get_employees),
    path('update-employee/<int:id>/', views.update_employee),
    path('delete-employee/<int:id>/', views.delete_employee),
    path('add-leave/', views.add_leave),
    path('leave-list/', views.leave_list),
    path('update-leave/<int:id>/', views.update_leave),
    path('api/roles/', views.get_roles),
    path('api/add-role/', views.add_role),
    path('api/update-role/<int:id>/', views.update_role),
    path('api/delete-role/<int:id>/', views.delete_role),
    path('api/technologies/', views.get_technologies),
    path('api/add-technology/', views.add_technology),
    path('api/update-technology/<int:id>/', views.update_technology),
    path('api/delete-technology/<int:id>/', views.delete_technology),
    path('download-slip/<int:emp_id>/<str:month>/', views.salary_slip_pdf, name='salary_slip_pdf'),
    
    path('create-admin/', views.create_admin),

]
