import pandas as pd
from celery import shared_task
from .models import Customer, Loan
from datetime import datetime

@shared_task
def load_customers_from_excel(file_path):
    df = pd.read_excel(file_path)
    for _, row in df.iterrows():
        Customer.objects.update_or_create(
            customer_id=row['Customer ID'],
            defaults={
                'first_name': row['First Name'],
                'last_name': row['Last Name'],
                'age': row['Age'],
                'phone_number': str(row['Phone Number']),
                'monthly_income': row['Monthly Salary'],
                'approved_limit': row['Approved Limit'],
                'current_debt': 0,
            }
        )
    return "Customers loaded"

@shared_task
def load_loans_from_excel(file_path):
    df = pd.read_excel(file_path)
    for _, row in df.iterrows():
        try:
            customer = Customer.objects.get(customer_id=row['Customer ID'])
        except Customer.DoesNotExist:
            continue

        Loan.objects.update_or_create(
            loan_id=row['Loan ID'],
            defaults={
                'customer': customer,
                'loan_amount': row['Loan Amount'],
                'tenure': row['Tenure'],
                'interest_rate': row['Interest Rate'],
                'monthly_payment': row['Monthly payment'],
                'emis_paid_on_time': row['EMIs paid on Time'],
                'start_date': pd.to_datetime(row['Date of Approval']).date(),
                'end_date': pd.to_datetime(row['End Date']).date()
            }
        )
    return "Loans loaded"
