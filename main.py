import math
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

app = FastAPI(title="AURA-EVP // Complete Multi-Part Emergency Green Corridor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# MAJOR BENGALURU HOSPITALS & JUNCTION CORRIDORS
# =========================================================
HOSPITALS = {
    "manipal_old_airport": {
        "name": "Manipal Hospital, Old Airport Road",
        "lat": 12.9592, "lon": 77.6482,
        "corridor_junctions": [
            {"id": "J1", "name": "Agara Signal", "lat": 12.9234, "lon": 77.6375, "amb_approach": "SOUTH", "lanes": {"NORTH": 10, "SOUTH": 16, "EAST": 14, "WEST": 12}},
            {"id": "J2", "name": "Sony World Signal", "lat": 12.9385, "lon": 77.6267, "amb_approach": "SOUTH", "lanes": {"NORTH": 12, "SOUTH": 22, "EAST": 18, "WEST": 15}},
            {"id": "J3", "name": "Ejipura Signal", "lat": 12.9535, "lon": 77.6365, "amb_approach": "WEST", "lanes": {"NORTH": 9, "SOUTH": 11, "EAST": 10, "WEST": 14}},
            {"id": "J4", "name": "Domlur Signal", "lat": 12.9610, "lon": 77.6387, "amb_approach": "SOUTH", "lanes": {"NORTH": 14, "SOUTH": 19, "EAST": 16, "WEST": 13}}
        ]
    },
    "fortis_bannerghatta": {
        "name": "Fortis Hospital, Bannerghatta Road",
        "lat": 12.9010, "lon": 77.5988,
        "corridor_junctions": [
            {"id": "J1", "name": "Jayadeva Junction", "lat": 12.9100, "lon": 77.5950, "amb_approach": "NORTH", "lanes": {"NORTH": 25, "SOUTH": 20, "EAST": 15, "WEST": 18}},
            {"id": "J2", "name": "BTM Layout 29th Main", "lat": 12.9060, "lon": 77.6050, "amb_approach": "WEST", "lanes": {"NORTH": 12, "SOUTH": 14, "EAST": 10, "WEST": 16}}
        ]
    },
    "apollo_bannerghatta": {
        "name": "Apollo Hospitals, Bannerghatta",
        "lat": 12.8995, "lon": 77.5975,
        "corridor_junctions": [
            {"id": "J1", "name": "Meenakshi Mall Signal", "lat": 12.8930, "lon": 77.5980, "amb_approach": "SOUTH", "lanes": {"NORTH": 15, "SOUTH": 18, "EAST": 12, "WEST": 14}}
        ]
    }
}

# =========================================================
# GLOBAL LIVE STATE & SIGNAL BRAIN
# =========================================================
live_state = {
    "active": False,
    "ambulance_id": "AMB-108",
    "lat": 12.9177,
    "lon": 77.6233,
    "speed_kmh": 65.0,
    "destination_id": "manipal_old_airport",
    "passed_junctions": [],
    "active_junction": {
        "id": "J1",
        "name": "Agara Signal",
        "distance_m": 1200.0,
        "eta_sec": 65.0,
        "amb_approach": "SOUTH",
        "lanes": {"NORTH": 10, "SOUTH": 16, "EAST": 14, "WEST": 12},
        "signals": {"NORTH": "RED", "SOUTH": "RED", "EAST": "GREEN", "WEST": "RED"},
        "t_clear_sec": 31.5,
        "trigger_threshold_sec": 39.0,
        "phase": "NORMAL_ADAPTIVE",
        "decision_reason": "Waiting for device live GPS transmission..."
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

class LiveGPSPacket(BaseModel):
    ambulance_id: str
    lat: float
    lon: float
    speed_kmh: float
    destination_id: str

class JunctionDensityPayload(BaseModel):
    vehicle_count: int = Field(..., ge=0, le=100, description="Live vehicle count from YOLOv8 / CCTV")
    cross_traffic_density: float | None = Field(default=None, ge=0.0, le=1.0)
    source: str = Field(default="YOLOv8_EDGE_CAMERA")


# =========================================================
# API ENDPOINTS
# =========================================================

@app.get("/api/hospitals")
async def get_hospitals():
    """Returns available hospital destinations and their corresponding junctions."""
    return {"hospitals": HOSPITALS}

@app.post("/api/driver/gps")
async def receive_driver_gps(packet: LiveGPSPacket):
    """
    Receives live device GPS and computes sequential closest-junction preemption math.
    """
    live_state["active"] = True
    live_state["ambulance_id"] = packet.ambulance_id
    live_state["lat"] = packet.lat
    live_state["lon"] = packet.lon
    live_state["speed_kmh"] = packet.speed_kmh
    live_state["destination_id"] = packet.destination_id
    live_state["last_updated"] = time.strftime("%H:%M:%S")

    selected_hospital = HOSPITALS.get(packet.destination_id, HOSPITALS["manipal_old_airport"])
    junctions = selected_hospital["corridor_junctions"]
    upcoming = None

    for j in junctions:
        dist = haversine_m(packet.lat, packet.lon, j["lat"], j["lon"])
        if dist < 40.0 and j["id"] not in live_state["passed_junctions"]:
            live_state["passed_junctions"].append(j["id"])

        if j["id"] not in live_state["passed_junctions"]:
            upcoming = (j, dist)
            break

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

        if eta_sec <= trigger_sec - yellow_buffer:
            phase = "GREEN_CORRIDOR_ACTIVE"
            signals[amb_lane] = "GREEN"
            progress_ratio = max(0.0, min(1.0, eta_sec / max(t_clear, 1.0)))
            lanes[amb_lane] = max(0, int(queue_in_amb_lane * progress_ratio))
            reason = f"⚡ GREEN CORRIDOR ACTIVE: Flushing {queue_in_amb_lane} cars in {amb_lane} lane."
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
        live_state["active_junction"]["decision_reason"] = f"🏥 Ambulance arrived at {selected_hospital['name']}!"

    return {"status": "GPS_RECEIVED", "closest_upcoming_junction": live_state["active_junction"]}

@app.post("/api/v1/junctions/{junction_id}/density")
async def update_junction_vehicle_density(payload: JunctionDensityPayload, junction_id: str):
    """
    **Part 3 (YOLOv8 Edge CCTV Webhook):** Pushes real-time waiting vehicle counts 
    from edge cameras into a specific junction, dynamically recalculating Queue Clearance Time.
    """
    selected_hospital = HOSPITALS.get(live_state.get("destination_id", "manipal_old_airport"))
    for j in selected_hospital["corridor_junctions"]:
        if j["id"].upper() == junction_id.upper():
            j["lanes"][j["amb_approach"]] = payload.vehicle_count
            if payload.cross_traffic_density is not None:
                j["cross_traffic_density"] = payload.cross_traffic_density
            
            if live_state["active_junction"]["id"].upper() == junction_id.upper():
                live_state["active_junction"]["lanes"] = dict(j["lanes"])
                
            return {
                "status": "updated",
                "junction_id": j["id"],
                "new_ambulance_lane_queue": payload.vehicle_count,
                "source": payload.source
            }
    return {"status": "error", "message": "Junction not found"}

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