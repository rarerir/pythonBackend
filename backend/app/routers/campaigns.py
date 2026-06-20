from fastapi import FastAPI, HTTPException, Depends, APIRouter
from sqlalchemy import UUID
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import Campaign
from backend.app.schemas import CampaignOut

router = APIRouter(prefix="/campaigns", tags=["campaigns"])

@router.post("/")
def create_campaign(campaign: Campaign):
    return {"code" : 200}

@router.get("/")
def campaign_list():
    return list


@router.get("/{id}", response_model=CampaignOut)
def get_campaign(id: str, db: Session = Depends(get_db)):
    try:
        campaign_id = UUID(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный формат ID")

    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Кампания не найдена")

    return campaign

@router.patch("/{id}")
def patch_campaign(id: str):
    return {"code" : 200}

@router.post("/{id}/evaluate")
def eval_status(id: str):
    return status