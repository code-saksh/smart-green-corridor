import math
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

app = FastAPI(title="AURA-EVP // Bengaluru 50 Real High-Density Signals Green Corridor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# 10 MAJOR BENGALURU HOSPITALS (EXACT GPS)
# =========================================================
HOSPITALS = {
    "manipal_old_airport": {
        "name": "Manipal Hospital, Old Airport Road (East/Central)",
        "lat": 12.9592, "lon": 77.6482,
    },
    "fortis_bannerghatta": {
        "name": "Fortis Hospital, Bannerghatta Road (South)",
        "lat": 12.8948, "lon": 77.5986,
    },
    "apollo_bannerghatta": {
        "name": "Apollo Hospitals, Bannerghatta (Deep South)",
        "lat": 12.8962, "lon": 77.5982,
    },
    "aster_cmi_hebbal": {
        "name": "Aster CMI Hospital, Hebbal (North)",
        "lat": 13.0545, "lon": 77.5916,
    },
    "manipal_yeshwantpur": {
        "name": "Manipal Hospital, Yeshwantpur (North-West)",
        "lat": 13.0184, "lon": 77.5504,
    },
    "suguna_rajajinagar": {
        "name": "Suguna Hospital, Rajajinagar (West)",
        "lat": 12.9982, "lon": 77.5528,
    },
    "ms_ramana_mathikere": {
        "name": "M.S. Ramaiah Memorial Hospital, Mathikere (North)",
        "lat": 13.0285, "lon": 77.5698,
    },
    "st_johns_koramangala": {
        "name": "St. John's Medical College Hospital, Koramangala (Central)",
        "lat": 12.9298, "lon": 77.6205,
    },
    "vydehi_whitefield": {
        "name": "Vydehi Hospital, Whitefield (East)",
        "lat": 12.9756, "lon": 77.7294,
    },
    "sakra_world_marathahalli": {
        "name": "Sakra World Hospital, Outer Ring Road (East)",
        "lat": 12.9292, "lon": 77.6844,
    }
}

# =========================================================
# BENGALURU'S 50 REAL HIGH-DENSITY TRAFFIC SIGNALS (EXACT GPS)
# =========================================================
BENGALURU_50_SIGNALS = [
    {"id": "BLR-01", "name": "Central Silk Board Junction", "lat": 12.9177, "lon": 77.6233},
    {"id": "BLR-02", "name": "Gottigere Bannerghatta Signal", "lat": 12.8565, "lon": 77.5878},
    {"id": "BLR-03", "name": "Hulimavu Gate Signal", "lat": 12.8778, "lon": 77.5955},
    {"id": "BLR-04", "name": "Meenakshi Mall Signal", "lat": 12.8825, "lon": 77.5966},
    {"id": "BLR-05", "name": "Arakere Gate Signal", "lat": 12.8888, "lon": 77.5976},
    {"id": "BLR-06", "name": "IIMB Main Gate Junction", "lat": 12.8988, "lon": 77.5995},
    {"id": "BLR-07", "name": "Bilekahalli Signal", "lat": 12.9056, "lon": 77.6010},
    {"id": "BLR-08", "name": "Jayadeva Flyover Junction", "lat": 12.9166, "lon": 77.5993},
    {"id": "BLR-09", "name": "BTM Water Tank Signal", "lat": 12.9165, "lon": 77.6101},
    {"id": "BLR-10", "name": "Udupi Garden BTM Signal", "lat": 12.9168, "lon": 77.6163},
    {"id": "BLR-11", "name": "Sagar Hospital Jayanagar Signal", "lat": 12.9255, "lon": 77.5948},
    {"id": "BLR-12", "name": "Dairy Circle Flyover Junction", "lat": 12.9366, "lon": 77.6015},
    {"id": "BLR-13", "name": "Jayanagar 4th Block Bus Stand Signal", "lat": 12.9290, "lon": 77.5835},
    {"id": "BLR-14", "name": "South End Circle Junction", "lat": 12.9362, "lon": 77.5768},
    {"id": "BLR-15", "name": "Banashankari Temple Bus Stand Junction", "lat": 12.9175, "lon": 77.5732},
    {"id": "BLR-16", "name": "Konanakunte Cross Metro Signal", "lat": 12.8845, "lon": 77.5695},
    {"id": "BLR-17", "name": "Lalbagh West Gate Signal", "lat": 12.9482, "lon": 77.5798},
    {"id": "BLR-18", "name": "Minerva Circle Junction", "lat": 12.9565, "lon": 77.5792},
    {"id": "BLR-19", "name": "Town Hall Main Junction", "lat": 12.9638, "lon": 77.5855},
    {"id": "BLR-20", "name": "Hudson Circle Junction", "lat": 12.9675, "lon": 77.5880},
    {"id": "BLR-21", "name": "Richmond Circle Junction", "lat": 12.9655, "lon": 77.5975},
    {"id": "BLR-22", "name": "Shanti Nagar Bus Stand Signal", "lat": 12.9558, "lon": 77.5945},
    {"id": "BLR-23", "name": "Nimhans / Hosur Road Signal", "lat": 12.9425, "lon": 77.5985},
    {"id": "BLR-24", "name": "St. John's Hospital Madivala Signal", "lat": 12.9278, "lon": 77.6212},
    {"id": "BLR-25", "name": "Koramangala Water Tank Signal", "lat": 12.9312, "lon": 77.6234},
    {"id": "BLR-26", "name": "Sony World Signal, Koramangala", "lat": 12.9385, "lon": 77.6267},
    {"id": "BLR-27", "name": "Ejipura Inner Ring Road Signal", "lat": 12.9455, "lon": 77.6325},
    {"id": "BLR-28", "name": "Domlur Flyover Signal", "lat": 12.9610, "lon": 77.6387},
    {"id": "BLR-29", "name": "Indiranagar 100ft CMH Road Signal", "lat": 12.9784, "lon": 77.6408},
    {"id": "BLR-30", "name": "Trinity Circle MG Road Signal", "lat": 12.9728, "lon": 77.6198},
    {"id": "BLR-31", "name": "Mayo Hall / Brigade Road Junction", "lat": 12.9742, "lon": 77.6095},
    {"id": "BLR-32", "name": "Anil Kumble Circle MG Road", "lat": 12.9765, "lon": 77.5993},
    {"id": "BLR-33", "name": "Balekundri / Cunningham Road Signal", "lat": 12.9825, "lon": 77.5955},
    {"id": "BLR-34", "name": "Chalukya Circle Junction", "lat": 12.9852, "lon": 77.5842},
    {"id": "BLR-35", "name": "Windsor Manor Bridge Signal", "lat": 12.9935, "lon": 77.5845},
    {"id": "BLR-36", "name": "Cauvery Theater Bellary Road Signal", "lat": 13.0012, "lon": 77.5838},
    {"id": "BLR-37", "name": "Mekhri Circle Underpass Signal", "lat": 13.0135, "lon": 77.5848},
    {"id": "BLR-38", "name": "Bhashyam Circle Sadashivanagar", "lat": 13.0068, "lon": 77.5735},
    {"id": "BLR-39", "name": "IISc / Yeshwantpur Flyover Signal", "lat": 13.0210, "lon": 77.5615},
    {"id": "BLR-40", "name": "MS Ramaiah New BEL Road Signal", "lat": 13.0315, "lon": 77.5685},
    {"id": "BLR-41", "name": "BEL Circle Outer Ring Road Junction", "lat": 13.0445, "lon": 77.5618},
    {"id": "BLR-42", "name": "Hebbal Flyover Main Junction", "lat": 13.0450, "lon": 77.5920},
    {"id": "BLR-43", "name": "Goraguntepalya Tumkur Road Signal", "lat": 13.0285, "lon": 77.5408},
    {"id": "BLR-44", "name": "Navrang Circle Rajajinagar Signal", "lat": 12.9985, "lon": 77.5552},
    {"id": "BLR-45", "name": "Agara Outer Ring Road Signal", "lat": 12.9234, "lon": 77.6405},
    {"id": "BLR-46", "name": "Iblur Outer Ring Road Junction", "lat": 12.9228, "lon": 77.6655},
    {"id": "BLR-47", "name": "Bellandur ORR Signal", "lat": 12.9295, "lon": 77.6775},
    {"id": "BLR-48", "name": "Marathahalli Bridge Signal", "lat": 12.9568, "lon": 77.7012},
    {"id": "BLR-49", "name": "KR Puram Tin Factory Junction", "lat": 12.9965, "lon": 77.6685},
    {"id": "BLR-50", "name": "Whitefield Hope Farm Junction", "lat": 12.9835, "lon": 77.7525}
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
        "id": "BLR-01",
        "name": "Central Silk Board Junction",
        "distance_m": 450.0,
        "eta_sec": 25.0,
        "amb_approach": "NORTH",
        "lanes": {"NORTH": 26, "SOUTH": 22, "EAST": 18, "WEST": 20},
        "signals": {"NORTH": "RED", "SOUTH": "RED", "EAST": "GREEN", "WEST": "RED"},
        "t_clear_sec": 28.0,
        "trigger_threshold_sec": 35.5,
        "phase": "NORMAL_ADAPTIVE",
        "decision_reason": "Monitoring Bengaluru's 50 High-Density Traffic Signals..."
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
    return {"hospitals": HOSPITALS, "signals": BENGALURU_50_SIGNALS}

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
        j_name = packet.closest_junction_name or f"Signal ({j_id})"
        dist_m = haversine_m(packet.lat, packet.lon, packet.closest_junction_lat, packet.closest_junction_lon)
        
        speed_ms = max(packet.speed_kmh / 3.6, 4.0)
        eta_sec = round(dist_m / speed_ms, 1)

        idx_num = sum(ord(c) for c in j_id)
        amb_lane = "NORTH" if idx_num % 2 == 0 else "SOUTH"
        
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
            reason = f"⚡ GREEN CORRIDOR ACTIVE: Flushing {queue_in_amb_lane} vehicles in {amb_lane} lane at {j_name}."
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
            reason = f"🧠 Approaching {j_name} ({round(dist_m)}m away). Balancing cross-traffic."

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
        live_state["active_junction"]["decision_reason"] = f"🏥 Corridor signals cleared! Ambulance arrived at {selected_hospital['name']}!"

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