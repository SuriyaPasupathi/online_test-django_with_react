import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const Home = () => {
  const navigate = useNavigate();

  // Check for authentication on component mount
  useEffect(() => {
    const accessToken = localStorage.getItem("access_token");
    if (!accessToken) {
      navigate("/Login_page");
    }
  }, [navigate]);

  // Function to handle Practice Session navigation
  const handlePracticeSession = () => {
    navigate("/abacus_question");
  };

  // Function to handle Test Session navigation
  const handleTestSession = () => {
    navigate("/test_session");
  };

  const handleLogout = async () => {
    const refreshToken = localStorage.getItem("refresh_token");
    const accessToken = localStorage.getItem("access_token");
  
    // Clear tokens first to prevent any issues if the API call fails
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    
    // Only attempt API call if we have tokens
    if (refreshToken && accessToken) {
      try {
        await axios.post(
          "http://127.0.0.1:8000/api/logout/",
          { refresh_token: refreshToken },
          { headers: { Authorization: `Bearer ${accessToken}` } }
        );
        console.log("Logout API call successful");
      } catch (error) {
        console.error("Logout API call failed:", error);
        // We've already cleared tokens, so no need to handle further
      }
    }
    
    alert("You have been logged out successfully.");
    navigate("/Login_page");
  };

  return (
    <div className="relative flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
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