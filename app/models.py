from django.db import models

# Create your models here.

from django.db import models

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField()
    phone_number = models.CharField(max_length=15)
    monthly_income = models.FloatField()
    approved_limit = models.FloatField(default=0.0)
    current_debt = models.FloatField(default=0.0)

    def save(self, *args, **kwargs):
        # Calculate approved_limit = 36 * monthly_income (rounded)
        self.approved_limit = round(self.monthly_income * 36, -5)
        super().save(*args, **kwargs)

class Loan(models.Model):
    loan_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, related_name='loans', on_delete=models.CASCADE)
    loan_amount = models.FloatField()
    tenure = models.IntegerField()  # in months
    interest_rate = models.FloatField()
    monthly_payment = models.FloatField()
    emis_paid_on_time = models.IntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField()
