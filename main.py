import math
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

app = FastAPI(title="AURA-EVP // Ultra-Dense 125-Signal Bengaluru Emergency Green Corridor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# 10+ MAJOR HOSPITALS
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
        "name": "Gottigere Cross Signal",
        "distance_m": 1200.0,
        "eta_sec": 65.0,
        "amb_approach": "NORTH",
        "lanes": {"NORTH": 15, "SOUTH": 12, "EAST": 8, "WEST": 10},
        "signals": {"NORTH": "RED", "SOUTH": "RED", "EAST": "GREEN", "WEST": "RED"},
        "t_clear_sec": 25.0,
        "trigger_threshold_sec": 32.5,
        "phase": "NORMAL_ADAPTIVE",
        "decision_reason": "Initializing 125-signal urban network..."
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
    vehicle_count: int = Field(..., ge=0, le=100)
    cross_traffic_density: float | None = Field(default=None, ge=0.0, le=1.0)
    source: str = Field(default="YOLOv8_EDGE_CAMERA")


# =========================================================
# 125-NAMED SIGNAL CORRIDOR GENERATOR
# =========================================================
def generate_corridor_junctions(orig_lat, orig_lon, dest_lat, dest_lon):
    junctions = []
    num_nodes = 125
    
    base_hubs = [
        "Gottigere Cross Signal", "Hulimavu Gate Signal", "Meenakshi Mall Junction", "IIMB Main Gate Signal", 
        "Bannerghatta Underpass", "Jayadeva Flyover Signal", "Central Silk Board Junction", "BTM 29th Main Signal", 
        "Koramangala Water Tank", "Sony World Signal", "Ejipura Ring Signal", "Domlur Flyover Signal", 
        "Trinity Church Junction", "M.G. Road Signal", "Hebbal Flyover Signal", "Mathikere Main Signal",
        "Yeshwantpur Circle", "Goraguntepalya Signal", "Peenya 1st Stage Signal", "Navrang Circle Signal",
        "Magadi Road Tollgate", "BEL Circle Signal", "Whitefield Main Signal", "ITPL Gate Signal", 
        "Hoodi Circle Signal", "Marathahalli Bridge", "Bellandur Junction", "Devarabisanahalli Signal",
        "Agara Signal", "Iblur Junction", "Jayanagar 4th Block", "Banashankari Temple Signal",
        "JP Nagar 15th Cross", "KR Puram Cable Bridge Signal", "Tin Factory Junction", "Hebbal Lake Signal",
        "Sadashivanagar Police Station Signal", "Mekhri Circle Signal", "Cunningham Road Junction", "Queens Road Signal",
        "Infantry Road Crossing", "Residency Road Signal", "Richmond Circle", "Shanti Nagar Bus Stand Signal",
        "Lalbagh West Gate Signal", "Basavanagudi Bull Temple Signal", "NR Colony Junction", "Chamrajpet Signal",
        "Kasturba Road Signal", "Hospital Emergency Gate Approach"
    ]
    
    for i in range(1, num_nodes + 1):
        ratio = i / (num_nodes + 1)
        j_lat = orig_lat + (dest_lat - orig_lat) * ratio
        j_lon = orig_lon + (dest_lon - orig_lon) * ratio
        
        j_id = f"J{i}"
        hub = base_hubs[(i - 1) % len(base_hubs)]
        j_name = f"{hub} [Sub-Node {i}]"
        
        junctions.append({
            "id": j_id,
            "name": j_name,
            "lat": round(j_lat, 4),
            "lon": round(j_lon, 4),
            "amb_approach": "NORTH" if i % 2 == 0 else "SOUTH",
            "lanes": {"NORTH": 10 + (i % 8), "SOUTH": 8 + (i % 6), "EAST": 6, "WEST": 8}
        })
    return junctions


# =========================================================
# API ENDPOINTS
# =========================================================

@app.get("/api/hospitals")
async def get_hospitals():
    return {"hospitals": HOSPITALS}

@app.post("/api/driver/gps")
async def receive_driver_gps(packet: LiveGPSPacket):
    live_state["active"] = True
    live_state["ambulance_id"] = packet.ambulance_id
    live_state["lat"] = packet.lat
    live_state["lon"] = packet.lon
    live_state["speed_kmh"] = packet.speed_kmh
    live_state["destination_id"] = packet.destination_id
    live_state["last_updated"] = time.strftime("%H:%M:%S")

    selected_hospital = HOSPITALS.get(packet.destination_id, HOSPITALS["manipal_old_airport"])
    junctions = generate_corridor_junctions(packet.lat, packet.lon, selected_hospital["lat"], selected_hospital["lon"])

    valid_junctions = []
    for j in junctions:
        dist = haversine_m(packet.lat, packet.lon, j["lat"], j["lon"])
        if dist < 30.0 and j["id"] not in live_state["passed_junctions"]:
            live_state["passed_junctions"].append(j["id"])

        if j["id"] not in live_state["passed_junctions"]:
            valid_junctions.append((j, dist))

    valid_junctions.sort(key=lambda x: x[1])
    upcoming = valid_junctions[0] if valid_junctions else None

    if upcoming:
        j_cfg, dist_m = upcoming
        speed_ms = max(packet.speed_kmh / 3.6, 4.0)
        eta_sec = round(dist_m / speed_ms, 1)

        amb_lane = j_cfg["amb_approach"]
        lanes = dict(j_cfg["lanes"])

        startup_delay = 2.0
        saturation_flow = 0.6
        queue_in_amb_lane = lanes.get(amb_lane, 10)
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
            reason = f"⚡ GREEN CORRIDOR ACTIVE: Flushing {queue_in_amb_lane} vehicles in {amb_lane} lane at {j_cfg['name']}."
        elif eta_sec <= trigger_sec:
            phase = "YELLOW_SAFETY_CLEARANCE"
            perp_lane = "EAST" if amb_lane in ["NORTH", "SOUTH"] else "NORTH"
            signals[perp_lane] = "YELLOW"
            reason = f"⚠️ PREEMPTION TRIGGERED at {j_cfg['name']}: Holding cross-traffic with 3s Yellow buffer."
        else:
            phase = "ADAPTIVE_CROSS_TRAFFIC"
            other_lanes = [k for k in lanes.keys() if k != amb_lane]
            busiest_cross = max(other_lanes, key=lambda k: lanes[k])
            signals[busiest_cross] = "GREEN"
            reason = f"🧠 Approaching {j_cfg['name']} ({round(dist_m)}m away). Managing local traffic."

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
        live_state["active_junction"]["decision_reason"] = f"🏥 Ambulance successfully arrived at {selected_hospital['name']}!"

    return {"status": "GPS_RECEIVED", "closest_upcoming_junction": live_state["active_junction"]}

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