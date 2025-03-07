import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const Home = () => {
  const navigate = useNavigate();
  const [notification, setNotification] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showNotification, setShowNotification] = useState(false); // State for toggling notification visibility

  // Fetch test notifications
  const handleNotificationClick = async () => {
    setLoading(true);
    setError(null);
    setShowNotification(!showNotification); // Toggle notification visibility

    try {
      const response = await fetch("http://localhost:8000/api/test_notification/");
      const data = await response.json();

      if (response.ok) {
        setNotification(data);
      } else {
        setError(data.error || "Failed to fetch notification");
      }
    } catch (error) {
      setError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  // Navigate to Practice Session
  const handlePracticeSession = () => navigate("/abacus_question");

  // Navigate to Test Session
  const handleTestSession = () => navigate("/test_session");

  // Handle Logout
  const handleLogout = async () => {
    try {
      const accessToken = localStorage.getItem("access_token");
      const refreshToken = localStorage.getItem("refresh_token");

      if (!accessToken || !refreshToken) {
        navigate("/login_page");
        return;
      }

      const response = await fetch("http://localhost:8000/api/logout/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ refresh: refreshToken }),
      });

      if (response.ok) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        navigate("/login_page");
      } else {
        throw new Error("Logout failed");
      }
    } catch (error) {
      navigate("/Register_page");
    }
  };

  return (
    <div className="relative flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
      {/* Page Title */}
      <h1 className="absolute top-6 text-xl sm:text-xl md:text-xl lg:text-4xl font-bold text-gray-900 text-center mb-6">
        Online Abacus Test
      </h1>

      {/* Notification Button */}
      <button
        onClick={handleNotificationClick}
        className="absolute top-4 left-4 bg-red-500 text-white px-4 py-2 rounded-lg shadow-md hover:bg-red-600 transition"
      >
        🔔 Notifications
      </button>

      {/* Display Notification */}
      {loading && <p className="text-gray-700 mt-4">Loading notification...</p>}
      {error && <p className="text-red-500 mt-4">{error}</p>}
      {showNotification && notification && (
        <div className="absolute top-16 left-4 bg-white p-4 rounded-lg shadow-md text-center">
          <p className="text-lg font-semibold">{notification.message}</p>
          <p className="text-sm text-gray-600">
            Test Date: {notification.formatted_date} | Time: {notification.formatted_time}
          </p>
        
        </div>
      )}

      {/* Logout Button */}
      <button
        onClick={handleLogout}
        className="absolute top-4 right-4 bg-gray-800 text-white px-4 py-2 rounded-lg shadow-md hover:bg-gray-900 transition"
      >
        Logout
      </button>

      {/* Image Section */}
      <div className="relative w-full max-w-3xl px-2 mt-8">
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
          className="bg-blue-500 text-white px-6 py-3 rounded-lg shadow-md hover:bg-blue-600 transition"
        >
          Practice Session
        </button>
        <button
          onClick={handleTestSession}
          className="bg-green-500 text-white px-6 py-3 rounded-lg shadow-md hover:bg-green-600 transition"
        >
          Test Session
        </button>
      </div>
    </div>
  );
};

export default Home;
