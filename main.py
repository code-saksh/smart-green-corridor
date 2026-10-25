import math
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

app = FastAPI(title="AURA-EVP // City-Wide Bengaluru Emergency Green Corridor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# COMPREHENSIVE BENGALURU HOSPITALS & REAL NAMED JUNCTIONS
# =========================================================
HOSPITALS = {
    "manipal_old_airport": {
        "name": "Manipal Hospital, Old Airport Road (East/Central)",
        "lat": 12.9592, "lon": 77.6482,
        "corridor_junctions": [
            {"id": "J1", "name": "Silk Board Junction", "lat": 12.9177, "lon": 77.6233, "amb_approach": "NORTH", "lanes": {"NORTH": 30, "SOUTH": 25, "EAST": 20, "WEST": 22}},
            {"id": "J2", "name": "BTM Water Tank Signal", "lat": 12.9210, "lon": 77.6180, "amb_approach": "EAST", "lanes": {"NORTH": 14, "SOUTH": 16, "EAST": 12, "WEST": 15}},
            {"id": "J3", "name": "Agara Signal", "lat": 12.9234, "lon": 77.6375, "amb_approach": "SOUTH", "lanes": {"NORTH": 10, "SOUTH": 16, "EAST": 14, "WEST": 12}},
            {"id": "J4", "name": "Iblur Junction", "lat": 12.9280, "lon": 77.6710, "amb_approach": "WEST", "lanes": {"NORTH": 18, "SOUTH": 20, "EAST": 15, "WEST": 19}},
            {"id": "J5", "name": "Sony World Signal", "lat": 12.9385, "lon": 77.6267, "amb_approach": "SOUTH", "lanes": {"NORTH": 12, "SOUTH": 22, "EAST": 18, "WEST": 15}},
            {"id": "J6", "name": "Ejipura Signal", "lat": 12.9535, "lon": 77.6365, "amb_approach": "WEST", "lanes": {"NORTH": 9, "SOUTH": 11, "EAST": 10, "WEST": 14}},
            {"id": "J7", "name": "Domlur Signal", "lat": 12.9610, "lon": 77.6387, "amb_approach": "SOUTH", "lanes": {"NORTH": 14, "SOUTH": 19, "EAST": 16, "WEST": 13}}
        ]
    },
    "fortis_bannerghatta": {
        "name": "Fortis Hospital, Bannerghatta Road (South)",
        "lat": 12.9010, "lon": 77.5988,
        "corridor_junctions": [
            {"id": "J1", "name": "Central Silk Board South", "lat": 12.9150, "lon": 77.6200, "amb_approach": "WEST", "lanes": {"NORTH": 28, "SOUTH": 24, "EAST": 18, "WEST": 20}},
            {"id": "J2", "name": "Jayadeva Junction", "lat": 12.9100, "lon": 77.5950, "amb_approach": "NORTH", "lanes": {"NORTH": 25, "SOUTH": 20, "EAST": 15, "WEST": 18}},
            {"id": "J3", "name": "BTM Layout 29th Main Cross Signal", "lat": 12.9060, "lon": 77.6050, "amb_approach": "WEST", "lanes": {"NORTH": 12, "SOUTH": 14, "EAST": 10, "WEST": 16}},
            {"id": "J4", "name": "Jayanagar 4th Block Signal", "lat": 12.9220, "lon": 77.5850, "amb_approach": "SOUTH", "lanes": {"NORTH": 16, "SOUTH": 19, "EAST": 14, "WEST": 15}}
        ]
    },
    "apollo_bannerghatta": {
        "name": "Apollo Hospitals, Bannerghatta (Deep South)",
        "lat": 12.8995, "lon": 77.5975,
        "corridor_junctions": [
            {"id": "J1", "name": "Meenakshi Mall Signal", "lat": 12.8930, "lon": 77.5980, "amb_approach": "SOUTH", "lanes": {"NORTH": 15, "SOUTH": 18, "EAST": 12, "WEST": 14}},
            {"id": "J2", "name": "IIMB Junction", "lat": 12.8950, "lon": 77.6010, "amb_approach": "NORTH", "lanes": {"NORTH": 14, "SOUTH": 16, "EAST": 11, "WEST": 13}},
            {"id": "J3", "name": "Hulimavu Gate Signal", "lat": 12.8850, "lon": 77.5990, "amb_approach": "EAST", "lanes": {"NORTH": 10, "SOUTH": 12, "EAST": 9, "WEST": 11}},
            {"id": "J4", "name": "Gottigere Single-Lane Cross", "lat": 12.8750, "lon": 77.5960, "amb_approach": "WEST", "lanes": {"NORTH": 8, "SOUTH": 10, "EAST": 7, "WEST": 9}}
        ]
    },
    "aster_cmi_hebbal": {
        "name": "Aster CMI Hospital, Hebbal (North)",
        "lat": 13.0525, "lon": 77.5947,
        "corridor_junctions": [
            {"id": "J1", "name": "Hebbal Flyover Junction", "lat": 13.0450, "lon": 77.5920, "amb_approach": "SOUTH", "lanes": {"NORTH": 22, "SOUTH": 28, "EAST": 19, "WEST": 16}},
            {"id": "J2", "name": "Kodigehalli Gate Signal", "lat": 13.0620, "lon": 77.5850, "amb_approach": "NORTH", "lanes": {"NORTH": 16, "SOUTH": 18, "EAST": 12, "WEST": 14}},
            {"id": "J3", "name": "Yelahanka Byepass Signal", "lat": 13.0900, "lon": 77.5970, "amb_approach": "WEST", "lanes": {"NORTH": 18, "SOUTH": 20, "EAST": 15, "WEST": 17}}
        ]
    },
    "manipal_yeshwantpur": {
        "name": "Manipal Hospital, Yeshwantpur (North-West)",
        "lat": 13.0245, "lon": 77.5520,
        "corridor_junctions": [
            {"id": "J1", "name": "Yeshwantpur Circle", "lat": 13.0280, "lon": 77.5540, "amb_approach": "WEST", "lanes": {"NORTH": 20, "SOUTH": 24, "EAST": 18, "WEST": 22}},
            {"id": "J2", "name": "Goraguntepalya Signal", "lat": 13.0320, "lon": 77.5450, "amb_approach": "SOUTH", "lanes": {"NORTH": 25, "SOUTH": 30, "EAST": 15, "WEST": 18}},
            {"id": "J3", "name": "Peenya 1st Stage Signal", "lat": 13.0350, "lon": 77.5300, "amb_approach": "EAST", "lanes": {"NORTH": 19, "SOUTH": 21, "EAST": 16, "WEST": 18}}
        ]
    },
    "suguna_rajajinagar": {
        "name": "Suguna Hospital, Rajajinagar (West)",
        "lat": 12.9900, "lon": 77.5530,
        "corridor_junctions": [
            {"id": "J1", "name": "Navrang Circle Signal", "lat": 12.9880, "lon": 77.5580, "amb_approach": "EAST", "lanes": {"NORTH": 14, "SOUTH": 16, "EAST": 12, "WEST": 15}},
            {"id": "J2", "name": "Rajajinagar 1st Block Cross", "lat": 12.9830, "lon": 77.5500, "amb_approach": "NORTH", "lanes": {"NORTH": 12, "SOUTH": 14, "EAST": 10, "WEST": 12}},
            {"id": "J3", "name": "Magadi Road Tollgate Signal", "lat": 12.9700, "lon": 77.5510, "amb_approach": "SOUTH", "lanes": {"NORTH": 16, "SOUTH": 18, "EAST": 13, "WEST": 15}}
        ]
    },
    "ms_ramana_mathikere": {
        "name": "M.S. Ramaiah Memorial Hospital, Mathikere (North)",
        "lat": 13.0310, "lon": 77.5640,
        "corridor_junctions": [
            {"id": "J1", "name": "MS Ramaiah Circle", "lat": 13.0330, "lon": 77.5620, "amb_approach": "SOUTH", "lanes": {"NORTH": 15, "SOUTH": 18, "EAST": 14, "WEST": 16}},
            {"id": "J2", "name": "Mathikere Signal", "lat": 13.0360, "lon": 77.5590, "amb_approach": "EAST", "lanes": {"NORTH": 11, "SOUTH": 13, "EAST": 12, "WEST": 14}},
            {"id": "J3", "name": "BEL Circle Signal", "lat": 13.0380, "lon": 77.5660, "amb_approach": "WEST", "lanes": {"NORTH": 17, "SOUTH": 20, "EAST": 15, "WEST": 18}}
        ]
    },
    "st_johns_koramangala": {
        "name": "St. John's Medical College Hospital, Koramangala (Central)",
        "lat": 12.9260, "lon": 77.6240,
        "corridor_junctions": [
            {"id": "J1", "name": "St Johns Signal", "lat": 12.9280, "lon": 77.6280, "amb_approach": "WEST", "lanes": {"NORTH": 18, "SOUTH": 22, "EAST": 16, "WEST": 20}},
            {"id": "J2", "name": "Koramangala Water Tank Signal", "lat": 12.9320, "lon": 77.6220, "amb_approach": "SOUTH", "lanes": {"NORTH": 14, "SOUTH": 16, "EAST": 12, "WEST": 15}},
            {"id": "J3", "name": "Koramangala 80 Feet Road Signal", "lat": 12.9350, "lon": 77.6300, "amb_approach": "NORTH", "lanes": {"NORTH": 15, "SOUTH": 17, "EAST": 13, "WEST": 16}}
        ]
    },
    "vydehi_whitefield": {
        "name": "Vydehi Hospital, Whitefield (East)",
        "lat": 12.9698, "lon": 77.7499,
        "corridor_junctions": [
            {"id": "J1", "name": "Whitefield Main Signal", "lat": 12.9650, "lon": 77.7450, "amb_approach": "NORTH", "lanes": {"NORTH": 20, "SOUTH": 24, "EAST": 18, "WEST": 22}},
            {"id": "J2", "name": "ITPL Gate Signal", "lat": 12.9850, "lon": 77.7390, "amb_approach": "WEST", "lanes": {"NORTH": 22, "SOUTH": 26, "EAST": 20, "WEST": 24}},
            {"id": "J3", "name": "Hoodi Circle Signal", "lat": 12.9900, "lon": 77.7150, "amb_approach": "SOUTH", "lanes": {"NORTH": 24, "SOUTH": 28, "EAST": 19, "WEST": 21}}
        ]
    },
    "sakra_world_marathahalli": {
        "name": "Sakra World Hospital, Outer Ring Road (East)",
        "lat": 12.9340, "lon": 77.6840,
        "corridor_junctions": [
            {"id": "J1", "name": "Marathahalli Bridge Signal", "lat": 12.9500, "lon": 77.7000, "amb_approach": "SOUTH", "lanes": {"NORTH": 32, "SOUTH": 35, "EAST": 24, "WEST": 28}},
            {"id": "J2", "name": "Bellandur Junction Signal", "lat": 12.9320, "lon": 77.6750, "amb_approach": "WEST", "lanes": {"NORTH": 28, "SOUTH": 30, "EAST": 22, "WEST": 25}},
            {"id": "J3", "name": "Devarabisanahalli Signal", "lat": 12.9300, "lon": 77.6850, "amb_approach": "NORTH", "lanes": {"NORTH": 20, "SOUTH": 22, "EAST": 17, "WEST": 19}}
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
        "name": "Silk Board Junction",
        "distance_m": 1200.0,
        "eta_sec": 65.0,
        "amb_approach": "NORTH",
        "lanes": {"NORTH": 30, "SOUTH": 25, "EAST": 20, "WEST": 22},
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
    vehicle_count: int = Field(..., ge=0, le=100)
    cross_traffic_density: float | None = Field(default=None, ge=0.0, le=1.0)
    source: str = Field(default="YOLOv8_EDGE_CAMERA")


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
    junctions = selected_hospital["corridor_junctions"]

    valid_junctions = []
    for j in junctions:
        dist = haversine_m(packet.lat, packet.lon, j["lat"], j["lon"])
        if dist < 35.0 and j["id"] not in live_state["passed_junctions"]:
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
            reason = f"⚡ GREEN CORRIDOR ACTIVE: Flushing {queue_in_amb_lane} cars in {amb_lane} lane for {j_cfg['name']}."
        elif eta_sec <= trigger_sec:
            phase = "YELLOW_SAFETY_CLEARANCE"
            perp_lane = "EAST" if amb_lane in ["NORTH", "SOUTH"] else "NORTH"
            signals[perp_lane] = "YELLOW"
            reason = f"⚠️ PREEMPTION TRIGGERED at {j_cfg['name']}: Stopping cross-traffic on {perp_lane}."
        else:
            phase = "ADAPTIVE_CROSS_TRAFFIC"
            other_lanes = [k for k in lanes.keys() if k != amb_lane]
            busiest_cross = max(other_lanes, key=lambda k: lanes[k])
            signals[busiest_cross] = "GREEN"
            reason = f"🧠 Approaching {j_cfg['name']} ({round(dist_m)}m away). Regulating cross-traffic."

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
    selected_hospital = HOSPITALS.get(live_state.get("destination_id", "manipal_old_airport"))
    for j in selected_hospital["corridor_junctions"]:
        if j["id"].upper() == junction_id.upper():
            j["lanes"][j["amb_approach"]] = payload.vehicle_count
            if live_state["active_junction"]["id"].upper() == junction_id.upper():
                live_state["active_junction"]["lanes"] = dict(j["lanes"])
            return {"status": "updated", "junction_id": j["id"], "new_queue": payload.vehicle_count}
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

@app.get("/driver-voice")
async def serve_driver_voice():
    with open("driver_voice.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.get("/junction")
async def serve_junction():
    with open("junction.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())