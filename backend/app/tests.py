import requests

res = requests.post("http://127.0.0.1:/api/campaigns")
res = requests.get("http://127.0.0.1:/api/campaigns")
res = requests.get("http://127.0.0.1:/api/campaigns/id")
res = requests.patch("http://127.0.0.1:/api/campaigns/id")

res = requests.put("http://127.0.0.1:/api/campaigns/id/schedule")
res = requests.get("http://127.0.0.1:/api/campaigns/id/schedule")
res = requests.delete("http://127.0.0.1:/api/campaigns/id/schedule")

res = requests.post("http://127.0.0.1:/api/campaigns/id/evaluate")



# 4. API эндпоинты
# POST /campaigns — создание кампании
# GET /campaigns — список кампаний с пагинацией
# GET /campaigns/{id} — получение кампании
# PATCH /campaigns/{id} — обновление кампании
# PUT /campaigns/{id}/schedule — установить расписание (заменяет все слоты)
# GET /campaigns/{id}/schedule — получить расписание
# DELETE /campaigns/{id}/schedule — удалить расписание
# POST /campaigns/{id}/evaluate — вычислить target_status по правилам