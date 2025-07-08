import requests
import tldextract
from urllib.parse import urlparse, parse_qs
import ssl
import socket
from datetime import datetime
import re
import os
from typing import Dict, List

class URLAnalyzer:
    def __init__(self):
        self.virustotal_api_key = os.getenv("VIRUSTOTAL_API_KEY")
        self.url_shorteners = [
            'bit.ly', 'tinyurl.com', 'goo.gl', 't.co', 'short.link',
            'ow.ly', 'buff.ly', 'is.gd', 'tiny.cc', 'rebrand.ly'
        ]
        self.suspicious_patterns = [
            r'urgent',
            r'click.*now',
            r'limited.*time',
            r'verify.*account',
            r'suspend.*account',
            r'confirm.*identity',
            r'update.*payment',
            r'free.*gift',
            r'congratulations',
            r'winner',
            r'claim.*prize'
        ]
    
    async def analyze_url(self, url: str) -> Dict:
        """Comprehensive URL analysis"""
        try:
            # Ensure URL has scheme
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            analysis = {
                'original_url': url,
                'domain_info': self._analyze_domain(url),
                'ssl_info': self._check_ssl(url),
                'suspicious_patterns': self._check_suspicious_patterns(url),
                'is_shortened': self._is_shortened_url(url),
                'virustotal_detections': 0,
                'domain_age_days': 365,  # Default
                'has_ssl': True  # Default
            }
            
            # VirusTotal analysis
            vt_result = await self._check_virustotal(url)
            analysis['virustotal_detections'] = vt_result.get('detections', 0)
            analysis['virustotal_details'] = vt_result.get('details', {})
            
            # SSL check
            ssl_info = self._check_ssl(url)
            analysis['has_ssl'] = ssl_info.get('valid', False)
            analysis['ssl_details'] = ssl_info
            
            return analysis
            
        except Exception as e:
            return {
                'error': str(e),
                'original_url': url,
                'domain_info': {},
                'suspicious_patterns': [],
                'virustotal_detections': 0,
                'has_ssl': False
            }
    
    def _analyze_domain(self, url: str) -> Dict:
        """Analyze domain characteristics"""
        try:
            parsed = urlparse(url)
            extracted = tldextract.extract(url)
            
            return {
                'domain': extracted.domain,
                'suffix': extracted.suffix,
                'subdomain': extracted.subdomain,
                'full_domain': f"{extracted.domain}.{extracted.suffix}",
                'path': parsed.path,
                'query_params': parse_qs(parsed.query),
                'scheme': parsed.scheme,
                'port': parsed.port,
                'suspicious_subdomain': self._check_suspicious_subdomain(extracted.subdomain),
                'typosquatting_score': self._calculate_typosquatting_score(extracted.domain)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _check_ssl(self, url: str) -> Dict:
        """Check SSL certificate validity"""
        try:
            parsed = urlparse(url)
            hostname = parsed.hostname
            port = parsed.port or (443 if parsed.scheme == 'https' else 80)
            
            if parsed.scheme != 'https':
                return {'valid': False, 'reason': 'Not HTTPS'}
            
            context = ssl.create_default_context()
            sock = socket.create_connection((hostname, port), timeout=10)
            ssock = context.wrap_socket(sock, server_hostname=hostname)
            
            cert = ssock.getpeercert()
            ssock.close()
            
            return {
                'valid': True,
                'issuer': dict(x[0] for x in cert['issuer']),
                'subject': dict(x[0] for x in cert['subject']),
                'not_after': cert['notAfter'],
                'not_before': cert['notBefore']
            }
            
        except Exception as e:
            return {'valid': False, 'error': str(e)}
    
    def _check_suspicious_patterns(self, url: str) -> List[str]:
        """Check for suspicious patterns in URL"""
        suspicious_found = []
        url_lower = url.lower()
        
        for pattern in self.suspicious_patterns:
            if re.search(pattern, url_lower):
                suspicious_found.append(pattern)
        
        # Check for excessive subdomains
        parsed = urlparse(url)
        if parsed.hostname:
            subdomain_count = len(parsed.hostname.split('.')) - 2
            if subdomain_count > 3:
                suspicious_found.append('excessive_subdomains')
        
        # Check for suspicious TLDs
        suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.cc']
        for tld in suspicious_tlds:
            if url_lower.endswith(tld):
                suspicious_found.append(f'suspicious_tld_{tld}')
        
        return suspicious_found
    
    def _is_shortened_url(self, url: str) -> bool:
        """Check if URL is shortened"""
        parsed = urlparse(url)
        return any(shortener in parsed.netloc for shortener in self.url_shorteners)
    
    def _check_suspicious_subdomain(self, subdomain: str) -> bool:
        """Check if subdomain looks suspicious"""
        if not subdomain:
            return False
        
        # Check for random-looking subdomains
        if len(subdomain) > 8 and subdomain.isalnum():
            return True
        
        # Check for security-related terms
        security_terms = ['secure', 'login', 'account', 'verify', 'update']
        return any(term in subdomain.lower() for term in security_terms)
    
    def _calculate_typosquatting_score(self, domain: str) -> int:
        """Calculate likelihood of typosquatting"""
        popular_domains = [
            'google', 'facebook', 'amazon', 'microsoft', 'apple',
            'paypal', 'ebay', 'twitter', 'instagram', 'linkedin'
        ]
        
        score = 0
        for popular in popular_domains:
            if self._levenshtein_distance(domain.lower(), popular) <= 2:
                score += 50
        
        return min(score, 100)
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    async def _check_virustotal(self, url: str) -> Dict:
        """Check URL with VirusTotal API"""
        if not self.virustotal_api_key:
            return {'detections': 0, 'details': {}}
        
        try:
            # VirusTotal URL scanning endpoint
            vt_url = "https://www.virustotal.com/vtapi/v2/url/report"
            params = {
                'apikey': self.virustotal_api_key,
                'resource': url
            }
            
            response = requests.get(vt_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    'detections': data.get('positives', 0),
                    'total_scans': data.get('total', 0),
                    'scan_date': data.get('scan_date', ''),
                    'details': data
                }
        except Exception as e:
            print(f"VirusTotal API error: {e}")
        
        return {'detections': 0, 'details': {}}