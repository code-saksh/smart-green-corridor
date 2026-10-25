import math
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="AURA-EVP // Driver App + Autonomous Signal Brain")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# 1. ROUTES & JUNCTIONS CONFIG (BENGALURU CORRIDOR)
# =========================================================
ROUTES = {
    "route_a": {
        "id": "route_a",
        "name": "Route A: Outer Ring Road (AI Recommended)",
        "total_distance_km": 6.4,
        "estimated_time_min": 7.5,
        "is_best_path": True,
        "reason": "Moderate, clearable queue density at junctions.",
        "junctions": [
            {
                "id": "J1", "name": "Agara Signal", "lat": 12.9234, "lon": 77.6375,
                "amb_approach": "SOUTH",
                "lanes": {"NORTH": 10, "SOUTH": 16, "EAST": 14, "WEST": 12}
            },
            {
                "id": "J2", "name": "Sony World Signal", "lat": 12.9385, "lon": 77.6267,
                "amb_approach": "SOUTH",
                "lanes": {"NORTH": 12, "SOUTH": 22, "EAST": 18, "WEST": 15}
            },
            {
                "id": "J3", "name": "Ejipura Signal", "lat": 12.9535, "lon": 77.6365,
                "amb_approach": "WEST",
                "lanes": {"NORTH": 9, "SOUTH": 11, "EAST": 10, "WEST": 14}
            },
            {
                "id": "J4", "name": "Domlur Signal", "lat": 12.9610, "lon": 77.6387,
                "amb_approach": "SOUTH",
                "lanes": {"NORTH": 14, "SOUTH": 19, "EAST": 16, "WEST": 13}
            },
        ]
    }
}

# Global Live State for Signals & Driver GPS
live_state = {
    "active": False,
    "ambulance_id": "AMB-108",
    "lat": 12.9177,
    "lon": 77.6233,
    "speed_kmh": 65.0,
    "passed_junctions": [],
    "active_junction": {
        "id": "J1",
        "name": "Agara Signal",
        "distance_m": 1450.0,
        "eta_sec": 80.0,
        "amb_approach": "SOUTH",
        "lanes": {"NORTH": 10, "SOUTH": 16, "EAST": 14, "WEST": 12},
        "signals": {"NORTH": "RED", "SOUTH": "RED", "EAST": "GREEN", "WEST": "RED"},
        "t_clear_sec": 31.5,
        "trigger_threshold_sec": 39.0,
        "phase": "NORMAL_ADAPTIVE",
        "decision_reason": "Waiting for Driver App GPS transmission..."
    },
    "last_updated": "STANDBY"
}

def haversine_m(lat1, lon1, lat2, lon2):
    R = 6371000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

class DriverGPSPacket(BaseModel):
    ambulance_id: str
    lat: float
    lon: float
    speed_kmh: float
    route_id: str = "route_a"

@app.get("/api/routes")
async def get_routes():
    return {"routes": ROUTES}

@app.post("/api/driver/gps")
async def receive_driver_gps(packet: DriverGPSPacket):
    live_state["active"] = True
    live_state["ambulance_id"] = packet.ambulance_id
    live_state["lat"] = packet.lat
    live_state["lon"] = packet.lon
    live_state["speed_kmh"] = packet.speed_kmh
    live_state["last_updated"] = time.strftime("%H:%M:%S")

    junctions = ROUTES["route_a"]["junctions"]
    upcoming = None

    for j in junctions:
        dist = haversine_m(packet.lat, packet.lon, j["lat"], j["lon"])
        if dist < 40.0 and j["id"] not in live_state["passed_junctions"]:
            live_state["passed_junctions"].append(j["id"])

        if j["id"] not in live_state["passed_junctions"]:
            upcoming = (j, dist)
            break  # Pick ONLY the closest upcoming junction

    if upcoming:
        j_cfg, dist_m = upcoming
        speed_ms = max(packet.speed_kmh / 3.6, 4.0)
        eta_sec = round(dist_m / speed_ms, 1)

        amb_lane = j_cfg["amb_approach"]
        lanes = dict(j_cfg["lanes"])

        # Queue Clearance Math: T_clear = T_startup + (N_vehicles / Saturation_Flow)
        startup_delay = 2.5
        saturation_flow = 0.55
        queue_in_amb_lane = lanes[amb_lane]
        t_clear = round(startup_delay + (queue_in_amb_lane / saturation_flow), 1)
        yellow_buffer = 3.5
        safety_margin = 4.0
        trigger_sec = round(t_clear + yellow_buffer + safety_margin, 1)

        signals = {"NORTH": "RED", "SOUTH": "RED", "EAST": "RED", "WEST": "RED"}

        # Autonomous Signal Logic
        if eta_sec <= trigger_sec - yellow_buffer:
            phase = "GREEN_CORRIDOR_ACTIVE"
            signals[amb_lane] = "GREEN"
            progress_ratio = max(0.0, min(1.0, eta_sec / max(t_clear, 1.0)))
            lanes[amb_lane] = max(0, int(queue_in_amb_lane * progress_ratio))
            reason = f"⚡ GREEN CORRIDOR ACTIVE: Flushing {queue_in_amb_lane} cars in {amb_lane} lane before ambulance arrival."
        elif eta_sec <= trigger_sec:
            phase = "YELLOW_SAFETY_CLEARANCE"
            perp_lane = "EAST" if amb_lane in ["NORTH", "SOUTH"] else "NORTH"
            signals[perp_lane] = "YELLOW"
            reason = f"⚠️ PREEMPTION TRIGGERED: Stopping cross-traffic on {perp_lane} with 3.5s Yellow safety buffer."
        else:
            phase = "ADAPTIVE_CROSS_TRAFFIC"
            other_lanes = [k for k in lanes.keys() if k != amb_lane]
            busiest_cross = max(other_lanes, key=lambda k: lanes[k])
            signals[busiest_cross] = "GREEN"
            reason = f"🧠 ML BALANCING: Ambulance is {round(dist_m)}m away. Clearing busiest cross-lane ({busiest_cross})."

        live_state["active_junction"] = {
            "id": j_cfg["id"],
            "name": j_cfg["name"],
            "distance_m": round(dist_m, 1),
            "eta_sec": eta_sec,
            "amb_approach": amb_lane,
            "lanes": lanes,
            "signals": signals,
            "t_clear_sec": t_clear,
            "trigger_threshold_sec": trigger_sec,
            "phase": phase,
            "decision_reason": reason
        }
    else:
        live_state["active_junction"]["phase"] = "DESTINATION_REACHED"
        live_state["active_junction"]["decision_reason"] = "🏥 Ambulance arrived at Manipal Hospital!"

    return {"status": "GPS_RECEIVED", "closest_upcoming_junction": live_state["active_junction"]}

@app.get("/api/live-state")
async def get_live_state():
    return live_state

@app.post("/api/driver/reset")
async def reset_trip():
    live_state["passed_junctions"] = []
    live_state["active"] = False
    return {"status": "RESET"}

@app.get("/driver")
@app.get("/")
async def serve_driver():
    with open("driver.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.get("/junction")
async def serve_junction():
    with open("junction.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())