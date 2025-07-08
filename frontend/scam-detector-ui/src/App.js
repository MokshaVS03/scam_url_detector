import React, { useState } from 'react';
import { Shield, AlertTriangle, CheckCircle, Loader, Languages } from 'lucide-react';
import './App.css';

const App = () => {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [language, setLanguage] = useState('en');

  const analyzeUrl = async (e) => {
    e.preventDefault();
    if (!url.trim()) {
      setError('Please enter a URL to analyze');
      return;
    }
    console.log(" analyzeUrl() triggered");

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await fetch('http://127.0.0.1:8000/analyze-url', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: url.trim(),
          language: language
        }),
      });
      console.log(" API response status:", response.status);
      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError('Failed to analyze URL. Please try again.');
      console.error('Analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'LOW': return 'text-green-600';
      case 'MEDIUM': return 'text-yellow-600';
      case 'HIGH': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getRiskIcon = (riskLevel) => {
    switch (riskLevel) {
      case 'LOW': return <CheckCircle className="w-6 h-6 text-green-600" />;
      case 'MEDIUM': return <AlertTriangle className="w-6 h-6 text-yellow-600" />;
      case 'HIGH': return <AlertTriangle className="w-6 h-6 text-red-600" />;
      default: return <Shield className="w-6 h-6 text-gray-600" />;
    }
  };

  const getTrustScoreColor = (score) => {
    if (score >= 70) return 'bg-green-500';
    if (score >= 40) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Shield className="w-8 h-6 text-blue-600" />
              <h1 className="text-2xl font-bold text-gray-900">
                Surakshak
              </h1>
            </div>
            <div className="flex items-center space-x-2">
              <Languages className="w-5 h-5 text-gray-600" />
              <select 
                value={language} 
                onChange={(e) => setLanguage(e.target.value)}
                className="px-3 py-1 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="en">English</option>
                <option value="kn">ಕನ್ನಡ</option>
              </select>
            </div>
          </div>
          <p className="mt-2 text-gray-600">
            Protect yourself from phishing and scam websites. Enter a suspicious URL to analyze.
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* URL Input Form */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="space-y-4">
            <div>
              <label htmlFor="url" className="block text-sm font-medium text-gray-700 mb-2">
                Enter URL to analyze:
              </label>
              <div className="flex space-x-3">
                <div className="flex-1 relative">
                  
                  <input
                    type="text"
                    id="url"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="https://suspicious-website.com"
                    className=" w-full pl-16 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    disabled={loading}
                  />
                </div>
                <button
                  type="submit"
                  onClick={analyzeUrl}
                  disabled={loading}
                  className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                >
                  {loading ? (
                    <>
                      <Loader className="w-4 h-4 animate-spin" />
                      <span>Analyzing...</span>
                    </>
                  ) : (
                    <>
                      <Shield className="w-4 h-4" />
                      <span>Analyze</span>
                    </>
                  )}
                </button>
              </div>
            </div>
            {error && (
              <div className="text-red-600 text-sm">{error}</div>
            )}
          </div>
        </div>

        {/* Results */}
        {result && (
          <div className="space-y-6">
            {/* Trust Score */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-900">Trust Score</h2>
                <div className="flex items-center space-x-2">
                  {getRiskIcon(result.risk_level)}
                  <span className={`font-semibold ${getRiskColor(result.risk_level)}`}>
                    {result.risk_level} RISK
                  </span>
                </div>
              </div>
              
              <div className="mb-4">
                <div className="flex justify-between text-sm text-gray-600 mb-2">
                  <span>Trust Score</span>
                  <span>{result.trust_score}/100</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div 
                    className={`h-3 rounded-full transition-all duration-500 ${getTrustScoreColor(result.trust_score)}`}
                    style={{ width: `${result.trust_score}%` }}
                  ></div>
                </div>
              </div>

              {/* Summary */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="font-medium text-gray-900 mb-2">Analysis Summary</h3>
                <p className="text-gray-700">
                  {language === 'kn' ? result.summary.kannada : result.summary.english}
                </p>
              </div>
            </div>

            {/* Recommendations */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Recommendations</h2>
              <div className="bg-blue-50 rounded-lg p-4">
                <p className="text-blue-800">
                  {language === 'kn' ? result.recommendations.kannada : result.recommendations.english}
                </p>
              </div>
            </div>

            {/* Technical Details */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Technical Details</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h3 className="font-medium text-gray-900 mb-2">Domain Information</h3>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>Domain: {result.details.domain_info.domain_info?.domain || 'N/A'}</li>
                    <li>SSL Valid: {result.details.domain_info.has_ssl ? 'Yes' : 'No'}</li>
                    <li>Suspicious Patterns: {result.details.domain_info.suspicious_patterns?.length || 0}</li>
                    <li>VirusTotal Detections: {result.details.domain_info.virustotal_detections || 0}</li>
                  </ul>
                </div>
                <div>
                  <h3 className="font-medium text-gray-900 mb-2">AI Analysis</h3>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>Phishing Detected: {result.details.ai_analysis.is_phishing ? 'Yes' : 'No'}</li>
                    <li>Confidence: {result.details.ai_analysis.confidence || 0}%</li>
                    <li>Urgency Language: {result.details.ai_analysis.urgency_detected ? 'Yes' : 'No'}</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Educational Content */}
        <div className="bg-white rounded-lg shadow-md p-6 mt-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            {language === 'kn' ? 'ಸುರಕ್ಷತಾ ಸಲಹೆಗಳು' : 'Safety Tips'}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-medium text-gray-900 mb-2">
                {language === 'kn' ? 'ಎಚ್ಚರಿಕೆ ಚಿಹ್ನೆಗಳು' : 'Warning Signs'}
              </h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• {language === 'kn' ? 'ತುರ್ತು ಭಾಷೆ' : 'Urgent language'}</li>
                <li>• {language === 'kn' ? 'ಅಪರಿಚಿತ ಕಳುಹಿಸುವವರು' : 'Unknown senders'}</li>
                <li>• {language === 'kn' ? 'ವೈಯಕ್ತಿಕ ಮಾಹಿತಿ ಕೋರಿಕೆ' : 'Requests for personal info'}</li>
                <li>• {language === 'kn' ? 'ಅನುಮಾನಾಸ್ಪದ ಲಿಂಕ್‌ಗಳು' : 'Suspicious links'}</li>
              </ul>
            </div>
            <div>
              <h3 className="font-medium text-gray-900 mb-2">
                {language === 'kn' ? 'ಸುರಕ್ಷಿತ ಅಭ್ಯಾಸಗಳು' : 'Safe Practices'}
              </h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• {language === 'kn' ? 'URL ಪರಿಶೀಲಿಸಿ' : 'Verify URLs'}</li>
                <li>• {language === 'kn' ? 'ಎರಡು ಬಾರಿ ಯೋಚಿಸಿ' : 'Think twice before clicking'}</li>
                <li>• {language === 'kn' ? 'ಅಧಿಕೃತ ಮೂಲಗಳನ್ನು ಬಳಸಿ' : 'Use official sources'}</li>
                <li>• {language === 'kn' ? 'ಸಾಫ್ಟ್‌ವೇರ್ ಅಪ್‌ಡೇಟ್ ಮಾಡಿ' : 'Keep software updated'}</li>
              </ul>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default App;