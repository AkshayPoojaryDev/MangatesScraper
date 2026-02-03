import React from 'react';

const JobDashboard = ({ status, children }) => {
    if (!status) return null;

    return (
        <div>
            {/* PROGRESS BAR */}
            <div className="mb-8">
                <div className="flex justify-between mb-2">
                    <span className="font-bold text-slate-700">Status: {status.status.toUpperCase()}</span>
                    <span className="text-gray-500">{status.progress}%</span>
                </div>
                <div className="w-full bg-gray-200 h-3 rounded-full overflow-hidden">
                    <div
                        className={`h-full transition-all duration-500 ease-out ${status.status === 'completed' ? 'bg-green-600' : 'bg-blue-500'
                            }`}
                        style={{ width: `${status.progress}%` }}
                    ></div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {children}
            </div>
        </div>
    );
};

export default JobDashboard;
