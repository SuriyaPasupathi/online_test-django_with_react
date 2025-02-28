import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

// Create axios instance with default config
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Add request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    console.log('API Request:', {
      url: config.url,
      method: config.method,
      headers: config.headers,
      data: config.data
    });
    return config;
  },
  (error) => {
    console.error('Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', {
      status: response.status,
      data: response.data
    });
    return response;
  },
  async (error) => {
    console.error('Response Error:', {
      status: error.response?.status,
      data: error.response?.data,
      message: error.message
    });

    if (error.response?.status === 401) {
      // Token expired or invalid
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post('http://127.0.0.1:8000/api/token/refresh/', {
            refresh: refreshToken
          });
          const newAccessToken = response.data.access;
          localStorage.setItem('access_token', newAccessToken);
          
          // Retry the original request
          error.config.headers.Authorization = `Bearer ${newAccessToken}`;
          return api(error.config);
        } catch (refreshError) {
          console.error('Token refresh failed:', refreshError);
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/Login_page';
        }
      }
    }
    return Promise.reject(error);
  }
);

const Home = () => {
  const navigate = useNavigate();
  const [error, setError] = useState(null);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const accessToken = localStorage.getItem("access_token");
        if (!accessToken) {
          navigate("/Login_page");
          return;
        }

        // Verify token is valid
        await api.get('/verify-token/');
      } catch (error) {
        console.error('Authentication check failed:', error);
        if (error.response?.status === 401) {
          navigate("/Login_page");
        } else {
          setError('Server connection error. Please try again later.');
        }
      }
    };

    checkAuth();
  }, [navigate]);

  const handlePracticeSession = () => {
    navigate("/abacus_question");
  };

  const handleTestSession = () => {
    navigate("/test_session");
  };

  const handleLogout = async () => {
    try {
      const refreshToken = localStorage.getItem("refresh_token");
      await api.post("/logout/", { refresh_token: refreshToken });
      
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      
      alert("You have been logged out successfully.");
      navigate("/Login_page");
    } catch (error) {
      console.error("Logout failed:", error);
      
      // Force logout on client side even if API call fails
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      
      alert("Logout completed with some errors. Please refresh the page.");
      navigate("/Login_page");
    }
  };

  return (
    <div className="relative flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
      {error && (
        <div className="absolute top-0 w-full bg-red-500 text-white p-3 text-center">
          {error}
        </div>
      )}

      <h1 className="absolute top-6 text-xl sm:text-xl md:text-xl lg:text-4xl font-bold text-gray-900 text-center mb-6">
        Online Abacus Test
      </h1>

      {/* Notification Button */}
      <button className="absolute top-4 left-4 bg-red-500 text-white px-4 py-2 rounded-lg shadow-md hover:bg-red-600">
        🔔 Notifications
      </button>

      {/* Logout Button */}
      <button
        onClick={handleLogout}
        className="absolute top-4 right-4 bg-gray-800 text-white px-4 py-2 rounded-lg shadow-md hover:bg-gray-900"
      >
        Logout
      </button>

      {/* Image Section */}
      <div className="relative w-full max-w-3xl px-2">
        <img
          src="https://media.istockphoto.com/id/968852086/photo/happy-teacher-and-kids-learning-to-count-on-abacus-at-preschool.jpg?s=612x612&w=0&k=20&c=KGJytQqvptIHtEFePsQhIqckbCoXyuDBHNLHINpOe5A="
          alt="Abacus Learning"
          className="rounded-lg shadow-lg w-full h-auto"
        />
        <p className="absolute bottom-4 left-1/2 transform -translate-x-1/2 text-black text-lg sm:text-xl md:text-2xl font-['Roboto'] italic px-4 py-2 whitespace-nowrap">
          You can learn something new every day
        </p>
      </div>

      {/* Bottom Right Buttons */}
      <div className="absolute bottom-4 right-4 flex flex-col sm:flex-row gap-4">
        <button
          onClick={handlePracticeSession}
          className="bg-blue-500 text-white px-6 py-3 rounded-lg shadow-md hover:bg-blue-600"
        >
          Practice Session
        </button>
        <button
          onClick={handleTestSession}
          className="bg-green-500 text-white px-6 py-3 rounded-lg shadow-md hover:bg-green-600"
        >
          Test Session
        </button>
      </div>
    </div>
  );
};

export default Home;