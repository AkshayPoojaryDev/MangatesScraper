import React, { useEffect, useRef } from 'react';

const LogViewer = ({ logs }) => {
    const logsEndRef = useRef(null);

    useEffect(() => {
        logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [logs]);

    return (
        <div>
            <h3 className="text-lg font-semibold text-slate-700 border-b-2 border-gray-100 pb-2 mb-0">Live Logs</h3>
            <div className="bg-slate-800 text-green-400 p-4 h-[300px] overflow-y-auto rounded-lg font-mono text-xs leading-relaxed mt-4">
                {logs.map((log, i) => (
                    <div key={i} className="mb-1 border-b border-slate-700 pb-1 last:border-0">
                        {log.includes('FAILED') ? <span className="text-red-500">{log}</span> : log}
                    </div>
                ))}
                <div ref={logsEndRef} />
            </div>
        </div>
    );
};

export default LogViewer;
