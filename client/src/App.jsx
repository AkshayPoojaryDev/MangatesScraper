import { useState, useEffect, useRef } from 'react'
import axios from 'axios'

const API_URL = "http://localhost:8000"

function App() {
  const [input, setInput] = useState("")
  const [jobId, setJobId] = useState(null)
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(false)
  const logsEndRef = useRef(null)

  // Start the Job
  const startScraping = async () => {
    const courses = input.split('\n').filter(line => line.trim() !== "")
    if (courses.length === 0) return alert("Please enter at least one course.")

    setLoading(true)
    try {
      const res = await axios.post(`${API_URL}/start`, { courses })
      setJobId(res.data.job_id)
      setStatus(null)
    } catch (err) {
      alert("Error connecting to server. Is the backend running?")
      setLoading(false)
    }
  }

  // Poll for Updates
  useEffect(() => {
    if (!jobId) return

    const interval = setInterval(async () => {
      try {
        const res = await axios.get(`${API_URL}/status/${jobId}`)
        setStatus(res.data)
        
        if (res.data.status === 'completed') {
          setLoading(false)
          clearInterval(interval)
        }
      } catch (err) {
        console.error("Polling error", err)
      }
    }, 1500) // Check every 1.5 seconds

    return () => clearInterval(interval)
  }, [jobId])

  // Auto-scroll logs
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [status?.logs])

  // Helper: Download Failed List
  const downloadFailedReport = () => {
    if (!status || status.failed.length === 0) return
    const text = status.failed.join('\n')
    const element = document.createElement("a")
    const file = new Blob([text], {type: 'text/plain'})
    element.href = URL.createObjectURL(file)
    element.download = "failed_courses.txt"
    document.body.appendChild(element)
    element.click()
  }

  return (
    <div style={{ minHeight: '100vh', background: '#f4f4f9', padding: '40px 20px', fontFamily: 'Segoe UI, sans-serif' }}>
      <div style={{ maxWidth: '900px', margin: '0 auto', background: 'white', borderRadius: '12px', boxShadow: '0 4px 20px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
        
        {/* HEADER */}
        <div style={{ background: '#2c3e50', padding: '20px 30px', color: 'white' }}>
          <h1 style={{ margin: 0, fontSize: '1.5rem' }}>Mangates Dynamic Scraper</h1>
          <p style={{ margin: '5px 0 0', opacity: 0.8, fontSize: '0.9rem' }}>Powered by Python FastAPI & React</p>
        </div>

        <div style={{ padding: '30px' }}>
          
          {/* INPUT SECTION (Hidden when running) */}
          {!jobId && (
            <div>
              <label style={{ display: 'block', marginBottom: '10px', fontWeight: '600', color: '#555' }}>
                Paste Course List (One per line):
              </label>
              <textarea 
                rows="12" 
                style={{ width: '100%', padding: '15px', borderRadius: '8px', border: '1px solid #ddd', fontSize: '14px', fontFamily: 'monospace', resize: 'vertical' }}
                placeholder="Ex: Agile Scrum Master mangates..."
                value={input}
                onChange={e => setInput(e.target.value)}
              />
              <div style={{ marginTop: '20px', textAlign: 'right' }}>
                <button 
                  onClick={startScraping} 
                  disabled={loading}
                  style={{ 
                    padding: '12px 30px', 
                    background: loading ? '#95a5a6' : '#27ae60', 
                    color: 'white', 
                    border: 'none', 
                    borderRadius: '6px', 
                    fontSize: '16px', 
                    cursor: loading ? 'not-allowed' : 'pointer',
                    transition: 'background 0.2s'
                  }}
                >
                  {loading ? "Starting..." : "Start Search & Download"}
                </button>
              </div>
            </div>
          )}

          {/* DASHBOARD SECTION */}
          {status && (
            <div>
              {/* PROGRESS BAR */}
              <div style={{ marginBottom: '30px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <span style={{ fontWeight: 'bold', color: '#2c3e50' }}>Status: {status.status.toUpperCase()}</span>
                  <span style={{ color: '#7f8c8d' }}>{status.progress}%</span>
                </div>
                <div style={{ width: '100%', background: '#ecf0f1', height: '12px', borderRadius: '6px', overflow: 'hidden' }}>
                  <div style={{ width: `${status.progress}%`, background: status.status === 'completed' ? '#27ae60' : '#3498db', height: '100%', transition: 'width 0.5s ease-out' }}></div>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                
                {/* LEFT COL: LOGS */}
                <div>
                  <h3 style={{ fontSize: '1.1rem', color: '#2c3e50', borderBottom: '2px solid #eee', paddingBottom: '10px' }}>Live Logs</h3>
                  <div style={{ background: '#2c3e50', color: '#2ecc71', padding: '15px', height: '300px', overflowY: 'auto', borderRadius: '8px', fontFamily: 'monospace', fontSize: '13px', lineHeight: '1.5' }}>
                    {status.logs.map((log, i) => (
                      <div key={i} style={{ marginBottom: '5px', borderBottom: '1px solid #34495e', paddingBottom: '2px' }}>
                        {log.includes('FAILED') ? <span style={{color: '#e74c3c'}}>{log}</span> : log}
                      </div>
                    ))}
                    <div ref={logsEndRef} />
                  </div>
                </div>

                {/* RIGHT COL: RESULTS */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                  
                  {/* SUCCESS LIST */}
                  <div style={{ flex: 1, background: '#f8f9fa', padding: '15px', borderRadius: '8px', border: '1px solid #e9ecef', overflowY: 'auto', maxHeight: '200px' }}>
                    <h4 style={{ margin: '0 0 10px', color: '#27ae60' }}>✓ Downloaded ({status.success.length})</h4>
                    {status.success.length === 0 && <p style={{color: '#aaa', fontSize: '0.9rem'}}>No files yet...</p>}
                    {status.success.map((f, i) => (
                      <div key={i} style={{ marginBottom: '5px' }}>
                        <a 
                          href={`${API_URL}/download/${f}`} 
                          target="_blank" 
                          rel="noreferrer"
                          style={{ color: '#2980b9', textDecoration: 'none', fontSize: '14px' }}
                        >
                          📄 {f}
                        </a>
                      </div>
                    ))}
                  </div>

                  {/* FAILED LIST */}
                  <div style={{ flex: 1, background: '#fff5f5', padding: '15px', borderRadius: '8px', border: '1px solid #fed7d7', overflowY: 'auto', maxHeight: '200px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                      <h4 style={{ margin: 0, color: '#c0392b' }}>✕ Failed ({status.failed.length})</h4>
                      {status.failed.length > 0 && (
                        <button 
                          onClick={downloadFailedReport}
                          style={{ fontSize: '11px', padding: '4px 8px', cursor: 'pointer', background: '#e74c3c', color: 'white', border: 'none', borderRadius: '4px' }}
                        >
                          Export List
                        </button>
                      )}
                    </div>
                    {status.failed.length === 0 && <p style={{color: '#aaa', fontSize: '0.9rem'}}>No failures yet...</p>}
                    {status.failed.map((f, i) => (
                      <div key={i} style={{ fontSize: '13px', color: '#c0392b', marginBottom: '4px' }}>• {f}</div>
                    ))}
                  </div>

                </div>
              </div>

              {/* NEW JOB BUTTON */}
              {status.status === 'completed' && (
                <div style={{ marginTop: '30px', textAlign: 'center' }}>
                  <button 
                    onClick={() => { setJobId(null); setStatus(null); }}
                    style={{ padding: '10px 25px', background: '#34495e', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' }}
                  >
                    Start New Batch
                  </button>
                </div>
              )}

            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default App