from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from deep_translator import GoogleTranslator
import asyncio
from services.url_analyzer import URLAnalyzer
from services.ai_analyzer import AIAnalyzer
from services.translator import TranslationService
from services.db import save_analysis
import pathlib


dotenv_path = pathlib.Path(__file__).parent / ".env"
print("Looking for .env at:", dotenv_path)  
load_dotenv(dotenv_path=dotenv_path)
print("Mongo URI from env:", os.getenv("MONGO_URI"))

app = FastAPI(title="Scam URL Detector API", version="1.0.0")


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
url_analyzer = URLAnalyzer()
ai_analyzer = AIAnalyzer()
translator = TranslationService()

class URLRequest(BaseModel):
    url: str
    language: str = "en"  # en or kn (kannada)

class URLResponse(BaseModel):
    url: str
    trust_score: int
    risk_level: str
    summary: dict
    details: dict
    recommendations: dict

@app.get("/")
async def root():
    return {"message": "Scam URL Detector API is running"}

@app.post("/analyze-url", response_model=URLResponse)
async def analyze_url(request: URLRequest):
    print(" POST /analyze-url was triggered!")
    try:
        # Step 1: Basic URL analysis
        url_data = await url_analyzer.analyze_url(request.url)

        # Step 2: AI content analysis
        ai_analysis = await ai_analyzer.analyze_content(request.url)

        # Step 3: Calculate trust score
        trust_score = calculate_trust_score(url_data, ai_analysis)
        
        # Step 4: Generate summary and recommendations
        summary = generate_summary(url_data, ai_analysis, trust_score)
        recommendations = generate_recommendations(trust_score)

        # Step 5: Translate if needed
        if request.language == "kn":
            summary = await translator.translate_to_kannada(summary)
            recommendations = await translator.translate_recommendations(recommendations)
        
        # Determine risk level
        risk_level = "LOW" if trust_score >= 70 else "MEDIUM" if trust_score >= 40 else "HIGH"
        
        try:
            print("Trying to save analysis to MongoDB...")

            await save_analysis({
                "url": request.url,
                "trust_score": trust_score,
                "risk_level": risk_level,
                "summary": summary,
                "recommendations": recommendations,
                "details": {
                    "domain_info": url_data,
                    "ai_analysis": ai_analysis
                }
            })
            print("Saved to MongoDB successfully.")
        except Exception as db_error:
            print("MongoDB Save Failed:", repr(db_error))


        return URLResponse(
            url=request.url,
            trust_score=trust_score,
            risk_level=risk_level,
            summary=summary,
            details={
                "domain_info": url_data,
                "ai_analysis": ai_analysis
            },
            recommendations=recommendations
        )
        
    except Exception as e:
        print(" Error inside analyze_url():", repr(e))
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

def calculate_trust_score(url_data: dict, ai_analysis: dict) -> int:
    """Calculate trust score based on various factors"""
    score = 100
    
    # VirusTotal detections
    if url_data.get("virustotal_detections", 0) > 0:
        score -= url_data["virustotal_detections"] * 15
    
    # Domain age
    if url_data.get("domain_age_days", 365) < 30:
        score -= 20
    
    # SSL certificate
    if not url_data.get("has_ssl", False):
        score -= 15
    
    # Suspicious patterns
    score -= len(url_data.get("suspicious_patterns", [])) * 10
    
    # AI analysis
    if ai_analysis.get("is_phishing", False):
        score -= 30
    
    if ai_analysis.get("urgency_detected", False):
        score -= 15
    
    return max(0, min(100, score))

def generate_summary(url_data: dict, ai_analysis: dict, trust_score: int) -> dict:
    """Generate human-readable summary"""
    if trust_score >= 70:
        return {
            "english": "This URL appears to be safe to visit. No significant threats detected.",
            "kannada": "ಈ ಲಿಂಕ್ ಸುರಕ್ಷಿತವಾಗಿ ಕಾಣುತ್ತದೆ. ಯಾವುದೇ ಗಮನಾರ್ಹ ಅಪಾಯಗಳು ಪತ್ತೆಯಾಗಿಲ್ಲ."
        }
    elif trust_score >= 40:
        return {
            "english": "This URL shows some suspicious characteristics. Exercise caution before visiting.",
            "kannada": "ಈ ಲಿಂಕ್ ಕೆಲವು ಅನುಮಾನಾಸ್ಪದ ಲಕ್ಷಣಗಳನ್ನು ತೋರಿಸುತ್ತದೆ. ಭೇಟಿ ನೀಡುವ ಮೊದಲು ಎಚ್ಚರಿಕೆ ವಹಿಸಿ."
        }
    else:
        return {
            "english": "⚠️ WARNING: This URL appears to be a scam or phishing site. Do not visit or enter any personal information.",
            "kannada": "⚠️ ಎಚ್ಚರಿಕೆ: ಈ ಲಿಂಕ್ ಮೋಸ ಅಥವಾ ಫಿಶಿಂಗ್ ಸೈಟ್ ಆಗಿ ಕಾಣುತ್ತದೆ. ಭೇಟಿ ನೀಡಬೇಡಿ ಅಥವಾ ಯಾವುದೇ ವೈಯಕ್ತಿಕ ಮಾಹಿತಿಯನ್ನು ನಮೂದಿಸಬೇಡಿ."
        }

def generate_recommendations(trust_score: int) -> dict:
    """Generate safety recommendations"""
    if trust_score >= 70:
        return {
            "english": "The site appears safe, but always verify the URL before entering sensitive information.",
            "kannada": "ಸೈಟ್ ಸುರಕ್ಷಿತವಾಗಿ ಕಾಣುತ್ತದೆ, ಆದರೆ ಸೂಕ್ಷ್ಮ ಮಾಹಿತಿಯನ್ನು ನಮೂದಿಸುವ ಮೊದಲು ಯಾವಾಗಲೂ URL ಅನ್ನು ಪರಿಶೀಲಿಸಿ."
        }
    elif trust_score >= 40:
        return {
            "english": "Proceed with caution. Verify the sender and avoid entering personal information.",
            "kannada": "ಎಚ್ಚರಿಕೆಯಿಂದ ಮುಂದುವರಿಯಿರಿ. ಕಳುಹಿಸಿದವರನ್ನು ಪರಿಶೀಲಿಸಿ ಮತ್ತು ವೈಯಕ್ತಿಕ ಮಾಹಿತಿಯನ್ನು ನಮೂದಿಸುವುದನ್ನು ತಪ್ಪಿಸಿ."
        }
    else:
        return {
            "english": "DO NOT visit this site. Block the sender and report as spam/phishing.",
            "kannada": "ಈ ಸೈಟ್‌ಗೆ ಭೇಟಿ ನೀಡಬೇಡಿ. ಕಳುಹಿಸಿದವರನ್ನು ನಿರ್ಬಂಧಿಸಿ ಮತ್ತು ಸ್ಪ್ಯಾಮ್/ಫಿಶಿಂಗ್ ಆಗಿ ವರದಿ ಮಾಡಿ."
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)