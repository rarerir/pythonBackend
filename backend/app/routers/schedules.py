from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import CampaignSchedule, Campaign
from backend.app.schemas import ScheduleCreate, ScheduleOut

router = APIRouter(prefix="/campaigns", tags=["schedules"])

def compcheck(campaign_id: UUID, db: Session):
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Кампания не найдена")

@router.put("/{campaign_id}/schedule", response_model=list[ScheduleOut])
def replace_schedule(campaign_id: UUID, data: list[ScheduleCreate], db: Session = Depends(get_db)):
    compcheck(campaign_id, db)
    db.query(CampaignSchedule).filter_by(campaign_id=campaign_id).delete()

    new_slots = []
    for slot_data in data:
        slot = CampaignSchedule(campaign_id=campaign_id, **slot_data.model_dump())
        db.add(slot)
        new_slots.append(slot)

    db.commit()
    for slot in new_slots:
        db.refresh(slot)
    return new_slots

@router.get("/{campaign_id}/schedule", response_model=list[ScheduleOut])
def get_schedule(campaign_id: UUID, db: Session = Depends(get_db)):
    compcheck(campaign_id, db)
    return db.query(CampaignSchedule).filter_by(campaign_id=campaign_id).all()

@router.delete("/{campaign_id}/schedule")
def delete_schedule(campaign_id: UUID, db: Session = Depends(get_db)):
    compcheck(campaign_id, db)
    db.query(CampaignSchedule).filter_by(campaign_id=campaign_id).delete()

    db.commit()
    return