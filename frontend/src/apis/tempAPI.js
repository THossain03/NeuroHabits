import axios from 'axios';

const API = axios.create({
    baseURL: '/api', // Proxy setup in `package.json` handles the backend URL
});

export const getData = () => API.get('/data');