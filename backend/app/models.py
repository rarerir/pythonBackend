from sqlalchemy import *
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base

import enum
class CampaignStatusEnum(str, enum.Enum):
    active = "active"
    paused = "paused"

# модель компании
class Campaign(Base):
    __tablename__ = "campaign"

    id = Column(UUID(as_uuid=True), primary_key=True,
                server_default=text("gen_random_uuid()"))
    name = Column(Text, nullable=False)

    current_status = Column(
        Enum(CampaignStatusEnum, name="campaign_status", create_type=False),
        nullable=False,
        server_default="paused"
    )
    target_status = Column(
        Enum(CampaignStatusEnum, name="campaign_status", create_type=False),
        nullable=False,
        server_default="paused"
    )

    is_managed = Column(Boolean, nullable=False, server_default=text("false"))
    budget_limit = Column(Numeric(12, 2))          # NULLable
    spend_today = Column(Numeric(12, 2), nullable=False, server_default=text("0"))
    stock_days_left = Column(Integer)              # NULLable
    stock_days_min = Column(Integer)               # NULLable
    schedule_enabled = Column(Boolean, nullable=False, server_default=text("false"))
    created_at = Column(DateTime(timezone=True), nullable=False,
                        server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False,
                        server_default=func.now())


    schedules = relationship("CampaignSchedule", back_populates="campaign",
                             cascade="all, delete-orphan")
    rule_triggers = relationship("RuleEvalLog", back_populates="campaign",
                                 cascade="all, delete-orphan")

# модель расписания
class CampaignSchedule(Base):
    __tablename__ = "campaign_schedule"

    id = Column(UUID(as_uuid=True), primary_key=True,
                server_default=text("gen_random_uuid()"))
    campaign_id = Column(UUID(as_uuid=True),
                         ForeignKey("campaign.id", ondelete="CASCADE"),
                         nullable=False)
    day_of_week = Column(SmallInteger, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    __table_args__ = (
        CheckConstraint("day_of_week BETWEEN 0 AND 6", name="day_of_week_check"),
        CheckConstraint("start_time < end_time", name="start_time_before_end"),
    )


    campaign = relationship("Campaign", back_populates="schedules")

# модель логов
class RuleEvalLog(Base):
    __tablename__ = "rule_evaluation_log"

    id = Column(UUID(as_uuid=True), primary_key=True,
                server_default=text("gen_random_uuid()"))
    campaign_id = Column(UUID(as_uuid=True),
                         ForeignKey("campaign.id", ondelete="CASCADE"),
                         nullable=False)
    triggered_rule = Column(Text)                 # NULLable
    previous_target = Column(
        Enum(CampaignStatusEnum, name="campaign_status", create_type=False)
    )
    new_target = Column(
        Enum(CampaignStatusEnum, name="campaign_status", create_type=False)
    )
    context = Column(Text, nullable=False, server_default="{}")  # JSONB как Text
    created_at = Column(DateTime(timezone=True), nullable=False,
                        server_default=func.now())


    campaign = relationship("Campaign", back_populates="rule_triggers")