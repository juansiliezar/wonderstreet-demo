# Enable postponed evaluation of annotations to allow forward references in type hints
# This resolves type checker errors when using class types (e.g., Address) in Optional annotations
from __future__ import annotations

from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

from ..rentals import Appliance, PhoneNumber, Address, TaxInformation


class TaskSubCategory(BaseModel):
    Id: int
    Name: Optional[str]


class TaskCategory(BaseModel):
    Id: int
    Name: Optional[str]
    Href: Optional[str]
    SubCategory: Optional[TaskSubCategory]


class UnitAgreement(BaseModel):
    Id: int
    Type: str
    Href: Optional[str]


class UserEntity(BaseModel):
    Type: str
    Id: Optional[int]
    FirstName: Optional[str]
    LastName: Optional[str]
    IsCompany: bool
    Href: Optional[str]


class Property(BaseModel):
    Id: int
    Type: str
    Href: Optional[str]


class Task(BaseModel):
    Id: int
    TaskType: str
    Category: Optional[TaskCategory]
    Title: Optional[str]
    Description: Optional[str]
    Property: Optional[Property]
    UnitId: Optional[int]
    UnitAgreement: Optional[UnitAgreement]
    RequestedByUserEntity: Optional[UserEntity]
    AssignedToUserId: int
    TaskStatus: str
    Priority: str
    DueDate: Optional[datetime]
    CreatedDateTime: datetime
    LastUpdatedDateTime: Optional[datetime]


class ResidentRequest(BaseModel):
    Id: int
    Category: Optional[TaskCategory]
    Title: Optional[str]
    Description: Optional[str]
    Property: Optional[Property]
    UnitId: int
    UnitAgreement: Optional[UnitAgreement]
    RequestedByUserEntity: Optional[UserEntity]
    AssignedToUserId: Optional[int]
    TaskStatus: str
    Priority: str
    DueDate: Optional[datetime]
    CreatedDateTime: datetime
    LastUpdatedDateTime: Optional[datetime]
    Appliance: Optional[Appliance]
    IsEntryPermittedByResident: Optional[bool]
    DoesResidentHavePets: Optional[bool]
    ResidentEntryNotes: Optional[str]


class VendorInsuranceDetails(BaseModel):
    Provider: Optional[str]
    PolicyNumber: Optional[str]
    ExpirationDate: Optional[datetime]


class VendorCategory(BaseModel):
    Id: int
    Name: Optional[str]


class Vendor(BaseModel):
    Id: int
    IsCompany: bool
    IsActive: bool
    FirstName: Optional[str]
    LastName: Optional[str]
    PrimaryEmail: Optional[str]
    AlternateEmail: Optional[str]
    CompanyName: Optional[str]
    PhoneNumbers: Optional[List[PhoneNumber]]
    Website: Optional[str]
    Category: Optional[VendorCategory]
    Address: Optional[Address]
    VendorInsurance: Optional[VendorInsuranceDetails]
    Comments: Optional[str]
    AccountNumber: Optional[str]
    ExpenseGLAccountId: Optional[int]
    TaxInformation: Optional[TaxInformation]
