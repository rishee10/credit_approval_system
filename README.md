# Credit Approval System - Backend Assignment

A Django-based REST API system for managing customer credit applications, loan eligibility checks, and loan approvals with automated credit scoring.

---

## 🎯 Overview

This Credit Approval System evaluates customer loan eligibility based on historical payment behavior, current debt obligations, and income levels. It automates credit scoring and ensures responsible lending by preventing over-leveraging.

---

## ✨ Features

- ✅ Customer registration with auto credit limit
- ✅ Scoring algorithm based on payment history
- ✅ Automated interest rate correction
- ✅ EMI Calculation using compound interest
- ✅ Prevents loans exceeding 50% salary EMI rule
- ✅ Full loan creation and tracking
- ✅ Asynchronous Excel loading with Celery

---

## 🛠️ Tech Stack

- Django 4.x
- Django REST Framework
- PostgreSQL
- Celery + Redis
- Pandas, OpenPyXL
- Docker + Docker Compose

---

## 🚀 Installation & Setup

### 🧰 Prerequisites
- Python 3.10+
- PostgreSQL 14+
- Redis
- Git & Docker

### 🧩 Steps to Setup Locally

1. **Clone Repo**
   ```
   git clone https://github.com/rishee10/credit_approval_system.git
   
   cd credit_approval_system
   ```
2. **Create Virtual Env and activate it**

     ```
     python -m venv venv
  
     venv\Scripts\activate
     ```

3. **Install Dependencies**
   ```
   pip install -r requirements.txt
   ```

4. **Set the database in the proj/settings.py file add your password and other detials**

5. **Run Migrations**
   ```
    python manage.py makemigrations
    python manage.py migrate
   ```

6. **Run Server**

   ```
   python manage.py runserver
   ```


## API Endpoints

## 1) Register Customer

     Endpoint: POST /register
     Description: Register a new customer with their details

## 2) Check Loan Eligibility

      Endpoint: POST /check-eligibility
      Description: Check if a customer is eligible for a loan based on credit score

## 3) Create Loan

    Endpoint: POST /create-loan
    Description: Create a new loan for an eligible customer

## 4) View Loan Details
    
    Endpoint: GET /view-loan/<loan_id>
    Description: View details of a specific loan

## 5) View Customer Loans

    Endpoint: GET /view-loans/<customer_id>
    Description: View all loans for a specific customer


     


   





