import React from 'react';

const CourseInput = ({ input, setInput, onStart, loading }) => {
    return (
        <div>
            <label className="block mb-2 font-semibold text-gray-600">
                Paste Course List (One per line):
            </label>
            <textarea
                rows="12"
                className="w-full p-4 rounded-lg border border-gray-200 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-y"
                placeholder="Ex: Agile Scrum Master mangates..."
                value={input}
                onChange={e => setInput(e.target.value)}
            />
            <div className="mt-5 text-right">
                <button
                    onClick={onStart}
                    disabled={loading}
                    className={`px-8 py-3 rounded-md text-white font-medium transition-colors ${loading
                            ? 'bg-gray-400 cursor-not-allowed'
                            : 'bg-green-600 hover:bg-green-700'
                        }`}
                >
                    {loading ? "Starting..." : "Start Search & Download"}
                </button>
            </div>
        </div>
    );
};

export default CourseInput;
