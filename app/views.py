from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import date
from dateutil.relativedelta import relativedelta
from .models import Customer, Loan
from .serializers import CustomerSerializer, LoanSerializer


def calculate_emi(principal, annual_rate, tenure_months):
    """
    Calculate EMI using the compound interest formula:
    EMI = P × r × (1 + r)^n / [(1 + r)^n - 1]
    where:
        P = principal loan amount
        r = monthly interest rate (annual rate / 12 / 100)
        n = tenure in months
    """
    if annual_rate == 0:
        return principal / tenure_months
    
    r = annual_rate / 100 / 12  # Monthly interest rate
    n = tenure_months
    
    emi = principal * r * ((1 + r) ** n) / (((1 + r) ** n) - 1)
    return emi


def credit_score(customer):
    """
    Calculate credit score (0-100) based on:
    1. Past loan payment behavior (50 points)
    2. Number of loans taken (30 points)
    3. Loan activity in current year (20 points)
    4. Total loan volume vs approved limit
    """
    loans = customer.loans.all()
    
    # New customer with no history gets perfect score
    if not loans:
        return 100
    
    total_loans = loans.count()
    
    # Check if current EMIs exceed 50% of salary
    current_emis = sum([loan.monthly_payment for loan in loans])
    if current_emis > customer.monthly_income * 0.5:
        return 0
    
    # Calculate score based on payment history
    total_emis = sum([loan.tenure for loan in loans])
    on_time_emis = sum([loan.emis_paid_on_time for loan in loans])
    
    if total_emis == 0:
        return 100
    
    # Payment history score (0-50 points)
    payment_ratio = on_time_emis / total_emis if total_emis > 0 else 1
    payment_score = payment_ratio * 50
    
    # Number of loans score (0-30 points)
    # Penalize too many loans
    if total_loans <= 3:
        loan_count_score = 30
    elif total_loans <= 5:
        loan_count_score = 20
    else:
        loan_count_score = 10
    
    # Loan volume score (0-20 points)
    total_loan_amount = sum([loan.loan_amount for loan in loans])
    if total_loan_amount <= customer.approved_limit * 0.5:
        volume_score = 20
    elif total_loan_amount <= customer.approved_limit:
        volume_score = 10
    else:
        volume_score = 5
    
    final_score = min(payment_score + loan_count_score + volume_score, 100)
    return int(final_score)


class RegisterCustomer(APIView):
    """
    Register a new customer
    POST /register
    """
    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            return Response({
                "customer_id": customer.customer_id,
                "name": f"{customer.first_name} {customer.last_name}",
                "age": customer.age,
                "monthly_income": customer.monthly_income,
                "approved_limit": customer.approved_limit,
                "phone_number": customer.phone_number
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckEligibility(APIView):
    """
    Check loan eligibility for a customer
    POST /check-eligibility
    
    Determines:
    - Credit score
    - Approval status
    - Corrected interest rate based on credit score
    - Monthly installment
    """
    def post(self, request):
        customer_id = request.data.get('customer_id')
        loan_amount = float(request.data.get('loan_amount'))
        interest_rate = float(request.data.get('interest_rate'))
        tenure = int(request.data.get('tenure'))
        
        # Validate customer exists
        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return Response(
                {'error': 'Customer not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Calculate credit score
        score = credit_score(customer)
        
        # Determine corrected interest rate based on credit score
        corrected_interest_rate = interest_rate
        approval = True
        
        if score > 50:
            corrected_interest_rate = interest_rate
        elif 30 <= score <= 50:
            corrected_interest_rate = max(interest_rate, 12)
        elif 10 <= score < 30:
            corrected_interest_rate = max(interest_rate, 16)
        else:  # score < 10
            approval = False
        
        # Calculate monthly installment
        monthly_installment = 0
        if approval:
            monthly_installment = calculate_emi(
                loan_amount, 
                corrected_interest_rate, 
                tenure
            )
            
            # Check if sum of all current EMIs + new EMI > 50% of monthly salary
            current_emis = sum([loan.monthly_payment for loan in customer.loans.all()])
            total_emis = current_emis + monthly_installment
            
            if total_emis > customer.monthly_income * 0.5:
                approval = False
                monthly_installment = 0
        
        # Prepare response
        response = {
            "customer_id": customer_id,
            "approval": approval,
            "interest_rate": interest_rate,
            "corrected_interest_rate": corrected_interest_rate,
            "tenure": tenure,
            "monthly_installment": round(monthly_installment, 2)
        }
        
        return Response(response)


class CreateLoan(APIView):
    """
    Create a new loan for a customer
    POST /create-loan
    
    Creates loan only if:
    - Credit score is sufficient
    - EMIs don't exceed 50% of monthly income
    """
    def post(self, request):
        customer_id = request.data.get('customer_id')
        loan_amount = float(request.data.get('loan_amount'))
        interest_rate = float(request.data.get('interest_rate'))
        tenure = int(request.data.get('tenure'))
        
        # Validate customer exists
        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return Response(
                {'error': 'Customer not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Calculate credit score
        score = credit_score(customer)
        
        # Determine corrected interest rate based on credit score
        corrected_interest_rate = interest_rate
        approval = True
        message = "Loan approved"
        
        if score > 50:
            corrected_interest_rate = interest_rate
        elif 30 <= score <= 50:
            corrected_interest_rate = max(interest_rate, 12)
        elif 10 <= score < 30:
            corrected_interest_rate = max(interest_rate, 16)
        else:
            approval = False
            message = "Loan rejected due to low credit score"
        
        # Calculate EMI
        monthly_installment = 0
        if approval:
            monthly_installment = calculate_emi(
                loan_amount, 
                corrected_interest_rate, 
                tenure
            )
            
            # Check EMI threshold
            current_emis = sum([loan.monthly_payment for loan in customer.loans.all()])
            total_emis = current_emis + monthly_installment
            
            if total_emis > customer.monthly_income * 0.5:
                approval = False
                message = "Loan rejected: EMIs exceed 50% of monthly income"
        
        # If not approved, return rejection response
        if not approval:
            return Response({
                "loan_id": None,
                "customer_id": customer_id,
                "loan_approved": False,
                "message": message,
                "monthly_installment": 0
            }, status=status.HTTP_200_OK)
        
        # Create loan in database
        start_date = date.today()
        end_date = start_date + relativedelta(months=tenure)
        
        loan = Loan.objects.create(
            customer=customer,
            loan_amount=loan_amount,
            tenure=tenure,
            interest_rate=corrected_interest_rate,
            monthly_payment=monthly_installment,
            emis_paid_on_time=0,
            start_date=start_date,
            end_date=end_date
        )
        
        return Response({
            "loan_id": loan.loan_id,
            "customer_id": customer_id,
            "loan_approved": True,
            "message": message,
            "monthly_installment": round(monthly_installment, 2)
        }, status=status.HTTP_201_CREATED)


class ViewLoan(APIView):
    """
    View details of a specific loan
    GET /view-loan/<loan_id>
    """
    def get(self, request, loan_id):
        try:
            loan = Loan.objects.get(loan_id=loan_id)
        except Loan.DoesNotExist:
            return Response(
                {'error': 'Loan not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        response = {
            "loan_id": loan.loan_id,
            "customer": {
                "id": loan.customer.customer_id,
                "first_name": loan.customer.first_name,
                "last_name": loan.customer.last_name,
                "phone_number": loan.customer.phone_number,
                "age": loan.customer.age
            },
            "loan_amount": loan.loan_amount,
            "interest_rate": loan.interest_rate,
            "monthly_installment": loan.monthly_payment,
            "tenure": loan.tenure
        }
        
        return Response(response)


class ViewLoans(APIView):
    """
    View all loans for a specific customer
    GET /view-loans/<customer_id>
    """
    def get(self, request, customer_id):
        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return Response(
                {'error': 'Customer not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        loans = customer.loans.all()
        
        loan_list = []
        for loan in loans:
            # Calculate remaining EMIs
            repayments_left = loan.tenure - loan.emis_paid_on_time
            
            loan_list.append({
                "loan_id": loan.loan_id,
                "loan_amount": loan.loan_amount,
                "interest_rate": loan.interest_rate,
                "monthly_installment": loan.monthly_payment,
                "repayments_left": repayments_left
            })
        
        return Response(loan_list)
