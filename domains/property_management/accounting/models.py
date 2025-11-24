# Enable postponed evaluation of annotations to allow forward references in type hints
# This resolves type checker errors when using class types (e.g., Address) in Optional annotations
from __future__ import annotations

from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class GLAccount(BaseModel):
    id: int
    AccountNumber: Optional[str]
    Name: Optional[str]
    Description: Optional[str]
    Type: Optional[str]
    SubType: Optional[str]
    IsDefaultGLAccount: Optional[bool]
    DefaultAccountName: Optional[str]
    IsContraAccount: Optional[bool]
    IsBankAccount: Optional[bool]
    CashFlowClassification: Optional[str]
    ExcludeFromCashBalance: Optional[bool]
    SubAccounts: Optional[List]
    IsActive: bool
    ParentGLAccountId: Optional[int]


class CheckPrintingInfo(BaseModel):
    EnableRemoteCheckPrinting: Optional[bool]
    EnableLocalCheckPrinting: Optional[bool]
    CheckLayoutType: Optional[str]
    SignatureHeading: Optional[str]
    FractionalNumber: Optional[str]
    BankInformationLine1: Optional[str]
    BankInformationLine2: Optional[str]
    BankInformationLine3: Optional[str]
    BankInformationLine4: Optional[str]
    BankInformationLine5: Optional[str]
    CompanyInformationLine1: Optional[str]
    CompanyInformationLine2: Optional[str]
    CompanyInformationLine3: Optional[str]
    CompanyInformationLine4: Optional[str]
    CompanyInformationLine5: Optional[str]


class ElectronicPayment(BaseModel):
    DebitTransactionLimit: Optional[int]
    CreditTransactionLimit: Optional[int]
    DebitMonthlyLimit: Optional[int]
    CreditMonthlyLimit: Optional[int]
    ResidentEFTConvenienceFeeAmount: Optional[int]
    ResidentCreditCardConvenienceFeeAmount: Optional[int]
    CreditCardServiceFeePercentage: Optional[int]
    IsCreditCardServiceFeePaidByResident: Optional[bool]


class BankAccount(BaseModel):
    Id: int
    GLAccounts: Optional[GLAccount]
    CheckPrintingInfo: Optional[CheckPrintingInfo]
    ElectronicPayments: Optional[ElectronicPayment]
    Name: Optional[str]
    Description: Optional[str]
    BankAccountType: Optional[str]
    Country: Optional[str]
    AccountNumber: Optional[str]
    RoutingNumber: Optional[str]
    IsActive: Optional[bool]
    Balance: Optional[float]
    AccountNumberUnmasked: Optional[str]


class AccountingEntityUnit(BaseModel):
    id: int
    href: Optional[int]


class AccountingEntity(BaseModel):
    id: int
    AccountingEntityType: Optional[str]
    Href: Optional[str]
    Unit: Optional[AccountingEntityUnit]


class BillMarkup(BaseModel):
    Amount: float
    Type: str


class BillLineItems(BaseModel):
    Id: int
    AccountingEntity: Optional[AccountingEntity]
    GLAccount: Optional[GLAccount]
    Amount: Optional[float]
    Markup: Optional[BillMarkup]
    Memo: Optional[str]


class Bill(BaseModel):
    Id: int
    Date: datetime
    DueDate: datetime
    PaidDate: Optional[datetime]
    Memo: Optional[str]
    VendorId: int
    WorkOrderId: Optional[int]
    ReferenceNumber: Optional[str]
    ApprovalStatus: Optional[str]
    Lines: Optional[List[BillLineItems]]


class BillPayments(BaseModel):
    Id: int
    BankAccountId: int
    EntryDate: datetime
    Memo: Optional[str]
    CheckNumber: Optional[str]
    PaidBillIds: Optional[List[int]]
    AppliedVendorCredits: Optional[List[object]]
    Lines: Optional[List[BillLineItems]]
