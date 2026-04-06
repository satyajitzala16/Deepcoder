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


# 👨‍💼 Employee
class Employee(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)

    salary = models.DecimalField(max_digits=10, decimal_places=2)

    yearly_paid_leaves = models.IntegerField(default=12)

    # 🔥 NEW FIELDS
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    technologies = models.ManyToManyField(Technology, blank=True)

    def __str__(self):
        return self.name


# 📅 Leave
class Leave(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="leaves")
    month = models.CharField(max_length=20)

    total_leaves = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    paid_leaves = models.DecimalField(max_digits=4, decimal_places=1, default=0)

    # 🔥 NEW FIELD
    comp_off_leaves = models.DecimalField(max_digits=4, decimal_places=1, default=0)


    class Meta:
        unique_together = ('employee', 'month')

    def __str__(self):
        return f"{self.employee.name} - {self.month}"


# 💰 Salary Record
class SalaryRecord(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="salary_records")
    month = models.CharField(max_length=20)

    total_leaves = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    paid_leaves = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    unpaid_leaves = models.DecimalField(max_digits=4, decimal_places=1, default=0)

    cut_amount = models.DecimalField(max_digits=10, decimal_places=2)
    final_salary = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('employee', 'month')

    def __str__(self):
        return f"{self.employee.name} - {self.month}"
    
# 🔐 Admin Model
class Admin(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.email    