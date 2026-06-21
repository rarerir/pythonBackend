from abc import ABC, abstractmethod
from datetime import datetime
from backend.app.models import Campaign
from schemas import CampaignStatusEnum

class Rule(ABC):
    @abstractmethod
    def evaluate(self, campaign: Campaign, current_datetime: datetime) -> CampaignStatusEnum | None:
        ...

# 1
class IsManaged(Rule):
    def evaluate(self, campaign, _):
        if not campaign.is_managed:
            return (campaign.current_status, "Управление выключено, не изменено")
        return None

# 2
class ScheduleEnabled(Rule):
    def evaluate(self, campaign, current_dt):
        if not campaign.schedule_enabled or not campaign.schedules:
            return None
        current_day = current_dt.weekday()
        current_time = current_dt.time()
        for slot in campaign.schedules:
            if slot.day_of_week == current_day and slot.start_time <= current_time <= slot.end_time:
                return None
        return ("paused", f"Текущее время {current_time:%H:%M} вне активного окна")

# 3
class LowStockRule(Rule):
    def evaluate(self, campaign, _):
        if campaign.stock_days_min is not None and campaign.stock_days_left is not None:
            if campaign.stock_days_left < campaign.stock_days_min:
                return ("paused", f"Осталось {campaign.stock_days_left} дн. при минимуме {campaign.stock_days_min} дн.")
        return None

# 4
class BudgetExceededRule(Rule):
    def evaluate(self, campaign, _):
        if campaign.budget_limit is not None and campaign.spend_today is not None:
            if campaign.spend_today >= campaign.budget_limit:
                return ("paused", f"Расход {campaign.spend_today} >= лимит {campaign.budget_limit}")
        return None


RULES_LIST = [
    IsManaged,
    ScheduleEnabled,
    LowStockRule,
    BudgetExceededRule,
    # Наивысший приоритет сверху
]
RULES_LIST = [cls() for cls in RULES_LIST]