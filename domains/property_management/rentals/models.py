# Enable postponed evaluation of annotations to allow forward references in type hints
# This resolves type checker errors when using class types (e.g., Address) in Optional annotations
from __future__ import annotations

from typing import Optional, List
from pydantic import BaseModel
from datetime import date, datetime

from ..accounting import GLAccount


class Address(BaseModel):
    AddressLine1: str
    AddressLine2: Optional[str]
    AddressLine3: Optional[str]
    City: str
    State: str
    PostalCode: str
    Country: str


class PhoneNumber(BaseModel):
    Number: str
    Type: str


class RentalManager(BaseModel):
    id: int
    FirstName: str
    LastName: str
    CompanyName: Optional[str]
    IsCompany: bool
    ProfilePhotoUrl: Optional[str]
    PhoneNumbers: List[PhoneNumber]


class Property(BaseModel):
    Id: int
    Name: str
    StructureDescription: Optional[str]
    NumberUnits: int
    IsActive: bool
    OperatingBankAccountId: int
    Reserve: Optional[float]
    Address: Address
    YearBuilt: int
    RentalType: Optional[str]
    RentalSubType: Optional[str]
    RentalManager: Optional[RentalManager]


class Unit(BaseModel):
    Id: int
    PropertyId: int
    BuildingName: Optional[str]
    UnitNumber: str
    Description: Optional[str]
    MarketRent: Optional[int]
    Address: Address
    UnitBedrooms: Optional[str]
    UnitBathrooms: Optional[str]
    IsUnitListed: Optional[bool]
    IsUnitOccupied: Optional[bool]


class Amenities(BaseModel):
    Features: Optional[List[str]]
    IncludedInRent: Optional[List[str]]


class Image(BaseModel):
    Id: int
    Description: Optional[str]
    PhysicalFileName: Optional[str]
    Provider: Optional[str]
    ShowInListing: Optional[bool]


class Appliance(BaseModel):
    Id: int
    PropertyId: int
    UnitId: int
    Name: Optional[str]
    Make: Optional[str]
    Model: Optional[str]
    Description: Optional[str]
    WarrantyEndDate: Optional[datetime]


class ApplianceServiceHistory(BaseModel):
    Id: int
    ServiceType: str
    Date: Optional[datetime]
    Details: Optional[str]


class TaxInformation(BaseModel):
    TaxPayerIdType: Optional[str]
    TaxPayerId: Optional[str]
    TaxPayerName1: Optional[str]
    TaxPayerName2: Optional[str]
    IncludeIn1099: Optional[bool]
    Address: Address


class Owner(BaseModel):
    id: int
    IsCompany: Optional[bool]
    IsActive: Optional[bool]
    FirstName: Optional[str]
    LastName: Optional[str]
    PhoneNumbers: Optional[List[PhoneNumber]]
    Email: str
    AlternateEmail: Optional[str]
    Comment: Optional[str]
    Address: Optional[Address]
    ManagementAgreementStartDate: Optional[datetime]
    ManagementAgreementEndDate: Optional[datetime]
    CompanyName: Optional[str]
    PropertyIds: List[int]
    TaxInformation: Optional[TaxInformation]


class EmergencyContact(BaseModel):
    Name: Optional[str]
    RelationshipDescription: Optional[str]
    Phone: Optional[PhoneNumber]
    Email: Optional[str]


class LeaseAccountDetails(BaseModel):
    SecurityDeposit: Optional[int]
    Rent: Optional[int]


class Cosigner(BaseModel):
    Id: int
    FirstName: str
    LastName: Optional[str]
    Email: Optional[str]
    AlternateEmail: Optional[str]
    PhoneNumbers: Optional[List[PhoneNumber]]
    CreatedDateTime: datetime
    Address: Optional[Address]
    MailingPreference: Optional[str]


class MoveOutData(BaseModel):
    TenantId: id
    MoveOutDate: Optional[datetime]
    NoticeGivenDate: Optional[datetime]


class Lease(BaseModel):
    Id: int
    PropertyId: int
    UnitId: int
    UnitNumber: str
    LeaseFromDate: datetime
    LeaseToDate: datetime
    LeaseType: Optional[str]
    LeaseStatus: str
    IsEvictionPending: Optional[bool]
    TermType: Optional[str]
    RenewalOfferStatus: Optional[str]
    CurrentTenants: Optional[List[Tenant]]
    CurrentNumberOfOccupants: Optional[int]
    AccountDetails: LeaseAccountDetails
    Cosigners: Optional[List[Cosigner]]
    AutomaticallyMoveOutTenants: Optional[bool]
    CreatedDateTime: datetime
    LastUpdatedDateTime: datetime
    MoveOutData: Optional[List[MoveOutData]]
    PaymentDueDay: int
    Tenants: Optional[List[Tenant]]


class Tenant(BaseModel):
    id: int
    FirstName: str
    LastName: str
    Email: str
    AlternateEmail: Optional[str]
    PhoneNumbers: Optional[List[PhoneNumber]]
    CreatedDateTime: datetime
    EmergencyContact: Optional[EmergencyContact]
    DateOfBirth: Optional[datetime]
    SMSOptInStatus: Optional[str]
    Address: Optional[Address]
    AlternateAddress: Optional[Address]
    MailingPreference: Optional[str]
    Leases: Optional[List[Lease]]
    Comment: Optional[str]
    TaxId: Optional[str]


class JournalLineItems(BaseModel):
    GLAccount: Optional[GLAccount]
    Amount: float
    IsCashPosting: bool
    ReferenceNumber: Optional[str]
    Memo: Optional[str]
    PropertyId: int
    UnitId: Optional[int]


class TransactionJournal(BaseModel):
    Memo: Optional[int]
    Lines: Optional[List[JournalLineItems]]


class Transaction(BaseModel):
    Id: int
    Date: datetime
    TransactionType: Optional[str]
    TransactionTypeEnum: str
    TotalAmount: float
    CheckNumber: Optional[str]
    LeaseId: Optional[int]
    PayeeTenantId: Optional[int]
    PaymentMethod: Optional[str]
    Journal: Optional[TransactionJournal]


class ChargeLineItems(BaseModel):
    Amount: float
    GLAccountId: int


class Charge(BaseModel):
    Id: int
    Date: datetime
    TotalAmount: float
    Memo: Optional[str]
    BillId: Optional[int]
    Lines: Optional[List[ChargeLineItems]]


class PayeePayer(BaseModel):
    Id: int
    Name: Optional[str]
    Type: str
    Href: Optional[str]


class RefundLineItems(BaseModel):
    Amount: float
    GLAccountId: int


class Refund(BaseModel):
    Id: int
    Date: datetime
    Payees: Optional[List[PayeePayer]]
    Memo: Optional[str]
    CheckNumber: Optional[str]
    BankAccountId: int
    Address: Optional[Address]
    TotalAmount: float
    Lines: Optional[List[RefundLineItems]]


class RecurringTransactionLineItems(BaseModel):
    GLAccountId: int
    Amount: float


class RecurringTransaction(BaseModel):
    Id: int
    TransactionType: str
    IsExpired: bool
    RentId: Optional[int]
    OffsettingGLAccountId: Optional[int]
    Lines: Optional[List[RecurringTransactionLineItems]]
    Amount: float
    Memo: Optional[str]
    FirstOccurrenceDate: Optional[date]
    NextOccurrenceDate: datetime
    PostDaysInAdvance: int
    Frequency: str
    Duration: str


class RecurringCharge(BaseModel):
    Id: int
    LeaseId: int
    GLAccountId: Optional[int]
    RentId: Optional[int]
    Amount: float
    Memo: Optional[str]
    OccurrencesRemaining: Optional[int]
    FirstOccurrenceDate: Optional[date]
    NextOccurrenceDate: datetime
    PostDaysInAdvance: int
    Frequency: str
    Duration: str


class RecurringCredit(BaseModel):
    Id: int
    LeaseId: int
    CreditType: str
    OffsettingGLAccountId: Optional[int]
    PostingRuleGLAccountId: Optional[int]
    Lines: Optional[List[RecurringTransactionLineItems]]
    Amount: float
    OccurrencesRemaining: Optional[int]
    FirstOccurrenceDate: Optional[date]
    NextOccurrenceDate: datetime
    PostDaysInAdvance: int
    Memo: Optional[str]
    Frequency: str
    Duration: str


class RecurringPayment(BaseModel):
    Id: int
    LeaseId: int
    Payer: Optional[PayeePayer]
    PaymentMethod: str
    Lines: Optional[RecurringTransactionLineItems]
    Amount: float
    OccurrencesRemaining: Optional[int]
    FirstOccurrenceDate: date
    NextOccurrenceDate: datetime
    PostDaysInAdvance: int
    Frequency: str
    Duration: str
    Memo: Optional[str]


class OutstandingBalanceLineItems(BaseModel):
    GLAccountId: int
    TotalBalance: float


class OutstandingBalance(BaseModel):
    LeaseId: int
    PropertyId: int
    UnitId: Optional[int]
    Balance0To30Days: float
    Balance31To60Days: float
    Balance61To90Days: float
    BalanceOver90Days: float
    TotalBalance: float
    Balances: Optional[List[OutstandingBalanceLineItems]]
    PastDueEmailSentDate: Optional[datetime]
    EvictionPendingDate: Optional[datetime]
    IsNoticeGiven: bool


class PaymentSettings(BaseModel):
    PaymentsEnabled: bool


class EFTPaymentSettings(BaseModel):
    PaymentsEnabled: Optional[PaymentSettings]


class CreditCardPaymentSettings(BaseModel):
    PaymentsEnabled: Optional[PaymentSettings]
