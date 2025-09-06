from fastapi import FastAPI,Body
import sqlite3

app = FastAPI()

# Hàm khởi tạo database
def init_db():
    conn = sqlite3.connect("demo.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS player (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        sport TEXT NOT NULL
    )
    """)

    cursor.execute("SELECT COUNT(*) FROM people")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO people (name, age, sport) VALUES (?, ?, ?)", ("Alice", 25, "Football"))
        cursor.execute("INSERT INTO people (name, age, sport) VALUES (?, ?, ?)", ("Bob", 30, "Tennis"))
        cursor.execute("INSERT INTO people (name, age, sport) VALUES (?, ?, ?)", ("Charlie", 22, "Basketball"))

    conn.commit()
    conn.close()


# API: thêm dữ liệu (thực thi INSERT query)
@app.post("/add_data")
def add_data(query):
    conn = sqlite3.connect("demo.db")
    conn.execute(query)
    conn.commit()
    conn.close()
    return {"status": "ok"}


# API: đọc dữ liệu (thực thi SELECT query)
@app.get("/read_data")
def read_data(query: str = "SELECT * FROM people"):
    conn = sqlite3.connect("demo.db")
    cursor = conn.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return {"data": rows}


# Khởi tạo DB khi app startup
@app.on_event("startup")
def startup_event():
    init_db()
