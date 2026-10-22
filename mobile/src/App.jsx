import { useState } from 'react'
import axios from 'axios'

function App() {
  const [text, setText] = useState('')
  const [language, setLanguage] = useState('Auto')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const analyzeMessage = async () => {
    if (!text.trim()) {
      setError('Please enter a message to analyze.')
      return
    }
    
    setLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await axios.post('http://localhost:8000/analyze', {
        text: text,
        language: language
      })
      setResult(response.data)
    } catch (err) {
      setError('Failed to connect to the server. Is api.py running?')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ padding: '20px', maxWidth: '600px', margin: '0 auto', fontFamily: 'sans-serif' }}>
      <h1>ScamLens Mobile</h1>
      <p>Understand suspicious messages before acting on them.</p>

      <textarea 
        rows="6" 
        style={{ width: '100%', padding: '10px', marginBottom: '10px' }}
        placeholder="Paste suspicious SMS or message here..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />

      <div style={{ marginBottom: '15px' }}>
        <label style={{ marginRight: '10px' }}>Language:</label>
        <select value={language} onChange={(e) => setLanguage(e.target.value)} style={{ padding: '5px' }}>
          <option value="Auto">Auto</option>
          <option value="English">English</option>
          <option value="Hindi">Hindi</option>
          <option value="Tamil">Tamil</option>
        </select>
      </div>

      <button 
        onClick={analyzeMessage} 
        disabled={loading}
        style={{ width: '100%', padding: '15px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '5px', fontSize: '16px' }}
      >
        {loading ? 'Analyzing...' : 'Analyze Message'}
      </button>

      {error && <p style={{ color: 'red', marginTop: '15px' }}>{error}</p>}

      {result && (
        <div style={{ marginTop: '20px', padding: '15px', border: '1px solid #ccc', borderRadius: '5px' }}>
          <h2>Risk Level: {result.level} (Score: {result.score})</h2>
          <p><strong>Explanation ({result.explanation_source}):</strong> {result.explanation}</p>
          
          <h3>Detected Signs:</h3>
          <ul>
            {result.findings.map((finding, index) => (
              <li key={index}>
                <strong>{finding.rule}:</strong> {finding.why}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default App