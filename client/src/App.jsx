import { useState, useEffect } from 'react';
import { startJob, getJobStatus } from './services/api';
import CourseInput from './components/CourseInput';
import JobDashboard from './components/JobStatus';
import LogViewer from './components/LogViewer';
import ResultList from './components/ResultList';

function App() {
  const [input, setInput] = useState("");
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  // Start the Job
  const handleStart = async () => {
    const courses = input.split('\n').filter(line => line.trim() !== "");
    if (courses.length === 0) return alert("Please enter at least one course.");

    setLoading(true);
    try {
      const data = await startJob(courses);
      setJobId(data.job_id);
      setStatus(null);
    } catch (err) {
      alert("Error connecting to server. Is the backend running?");
      setLoading(false);
    }
  };

  // Poll for Updates
  useEffect(() => {
    if (!jobId) return;

    const interval = setInterval(async () => {
      try {
        const data = await getJobStatus(jobId);
        setStatus(data);

        if (data.status === 'completed') {
          setLoading(false);
          clearInterval(interval);
        }
      } catch (err) {
        console.error("Polling error", err);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [jobId]);

  const handleReset = () => {
    setJobId(null);
    setStatus(null);
  };

  return (
    <div className="min-h-screen bg-gray-100 py-10 px-4 font-sans text-slate-700">
      <div className="max-w-4xl mx-auto bg-white rounded-xl shadow-lg overflow-hidden">

        {/* HEADER */}
        <div className="bg-slate-800 text-white p-8">
          <h1 className="text-2xl font-bold m-0">Mangates Dynamic Scraper</h1>
          <p className="mt-1 opacity-80 text-sm">Powered by Python FastAPI & React</p>
        </div>

        <div className="p-8">

          {/* INPUT SECTION */}
          {!jobId && (
            <CourseInput
              input={input}
              setInput={setInput}
              onStart={handleStart}
              loading={loading}
            />
          )}

          {/* DASHBOARD SECTION */}
          {status && (
            <JobDashboard status={status}>
              <LogViewer logs={status.logs} />
              <ResultList
                success={status.success}
                failed={status.failed}
                onReset={handleReset}
                isCompleted={status.status === 'completed'}
              />
            </JobDashboard>
          )}

        </div>
      </div>
    </div>
  );
}

export default App;