from typing import List
from fastapi import APIRouter, Depends, HTTPException

from services import JagritiService
from models import StateResponse, CommissionResponse
from app.deps import get_jagriti_service


router = APIRouter(tags=["metadata"])


@router.get("/states", response_model=List[StateResponse])
async def get_states(service: JagritiService = Depends(get_jagriti_service)):
    try:
        return await service.get_states()
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch states")


@router.get("/commissions/{state_id}", response_model=List[CommissionResponse])
async def get_commissions(state_id: str, service: JagritiService = Depends(get_jagriti_service)):
    try:
        return await service.get_commissions(state_id)
    except Exception:
        raise HTTPException(
            status_code=500, detail="Failed to fetch commissions")
