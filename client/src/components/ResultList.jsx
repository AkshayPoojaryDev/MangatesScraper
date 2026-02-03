import React from 'react';
import { getDownloadUrl } from '../services/api';

const ResultList = ({ success, failed, onReset, isCompleted }) => {

    const downloadFailedReport = () => {
        if (!failed || failed.length === 0) return;
        const text = failed.join('\n');
        const element = document.createElement("a");
        const file = new Blob([text], { type: 'text/plain' });
        element.href = URL.createObjectURL(file);
        element.download = "failed_courses.txt";
        document.body.appendChild(element);
        element.click();
    };

    return (
        <div className="flex flex-col gap-6">

            {/* SUCCESS LIST */}
            <div className="flex-1 bg-gray-50 p-4 rounded-lg border border-gray-200 overflow-y-auto max-h-[200px]">
                <h4 className="m-0 mb-3 text-green-600 font-bold">✓ Downloaded ({success.length})</h4>
                {success.length === 0 && <p className="text-gray-400 text-sm">No files yet...</p>}
                {success.map((f, i) => (
                    <div key={i} className="mb-1">
                        <a
                            href={getDownloadUrl(f)}
                            target="_blank"
                            rel="noreferrer"
                            className="text-blue-600 hover:text-blue-800 text-sm no-underline hover:underline"
                        >
                            📄 {f}
                        </a>
                    </div>
                ))}
            </div>

            {/* FAILED LIST */}
            <div className="flex-1 bg-red-50 p-4 rounded-lg border border-red-100 overflow-y-auto max-h-[200px]">
                <div className="flex justify-between items-center mb-3">
                    <h4 className="m-0 text-red-700 font-bold">✕ Failed ({failed.length})</h4>
                    {failed.length > 0 && (
                        <button
                            onClick={downloadFailedReport}
                            className="text-[11px] px-2 py-1 cursor-pointer bg-red-500 text-white border-0 rounded hover:bg-red-600 transition-colors"
                        >
                            Export List
                        </button>
                    )}
                </div>
                {failed.length === 0 && <p className="text-gray-400 text-sm">No failures yet...</p>}
                {failed.map((f, i) => (
                    <div key={i} className="text-xs text-red-600 mb-1">• {f}</div>
                ))}
            </div>

            {/* NEW JOB BUTTON */}
            {isCompleted && (
                <div className="mt-4 text-center">
                    <button
                        onClick={onReset}
                        className="px-6 py-2 bg-slate-700 text-white rounded-md hover:bg-slate-800 transition-colors"
                    >
                        Start New Batch
                    </button>
                </div>
            )}

        </div>
    );
};

export default ResultList;
