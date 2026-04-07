from django.db import models


# 🏷️ Role Model
class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


# 💻 Technology Model
class Technology(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


# 🏢 Company (NEW - for salary slip header)
class Company(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()

    def __str__(self):
        return self.name


# 👨‍💼 Employee
class Employee(models.Model):
    employee_id = models.CharField(max_length=20, unique=True)

    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)

    date_of_joining = models.DateField(null=True, blank=True)

    salary = models.DecimalField(max_digits=10, decimal_places=2)
    yearly_paid_leaves = models.IntegerField(default=12)

    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    technologies = models.ManyToManyField(Technology, blank=True)

    def __str__(self):
        return f"{self.name} ({self.employee_id})"


# 📅 Leave
class Leave(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="leaves")
    month = models.CharField(max_length=20)

    total_leaves = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    paid_leaves = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    comp_off_leaves = models.DecimalField(max_digits=4, decimal_places=1, default=0)

    class Meta:
        unique_together = ('employee', 'month')

    def __str__(self):
        return f"{self.employee.name} - {self.month}"


# 💰 Salary Slip (MAIN MODEL)
class SalarySlip(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="salary_slips")
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True)

    month = models.CharField(max_length=20)
    pay_days = models.IntegerField(default=30)

    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('employee', 'month')

    def __str__(self):
        return f"{self.employee.name} - {self.month}"


# 💸 Earnings (Flexible - Basic, HRA, etc.)
class Earning(models.Model):
    salary_slip = models.ForeignKey(SalarySlip, on_delete=models.CASCADE, related_name="earnings")
    name = models.CharField(max_length=100)  # Basic, HRA, etc.
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} - {self.amount}"


# 💸 Deductions (Flexible - PF, TDS, etc.)
class Deduction(models.Model):
    salary_slip = models.ForeignKey(SalarySlip, on_delete=models.CASCADE, related_name="deductions")
    name = models.CharField(max_length=100)  # TDS, PF, etc.
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} - {self.amount}"


# 🔐 Admin
class Admin(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.email