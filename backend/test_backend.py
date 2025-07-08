import asyncio
import sys
import os

# Fix encoding issues on Windows
if sys.platform == "win32":
    # Set console to UTF-8
    os.system("chcp 65001 > nul")
    # Set stdout encoding
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.url_analyzer import URLAnalyzer
from services.ai_analyzer import AIAnalyzer
from services.translator import TranslationService

async def test_services():
    print("Testing Scam URL Detector Services...")
    print("=" * 50)
    
    # Initialize services
    url_analyzer = URLAnalyzer()
    ai_analyzer = AIAnalyzer()
    translator = TranslationService()
    
    # Test URLs
    test_urls = [
        "https://google.com",
        "https://example.com",
        "http://suspicious-site.tk"
    ]
    
    for url in test_urls:
        print(f"\nTesting URL: {url}")
        print("-" * 30)
        
        # Test URL Analysis
        try:
            url_result = await url_analyzer.analyze_url(url)
            print(f"✓ URL Analysis completed")
            print(f"  - Domain: {url_result.get('domain_info', {}).get('domain', 'N/A')}")
            print(f"  - SSL Valid: {url_result.get('has_ssl', False)}")
            print(f"  - Suspicious patterns: {len(url_result.get('suspicious_patterns', []))}")
        except Exception as e:
            print(f"✗ URL Analysis failed: {e}")
        
        # Test AI Analysis
        try:
            ai_result = await ai_analyzer.analyze_content(url)
            print(f"✓ AI Analysis completed")
            print(f"  - Is Phishing: {ai_result.get('is_phishing', False)}")
            print(f"  - Confidence: {ai_result.get('confidence', 0)}%")
        except Exception as e:
            print(f"✗ AI Analysis failed: {e}")
        
        # Test Translation
        try:
            summary = {"english": "This site appears safe to visit."}
            translated = await translator.translate_to_kannada(summary)
            print(f"✓ Translation completed")
            print(f"  - English: {translated.get('english', 'N/A')}")
            print(f"  - Kannada: {translated.get('kannada', 'N/A')}")
        except Exception as e:
            print(f"✗ Translation failed: {e}")
    
    print("\n" + "=" * 50)
    print("Testing completed!")

if __name__ == "__main__":
    asyncio.run(test_services())