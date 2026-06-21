import uvicorn
from fastapi import FastAPI

from backend.app.routers import campaigns, schedules

app = FastAPI()
app.include_router(campaigns.router)
app.include_router(schedules.router)

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000)