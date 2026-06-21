from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, Depends, APIRouter
from requests.packages import target

from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import Campaign, RuleEvalLog
from backend.app.schemas import CampaignOut, CampaignCreate, CampaignUpdate

from backend.app.rules import RULES_LIST, Rule

router = APIRouter(prefix="/campaigns", tags=["campaigns"])

def get_campaign_local(id: UUID, db: Session):
    campaign = db.get(Campaign, id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Кампания не найдена")
    return campaign

@router.post("/", response_model=CampaignOut)
def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_db)):
    campaign = Campaign(**campaign.model_dump())
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign

@router.get("/", response_model=list[CampaignOut])
def campaign_list(db: Session = Depends(get_db)):
    return db.query(Campaign).all()


@router.get("/{id}", response_model=CampaignOut)
def get_campaign(id: UUID, db: Session = Depends(get_db)):
    return get_campaign_local(id, db)

@router.patch("/{id}", response_model=CampaignOut)
def patch_campaign(id: UUID, data : CampaignUpdate, db: Session = Depends(get_db)):
    campaign = get_campaign_local(id, db)
    data = data.model_dump(exclude_unset=True)

    for field, value in data.items():
        setattr(campaign, field, value)

    db.commit()
    db.refresh(campaign)
    return campaign

@router.post("/{campaign_id}/evaluate")
def evaluate(campaign_id: UUID, db: Session = Depends(get_db)):
    campaign = get_campaign_local(campaign_id, db)

    for rule in RULES_LIST:
        current = rule.evaluate(campaign, datetime.now())
        if current:
            return current
    return ('active', 'Ограничений нет')