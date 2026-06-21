from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, Depends, APIRouter

from sqlalchemy.orm import Session, Query

from backend.app.database import get_db
from backend.app.models import Campaign, RuleEvalLog
from backend.app.schemas import CampaignOut, CampaignCreate, CampaignUpdate, PaginatedHistoryResponse, CampaignSnapshot, \
    HistoryOut

from backend.app.rules import RULES_LIST

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

@router.post("/{campaign_id}/evaluate", response_model=HistoryOut)
def evaluate(campaign_id: UUID, db: Session = Depends(get_db)):
    campaign = get_campaign_local(campaign_id, db)
    target_status = "active"
    details = "Нет ограничений"
    triggered_rule_name = None

    for rule in RULES_LIST:
        current = rule.evaluate(campaign, datetime.now())
        if current:
            target_status, details = current
            triggered_rule_name = rule.__class__.__name__
            break
    campaign.target_status = target_status
    snapshot = CampaignSnapshot(
        time=datetime.now(),
        details=details,
        **CampaignOut.model_validate(campaign).model_dump(exclude={'id', 'created_at', 'updated_at'})
    )
    log = RuleEvalLog(
        campaign_id=campaign.id,
        triggered_rule=triggered_rule_name,
        previous_target=campaign.target_status,
        new_target=target_status,
        context=snapshot.model_dump(mode='json'),
        created_at=datetime.now(),
    )
    db.add(log)
    db.commit()
    db.refresh(campaign)
    return log

@router.get("/{campaign_id}/evaluation-history", response_model=PaginatedHistoryResponse)
def evaluation_history(campaign_id : UUID, limit: int = Query(10, ge=1, le=100),
                       offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Кампания не найдена")

    total = db.query(RuleEvalLog).filter_by(campaign_id=campaign_id).count()
    items = (
        db.query(RuleEvalLog)
        .filter_by(campaign_id=campaign_id)
        .order_by(RuleEvalLog.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    history_items = [HistoryOut.model_validate(item) for item in items]
    return PaginatedHistoryResponse(total=total, items=history_items)