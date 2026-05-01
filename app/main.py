from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from math import radians, cos, sin, asin, sqrt
from .database import engine, SessionLocal
from .models import Base, NGO
from fastapi import Query
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title="Real-Time Food Waste AI System")

Base.metadata.create_all(bind=engine)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- APP SETUP ----------------

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)
manager = ConnectionManager()

# ---------------- DATABASE DEPENDENCY ----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------- ROOT ----------------
@app.get("/")
def root():
    return {"status": "Server running"}

# ---------------- NGO SCHEMAS ----------------
class NGOCreate(BaseModel):
    name: str
    latitude: float
    longitude: float


# ---------------- NGO ROUTES ----------------
@app.post("/ngo/register")
def register_ngo(ngo: NGOCreate, db: Session = Depends(get_db)):
    new_ngo = NGO(
        name=ngo.name,
        latitude=ngo.latitude,
        longitude=ngo.longitude,
        is_verified=False
    )
    db.add(new_ngo)
    db.commit()
    db.refresh(new_ngo)

    return {
        "message": "NGO registered. Waiting for admin verification.",
        "ngo_id": new_ngo.id
    }

@app.post("/ngo/verify/{ngo_id}")
def verify_ngo(ngo_id: int, db: Session = Depends(get_db)):
    ngo = db.query(NGO).filter(NGO.id == ngo_id).first()
    if not ngo:
        return {"error": "NGO not found"}

    ngo.is_verified = True
    db.commit()

    return {"message": f"NGO {ngo.name} verified successfully"}
def calculate_distance(lat1, lon1, lat2, lon2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return 6371 * c
def calculate_priority(expiry_hours, distance_km, ngo):
    distance_km = max(distance_km, 0.1)
    expiry_hours = max(expiry_hours, 0.1)
    acceptance_rate = (ngo.accept_count + 1) / (ngo.response_count + 1)
    response_speed = 1 / (ngo.avg_response_time + 1)

    expiry_weight = 0.5 if expiry_hours < 3 else 0.3
    distance_weight = 0.3
    reliability_weight = 0.2

    return (
        (1 / expiry_hours) * expiry_weight +
        (1 / distance_km) * distance_weight +
        acceptance_rate * reliability_weight +
        response_speed * 0.1
    )



class FoodCreate(BaseModel):
    food_name: str
    latitude: float
    longitude: float
    expiry_hours: int

@app.post("/food/post")
async def post_food(food: FoodCreate, db: Session = Depends(get_db)):

    verified_ngos = db.query(NGO).filter(NGO.is_verified == True).all()

    if not verified_ngos:
        return {"message": "Food posted, but no verified NGOs available"}

    best_ngo = None
    best_score = 0

    for ngo in verified_ngos:
        distance = calculate_distance(
            food.latitude, food.longitude,
            ngo.latitude, ngo.longitude
        )

        score = calculate_priority(food.expiry_hours, distance, ngo)

        if score > best_score:
            best_score = score
            best_ngo = ngo
    await manager.broadcast(
    f"🍱 New food posted: {food.food_name} | Expiry: {food.expiry_hours} hrs"
)

    return {
        "message": "Food posted successfully",
        "assigned_ngo": best_ngo.name,
        "priority_score": round(best_score, 3)
    }
@app.post("/ngo/feedback/{ngo_id}")
def ngo_feedback(
    ngo_id: int,
    accepted: bool = Query(..., description="Did NGO accept the food?"),
    response_time: float = Query(..., description="Response time in minutes"),
    db: Session = Depends(get_db)
):
    ngo = db.query(NGO).filter(NGO.id == ngo_id).first()
    if not ngo:
        return {"error": "NGO not found"}

    ngo.response_count += 1

    if accepted:
        ngo.accept_count += 1
        ngo.reliability_score = min(1.0, ngo.reliability_score + 0.05)
    else:
        ngo.reliability_score = max(0.0, ngo.reliability_score - 0.05)

    ngo.avg_response_time = (
        (ngo.avg_response_time * (ngo.response_count - 1)) + response_time
    ) / ngo.response_count

    db.commit()

    return {
        "message": "Feedback recorded successfully",
        "accept_count": ngo.accept_count,
        "response_count": ngo.response_count,
        "reliability_score": round(ngo.reliability_score, 2)
    }

@app.websocket("/ws/ngos")
async def ngo_notifications(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
# ---------- NGO FEEDBACK (AI LEARNING) ----------

