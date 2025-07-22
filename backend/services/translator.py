import openai
import os
from typing import Dict
from deep_translator import GoogleTranslator

class TranslationService:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        
        # Pre-defined translations for common phrases
        self.predefined_translations = {
            "This URL appears to be safe to visit. No significant threats detected.": 
                "ಈ ಲಿಂಕ್ ಸುರಕ್ಷಿತವಾಗಿ ಕಾಣುತ್ತದೆ. ಯಾವುದೇ ಗಮನಾರ್ಹ ಅಪಾಯಗಳು ಪತ್ತೆಯಾಗಿಲ್ಲ.",
            "This URL shows some suspicious characteristics. Exercise caution before visiting.":
                "ಈ ಲಿಂಕ್ ಕೆಲವು ಅನುಮಾನಾಸ್ಪದ ಲಕ್ಷಣಗಳನ್ನು ತೋರಿಸುತ್ತದೆ. ಭೇಟಿ ನೀಡುವ ಮೊದಲು ಎಚ್ಚರಿಕೆ ವಹಿಸಿ.",
            "⚠️ WARNING: This URL appears to be a scam or phishing site. Do not visit or enter any personal information.":
                "⚠️ ಎಚ್ಚರಿಕೆ: ಈ ಲಿಂಕ್ ಮೋಸ ಅಥವಾ ಫಿಶಿಂಗ್ ಸೈಟ್ ಆಗಿ ಕಾಣುತ್ತದೆ. ಭೇಟಿ ನೀಡಬೇಡಿ ಅಥವಾ ಯಾವುದೇ ವೈಯಕ್ತಿಕ ಮಾಹಿತಿಯನ್ನು ನಮೂದಿಸಬೇಡಿ.",
            "The site appears safe, but always verify the URL before entering sensitive information.":
                "ಸೈಟ್ ಸುರಕ್ಷಿತವಾಗಿ ಕಾಣುತ್ತದೆ, ಆದರೆ ಸೂಕ್ಷ್ಮ ಮಾಹಿತಿಯನ್ನು ನಮೂದಿಸುವ ಮೊದಲು ಯಾವಾಗಲೂ URL ಅನ್ನು ಪರಿಶೀಲಿಸಿ.",
            "Proceed with caution. Verify the sender and avoid entering personal information.":
                "ಎಚ್ಚರಿಕೆಯಿಂದ ಮುಂದುವರಿಯಿರಿ. ಕಳುಹಿಸಿದವರನ್ನು ಪರಿಶೀಲಿಸಿ ಮತ್ತು ವೈಯಕ್ತಿಕ ಮಾಹಿತಿಯನ್ನು ನಮೂದಿಸುವುದನ್ನು ತಪ್ಪಿಸಿ.",
            "DO NOT visit this site. Block the sender and report as spam/phishing.":
                "ಈ ಸೈಟ್‌ಗೆ ಭೇಟಿ ನೀಡಬೇಡಿ. ಕಳುಹಿಸಿದವರನ್ನು ನಿರ್ಬಂಧಿಸಿ ಮತ್ತು ಸ್ಪ್ಯಾಮ್/ಫಿಶಿಂಗ್ ಆಗಿ ವರದಿ ಮಾಡಿ."
        }
    
    async def translate_to_kannada(self, summary: Dict) -> Dict:
        """Translate summary to Kannada"""
        if not summary.get('english'):
            return summary
        
        english_text = summary['english']
        
        # Check if we have a predefined translation
        if english_text in self.predefined_translations:
            return {
                'english': english_text,
                'kannada': self.predefined_translations[english_text]
            }
        
        # Use AI translation if available
        if self.openai_api_key:
            try:
                kannada_text = await self._ai_translate_to_kannada(english_text)
                return {
                    'english': english_text,
                    'kannada': kannada_text
                }
            except Exception as e:
                print(f"AI translation failed: {e}")
        
        # Fallback to basic translation
        return {
            'english': english_text,
            'kannada': self._basic_translate_to_kannada(english_text)
        }
    
    async def translate_recommendations(self, recommendations: Dict) -> Dict:
        """Translate recommendations to Kannada"""
        if not recommendations.get('english'):
            return recommendations
        
        english_text = recommendations['english']
        
        # Check predefined translations
        if english_text in self.predefined_translations:
            return {
                'english': english_text,
                'kannada': self.predefined_translations[english_text]
            }
        
        # Use AI translation
        if self.openai_api_key:
            try:
                kannada_text = await self._ai_translate_to_kannada(english_text)
                return {
                    'english': english_text,
                    'kannada': kannada_text
                }
            except Exception as e:
                print(f"AI translation failed: {e}")
        
        # Fallback
        return {
            'english': english_text,
            'kannada': self._basic_translate_to_kannada(english_text)
        }
    
    async def _ai_translate_to_kannada(self, text: str) -> str:
        """Use AI to translate text to Kannada"""
        try:
            prompt = f"""
            Translate the following cybersecurity-related text from English to Kannada. 
            The translation should be accurate and appropriate for elderly users who may not be tech-savvy.
            Keep technical terms like "URL", "phishing", "scam" in English with Kannada explanations where needed.
            
            Text to translate: {text}
            
            Provide only the Kannada translation.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional translator specializing in English to Kannada translation, particularly for cybersecurity content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.1
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"AI translation error: {e}")
            return self._basic_translate_to_kannada(text)
    
    def _basic_translate_to_kannada(self, text: str) -> str:
        """Basic fallback translation using keyword replacement"""
        # Simple keyword-based translation as fallback
        translations = {
            "safe": "ಸುರಕ್ಷಿತ",
            "unsafe": "ಅಸುರಕ್ಷಿತ",
            "dangerous": "ಅಪಾಯಕಾರಿ",
            "warning": "ಎಚ್ಚರಿಕೆ",
            "caution": "ಎಚ್ಚರಿಕೆ",
            "scam": "ಮೋಸ",
            "phishing": "ಫಿಶಿಂಗ್",
            "suspicious": "ಅನುಮಾನಾಸ್ಪದ",
            "verify": "ಪರಿಶೀಲಿಸಿ",
            "do not": "ಬೇಡಿ",
            "click": "ಕ್ಲಿಕ್ ಮಾಡಿ",
            "visit": "ಭೇಟಿ ನೀಡಿ",
            "personal information": "ವೈಯಕ್ತಿಕ ಮಾಹಿತಿ"
        }
        
        kannada_text = text.lower()
        for english, kannada in translations.items():
            kannada_text = kannada_text.replace(english, kannada)
        
        return kannada_text + " (ಆಟೋ ಅನುವಾದ)"