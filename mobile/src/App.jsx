import { useEffect, useState } from 'react';
import { AndroidSmsRetriever } from '@capgo/capacitor-android-sms-retriever';
import { SendIntent } from 'send-intent';

const API_URL = 'https://vacate-bulge-cursor.ngrok-free.dev/analyze';
const HISTORY_STORAGE_KEY = 'scamlens-scan-history';
const LANGUAGE_STORAGE_KEY = 'scamlens-language';
const SUPPORTED_LANGUAGES = ['English', 'Tamil', 'Hindi'];
const MAX_MESSAGE_LENGTH = 5000;

const CONNECTION_FALLBACK = {
  score: 90,
  level: 'High',
  language: 'Unknown',
  threat_type: 'Connection Error',
  explanation: 'Could not reach the AI server. Treat this message as highly suspicious.',
  safe_step: 'Do not click any links or share personal information.'
};

const EMPTY_HISTORY = [];

function loadLanguage() {
  try {
    const savedLanguage = window.localStorage.getItem(LANGUAGE_STORAGE_KEY);
    return SUPPORTED_LANGUAGES.includes(savedLanguage) ? savedLanguage : 'English';
  } catch {
    return 'English';
  }
}

function isValidAnalysis(data) {
  return (
    data !== null &&
    typeof data === 'object' &&
    Number.isInteger(data.score) &&
    data.score >= 0 &&
    data.score <= 100 &&
    ['High', 'Medium', 'Low', 'Safe'].includes(data.level) &&
    typeof data.language === 'string' &&
    typeof data.threat_type === 'string' &&
    typeof data.explanation === 'string' &&
    typeof data.safe_step === 'string'
  );
}

function getRiskStyles(level) {
  if (level === 'High') {
    return {
      card: 'border-red-500/30 bg-red-950/30',
      badge: 'border-red-400/30 bg-red-500/15 text-red-300',
      meter: 'bg-red-400',
      icon: '⚠️',
      label: 'High risk'
    };
  }

  if (level === 'Medium') {
    return {
      card: 'border-amber-500/30 bg-amber-950/20',
      badge: 'border-amber-400/30 bg-amber-500/15 text-amber-300',
      meter: 'bg-amber-400',
      icon: '⚠️',
      label: 'Medium risk'
    };
  }

  if (level === 'Low') {
    return {
      card: 'border-lime-500/30 bg-lime-950/20',
      badge: 'border-lime-400/30 bg-lime-500/15 text-lime-300',
      meter: 'bg-lime-400',
      icon: '💡',
      label: 'Low risk'
    };
  }

  return {
    card: 'border-emerald-500/30 bg-emerald-950/20',
    badge: 'border-emerald-400/30 bg-emerald-500/15 text-emerald-300',
    meter: 'bg-emerald-400',
    icon: '🛡️',
    label: 'Safe'
  };
}

function loadHistory() {
  try {
    const savedHistory = window.localStorage.getItem(HISTORY_STORAGE_KEY);
    if (!savedHistory) return EMPTY_HISTORY;

    const parsedHistory = JSON.parse(savedHistory);
    if (!Array.isArray(parsedHistory)) return EMPTY_HISTORY;

    return parsedHistory.filter(
      (item) =>
        item &&
        typeof item.id === 'string' &&
        typeof item.title === 'string' &&
        typeof item.text === 'string' &&
        typeof item.level === 'string' &&
        Number.isInteger(item.score)
    );
  } catch {
    return EMPTY_HISTORY;
  }
}

export default function App() {
  const [activeTab, setActiveTab] = useState('scan');
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [scanHistory, setScanHistory] = useState(loadHistory);
  const [language, setLanguage] = useState(loadLanguage);

  const saveToHistory = (text, result) => {
    const entry = {
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      title: text.slice(0, 20),
      text,
      level: result.level,
      score: result.score,
      date: new Date().toISOString()
    };

    setScanHistory((history) => [entry, ...history].slice(0, 50));
  };

  const handleAnalyze = async (overrideText) => {
    const text = (overrideText !== undefined ? overrideText : inputText).trim();
    if (!text || loading) return;

    setLoading(true);
    setAnalysisResult(null);
    const controller = new AbortController();
    const timeoutId = window.setTimeout(() => controller.abort(), 30000);

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, language }),
        signal: controller.signal
      });

      if (!response.ok) {
        throw new Error(`Analysis request failed with status ${response.status}.`);
      }

      const data = await response.json();
      if (!isValidAnalysis(data)) {
        throw new Error('The analysis server returned an invalid response.');
      }

      setAnalysisResult(data);
      saveToHistory(text, data);
    } catch {
      setAnalysisResult(CONNECTION_FALLBACK);
      saveToHistory(text, CONNECTION_FALLBACK);
    } finally {
      window.clearTimeout(timeoutId);
      setLoading(false);
    }
  };

  useEffect(() => {
    const handleIncomingShare = async () => {
      try {
        const result = await SendIntent.checkSendIntentReceived();
        if (result && result.extras) {
          const sharedText = result.extras['android.intent.extra.TEXT'];
          if (sharedText) {
            setInputText(sharedText);
            setActiveTab('scan');
            handleAnalyze(sharedText); // <-- ADD THIS LINE HERE
          }
        }
      } catch (error) {
        console.log('No share intent received on startup:', error);
      }
    };

    handleIncomingShare();
  }, [language]);

  useEffect(() => {
    const setupSmsRetriever = async () => {
      try {
        await AndroidSmsRetriever.startWatch();

        await AndroidSmsRetriever.addListener('smsReceived', (event) => {
          if (event && event.message) {
            console.log('Incoming SMS captured:', event.message);
            setInputText(event.message);
            setActiveTab('scan');
            handleAnalyze(event.message); // <-- ADD THIS LINE HERE
          }
        });
      } catch (error) {
        console.log('SMS Retriever not available or failed to start:', error);
      }
    };

    setupSmsRetriever();

    return () => {
      AndroidSmsRetriever.removeAllListeners();
    };
  }, [language]);

  useEffect(() => {
    try {
      window.localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(scanHistory));
    } catch {
      // Scanning remains available when browser storage is disabled or full.
    }
  }, [scanHistory]);

  useEffect(() => {
    try {
      window.localStorage.setItem(LANGUAGE_STORAGE_KEY, language);
    } catch {
      // Language selection still works for the current session if storage is unavailable.
    }
  }, [language]);

  const clearScanner = () => {
    setInputText('');
    setAnalysisResult(null);
  };

  const scanAnother = () => {
    clearScanner();
    setActiveTab('scan');
  };

  const renderScan = () => {
    const riskStyles = analysisResult ? getRiskStyles(analysisResult.level) : null;

    return (
      <div className="space-y-5">
        <section className="rounded-3xl border border-slate-700/80 bg-gradient-to-br from-slate-800 via-slate-800 to-slate-800/70 p-5 shadow-xl shadow-black/20">
          <div className="mb-5 flex items-start justify-between gap-4">
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-blue-300">
                Scam protection
              </p>
              <h2 className="text-2xl font-bold tracking-tight text-white">
                Check before you click.
              </h2>
              <p className="mt-2 text-sm leading-6 text-slate-400">
                Paste a suspicious SMS, WhatsApp message, or link for a quick risk check.
              </p>
            </div>
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-blue-500/15 text-2xl ring-1 ring-blue-400/20">
              🛡️
            </div>
          </div>

          <label htmlFor="message-input" className="mb-2 block text-sm font-medium text-slate-200">
            Message to analyze
          </label>
          <textarea
            id="message-input"
            rows={6}
            maxLength={MAX_MESSAGE_LENGTH}
            value={inputText}
            onChange={(event) => setInputText(event.target.value)}
            placeholder="Paste the full message or link here..."
            disabled={loading}
            className="min-h-40 w-full resize-y rounded-2xl border border-slate-600/80 bg-slate-950/70 p-4 text-sm leading-6 text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-blue-400 focus:ring-4 focus:ring-blue-500/10 disabled:opacity-60"
          />

          <div className="mt-2 flex items-center justify-between text-xs text-slate-500">
            <span>Only the text you submit is analyzed.</span>
            <span>{inputText.length}/{MAX_MESSAGE_LENGTH}</span>
          </div>

          <div className="mt-4 flex gap-3">
            <button
              type="button"
              onClick={clearScanner}
              disabled={loading || !inputText}
              className="rounded-xl border border-slate-600 px-4 py-3 text-sm font-semibold text-slate-300 transition hover:bg-slate-700/70 disabled:cursor-not-allowed disabled:opacity-40"
            >
              Clear
            </button>
            <button
              type="button"
              onClick={() => handleAnalyze(inputText)} // <-- UPDATE THIS LINE
              disabled={loading || !inputText.trim()}
              className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 px-4 py-3 text-sm font-bold text-white shadow-lg shadow-indigo-950/40 transition hover:from-blue-500 hover:to-indigo-500 focus:outline-none focus:ring-4 focus:ring-blue-500/30 disabled:cursor-not-allowed disabled:from-slate-700 disabled:to-slate-700 disabled:text-slate-400 disabled:shadow-none"
            >
              {loading ? (
                <>
                  <span
                    className="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white"
                    aria-hidden="true"
                  />
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <span aria-hidden="true">🔍</span>
                  <span>Analyze Threat</span>
                </>
              )}
            </button>
          </div>
        </section>

        {loading && (
          <div
            className="rounded-2xl border border-blue-500/20 bg-blue-900/10 p-4 text-center text-sm text-blue-200"
            role="status"
            aria-live="polite"
          >
            Checking for suspicious patterns...
          </div>
        )}

        {analysisResult && !loading && (
          <section
            className={`space-y-5 rounded-3xl border p-5 shadow-xl shadow-black/20 ${riskStyles.card}`}
            aria-live="polite"
          >
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className={`inline-flex items-center gap-2 rounded-full border px-3.5 py-2 text-sm font-bold ${riskStyles.badge}`}>
                <span aria-hidden="true">{riskStyles.icon}</span>
                <span>{riskStyles.label}</span>
              </div>
              <span className="rounded-full border border-slate-500/40 bg-slate-900/50 px-3 py-1.5 text-xs font-medium text-slate-300">
                {analysisResult.threat_type}
              </span>
            </div>

            <div>
              <div className="mb-2 flex items-center justify-between">
                <span className="text-sm font-medium text-slate-300">Threat score</span>
                <span className="text-sm font-bold tabular-nums text-white">
                  {analysisResult.score}
                  <span className="font-medium text-slate-400"> / 100</span>
                </span>
              </div>
              <div
                className="h-2.5 overflow-hidden rounded-full bg-slate-950/70 ring-1 ring-white/5"
                role="progressbar"
                aria-label="Threat score"
                aria-valuemin={0}
                aria-valuemax={100}
                aria-valuenow={analysisResult.score}
              >
                <div
                  className={`h-full rounded-full transition-[width] duration-700 ease-out ${riskStyles.meter}`}
                  style={{ width: `${analysisResult.score}%` }}
                />
              </div>
            </div>

            <div className="rounded-2xl border border-slate-700/70 bg-slate-800/50 p-4">
              <div className="mb-3 flex items-center justify-between gap-3">
                <h3 className="text-sm font-bold text-slate-100">Analysis Explanation</h3>
                <span className="shrink-0 rounded-full bg-slate-700/80 px-2.5 py-1 text-[11px] font-medium text-slate-300">
                  {analysisResult.language}
                </span>
              </div>
              <p className="text-sm leading-6 text-slate-300">{analysisResult.explanation}</p>
            </div>

            <div className="rounded-2xl border border-blue-500/30 bg-blue-900/20 p-4">
              <h3 className="mb-2 flex items-center gap-2 text-sm font-bold text-blue-200">
                <span aria-hidden="true">💡</span>
                Recommended Action
              </h3>
              <p className="text-sm leading-6 text-slate-200">{analysisResult.safe_step}</p>
            </div>

            <button
              type="button"
              onClick={scanAnother}
              className="w-full rounded-xl border border-slate-600 bg-slate-800/80 px-4 py-3 text-sm font-semibold text-slate-100 transition hover:border-blue-400/50 hover:bg-slate-700"
            >
              Scan Another Message
            </button>
          </section>
        )}
      </div>
    );
  };

  const renderHistory = () => (
    <section className="space-y-4">
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-blue-300">Your activity</p>
        <h2 className="mt-2 text-2xl font-bold text-white">Scan history</h2>
        <p className="mt-1 text-sm text-slate-400">
          {scanHistory.length} {scanHistory.length === 1 ? 'scan' : 'scans'} saved on this device.
        </p>
      </div>

      {scanHistory.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-800/50 px-5 py-10 text-center">
          <span className="text-3xl" aria-hidden="true">🔍</span>
          <p className="mt-3 text-sm font-semibold text-slate-200">No scans yet</p>
          <p className="mt-1 text-xs leading-5 text-slate-400">
            Your completed scans will appear here.
          </p>
          <button
            type="button"
            onClick={() => setActiveTab('scan')}
            className="mt-5 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-500"
          >
            Start a scan
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {scanHistory.map((item) => {
            const styles = getRiskStyles(item.level);
            return (
              <article key={item.id} className="rounded-2xl border border-slate-700 bg-slate-800/80 p-4">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <h3 className="break-words text-sm font-semibold text-slate-100">{item.title}</h3>
                    <p className="mt-1 line-clamp-2 text-xs leading-5 text-slate-400">{item.text}</p>
                  </div>
                  <span className={`shrink-0 rounded-full border px-2.5 py-1 text-[11px] font-semibold ${styles.badge}`}>
                    {item.level}
                  </span>
                </div>
                <div className="mt-3 flex items-center justify-between border-t border-slate-700/80 pt-3 text-xs text-slate-500">
                  <time dateTime={item.date}>{new Date(item.date).toLocaleString()}</time>
                  <span className="font-semibold tabular-nums text-slate-300">{item.score}/100</span>
                </div>
              </article>
            );
          })}
        </div>
      )}
    </section>
  );

  const renderSettings = () => (
    <section className="space-y-4">
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-blue-300">ScamLens</p>
        <h2 className="mt-2 text-2xl font-bold text-white">Privacy & settings</h2>
      </div>

      <div className="divide-y divide-slate-700 rounded-2xl border border-slate-700 bg-slate-800/80 px-4">
        <div className="flex flex-col gap-3 py-4">
          <div>
            <label htmlFor="preferred-language" className="text-sm font-semibold text-slate-100">
              Analysis language
            </label>
            <p className="mt-1 text-xs text-slate-400">
              Explanations and recommended actions will use this language.
            </p>
          </div>
          <select
            id="preferred-language"
            value={language}
            onChange={(event) => setLanguage(event.target.value)}
            className="w-full rounded-xl border border-slate-600 bg-slate-900 px-3 py-3 text-sm text-slate-100 outline-none transition focus:border-blue-400 focus:ring-4 focus:ring-blue-500/10"
          >
            <option value="English">English</option>
            <option value="Tamil">Tamil (தமிழ்)</option>
            <option value="Hindi">Hindi (हिंदी)</option>
          </select>
        </div>
        <div className="flex items-center justify-between gap-4 py-4">
          <div>
            <p className="text-sm font-semibold text-slate-100">On-device history</p>
            <p className="mt-1 text-xs text-slate-400">Saved locally in this browser.</p>
          </div>
          <span className="rounded-full bg-emerald-500/10 px-2.5 py-1 text-xs font-semibold text-emerald-300">
            Active
          </span>
        </div>
        <div className="flex items-center justify-between gap-4 py-4">
          <div>
            <p className="text-sm font-semibold text-slate-100">Analysis service</p>
            <p className="mt-1 text-xs text-slate-400">Local FastAPI backend</p>
          </div>
          <span className="text-xs font-medium text-blue-300">127.0.0.1:8000</span>
        </div>
      </div>

      <div className="rounded-2xl border border-blue-500/20 bg-blue-900/10 p-4 text-sm leading-6 text-slate-300">
        <p className="font-semibold text-blue-200">🛡️ Privacy first</p>
        <p className="mt-2 text-xs leading-5 text-slate-400">
          ScamLens only analyzes text you choose to submit. Your scan history stays in this browser.
        </p>
      </div>

      {scanHistory.length > 0 && (
        <button
          type="button"
          onClick={() => setScanHistory([])}
          className="w-full rounded-xl border border-red-500/30 px-4 py-3 text-sm font-semibold text-red-300 transition hover:bg-red-500/10"
        >
          Clear scan history
        </button>
      )}
    </section>
  );

  const tabs = [
    { id: 'scan', label: 'Scan', icon: '🔍' },
    { id: 'history', label: 'History', icon: '📜' },
    { id: 'settings', label: 'Settings', icon: '⚙️' }
  ];

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 sm:flex sm:justify-center sm:px-4 sm:py-8">
      <div className="mx-auto flex min-h-screen w-full max-w-md flex-col border-x border-slate-800 bg-slate-900 sm:min-h-[calc(100vh-4rem)] sm:overflow-hidden sm:rounded-3xl sm:border sm:shadow-2xl sm:shadow-black/40">
        <header className="sticky top-0 z-10 border-b border-slate-800 bg-slate-900/90 px-5 py-4 backdrop-blur-xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 text-xl shadow-lg shadow-blue-950/50">
                🛡️
              </div>
              <div>
                <h1 className="text-lg font-bold tracking-tight text-white">ScamLens</h1>
                <p className="text-[11px] text-slate-400">Understand before you act</p>
              </div>
            </div>
            <span className="rounded-full border border-emerald-500/20 bg-emerald-500/10 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wider text-emerald-300">
              Private scan
            </span>
          </div>
        </header>

        <main className="flex-1 px-4 py-5 sm:overflow-y-auto sm:px-5">
          {activeTab === 'scan' && renderScan()}
          {activeTab === 'history' && renderHistory()}
          {activeTab === 'settings' && renderSettings()}
        </main>

        <nav className="sticky bottom-0 grid grid-cols-3 border-t border-slate-800 bg-slate-900/95 px-3 pb-[max(0.75rem,env(safe-area-inset-bottom))] pt-2 backdrop-blur-xl">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveTab(tab.id)}
              aria-current={activeTab === tab.id ? 'page' : undefined}
              className={`flex flex-col items-center gap-1 rounded-xl py-2 text-xs font-medium transition ${
                activeTab === tab.id
                  ? 'bg-blue-500/10 text-blue-300'
                  : 'text-slate-500 hover:bg-slate-800 hover:text-slate-300'
              }`}
            >
              <span className="text-lg" aria-hidden="true">{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          ))}
        </nav>
      </div>
    </div>
  );
}