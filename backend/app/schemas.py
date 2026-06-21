from pydantic import BaseModel, UUID4, Field
from datetime import datetime, time
from decimal import Decimal
from enum import Enum

class CampaignStatusEnum(str, Enum):
    active = "active"
    paused = "paused"

# кампании
class CampaignBase(BaseModel):
    name: str
    target_status: CampaignStatusEnum = CampaignStatusEnum.paused
    is_managed: bool = False
    budget_limit: Decimal | None = None
    spend_today: Decimal = Decimal("0")
    stock_days_left: int | None = None
    stock_days_min: int | None = None
    schedule_enabled: bool = False
    current_status: CampaignStatusEnum = CampaignStatusEnum.paused

class CampaignCreate(CampaignBase):
    pass

class CampaignUpdate(BaseModel):
    name: str | None = None
    target_status: CampaignStatusEnum | None = None
    is_managed: bool | None = None
    budget_limit: Decimal | None = None
    spend_today: Decimal | None = None
    stock_days_left: int | None = None
    stock_days_min: int | None = None
    schedule_enabled: bool | None = None
    current_status: CampaignStatusEnum | None = None

class CampaignOut(CampaignBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}

# расписания
class ScheduleBase(BaseModel):
    day_of_week: int = Field(ge=0, le=6)
    start_time: time
    end_time: time

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleOut(ScheduleBase):
    id: UUID4
    campaign_id: UUID4
    model_config = {"from_attributes": True}

# логи
class HistoryOut(BaseModel):
    id: UUID4
    campaign_id: UUID4
    triggered_rule: str | None = None
    previous_target: CampaignStatusEnum | None = None
    new_target: CampaignStatusEnum | None = None
    context: dict = {}
    created_at: datetime
    model_config = {"from_attributes": True}