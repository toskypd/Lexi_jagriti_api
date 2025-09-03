from typing import Optional
from pydantic import BaseModel, Field
from datetime import date
from enum import Enum


class SearchType(str, Enum):
    """Search types for E-Jagriti API case searches.

    Each enum maps to a numeric serchType value:
    1 = CASE_NUMBER
    2 = COMPLAINANT 
    3 = RESPONDENT
    4 = COMPLAINANT_ADVOCATE
    5 = RESPONDENT_ADVOCATE
    6 = INDUSTRY_TYPE
    7 = JUDGE
    """
    CASE_NUMBER = "CASE NUMBER"
    COMPLAINANT = "COMPLAINANT / APPELLANT /PETITIONER"
    RESPONDENT = "RESPONDENT / OPPOSITE PARTY"
    COMPLAINANT_ADVOCATE = "COMPLAINANT / APPELLANT /PETITIONER ADVOCATE"
    RESPONDENT_ADVOCATE = "RESPONDENT / OPPOSITE PARTY ADVOCATE"
    INDUSTRY_TYPE = "INDUSTRY TYPE"
    JUDGE = "JUDGE"


class OrderType(str, Enum):
    DAILY_ORDER = "DAILY ORDER"


class CommissionType(str, Enum):
    DCDRC = "DCDRC"

# Request Models


class CaseSearchRequest(BaseModel):
    state_id: str = Field(..., description="State ID", examples=["11290000"])
    commission_id: str = Field(..., description="Commission ID", examples=[
                               "15290525"])
    search_value: str = Field(..., description="Search value")
    from_date: Optional[date] = Field(
        default=date(2025, 1, 1), description="From date for case filing (optional)")
    to_date: Optional[date] = Field(
        default=None, description="To date for case filing (optional)")


class CaseNumberSearchRequest(CaseSearchRequest):
    """Request model for case number search with complete example"""
    search_value: str = Field(
        ..., description="Case number to search for", examples=[
            "DC/AB4/525/CC/72/2025"
        ]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "state_id": "11290000",
                "commission_id": "15290525",
                "search_value": "DC/AB4/525/CC/72/2025",
                "from_date": "2025-01-01",
                "to_date": "2025-09-03"
            }
        }


class ComplainantSearchRequest(CaseSearchRequest):
    search_value: str = Field(
        ..., description="Complainant/Appellant/Petitioner name", examples=["KUMAR"])


class RespondentSearchRequest(CaseSearchRequest):
    search_value: str = Field(
        ..., description="Respondent/Opposite Party name", examples=["FLIPKART"])


class ComplainantAdvocateSearchRequest(CaseSearchRequest):
    search_value: str = Field(
        ..., description="Complainant/Appellant/Petitioner Advocate name", examples=["SHARMA"])


class RespondentAdvocateSearchRequest(CaseSearchRequest):
    search_value: str = Field(
        ..., description="Respondent/Opposite Party Advocate name", examples=["GUPTA"])


class IndustryTypeSearchRequest(CaseSearchRequest):
    search_value: str = Field(..., description="Industry type/category",
                              examples=["INSURANCE"])


class JudgeSearchRequest(CaseSearchRequest):
    search_value: str = Field(..., description="Judge name", examples=[
                              "SHARMA"])

# Response Models


class CaseResponse(BaseModel):
    case_number: str
    case_stage: str
    filing_date: str
    complainant: str
    complainant_advocate: str
    respondent: str
    respondent_advocate: str
    document_link: str


class StateResponse(BaseModel):
    state_id: str
    state_name: str


class CommissionResponse(BaseModel):
    commission_id: str
    commission_name: str
    state_id: str


class ErrorResponse(BaseModel):
    error: str
    message: str
    status_code: int

# Internal Models for API communication


class JagritiSearchPayload(BaseModel):
    """Payload structure that matches E-Jagriti API exactly based on real API calls"""
    commissionId: int  # Numeric commission ID
    dateRequestType: int = 1  # Always 1 for CASE_FILING_DATE
    fromDate: str  # YYYY-MM-DD format (ISO)
    toDate: str    # YYYY-MM-DD format (ISO)
    judgeId: str = ""  # Empty string for judge ID
    orderType: int = 1  # Always 1 for DAILY_ORDER
    # 1-7 for different search types (note: 'serch' not 'search')
    serchType: int
    serchTypeValue: str  # The actual search value
