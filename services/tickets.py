from __future__ import annotations

from datetime import datetime

from database import connect

VALID_STATUS = {"OPEN", "IN_PROGRESS", "WAITING", "RESOLVED", "CLOSED"}
VALID_PRIORITY = {"LOW", "NORMAL", "HIGH", "URGENT"}

def create_ticket(public_id: str, title: str, customer_name="", category="", priority="NORMAL"):
    priority = priority.upper()
    if priority not in VALID_PRIORITY:
        raise ValueError("Invalid priority.")
    now = datetime.now().isoformat(timespec="seconds")
    with connect() as conn:
        cursor = conn.execute(
            """INSERT INTO tickets(public_id,title,customer_name,category,status,priority,created_at,updated_at)
               VALUES(?,?,?,?, 'OPEN', ?, ?, ?)""",
            (public_id.strip(), title.strip(), customer_name.strip(), category.strip(), priority, now, now),
        )
        ticket_id = cursor.lastrowid
        conn.execute(
            "INSERT INTO ticket_events(ticket_id,event_type,details,occurred_at) VALUES(?, 'CREATED', ?, ?)",
            (ticket_id, "Ticket created", now),
        )
    return get_ticket(ticket_id)

def get_ticket(ticket_id: int):
    with connect() as conn:
        row = conn.execute("SELECT * FROM tickets WHERE id=?", (ticket_id,)).fetchone()
        return dict(row) if row else None

def list_tickets(status=None, limit=100):
    sql = "SELECT * FROM tickets"
    params = []
    if status:
        status = status.upper()
        if status not in VALID_STATUS:
            raise ValueError("Invalid status.")
        sql += " WHERE status=?"
        params.append(status)
    sql += " ORDER BY updated_at DESC LIMIT ?"
    params.append(int(limit))
    with connect() as conn:
        return [dict(row) for row in conn.execute(sql, params)]

def update_status(ticket_id: int, status: str, actor_id=None):
    status = status.upper()
    if status not in VALID_STATUS:
        raise ValueError("Invalid status.")
    now = datetime.now().isoformat(timespec="seconds")
    with connect() as conn:
        conn.execute("UPDATE tickets SET status=?,updated_at=? WHERE id=?", (status, now, ticket_id))
        conn.execute(
            "INSERT INTO ticket_events(ticket_id,actor_id,event_type,details,occurred_at) VALUES(?,?, 'STATUS_CHANGED', ?, ?)",
            (ticket_id, actor_id, status, now),
        )
    return get_ticket(ticket_id)
