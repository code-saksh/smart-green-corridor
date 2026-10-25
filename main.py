import math
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="AURA-EVP // Autonomous Emergency Green Corridor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# 1. ROUTES WITH LIVE CONGESTION ZONES
# =========================================================
ROUTES = {
    "route_a": {
        "id": "route_a",
        "name": "Route A: Outer Ring Road -> Inner Ring Road (AI Recommended)",
        "total_distance_km": 6.4,
        "avg_congestion_pct": 38,
        "estimated_time_min": 7.5,
        "is_best_path": True,
        "reason": "Moderate, clearable queue density at junctions. Highest green-corridor efficiency.",
        "waypoints": [
            [12.9177, 77.6233],  # Start: Silk Board
            [12.9205, 77.6300],
            [12.9234, 77.6375],  # J1: Agara Signal
            [12.9285, 77.6360],
            [12.9345, 77.6305],
            [12.9385, 77.6267],  # J2: Sony World Signal
            [12.9460, 77.6315],
            [12.9535, 77.6365],  # J3: Ejipura Signal
            [12.9610, 77.6387],  # J4: Domlur Signal
            [12.9592, 77.6482],  # Destination: Manipal Hospital
        ],
        "congestion_segments": [
            {"coords": [[12.9177, 77.6233], [12.9234, 77.6375]], "level": "MODERATE", "color": "#f59e0b"},
            {"coords": [[12.9234, 77.6375], [12.9385, 77.6267]], "level": "LOW", "color": "#10b981"},
            {"coords": [[12.9385, 77.6267], [12.9535, 77.6365]], "level": "MODERATE", "color": "#f59e0b"},
            {"coords": [[12.9535, 77.6365], [12.9592, 77.6482]], "level": "LOW", "color": "#10b981"},
        ],
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
    },
    "route_b": {
        "id": "route_b",
        "name": "Route B: Hosur Road -> Brigade Road (Avoided)",
        "total_distance_km": 5.8,
        "avg_congestion_pct": 89,
        "estimated_time_min": 19.0,
        "is_best_path": False,
        "reason": "Severe gridlock detected (89% density). Zero room for queue dissipation.",
        "waypoints": [
            [12.9177, 77.6233],
            [12.9300, 77.6150],
            [12.9420, 77.6100],
            [12.9550, 77.6200],
            [12.9592, 77.6482],
        ],
        "congestion_segments": [
            {"coords": [[12.9177, 77.6233], [12.9420, 77.6100]], "level": "SEVERE_GRIDLOCK", "color": "#ef4444"},
            {"coords": [[12.9420, 77.6100], [12.9592, 77.6482]], "level": "HIGH", "color": "#f97316"},
        ],
        "junctions": []
    }
}

# =========================================================
# 2. GLOBAL LIVE STATE & 4-WAY JUNCTION ML BRAIN
# =========================================================
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
        "decision_reason": "Waiting for Ambulance GPS to enter Preemption Threshold..."
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
async def get_available_routes():
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
            break  # Strictly alert ONLY the closest upcoming junction!

    if upcoming:
        j_cfg, dist_m = upcoming
        speed_ms = max(packet.speed_kmh / 3.6, 4.0)
        eta_sec = round(dist_m / speed_ms, 1)

        amb_lane = j_cfg["amb_approach"]
        lanes = dict(j_cfg["lanes"])

        # Calculate Queue Clearance Time (T_clear) for the ambulance's lane
        startup_delay = 2.5
        saturation_flow = 0.55  # cars per second
        queue_in_amb_lane = lanes[amb_lane]
        t_clear = round(startup_delay + (queue_in_amb_lane / saturation_flow), 1)
        yellow_buffer = 3.5
        safety_margin = 4.0
        trigger_sec = round(t_clear + yellow_buffer + safety_margin, 1)

        signals = {"NORTH": "RED", "SOUTH": "RED", "EAST": "RED", "WEST": "RED"}

        # Autonomous ML 4-Way Phase Logic
        if eta_sec <= trigger_sec - yellow_buffer:
            phase = "GREEN_CORRIDOR_ACTIVE"
            signals[amb_lane] = "GREEN"
            # Drain queue as green signal flushes traffic ahead of ambulance
            progress_ratio = max(0.0, min(1.0, eta_sec / max(t_clear, 1.0)))
            lanes[amb_lane] = max(0, int(queue_in_amb_lane * progress_ratio))
            reason = (
                f"⚡ GREEN CORRIDOR LOCKED: Flushing {queue_in_amb_lane} vehicles in {amb_lane} lane "
                f"so queue reaches 0 before ambulance arrival (ETA {eta_sec}s <= T_clear {t_clear}s)."
            )
        elif eta_sec <= trigger_sec:
            phase = "YELLOW_SAFETY_CLEARANCE"
            # Transition perpendicular traffic safely to Yellow before turning Red
            perp_lane = "EAST" if amb_lane in ["NORTH", "SOUTH"] else "NORTH"
            signals[perp_lane] = "YELLOW"
            reason = (
                f"⚠️ PREEMPTION TRIGGERED (ETA {eta_sec}s <= {trigger_sec}s): "
                f"Stopping cross-traffic on {perp_lane} with mandatory 3.5s Yellow safety buffer."
            )
        else:
            phase = "ADAPTIVE_CROSS_TRAFFIC"
            # Regulate the highest-density cross-traffic lane while ambulance is still far away
            other_lanes = [k for k in lanes.keys() if k != amb_lane]
            busiest_cross = max(other_lanes, key=lambda k: lanes[k])
            signals[busiest_cross] = "GREEN"
            reason = (
                f"🧠 ML BALANCING: Ambulance is {round(dist_m)}m away (ETA {eta_sec}s > Trigger {trigger_sec}s). "
                f"Clearing busiest cross-lane ({busiest_cross}: {lanes[busiest_cross]} cars) first."
            )

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
        live_state["active_junction"]["decision_reason"] = "🏥 Ambulance crossed all junctions and reached Manipal Hospital!"

    return {
        "status": "GPS_RECEIVED",
        "closest_upcoming_junction": live_state["active_junction"],
        "passed_junctions": live_state["passed_junctions"]
    }

@app.get("/api/live-state")
async def get_live_state():
    return live_state

@app.post("/api/driver/reset")
async def reset_driver_trip():
    live_state["passed_junctions"] = []
    live_state["active"] = False
    live_state["active_junction"]["phase"] = "NORMAL_ADAPTIVE"
    live_state["active_junction"]["distance_m"] = 1450.0
    live_state["active_junction"]["eta_sec"] = 80.0
    return {"status": "RESET"}

@app.get("/")
@app.get("/driver")
async def serve_driver_app():
    with open("driver.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.get("/junction")
async def serve_junction_simulator():
    with open("junction.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())