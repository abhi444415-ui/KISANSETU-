# -*- coding: utf-8 -*-
import os
import time
import random
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(
    title="🌱 Smart Crop Health Early Warning API",
    description="Backend API for crop disease detection, weather risk forecasting, IoT pest surveillance, and expert validation",
    version="1.0.0"
)

# Enable CORS for local development & frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CROPS_DATABASE = {
    "Rice": {
        "varieties": ["Pusa Basmati 1121", "IR64", "Swarna", "MTU 1010"],
        "diseases": [
            {
                "id": "rice_stem_borer",
                "name": "Yellow Stem Borer (Scirpophaga incertulas)",
                "confidence": 0.93,
                "symptoms": ["Deadhearts in vegetative stage", "Whiteheads during flowering", "Bore holes in stem base"],
                "risk_level": "CRITICAL",
                "ipm": {
                    "prevention": "Use resistant varieties, synchronized planting, clip leaf tips during transplanting.",
                    "monitoring": "Install pheromone traps (5 traps/ha) and light traps to monitor moth activity.",
                    "biological": "Release Trichogramma japonicum @ 100,000 parasites/ha.",
                    "chemical": "Chlorantraniliprole 18.5% SC @ 150 ml/ha if deadhearts exceed 10% threshold. Observe 47-day PHI."
                }
            },
            {
                "id": "rice_blast",
                "name": "Rice Blast (Magnaporthe oryzae)",
                "confidence": 0.89,
                "symptoms": ["Spindle-shaped lesions with grayish centers", "Node discoloration", "Neck rot"],
                "risk_level": "HIGH",
                "ipm": {
                    "prevention": "Avoid excess nitrogen fertilizer, maintain proper water depth.",
                    "monitoring": "Inspect field margins and young leaves daily during foggy weather.",
                    "biological": "Seed treatment with Pseudomonas fluorescens @ 10g/kg.",
                    "chemical": "Tricyclazole 75% WP @ 0.6 g/L water if leaf blast affects >5% area."
                }
            }
        ]
    },
    "Tomato": {
        "varieties": ["Arka Rakshak", "Pusa Ruby", "Heemsohna", "Abhinav"],
        "diseases": [
            {
                "id": "tomato_early_blight",
                "name": "Early Blight (Alternaria solani)",
                "confidence": 0.91,
                "symptoms": ["Target-like concentric ring brown lesions", "Yellowing around lower leaves", "Premature defoliation"],
                "risk_level": "HIGH",
                "ipm": {
                    "prevention": "Crop rotation with non-solanaceous crops, wider spacing, drip irrigation to reduce leaf wetness.",
                    "monitoring": "Weekly leaf scouting starting at lower canopy after flowering.",
                    "biological": "Spray Trichoderma harzianum @ 5g/L water preventatively.",
                    "chemical": "Mancozeb 75% WP @ 2.5 g/L or Azoxystrobin 23% SC @ 1 ml/L. Follow 5-day PHI and wear full PPE."
                }
            },
            {
                "id": "tomato_late_blight",
                "name": "Late Blight (Phytophthora infestans)",
                "confidence": 0.94,
                "symptoms": ["Water-soaked dark lesions", "White cottony fungal growth on leaf underside in high humidity", "Rapid stem blackening"],
                "risk_level": "CRITICAL",
                "ipm": {
                    "prevention": "Destroy infected plant residue, avoid overhead sprinkler irrigation.",
                    "monitoring": "Daily humidity monitoring (>85% RH for 8+ consecutive hours is high risk).",
                    "biological": "Bacillus subtilis bio-fungicide spray.",
                    "chemical": "Cymoxanil + Mancozeb @ 2 g/L. Apply immediately upon detection."
                }
            }
        ]
    },
    "Wheat": {
        "varieties": ["HD 2967", "DBW 187", "PBW 550", "GW 322"],
        "diseases": [
            {
                "id": "wheat_yellow_rust",
                "name": "Stripe / Yellow Rust (Puccinia striiformis)",
                "confidence": 0.88,
                "symptoms": ["Yellow pustules arranged in linear stripes on leaves", "Stunted growth", "Powdery yellow spores"],
                "risk_level": "HIGH",
                "ipm": {
                    "prevention": "Plant rust-resistant varieties like DBW 187; balance N-P-K fertilizer ratio.",
                    "monitoring": "Scout fields regularly in December-February when cool temperatures prevail.",
                    "biological": "Bio-formulation treatment with Neem oil 1500 ppm.",
                    "chemical": "Propiconazole 25% EC @ 1 ml/L water at first appearance of yellow stripes."
                }
            }
        ]
    },
    "Potato": {
        "varieties": ["Kufri Pukhraj", "Kufri Jyoti", "Kufri Bahar"],
        "diseases": [
            {
                "id": "potato_late_blight",
                "name": "Potato Late Blight (Phytophthora infestans)",
                "confidence": 0.95,
                "symptoms": ["Irregular dark lesions on leaf tips", "White mildew on lower surface", "Foul smelling decaying foliage"],
                "risk_level": "CRITICAL",
                "ipm": {
                    "prevention": "High earthing up, use disease-free certified seed tubers.",
                    "monitoring": "Track cumulative rainy days and fog hours.",
                    "biological": "Pseudomonas fluorescens soil drenching.",
                    "chemical": "Metalaxyl 8% + Mancozeb 64% WP @ 2.5 g/L."
                }
            }
        ]
    },
    "Cotton": {
        "varieties": ["RCH 659", "Bunny Bt", "Bhakti"],
        "diseases": [
            {
                "id": "cotton_pink_bollworm",
                "name": "Pink Bollworm (Pectinophora gossypiella)",
                "confidence": 0.86,
                "symptoms": ["Rosetted flowers ('rosette flower' symptom)", "Bores into developing bolls", "Lint staining"],
                "risk_level": "HIGH",
                "ipm": {
                    "prevention": "Adopt crop termination by December, destroy crop residues.",
                    "monitoring": "Pheromone trap monitoring (8 moths/trap/night for 3 consecutive nights = trigger).",
                    "biological": "Release Trichogramma chilonis @ 150,000/ha.",
                    "chemical": "Profofos 50% EC @ 2 ml/L or Emamectin benzoate 5% SG @ 0.4 g/L."
                }
            }
        ]
    },
    "Maize": {
        "varieties": ["Pioneer 3396", "DKC 9108", "HQPM 1"],
        "diseases": [
            {
                "id": "maize_fall_armyworm",
                "name": "Fall Armyworm (Spodoptera frugiperda)",
                "confidence": 0.92,
                "symptoms": ["Pin-hole damage on young leaves", "Frass accumulation in whorls", "Skeletonized foliage"],
                "risk_level": "CRITICAL",
                "ipm": {
                    "prevention": "Deep autumn plowing, intercropping with cowpea/desmodium.",
                    "monitoring": "Check 20 consecutive plants in 5 locations per field.",
                    "biological": "Apply Metarhizium anisopliae or sand/ash mixture in whorls.",
                    "chemical": "Spinetoram 11.7% SC @ 0.5 ml/L or Chlorantraniliprole 18.5% SC @ 0.4 ml/L."
                }
            }
        ]
    }
}

HOTSPOTS_DATA = [
    {
        "id": "h1",
        "village": "Rampur",
        "district": "Gorakhpur",
        "lat": 26.7606,
        "lng": 83.3732,
        "crop": "Rice",
        "reports_count": 23,
        "main_issue": "Yellow Stem Borer Outbreak",
        "risk_score": 87,
        "risk_level": "CRITICAL",
        "trend": "increasing",
        "extension_worker": "Ramesh Kumar (Ext-402)",
        "last_report": "12 mins ago"
    },
    {
        "id": "h2",
        "village": "Shivpur",
        "district": "Varanasi",
        "lat": 25.3176,
        "lng": 82.9739,
        "crop": "Tomato",
        "reports_count": 14,
        "main_issue": "Early Blight Spreading",
        "risk_score": 72,
        "risk_level": "HIGH",
        "trend": "increasing",
        "extension_worker": "Sneh Lata (Ext-308)",
        "last_report": "45 mins ago"
    },
    {
        "id": "h3",
        "village": "Lakshmi Nagar",
        "district": "Barabanki",
        "lat": 26.9271,
        "lng": 81.1834,
        "crop": "Wheat",
        "reports_count": 8,
        "main_issue": "Stripe Rust Warning",
        "risk_score": 51,
        "risk_level": "MODERATE",
        "trend": "stable",
        "extension_worker": "Amit Verma (Ext-112)",
        "last_report": "2 hours ago"
    },
    {
        "id": "h4",
        "village": "Chandpur",
        "district": "Bijnor",
        "lat": 29.1352,
        "lng": 78.2721,
        "crop": "Maize",
        "reports_count": 31,
        "main_issue": "Fall Armyworm Infestation",
        "risk_score": 94,
        "risk_level": "CRITICAL",
        "trend": "increasing",
        "extension_worker": "Priya Sharma (Ext-501)",
        "last_report": "5 mins ago"
    },
    {
        "id": "h5",
        "village": "Green Valley",
        "district": "Ludhiana",
        "lat": 30.9010,
        "lng": 75.8573,
        "crop": "Cotton",
        "reports_count": 5,
        "main_issue": "Pink Bollworm Rosette",
        "risk_score": 38,
        "risk_level": "LOW",
        "trend": "decreasing",
        "extension_worker": "Gurpreet Singh (Ext-204)",
        "last_report": "5 hours ago"
    }
]

EXPERTS_DIRECTORY = [
    {
        "id": "exp_1",
        "name": "Dr. Ramesh Kumar (Dr. Ramesh Kumar)",
        "role": "Senior Agronomist / Plant Pathologist",
        "phone": "+91 98765 43210",
        "specialization": "Rice, Wheat & Cereals",
        "experience": "16 Years (ICAR Certified)",
        "status": "Available",
        "avatar": "👨‍🔬"
    },
    {
        "id": "exp_2",
        "name": "Dr. Anita Verma (Dr. Anita Verma)",
        "role": "Horticulture Specialist",
        "phone": "+91 98123 45678",
        "specialization": "Tomato, Potato & Vegetables",
        "experience": "12 Years",
        "status": "Available",
        "avatar": "👩‍🔬"
    },
    {
        "id": "exp_3",
        "name": "Dr. Suresh Patel (Dr. Suresh Patel)",
        "role": "Entomologist & Pest Specialist",
        "phone": "+91 97654 32109",
        "specialization": "Cotton, Maize & Stem Borers",
        "experience": "14 Years",
        "status": "In Field Visit",
        "avatar": "👨‍⚕️"
    }
]

# API Endpoints

@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "system": "🌱 Smart Crop Health Early Warning & Decision Support System",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

@app.get("/api/crops")
def get_crops():
    return CROPS_DATABASE

@app.get("/api/experts")
def get_experts():
    return EXPERTS_DIRECTORY

class RiskCalcInput(BaseModel):
    image_score: float = 35.0
    weather_score: float = 20.0
    pest_trap_score: float = 20.0
    historical_score: float = 10.0
    crop_stage_score: float = 10.0
    soil_score: float = 5.0

@app.post("/api/risk/calculate")
def calculate_risk(input_data: RiskCalcInput):
    total = (
        input_data.image_score * 0.35 +
        input_data.weather_score * 0.25 +
        input_data.pest_trap_score * 0.20 +
        input_data.historical_score * 0.10 +
        input_data.crop_stage_score * 0.05 +
        input_data.soil_score * 0.05
    )
    score = min(100, max(0, round(total, 1)))
    level = "CRITICAL" if score >= 80 else ("HIGH" if score >= 65 else ("MODERATE" if score >= 40 else "LOW"))
    return {
        "score": score,
        "level": level,
        "breakdown": input_data.dict()
    }

@app.get("/api/weather")
def get_weather():
    return {
        "current": {
            "temp": 29.4,
            "humidity": 84,
            "rainfall_mm": 18.2,
            "wind_kmh": 11.5,
            "condition": "Humid & Overcast",
            "risk_assessment": "HIGH - Persistent high humidity (>80%) and warm temp (28-30°C) favor rapid fungal & bacterial multiplication."
        },
        "forecast": [
            {"day": "Mon", "temp": 29, "humidity": 84, "rain": "18mm", "risk": "HIGH"},
            {"day": "Tue", "temp": 30, "humidity": 88, "rain": "24mm", "risk": "CRITICAL"},
            {"day": "Wed", "temp": 28, "humidity": 82, "rain": "12mm", "risk": "HIGH"},
            {"day": "Thu", "temp": 31, "humidity": 75, "rain": "2mm", "risk": "MODERATE"},
            {"day": "Fri", "temp": 32, "humidity": 68, "rain": "0mm", "risk": "LOW"},
            {"day": "Sat", "temp": 30, "humidity": 72, "rain": "0mm", "risk": "MODERATE"},
            {"day": "Sun", "temp": 29, "humidity": 80, "rain": "8mm", "risk": "HIGH"}
        ]
    }

@app.get("/api/iot/sensors")
def get_iot_sensors():
    return {
        "status": "Online",
        "trap_chart_data": [
            {"day": "Day 1", "count": 4},
            {"day": "Day 2", "count": 6},
            {"day": "Day 3", "count": 8},
            {"day": "Day 4", "count": 12},
            {"day": "Day 5", "count": 18}
        ],
        "metrics": {
            "temperature": "29.4°C",
            "soil_moisture": "64%",
            "humidity": "84%",
            "trap_count": "18 insects (Threshold Exceeded)",
            "leaf_wetness": "7.5 hrs"
        },
        "alert": "⚠️ Pest trap counts increased by 350% over 5 days. Economic Threshold Exceeded."
    }

@app.get("/api/hotspots")
def get_hotspots():
    return HOTSPOTS_DATA

@app.get("/api/analytics")
def get_analytics():
    return {
        "metrics": {
            "total_reports": 12450,
            "high_risk": 1240,
            "hotspots": 86,
            "expert_validated": "74%",
            "active_investigations": 31,
            "avg_response_hours": 3.8
        },
        "district_risk": [
            {"district": "Gorakhpur", "risk_index": 87, "reports": 3420},
            {"district": "Varanasi", "risk_index": 72, "reports": 2180},
            {"district": "Barabanki", "risk_index": 51, "reports": 1850},
            {"district": "Bijnor", "risk_index": 94, "reports": 4100},
            {"district": "Ludhiana", "risk_index": 38, "reports": 900}
        ],
        "crop_distribution": [
            {"crop": "Rice", "percentage": 42},
            {"crop": "Tomato", "percentage": 24},
            {"crop": "Wheat", "percentage": 18},
            {"crop": "Cotton", "percentage": 10},
            {"crop": "Maize", "percentage": 6}
        ]
    }

@app.post("/api/chatbot")
def hindi_kisan_chatbot(data: Dict[str, Any] = Body(...)):
    message = data.get("message", "").lower()
    
    if "yellow" in message or "blight" in message or "dhabbe" in message or "peele" in message or "पीले" in message:
        reply = "🌾 Aapki fasal me peele dhabbe (yellow blight) ki samasya ho sakti hai. Trichoderma (5g/L) ka chhidkaav karein."
    elif "rice" in message or "borer" in message or "dhan" in message or "धान" in message or "keede" in message:
        reply = "🐛 Dhaan ke keede (Stem Borer) ke liye pheromone trap 5/ha lagayein."
    elif "rain" in message or "weather" in message or "barish" in message or "मौसम" in message:
        reply = "🌧️ Agle 48 ghanto me high humidity ka anumaan hai. Barish ke baad hi kitnashak spray karein."
    elif "call" in message or "expert" in message or "doctor" in message or "कॉल" in message:
        reply = "📞 Aap 'Call Expert' button se Dr. Ramesh Kumar (+91 98765 43210) se baat kar sakte hain."
    else:
        reply = "🙏 Namaste Kisan Bhai! Main aapka Kisan AI sahayak hoon. Apni fasal ki photo scan karein ya koi sawaal poohein."
        
    return {
        "reply": reply,
        "timestamp": time.strftime("%H:%M")
    }

@app.post("/api/scan")
def process_scan(data: Dict[str, Any] = Body(...)):
    return {
        "status": "success",
        "predicted_disease": data.get("disease", "Early Blight (Alternaria solani)"),
        "confidence": data.get("confidence", 91),
        "risk_score": data.get("risk", 82),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

@app.post("/api/expert/validate")
def expert_validate(data: Dict[str, Any] = Body(...)):
    return {
        "status": "success",
        "case_id": data.get("case_id"),
        "action": data.get("action"),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

@app.post("/api/lab/referral")
def lab_referral(data: Dict[str, Any] = Body(...)):
    return {
        "status": "success",
        "referral_id": f"LAB-{random.randint(1000, 9999)}",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

@app.post("/api/sync")
def sync_offline(data: List[Dict[str, Any]] = Body(...)):
    return {
        "status": "synced",
        "count": len(data),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

# Absolute path resolution for static files (Render / Cloud deployment safe)
js_dir = os.path.join(BASE_DIR, "js")
if os.path.exists(js_dir):
    app.mount("/js", StaticFiles(directory=js_dir), name="js")

style_file = os.path.join(BASE_DIR, "style.css")
@app.get("/style.css")
def serve_css():
    if os.path.exists(style_file):
        return FileResponse(style_file, media_type="text/css")
    raise HTTPException(status_code=404, detail="CSS file not found")

index_file = os.path.join(BASE_DIR, "index.html")
@app.get("/")
def serve_root():
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Smart Crop Health API is running"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
