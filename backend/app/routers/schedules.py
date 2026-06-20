from fastapi import APIRouter

router = APIRouter(prefix="/campaigns", tags=["schedules"])

@router.put("/{id}/schedule")
def replace_schedule(id: str):
    return

@router.get("/{id}/schedule")
def get_schedule(id: str):
    return

@router.delete("/{id}/schedule")
def delete_schedule(id: str):
    return delete_schedule(id)