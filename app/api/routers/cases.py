from typing import List
from fastapi import APIRouter, Depends, HTTPException

from models import (
    CaseNumberSearchRequest, ComplainantSearchRequest, RespondentSearchRequest,
    ComplainantAdvocateSearchRequest, RespondentAdvocateSearchRequest,
    IndustryTypeSearchRequest, JudgeSearchRequest, CaseResponse, SearchType
)
from services import JagritiService
from utils import validate_search_value
from app.deps import get_jagriti_service


router = APIRouter(tags=["cases"])


@router.post("/by-case-number", response_model=List[CaseResponse])
async def search_by_case_number(request: CaseNumberSearchRequest, service: JagritiService = Depends(get_jagriti_service)):
    if not validate_search_value(request.search_value):
        raise HTTPException(status_code=400, detail="Invalid search value")
    try:
        return await service.search_cases(request, SearchType.CASE_NUMBER)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Search failed")


@router.post("/by-complainant", response_model=List[CaseResponse])
async def search_by_complainant(request: ComplainantSearchRequest, service: JagritiService = Depends(get_jagriti_service)):
    if not validate_search_value(request.search_value):
        raise HTTPException(status_code=400, detail="Invalid search value")
    try:
        return await service.search_cases(request, SearchType.COMPLAINANT)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Search failed")


@router.post("/by-respondent", response_model=List[CaseResponse])
async def search_by_respondent(request: RespondentSearchRequest, service: JagritiService = Depends(get_jagriti_service)):
    if not validate_search_value(request.search_value):
        raise HTTPException(status_code=400, detail="Invalid search value")
    try:
        return await service.search_cases(request, SearchType.RESPONDENT)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Search failed")


@router.post("/by-complainant-advocate", response_model=List[CaseResponse])
async def search_by_complainant_advocate(request: ComplainantAdvocateSearchRequest, service: JagritiService = Depends(get_jagriti_service)):
    if not validate_search_value(request.search_value):
        raise HTTPException(status_code=400, detail="Invalid search value")
    try:
        return await service.search_cases(request, SearchType.COMPLAINANT_ADVOCATE)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Search failed")


@router.post("/by-respondent-advocate", response_model=List[CaseResponse])
async def search_by_respondent_advocate(request: RespondentAdvocateSearchRequest, service: JagritiService = Depends(get_jagriti_service)):
    if not validate_search_value(request.search_value):
        raise HTTPException(status_code=400, detail="Invalid search value")
    try:
        return await service.search_cases(request, SearchType.RESPONDENT_ADVOCATE)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Search failed")


@router.post("/by-industry-type", response_model=List[CaseResponse])
async def search_by_industry_type(request: IndustryTypeSearchRequest, service: JagritiService = Depends(get_jagriti_service)):
    if not validate_search_value(request.search_value):
        raise HTTPException(status_code=400, detail="Invalid search value")
    try:
        return await service.search_cases(request, SearchType.INDUSTRY_TYPE)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Search failed")


@router.post("/by-judge", response_model=List[CaseResponse])
async def search_by_judge(request: JudgeSearchRequest, service: JagritiService = Depends(get_jagriti_service)):
    if not validate_search_value(request.search_value):
        raise HTTPException(status_code=400, detail="Invalid search value")
    try:
        return await service.search_cases(request, SearchType.JUDGE)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Search failed")
