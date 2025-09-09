from fastapi import FastAPI, Body, HTTPException
from pydantic import BaseModel
from typing import Optional
import sqlite3

app = FastAPI()
DB_FILE = "demo.db"

# -------------------------------
# Database init
# -------------------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age INTEGER,
        sport TEXT
    )
    """)
    cursor.execute("SELECT COUNT(*) FROM player")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO player (name, age, sport) VALUES (?, ?, ?)", ("Alice", 25, "Football"))
        cursor.execute("INSERT INTO player (name, age, sport) VALUES (?, ?, ?)", ("Bob", 30, "Tennis"))
        cursor.execute("INSERT INTO player (name, age, sport) VALUES (?, ?, ?)", ("Charlie", 22, "Basketball"))
    conn.commit()
    conn.close()


# -------------------------------
# Pydantic models
# -------------------------------
class Player(BaseModel):
    name: str
    age: int
    sport: str

class PlayerUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    sport: Optional[str] = None


# -------------------------------
# CRUD API
# -------------------------------
@app.post("/add_player")
def add_player(player: Player):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO player (name, age, sport) VALUES (?, ?, ?)",
            (player.name, player.age, player.sport)
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return {"status": "ok", "id": new_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/read_players")
def read_players():
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, age, sport FROM player")
        rows = cursor.fetchall()
        conn.close()
        return {"data": rows}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/update_player/{player_id}")
def update_player(player_id: int, player: PlayerUpdate):
    try:
        update_fields = []
        values = []
        if player.name is not None:
            update_fields.append("name=?")
            values.append(player.name)
        if player.age is not None:
            update_fields.append("age=?")
            values.append(player.age)
        if player.sport is not None:
            update_fields.append("sport=?")
            values.append(player.sport)

        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields provided for update")

        values.append(player_id)

        query = f"UPDATE player SET {', '.join(update_fields)} WHERE id=?"
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(query, tuple(values))
        conn.commit()
        conn.close()
        return {"status": "ok", "updated_id": player_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/delete_player/{player_id}")
def delete_player(player_id: int):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM player WHERE id=?", (player_id,))
        conn.commit()
        conn.close()
        return {"status": "ok", "deleted_id": player_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/run_query")
def run_query(query: str = Body(..., embed=True)):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return {"data": rows}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid query: {e}")


# -------------------------------
# App startup
# -------------------------------
@app.on_event("startup")
def startup_event():
    init_db()
