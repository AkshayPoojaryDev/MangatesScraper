import axios from 'axios';

const API_URL = "http://localhost:8000";

const api = axios.create({
    baseURL: API_URL,
});

export const startJob = async (courses) => {
    const res = await api.post('/start', { courses });
    return res.data;
};

export const getJobStatus = async (jobId) => {
    const res = await api.get(`/status/${jobId}`);
    return res.data;
};

export const getDownloadUrl = (filename) => {
    return `${API_URL}/download/${filename}`;
}

export default api;
