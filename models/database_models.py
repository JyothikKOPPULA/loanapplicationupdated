from sqlalchemy import Column, String, Integer, Float, Date, DateTime, ForeignKey, Text, BigInteger, DECIMAL
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class MasterCustomerData(Base):
    __tablename__ = "Master_Customer_Data"

    Customer_ID = Column(String(20), primary_key=True)
    Name = Column(String(100))
    Fathers_Name = Column(String(100))
    DOB = Column(Date)
    Age = Column(Integer)
    Gender = Column(String(10))
    Marital_Status = Column(String(20))
    Address = Column(Text)
    City = Column(String(50))
    State = Column(String(50))
    Pincode = Column(Integer)
    Mobile = Column(BigInteger)
    Alternate_Mobile = Column(BigInteger)
    Email = Column(String(100))
    PAN = Column(String(20))
    Aadhaar = Column(BigInteger)
    Nationality = Column(String(50))
    Customer_Since = Column(Date)
    Risk_Category = Column(String(20))
    Fraud_Flag = Column(String(20))
    KYC_Status = Column(String(20))
    Customer_Type = Column(String(50))
    Annual_Income_Range = Column(String(50))

    # Relationships
    employment_info = relationship("EmploymentInfo", back_populates="customer")
    bank_info = relationship("BankInfo", back_populates="customer")
    loan_info = relationship("LoanInfo", back_populates="customer")
    transaction_history = relationship("TransactionHistory", back_populates="customer")
    audit_log = relationship("AuditLog", back_populates="customer")

class EmploymentInfo(Base):
    __tablename__ = "Employment_Info"

    Customer_ID = Column(String(20), ForeignKey('Master_Customer_Data.Customer_ID'), primary_key=True)
    Employment_Type = Column(String(50))
    Employment_Category = Column(String(50))
    Employer_Name = Column(String(100))
    Designation = Column(String(100))
    Work_Address = Column(Text)
    Work_Experience_Years = Column(Integer)
    Monthly_Income = Column(Integer)
    Other_Income = Column(Integer)
    Total_Monthly_Income = Column(Integer)
    Income_Verification = Column(String(50))
    Employment_Status = Column(String(50))
    Employer_Contact = Column(BigInteger)
    HR_Email = Column(String(100))
    Joining_Date = Column(Date)
    Previous_Employer = Column(String(100))

    # Relationship
    customer = relationship("MasterCustomerData", back_populates="employment_info")

class BankInfo(Base):
    __tablename__ = "Bank_Info"

    Customer_ID = Column(String(20), ForeignKey('Master_Customer_Data.Customer_ID'), primary_key=True)
    Bank_Name = Column(String(100))
    Account_Number = Column(String(30))
    IFSC = Column(String(20))
    Account_Type = Column(String(20))
    Account_Balance = Column(DECIMAL(15,2))
    Account_Opening_Date = Column(Date)
    Branch_Name = Column(String(100))
    Branch_Code = Column(String(20))
    Relationship_Manager = Column(String(100))
    Customer_Category = Column(String(50))
    Debit_Card_Status = Column(String(20))
    Internet_Banking = Column(String(20))
    Mobile_Banking = Column(String(20))
    Average_Monthly_Balance = Column(DECIMAL(15,2))
    Account_Status = Column(String(20))

    # Relationship
    customer = relationship("MasterCustomerData", back_populates="bank_info")

class LoanInfo(Base):
    __tablename__ = "Loan_Info"

    Customer_ID = Column(String(20), ForeignKey('Master_Customer_Data.Customer_ID'), primary_key=True)
    Loan_Required = Column(String(10))
    Loan_Amount = Column(Integer)
    Loan_Purpose = Column(String(50))
    EMI = Column(DECIMAL(10,2))
    Interest_Rate = Column(DECIMAL(5,2))
    Tenure_Months = Column(Integer)
    Application_Date = Column(Date)
    Loan_Status = Column(String(50))
    Credit_Score = Column(Integer)
    Collateral_Required = Column(String(10))
    Processing_Fee = Column(DECIMAL(10,2))
    Loan_Type = Column(String(50))
    Repayment_Method = Column(String(50))
    Insurance_Required = Column(String(10))
    Document_Verifier_ID = Column(String(50))
    Document_Verifier_Name = Column(String(100))
    Field_Agent_ID = Column(String(50))
    Field_Agent_Name = Column(String(100))
    Bank_Manager_ID = Column(String(50))
    Bank_Manager_Name = Column(String(100))
    Loan_Officer_ID = Column(String(50))
    Loan_Officer_Name = Column(String(100))

    # Relationship
    customer = relationship("MasterCustomerData", back_populates="loan_info")

class TransactionHistory(Base):
    __tablename__ = "Transaction_History"

    Customer_ID = Column(String(20), ForeignKey('Master_Customer_Data.Customer_ID'), primary_key=True)
    Transaction_Date = Column(Date)
    Transaction_Type = Column(String(20))
    Amount = Column(DECIMAL(10,2))
    Description = Column(Text)
    Transaction_ID = Column(String(30))
    Channel = Column(String(50))
    Status = Column(String(20))

    # Relationship
    customer = relationship("MasterCustomerData", back_populates="transaction_history")

class AuditLog(Base):
    __tablename__ = "Audit_Log"

    Customer_ID = Column(String(20), ForeignKey('Master_Customer_Data.Customer_ID'), primary_key=True)
    Audit_Date = Column(Date)
    Audit_Type = Column(String(100))
    Audit_Status = Column(String(50))
    Auditor_ID = Column(String(50))
    Auditor_Name = Column(String(100))
    Remarks = Column(Text)
    Follow_Up_Required = Column(String(10))
    Risk_Score = Column(Integer)
    Next_Review_Date = Column(Date)

    # Relationship
    customer = relationship("MasterCustomerData", back_populates="audit_log")

class BankEmployees(Base):
    __tablename__ = "Bank_Employees"

    Employee_ID = Column(String(50), primary_key=True)
    Name = Column(String(100))
    Role = Column(String(50))
    Email = Column(String(100))
    Phone = Column(BigInteger)
    Branch = Column(String(100))
    Employee_Code = Column(String(20))
    Department = Column(String(50))
