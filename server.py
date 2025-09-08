from fastapi import FastAPI, Body, HTTPException
from pydantic import BaseModel
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
    CREATE TABLE IF NOT EXISTS player (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        sport TEXT NOT NULL
    )
    """)

    # Thêm dữ liệu mẫu nếu bảng rỗng
    cursor.execute("SELECT COUNT(*) FROM player")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO player (name, age, sport) VALUES (?, ?, ?)", ("Alice", 25, "Football"))
        cursor.execute("INSERT INTO player (name, age, sport) VALUES (?, ?, ?)", ("Bob", 30, "Tennis"))
        cursor.execute("INSERT INTO player (name, age, sport) VALUES (?, ?, ?)", ("Charlie", 22, "Basketball"))

    conn.commit()
    conn.close()


# -------------------------------
# Pydantic model
# -------------------------------
class Player(BaseModel):
    name: str
    age: int
    sport: str


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
def update_player(player_id: int, player: Player):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE player SET name=?, age=?, sport=? WHERE id=?",
            (player.name, player.age, player.sport, player_id)
        )
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


# -------------------------------
# Tuỳ chọn: Query raw SQL an toàn
# -------------------------------
@app.post("/run_query")
def run_query(query: str = Body(..., embed=True)):
    """
    Chỉ dùng cho SELECT. Có try/except để tránh crash.
    """
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
