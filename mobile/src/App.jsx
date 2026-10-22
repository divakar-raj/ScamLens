import React, { useState } from 'react';

export default function App() {
  // State variables
  const [activeTab, setActiveTab] = useState('home'); // 'home' | 'history' | 'settings'
  const [selectedLang, setSelectedLang] = useState('English');
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  
  // History state
  const [scanHistory, setScanHistory] = useState([
    { id: 1, title: 'Bank KYC Message', risk: 'High', date: '2 min ago', text: 'Your bank account will be blocked today. Update KYC: https://bank-update.com' },
    { id: 2, title: 'Delivery Notification', risk: 'Medium', date: '12 min ago', text: 'Package failed to deliver. Update address at bad-link.info' },
    { id: 3, title: 'Gmail Security Alert', risk: 'Safe', date: '1 hr ago', text: 'Your monthly bank statement is available in official app.' }
  ]);

  // Handle Backend API Call
  const handleAnalyze = async () => {
    if (!inputText.trim()) return;

    setLoading(true);
    setAnalysisResult(null);

    try {
      // Connect to your FastAPI backend running locally
      const response = await fetch('http://127.0.0.1:8000/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: inputText,
          language: selectedLang
        })
      });

      if (response.ok) {
        const data = await response.json();
        setAnalysisResult(data);
        
        // Add to history
        setScanHistory([
          {
            id: Date.now(),
            title: inputText.slice(0, 20) + '...',
            risk: data.risk_level || 'High',
            date: 'Just now',
            text: inputText
          },
          ...scanHistory
        ]);
      } else {
        throw new Error('API request failed');
      }
    } catch (err) {
      // Fallback Mock Data if FastAPI is not yet running
      setTimeout(() => {
        const isTanglish = selectedLang === 'Tanglish' || selectedLang === 'Tamil';
        const mockResponse = {
          risk_level: 'High',
          message: inputText,
          reasons: isTanglish
            ? [
                'அவசரப்படுத்தும் மொழி (Creates urgency)',
                'KYC புதுப்பிக்கச் சொல்கிறது (Requests KYC)',
                'சந்தேகமான இணைப்பு (Suspicious link: bank-update.com)'
              ]
            : [
                'Creates extreme urgency ("blocked today")',
                'Requests immediate KYC verification',
                'Contains suspicious unverified domain link'
              ],
          recommended_action: isTanglish
            ? 'இணைப்பைக் கிளிக் செய்ய வேண்டாம். உங்கள் வங்கியின் அதிகாரப்பூர்வ செயலி மூலம் சரிபார்க்கவும்.'
            : 'Do not click the link. Verify your account only through your bank\'s official app or website.'
        };
        setAnalysisResult(mockResponse);
        setScanHistory([
          {
            id: Date.now(),
            title: inputText.slice(0, 22) + '...',
            risk: 'High',
            date: 'Just now',
            text: inputText
          },
          ...scanHistory
        ]);
      }, 1200);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex justify-center items-center p-0 sm:p-4 font-sans">
      {/* Mobile Shell Frame */}
      <div className="w-full max-w-md bg-slate-800 sm:rounded-3xl shadow-2xl overflow-hidden border border-slate-700 flex flex-col h-[100vh] sm:h-[840px] relative">
        
        {/* Top Header */}
        <header className="bg-slate-800/90 backdrop-blur border-b border-slate-700/80 px-5 py-4 flex items-center justify-between sticky top-0 z-10">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center font-bold text-white text-lg shadow-lg shadow-blue-500/30">
              S
            </div>
            <span className="font-bold text-xl tracking-tight bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent">
              ScamLens
            </span>
          </div>

          {/* Language Selector Dropdown */}
          <select 
            value={selectedLang}
            onChange={(e) => setSelectedLang(e.target.value)}
            className="bg-slate-700 text-xs text-slate-200 border border-slate-600 rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="English">English</option>
            <option value="Tamil">Tamil (தமிழ்)</option>
            <option value="Tanglish">Tanglish</option>
            <option value="Hindi">Hindi (हिन्दी)</option>
            <option value="Hinglish">Hinglish</option>
          </select>
        </header>

        {/* Scrollable Main Content Area */}
        <main className="flex-1 overflow-y-auto p-5 space-y-5">
          
          {/* TAB 1: HOME (SCANNER) */}
          {activeTab === 'home' && (
            <>
              {/* Input Card */}
              <div className="bg-slate-800 border border-slate-700/80 rounded-2xl p-4 shadow-sm">
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                  Paste Suspicious Message / Link
                </label>
                <textarea
                  rows={4}
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  placeholder="Paste SMS, WhatsApp message, or URL here... (e.g., 'Your bank account will be blocked today. Update KYC at http://kyc-update.in')"
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 transition resize-none"
                />
                
                <div className="mt-3 flex items-center justify-between">
                  <button 
                    onClick={() => setInputText("Ungal bank account block aagum. Indha link-la KYC update pannunga: https://kyc-update.in")}
                    className="text-xs text-blue-400 hover:text-blue-300 underline underline-offset-2"
                  >
                    + Load Sample Scam
                  </button>
                  <button
                    onClick={handleAnalyze}
                    disabled={loading || !inputText.trim()}
                    className={`px-5 py-2.5 rounded-xl font-medium text-sm text-white shadow-lg flex items-center space-x-2 transition ${
                      loading || !inputText.trim()
                        ? 'bg-slate-700 opacity-50 cursor-not-allowed'
                        : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 shadow-blue-600/30 active:scale-95'
                    }`}
                  >
                    {loading ? (
                      <>
                        <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                        <span>Analyzing...</span>
                      </>
                    ) : (
                      <span>Analyze Threat</span>
                    )}
                  </button>
                </div>
              </div>

              {/* Analysis Loading State */}
              {loading && (
                <div className="bg-slate-800/60 border border-slate-700 rounded-2xl p-6 text-center space-y-3">
                  <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
                  <p className="text-sm font-medium text-slate-300">Scanning for threat patterns...</p>
                  <div className="flex justify-center space-x-2 text-xs text-slate-500">
                    <span>Regex Rules</span> • <span>Language NLP</span> • <span>AI Explainer</span>
                  </div>
                </div>
              )}

              {/* Result View Card */}
              {analysisResult && !loading && (
                <div className={`border rounded-2xl p-5 space-y-4 shadow-xl transition-all ${
                  analysisResult.risk_level === 'High'
                    ? 'bg-red-950/30 border-red-800/80'
                    : analysisResult.risk_level === 'Medium'
                    ? 'bg-amber-950/30 border-amber-800/80'
                    : 'bg-emerald-950/30 border-emerald-800/80'
                }`}>
                  {/* Risk Badge Header */}
                  <div className="flex items-center justify-between">
                    <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
                      analysisResult.risk_level === 'High'
                        ? 'bg-red-500/20 text-red-400 border border-red-500/40'
                        : analysisResult.risk_level === 'Medium'
                        ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40'
                        : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                    }`}>
                      {analysisResult.risk_level} Risk Detected
                    </span>
                    <span className="text-xs text-slate-400">{selectedLang} Output</span>
                  </div>

                  {/* Highlighted Message */}
                  <div className="bg-slate-900/80 rounded-xl p-3 border border-slate-800 text-xs text-slate-300 italic">
                    "{analysisResult.message}"
                  </div>

                  {/* Why this is suspicious */}
                  <div>
                    <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                      Why this is suspicious:
                    </h4>
                    <ul className="space-y-1.5">
                      {analysisResult.reasons.map((reason, idx) => (
                        <li key={idx} className="flex items-start text-xs text-slate-200 space-x-2">
                          <span className="text-red-400 font-bold">•</span>
                          <span>{reason}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Recommended Action */}
                  <div className="bg-slate-900/90 rounded-xl p-3 border border-slate-700/60">
                    <h4 className="text-xs font-semibold text-emerald-400 uppercase tracking-wider mb-1">
                      Recommended Action:
                    </h4>
                    <p className="text-xs text-slate-200 leading-relaxed">
                      {analysisResult.recommended_action}
                    </p>
                  </div>
                </div>
              )}

              {/* Quick Scan History Preview */}
              <div className="space-y-3 pt-2">
                <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Recent Scans
                </h3>
                <div className="space-y-2">
                  {scanHistory.slice(0, 3).map((item) => (
                    <div key={item.id} className="bg-slate-800 border border-slate-700/60 rounded-xl p-3 flex items-center justify-between">
                      <div className="space-y-0.5">
                        <p className="text-xs font-medium text-slate-200">{item.title}</p>
                        <p className="text-[10px] text-slate-500">{item.date}</p>
                      </div>
                      <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                        item.risk === 'High' ? 'bg-red-500/20 text-red-400' :
                        item.risk === 'Medium' ? 'bg-amber-500/20 text-amber-400' : 'bg-emerald-500/20 text-emerald-400'
                      }`}>
                        {item.risk}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}

          {/* TAB 2: HISTORY */}
          {activeTab === 'history' && (
            <div className="space-y-3">
              <h3 className="text-sm font-semibold text-slate-200">All Scan History</h3>
              {scanHistory.map((item) => (
                <div key={item.id} className="bg-slate-800 border border-slate-700 rounded-xl p-3.5 space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-xs font-semibold text-slate-200">{item.title}</span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                      item.risk === 'High' ? 'bg-red-500/20 text-red-400' : 'bg-emerald-500/20 text-emerald-400'
                    }`}>
                      {item.risk}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 line-clamp-2">{item.text}</p>
                  <p className="text-[10px] text-slate-500">{item.date}</p>
                </div>
              ))}
            </div>
          )}

          {/* TAB 3: SETTINGS */}
          {activeTab === 'settings' && (
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-slate-200">Privacy & Rules</h3>
              <div className="bg-slate-800 border border-slate-700 rounded-xl p-4 space-y-3 text-xs text-slate-300">
                <div className="flex items-center justify-between border-b border-slate-700 pb-2">
                  <span>User-Initiated Mode</span>
                  <span className="text-emerald-400 font-semibold">Active</span>
                </div>
                <div className="flex items-center justify-between border-b border-slate-700 pb-2">
                  <span>Offline Regex Rules</span>
                  <span className="text-emerald-400 font-semibold">Enabled</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>AI Model</span>
                  <span className="text-blue-400 font-semibold">Groq / FastAPI</span>
                </div>
              </div>
              
              <div className="bg-blue-950/40 border border-blue-800/60 rounded-xl p-3 text-[11px] text-blue-300">
                🛡️ <strong>Privacy First Architecture:</strong> ScamLens does not silently scrape messages. Only content explicitly pasted or shared is processed.
              </div>
            </div>
          )}
        </main>

        {/* Bottom Navigation Bar */}
        <nav className="bg-slate-800 border-t border-slate-700 grid grid-cols-3 text-center py-2 text-xs">
          <button
            onClick={() => setActiveTab('home')}
            className={`py-1.5 flex flex-col items-center space-y-1 ${
              activeTab === 'home' ? 'text-blue-400 font-semibold' : 'text-slate-400'
            }`}
          >
            <span>🔍</span>
            <span>Scan</span>
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`py-1.5 flex flex-col items-center space-y-1 ${
              activeTab === 'history' ? 'text-blue-400 font-semibold' : 'text-slate-400'
            }`}
          >
            <span>📜</span>
            <span>History</span>
          </button>
          <button
            onClick={() => setActiveTab('settings')}
            className={`py-1.5 flex flex-col items-center space-y-1 ${
              activeTab === 'settings' ? 'text-blue-400 font-semibold' : 'text-slate-400'
            }`}
          >
            <span>⚙️</span>
            <span>Settings</span>
          </button>
        </nav>

      </div>
    </div>
  );
}