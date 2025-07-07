from fastapi import FastAPI, HTTPException, status, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from database import get_db, engine, Base
from pydantic import BaseModel, EmailStr, constr
from models.database_models import (
    MasterCustomerData,
    EmploymentInfo,
    LoanInfo,
    BankInfo,
    TransactionHistory,
    AuditLog,
    BankEmployees
)
import uvicorn
import os
from dotenv import load_dotenv
load_dotenv()
# Create database tables
Base.metadata.create_all(bind=engine)

# Get root_path from environment variable, default to "" for local development
root_path = os.getenv("ROOT_PATH", "")

app = FastAPI(
    title="Loan Processing API",
    description="REST API for loan processing and orchestration. Supports Aadhaar and PAN verification, and processes loan applications in Indian Rupees (₹).",
    version="1.0.0",
    root_path=root_path,
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    servers=[
        {
            "url": "https://applicationagentupdated.azurewebsites.net"
        }
    ],
    openapi_tags=[
        {
            "name": "ExecuteFunction",
            "description": "Operations for loan processing and orchestration"
        },
        {
            "name": "root",
            "description": "Root endpoint operations"
        },
        {
            "name": "health",
            "description": "Health check operations"
        },
         {
            "name": "Application",
            "description": "Operations for loan application process including personal, employment, and loan details"
        }
    ]
)

# Add CORS middleware with specific configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
    max_age=3600,  # Maximum time to cache preflight requests
)

# Pydantic models for request validation
class PersonalDetailsRequest(BaseModel):
    name: str
    fathers_name: str
    dob: date
    age: int
    gender: str
    marital_status: str
    address: str
    city: str
    state: str
    pincode: int  # Changed to int
    mobile: int  # Changed to int
    alternate_mobile: Optional[int] = None  # Changed to Optional[int]
    email: str
    nationality: str

class EmploymentDetailsRequest(BaseModel):
    designation: str
    monthly_income: float

class LoanApplicationRequest(BaseModel):
    loan_amount: float
    loan_required: str = "Yes"
    application_date: Optional[date] = None
    loan_status: str = "PENDING"

@app.get("/",
         tags=["root"],
         operation_id="GetRoot")
def read_root():
    """
    Welcome endpoint for the Loan Processing API.
    
    Returns:
    - Dict: Welcome message
    """
    return {"message": "Welcome to Loan Processing API"}

@app.get("/health",
         tags=["health"],
         operation_id="HealthCheck")
async def health_check(
    db: Session = Depends(get_db)
):
    """
    Health check endpoint that verifies database connectivity.
    
    Parameters:
    - db: Database session dependency
    
    Returns:
    - Dict: Health status with database connectivity information
    """
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected",
            "details": {
                "api_version": "1.0.0",
                "environment": os.getenv("ENVIRONMENT", "production")
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "database": "disconnected",
            "error": str(e)
        }

@app.get("/api/users/{customer_id}/summary",
         tags=["ExecuteFunction"],
         operation_id="GetCustomerSummary")
async def get_customer_summary(
    customer_id: str,
    db: Session = Depends(get_db)
):
    """
    Get customer summary including loan history, income, and credit score.
    
    Parameters:
    - customer_id: Unique identifier of the customer
    - db: Database session dependency
    
    Returns:
    - Dict: Customer profile with loan details and financial information
    """
    # Get customer and employment info
    customer = db.query(MasterCustomerData).filter_by(Customer_ID=customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    employment = db.query(EmploymentInfo).filter_by(Customer_ID=customer_id).first()

    # Get all loans with amount > 0 (active applications or disbursed loans)
    loans = db.query(LoanInfo).filter(
        LoanInfo.Customer_ID == customer_id,
        LoanInfo.Loan_Required == "Yes",
        LoanInfo.Loan_Amount > 0
    ).all()

    # Get credit score from most recent loan application
    latest_loan = db.query(LoanInfo).filter_by(
        Customer_ID=customer_id,
        Loan_Required="Yes"
    ).order_by(LoanInfo.Application_Date.desc()).first()
    
    credit_score = latest_loan.Credit_Score if latest_loan else None

    # Format existing loans
    existing_loans = []
    for loan in loans:
        existing_loans.append({
            "type": loan.Loan_Purpose,  # Using Loan_Purpose as it contains "Car", "Home", etc.
            "amount": float(loan.Loan_Amount),
            "monthly_emi": float(loan.EMI) if loan.EMI else 0,
            "tenure_years": (loan.Tenure_Months or 0) // 12,  # Convert months to years
            "status": loan.Loan_Status
        })

    return {
        "customer_id": customer.Customer_ID,
        "name": customer.Name,
        "monthly_income": float(employment.Monthly_Income) if employment else 0,
        "credit_score": credit_score,
        "existing_loans": existing_loans
    }


@app.get("/api/users/search",
         tags=["ExecuteFunction"],
         operation_id="GetCustomerIdByName")
async def get_customer_id_by_name(
    name: str,
    db: Session = Depends(get_db)
):
    """
    Get Customer ID based on customer name.
    
    Parameters:
    - name: Name of the customer to search for
    - db: Database session dependency
    
    Returns:
    - Dict: List of matching customers with their details
    """
    # Search for customers with similar names (case-insensitive)
    customers = db.query(MasterCustomerData).filter(
        MasterCustomerData.Name.ilike(f"%{name}%")
    ).all()
    
    if not customers:
        raise HTTPException(
            status_code=404,
            detail=f"No customers found with name containing '{name}'"
        )

    # Return list of matching customers with relevant details
    results = []
    for customer in customers:
        results.append({
            "customer_id": customer.Customer_ID,
            "name": customer.Name,
            "age": customer.Age,
            "city": customer.City,
            "state": customer.State,
            "customer_since": customer.Customer_Since.isoformat() if customer.Customer_Since else None
        })

    return {
        "search_term": name,
        "matches_found": len(results),
        "customers": results
    }

@app.post("/api/start-application/personal-details",
         tags=["ExecuteFunction"],
         operation_id="CreatePersonalDetails")
async def create_personal_details(
    details: PersonalDetailsRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new customer with personal details and generate a unique customer ID.
    
    Parameters:
    - details: Personal details of the customer
    - db: Database session dependency
    
    Returns:
    - Dict: Created customer details with generated customer ID
    """
    # Get the latest customer ID and increment
    latest_customer = db.query(MasterCustomerData).order_by(
        MasterCustomerData.Customer_ID.desc()
    ).first()
    
    # Start from CUST0111 if specified, or determine next number
    if latest_customer:
        last_num = int(latest_customer.Customer_ID[4:])
        new_num = max(last_num + 1, 111)  # Ensure it starts at least from 111
    else:
        new_num = 111
    
    customer_id = f"CUST{new_num:04d}"
      # Create new customer
    new_customer = MasterCustomerData(
        Customer_ID=customer_id,
        Name=details.name,
        Fathers_Name=details.fathers_name,
        DOB=details.dob,
        Age=details.age,
        Gender=details.gender,
        Marital_Status=details.marital_status,
        Address=details.address,
        City=details.city,
        State=details.state,
        Pincode=details.pincode,
        Mobile=details.mobile,
        Alternate_Mobile=details.alternate_mobile,
        Email=details.email,
        Nationality=details.nationality,
        Customer_Since=datetime.now().date()
    )
    
    try:
        db.add(new_customer)
        db.commit()
        db.refresh(new_customer)
        
        return {
            "message": "Customer created successfully",
            "customer_id": customer_id,
            "details": {
                "name": new_customer.Name,
                "email": new_customer.Email,
                "mobile": str(new_customer.Mobile),
                "customer_since": new_customer.Customer_Since.isoformat()
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create customer: {str(e)}"
        )

@app.post("/api/users/{customer_id}/employment-details",
         tags=["ExecuteFunction"],
         operation_id="AddEmploymentDetails")
async def add_employment_details(
    customer_id: str,
    details: EmploymentDetailsRequest,
    db: Session = Depends(get_db)
):
    """
    Add employment details for an existing customer.
    
    Parameters:
    - customer_id: Customer ID to add employment details for
    - details: Employment details
    - db: Database session dependency
    
    Returns:
    - Dict: Added employment details
    """
    # Verify customer exists
    customer = db.query(MasterCustomerData).filter_by(Customer_ID=customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Create employment info
    employment = EmploymentInfo(
        Customer_ID=customer_id,
        Designation=details.designation,
        Monthly_Income=int(details.monthly_income),
        Employment_Status="Active",  # Default values
        Income_Verification="Pending"
    )
    
    try:
        db.add(employment)
        db.commit()
        db.refresh(employment)
        
        return {
            "message": "Employment details added successfully",
            "customer_id": customer_id,
            "details": {
                "designation": employment.Designation,
                "monthly_income": float(employment.Monthly_Income),
                "status": employment.Employment_Status,
                "verification": employment.Income_Verification
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add employment details: {str(e)}"
        )

@app.post("/api/users/{customer_id}/loan-info",
         tags=["ExecuteFunction"],
         operation_id="AddLoanInfo")
async def add_loan_info(
    customer_id: str,
    details: LoanApplicationRequest,
    db: Session = Depends(get_db)
):
    """
    Add loan application information for a customer.
    
    Parameters:
    - customer_id: Customer ID to add loan info for
    - details: Loan application details
    - db: Database session dependency
    
    Returns:
    - Dict: Added loan application details
    """
    # Verify customer exists
    customer = db.query(MasterCustomerData).filter_by(Customer_ID=customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Create loan info
    loan = LoanInfo(
        Customer_ID=customer_id,
        Loan_Required=details.loan_required,
        Loan_Amount=int(details.loan_amount),
        Loan_Purpose="Home",  # Always set to Home
        Application_Date=details.application_date or datetime.now().date(),
        Loan_Status=details.loan_status,
        Collateral_Required="documents"  # Always set to documents
    )
    
    try:
        db.add(loan)
        db.commit()
        db.refresh(loan)
        
        return {
            "message": "Loan application added successfully",
            "customer_id": customer_id,
            "details": {
                "loan_amount": float(loan.Loan_Amount),
                "loan_purpose": loan.Loan_Purpose,
                "application_date": loan.Application_Date.isoformat(),
                "status": loan.Loan_Status,
                "collateral": loan.Collateral_Required
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add loan information: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENV", "dev") == "dev"
    )
