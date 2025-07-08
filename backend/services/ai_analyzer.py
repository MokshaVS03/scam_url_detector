import requests
from bs4 import BeautifulSoup
import openai
import os
import re
from typing import Dict, List
import asyncio

class AIAnalyzer:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        
        self.phishing_keywords = [
            'urgent', 'verify', 'suspend', 'confirm', 'update',
            'click here', 'act now', 'limited time', 'expire',
            'congratulations', 'winner', 'prize', 'free gift',
            'security alert', 'account locked', 'payment failed'
        ]
        
        self.form_indicators = [
            'password', 'credit card', 'ssn', 'social security',
            'bank account', 'login', 'signin', 'card number'
        ]
    
    async def analyze_content(self, url: str) -> Dict:
        """Analyze webpage content for phishing indicators"""
        try:
            # Fetch webpage content
            content_data = await self._fetch_webpage_content(url)
            
            if not content_data.get('success'):
                return {
                    'error': content_data.get('error', 'Failed to fetch content'),
                    'is_phishing': False,
                    'confidence': 0
                }
            
            # Basic pattern analysis
            basic_analysis = self._analyze_basic_patterns(content_data)
            
            # AI-powered analysis
            ai_analysis = await self._ai_content_analysis(content_data)
            
            # Combine results
            combined_analysis = {
                'is_phishing': basic_analysis['is_phishing'] or ai_analysis['is_phishing'],
                'confidence': max(basic_analysis['confidence'], ai_analysis['confidence']),
                'urgency_detected': basic_analysis['urgency_detected'],
                'form_analysis': basic_analysis['form_analysis'],
                'keyword_matches': basic_analysis['keyword_matches'],
                'ai_reasoning': ai_analysis.get('reasoning', ''),
                'content_summary': content_data.get('text', '')[:500] + '...' if len(content_data.get('text', '')) > 500 else content_data.get('text', '')
            }
            
            return combined_analysis
            
        except Exception as e:
            return {
                'error': str(e),
                'is_phishing': False,
                'confidence': 0
            }
    
    async def _fetch_webpage_content(self, url: str) -> Dict:
        """Fetch and parse webpage content"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract text content
            text_content = soup.get_text(separator=' ', strip=True)
            
            # Extract forms
            forms = []
            for form in soup.find_all('form'):
                form_data = {
                    'action': form.get('action', ''),
                    'method': form.get('method', 'get'),
                    'inputs': []
                }
                
                for input_tag in form.find_all(['input', 'textarea', 'select']):
                    form_data['inputs'].append({
                        'type': input_tag.get('type', 'text'),
                        'name': input_tag.get('name', ''),
                        'placeholder': input_tag.get('placeholder', ''),
                        'required': input_tag.get('required', False)
                    })
                
                forms.append(form_data)
            
            # Extract links
            links = [a.get('href', '') for a in soup.find_all('a', href=True)]
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text(strip=True) if title else ''
            
            return {
                'success': True,
                'text': text_content,
                'title': title_text,
                'forms': forms,
                'links': links,
                'html_length': len(response.content)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _analyze_basic_patterns(self, content_data: Dict) -> Dict:
        """Analyze content for basic phishing patterns"""
        text = content_data.get('text', '').lower()
        title = content_data.get('title', '').lower()
        forms = content_data.get('forms', [])
        
        # Check for phishing keywords
        keyword_matches = []
        for keyword in self.phishing_keywords:
            if keyword in text or keyword in title:
                keyword_matches.append(keyword)
        
        # Check for urgency indicators
        urgency_patterns = [
            r'urgent.*action',
            r'expire.*soon',
            r'immediate.*attention',
            r'within.*\d+.*hours?',
            r'act.*now',
            r'limited.*time'
        ]
        
        urgency_detected = any(re.search(pattern, text) for pattern in urgency_patterns)
        
        # Analyze forms
        form_analysis = {
            'has_forms': len(forms) > 0,
            'suspicious_forms': [],
            'credential_harvesting': False
        }
        
        for form in forms:
            form_text = ' '.join([inp.get('name', '') + ' ' + inp.get('placeholder', '') for inp in form.get('inputs', [])])
            
            suspicious_indicators = []
            for indicator in self.form_indicators:
                if indicator in form_text.lower():
                    suspicious_indicators.append(indicator)
            
            if suspicious_indicators:
                form_analysis['suspicious_forms'].append({
                    'action': form.get('action', ''),
                    'indicators': suspicious_indicators
                })
                form_analysis['credential_harvesting'] = True
        
        # Calculate confidence
        confidence = 0
        if keyword_matches:
            confidence += len(keyword_matches) * 15
        if urgency_detected:
            confidence += 25
        if form_analysis['credential_harvesting']:
            confidence += 30
        
        confidence = min(confidence, 100)
        
        return {
            'is_phishing': confidence > 40,
            'confidence': confidence,
            'urgency_detected': urgency_detected,
            'form_analysis': form_analysis,
            'keyword_matches': keyword_matches
        }
    
    async def _ai_content_analysis(self, content_data: Dict) -> Dict:
        """Use AI to analyze content for phishing"""
        if not self.openai_api_key:
            return {
                'is_phishing': False,
                'confidence': 0,
                'reasoning': 'AI analysis unavailable - no API key'
            }
        
        try:
            text = content_data.get('text', '')
            title = content_data.get('title', '')
            
            # Limit text length for API efficiency
            analysis_text = (title + ' ' + text)[:2000]
            
            prompt = f"""
            Analyze the following webpage content for phishing/scam indicators:
            
            Title: {title}
            Content: {analysis_text}
            
            Consider these factors:
            1. Urgency language and pressure tactics
            2. Requests for personal/financial information
            3. Grammatical errors and poor writing quality
            4. Suspicious offers or claims
            5. Impersonation of legitimate organizations
            6. Fear-based messaging
            
            Respond with a JSON object containing:
            - is_phishing: boolean
            - confidence: number (0-100)
            - reasoning: string explaining the analysis
            - risk_factors: array of identified risk factors
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a cybersecurity expert specializing in phishing detection."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.1
            )
            
            ai_response = response.choices[0].message.content
            
            # Try to parse JSON response
            try:
                import json
                result = json.loads(ai_response)
                return {
                    'is_phishing': result.get('is_phishing', False),
                    'confidence': result.get('confidence', 0),
                    'reasoning': result.get('reasoning', ''),
                    'risk_factors': result.get('risk_factors', [])
                }
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    'is_phishing': 'phishing' in ai_response.lower() or 'scam' in ai_response.lower(),
                    'confidence': 50,
                    'reasoning': ai_response
                }
                
        except Exception as e:
            return {
                'is_phishing': False,
                'confidence': 0,
                'reasoning': f'AI analysis failed: {str(e)}'
            }