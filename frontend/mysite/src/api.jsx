import axios from "axios";

const getAPI = axios.create({
    baseURL: "http://127.0.0.1:8000",
    timeout: 5000,  // Set timeout to avoid infinite waits
    headers: { "Content-Type": "application/json" },
});

// Automatically attach token to requests
getAPI.interceptors.request.use(
    (config) => {
        const accessToken = localStorage.getItem("access_token");
        if (accessToken) {
            config.headers.Authorization = `Bearer ${accessToken}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

export default getAPI;
