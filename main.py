import math
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

app = FastAPI(title="AURA-EVP // Top 50 High-Density Bengaluru Emergency Green Corridor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# 10 MAJOR HOSPITALS COVERING ALL ZONES OF BENGALURU
# =========================================================
HOSPITALS = {
    "manipal_old_airport": {
        "name": "Manipal Hospital, Old Airport Road (East/Central)",
        "lat": 12.9592, "lon": 77.6482,
    },
    "fortis_bannerghatta": {
        "name": "Fortis Hospital, Bannerghatta Road (South)",
        "lat": 12.9010, "lon": 77.5988,
    },
    "apollo_bannerghatta": {
        "name": "Apollo Hospitals, Bannerghatta (Deep South)",
        "lat": 12.8995, "lon": 77.5975,
    },
    "aster_cmi_hebbal": {
        "name": "Aster CMI Hospital, Hebbal (North)",
        "lat": 13.0525, "lon": 77.5947,
    },
    "manipal_yeshwantpur": {
        "name": "Manipal Hospital, Yeshwantpur (North-West)",
        "lat": 13.0245, "lon": 77.5520,
    },
    "suguna_rajajinagar": {
        "name": "Suguna Hospital, Rajajinagar (West)",
        "lat": 12.9900, "lon": 77.5530,
    },
    "ms_ramana_mathikere": {
        "name": "M.S. Ramaiah Memorial Hospital, Mathikere (North)",
        "lat": 13.0310, "lon": 77.5640,
    },
    "st_johns_koramangala": {
        "name": "St. John's Medical College Hospital, Koramangala (Central)",
        "lat": 12.9260, "lon": 77.6240,
    },
    "vydehi_whitefield": {
        "name": "Vydehi Hospital, Whitefield (East)",
        "lat": 12.9698, "lon": 77.7499,
    },
    "sakra_world_marathahalli": {
        "name": "Sakra World Hospital, Outer Ring Road (East)",
        "lat": 12.9340, "lon": 77.6840,
    }
}

# =========================================================
# TOP 50 HIGH-DENSITY BENGALURU TRAFFIC SIGNALS
# =========================================================
TOP_50_SIGNALS = [
    "Central Silk Board Junction", "KR Puram Tin Factory Signal", "Hebbal Flyover Main Junction", "Sony World Signal, Koramangala",
    "Marathahalli Bridge Junction", "Jayadeva Hospital Flyover Signal", "Goraguntepalya Junction", "Iblur Outer Ring Road Signal",
    "Agara Lake Junction", "Domlur Flyover Signal", "Trinity Circle Signal", "Richmond Circle Junction",
    "Mekhri Circle Underpass Signal", "Yeshwantpur Circle Signal", "Town Hall Main Junction", "Majestic Kempegowda Signal",
    "Hudson Circle Junction", "Anand Rao Circle Signal", "Chalukya Circle Junction", "Windsor Manor Bridge Signal",
    "Cauvery Theater Junction", "Bhashyam Circle, Sadashivanagar", "BEL Circle Junction", "Jalahalli Cross Signal",
    "Peenya 1st Stage Junction", "8th Mile Tumkur Road Signal", "Navrang Circle, Rajajinagar", "Magadi Road Tollgate Signal",
    "Vijayanagar Water Tank Junction", "Nayandahalli Flyover Junction", "Deepanjali Nagar Signal", "Banashankari Bus Stand Junction",
    "Jayanagar 4th Block Signal", "South End Circle Junction", "Lalbagh West Gate Signal", "Minerva Circle Junction",
    "JC Road Corporation Signal", "Shanti Nagar Bus Station Signal", "Double Road Kengal Hanumanthaiah Signal", "Dairy Circle Flyover Junction",
    "St. John's Hospital Signal", "Water Tank Junction, Koramangala", "Ejipura Inner Ring Road Signal", "Indiranagar 100ft Road CMH Signal",
    "Old Madras Road Baiyappanahalli Signal", "Whitefield Hope Farm Junction", "ITPL Main Gate Signal", "Hoodi Circle Junction",
    "Graphite India Signal, Whitefield", "Bellandur Gate ORR Signal"
]

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
        "name": "Central Silk Board Junction",
        "distance_m": 450.0,
        "eta_sec": 25.0,
        "amb_approach": "NORTH",
        "lanes": {"NORTH": 26, "SOUTH": 22, "EAST": 18, "WEST": 20},
        "signals": {"NORTH": "RED", "SOUTH": "RED", "EAST": "GREEN", "WEST": "RED"},
        "t_clear_sec": 28.0,
        "trigger_threshold_sec": 35.5,
        "phase": "NORMAL_ADAPTIVE",
        "decision_reason": "Monitoring Top 50 High-Density Bengaluru Signal Grid..."
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
    closest_junction_id: str | None = None
    closest_junction_name: str | None = None
    closest_junction_lat: float | None = None
    closest_junction_lon: float | None = None
    passed_junction_ids: list[str] | None = None

class JunctionDensityPayload(BaseModel):
    vehicle_count: int = Field(..., ge=0, le=100)
    cross_traffic_density: float | None = Field(default=None, ge=0.0, le=1.0)
    source: str = Field(default="YOLOv8_EDGE_CAMERA")

# =========================================================
# API ENDPOINTS
# =========================================================

@app.get("/api/hospitals")
async def get_hospitals():
    return {"hospitals": HOSPITALS, "top_50_signals": TOP_50_SIGNALS}

@app.post("/api/driver/gps")
async def receive_driver_gps(packet: LiveGPSPacket):
    live_state["active"] = True
    live_state["ambulance_id"] = packet.ambulance_id
    live_state["lat"] = packet.lat
    live_state["lon"] = packet.lon
    live_state["speed_kmh"] = packet.speed_kmh
    live_state["destination_id"] = packet.destination_id
    live_state["last_updated"] = time.strftime("%H:%M:%S")

    if packet.passed_junction_ids is not None:
        live_state["passed_junctions"] = packet.passed_junction_ids

    selected_hospital = HOSPITALS.get(packet.destination_id, HOSPITALS["manipal_old_airport"])

    if packet.closest_junction_id and packet.closest_junction_lat is not None and packet.closest_junction_lon is not None:
        j_id = packet.closest_junction_id
        j_name = packet.closest_junction_name or f"High-Density Signal ({j_id})"
        dist_m = haversine_m(packet.lat, packet.lon, packet.closest_junction_lat, packet.closest_junction_lon)
        
        speed_ms = max(packet.speed_kmh / 3.6, 4.0)
        eta_sec = round(dist_m / speed_ms, 1)

        idx_num = int(j_id.replace("J", "")) if j_id.startswith("J") and j_id[1:].isdigit() else 1
        amb_lane = "NORTH" if idx_num % 2 == 0 else "SOUTH"
        
        # High-density queue numbers
        lanes = {
            "NORTH": 18 + (idx_num % 12),
            "SOUTH": 16 + (idx_num % 10),
            "EAST": 14 + (idx_num % 8),
            "WEST": 15 + (idx_num % 9)
        }

        startup_delay = 2.0
        saturation_flow = 0.65
        queue_in_amb_lane = lanes[amb_lane]
        t_clear = round(startup_delay + (queue_in_amb_lane / saturation_flow), 1)
        yellow_buffer = 3.0
        safety_margin = 3.5
        trigger_sec = round(t_clear + yellow_buffer + safety_margin, 1)

        signals = {"NORTH": "RED", "SOUTH": "RED", "EAST": "RED", "WEST": "RED"}

        if eta_sec <= trigger_sec - yellow_buffer:
            phase = "GREEN_CORRIDOR_ACTIVE"
            signals[amb_lane] = "GREEN"
            progress_ratio = max(0.0, min(1.0, eta_sec / max(t_clear, 1.0)))
            lanes[amb_lane] = max(0, int(queue_in_amb_lane * progress_ratio))
            reason = f"⚡ GREEN CORRIDOR ACTIVE: Flushing high-density queue ({queue_in_amb_lane} vehicles) in {amb_lane} lane at {j_name}."
        elif eta_sec <= trigger_sec:
            phase = "YELLOW_SAFETY_CLEARANCE"
            perp_lane = "EAST" if amb_lane in ["NORTH", "SOUTH"] else "NORTH"
            signals[perp_lane] = "YELLOW"
            reason = f"⚠️ PREEMPTION TRIGGERED at {j_name}: Clearing cross-traffic with 3s Yellow buffer."
        else:
            phase = "ADAPTIVE_CROSS_TRAFFIC"
            other_lanes = [k for k in lanes.keys() if k != amb_lane]
            busiest_cross = max(other_lanes, key=lambda k: lanes[k])
            signals[busiest_cross] = "GREEN"
            reason = f"🧠 Approaching {j_name} ({round(dist_m)}m away). Balancing high-density cross-traffic."

        live_state["active_junction"] = {
            "id": j_id,
            "name": j_name,
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
        live_state["active_junction"]["decision_reason"] = f"🏥 All 50 high-density signals cleared! Ambulance arrived at {selected_hospital['name']}!"

    return {
        "status": "GPS_RECEIVED",
        "closest_upcoming_junction": live_state["active_junction"] if packet.closest_junction_id else None,
        "passed_junctions": live_state["passed_junctions"]
    }

@app.post("/api/v1/junctions/{junction_id}/density")
async def update_junction_vehicle_density(payload: JunctionDensityPayload, junction_id: str):
    if live_state["active_junction"]["id"].upper() == junction_id.upper():
        amb_lane = live_state["active_junction"]["amb_approach"]
        live_state["active_junction"]["lanes"][amb_lane] = payload.vehicle_count
        return {"status": "updated", "junction_id": junction_id, "new_queue": payload.vehicle_count}
    return {"status": "error", "message": "Junction not currently active"}

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

@app.get("/driver-voice")
async def serve_driver_voice():
    with open("driver_voice.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.get("/junction")
async def serve_junction():
    with open("junction.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())