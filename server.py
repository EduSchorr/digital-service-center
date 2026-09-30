from fastapi import FastAPI, HTTPException

from database import init_db
from services.tickets import create_ticket, list_tickets, update_status

app = FastAPI(title="Digital Service Center", version="portfolio")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/api/health")
def health():
    return {"ok": True, "portfolio": True}

@app.get("/api/tickets")
def tickets(status: str | None = None):
    try:
        return list_tickets(status=status)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

@app.post("/api/tickets")
def new_ticket(payload: dict):
    try:
        return create_ticket(
            public_id=str(payload["public_id"]),
            title=str(payload["title"]),
            customer_name=str(payload.get("customer_name") or ""),
            category=str(payload.get("category") or ""),
            priority=str(payload.get("priority") or "NORMAL"),
        )
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc))

@app.post("/api/tickets/{ticket_id}/status")
def change_status(ticket_id: int, payload: dict):
    try:
        result = update_status(ticket_id, str(payload["status"]))
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    if not result:
        raise HTTPException(status_code=404, detail="Ticket not found.")
    return result
