import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const Home = () => {
  const navigate = useNavigate();
  const [notification, setNotification] = useState(null); // Store notification data
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Function to handle fetching test notifications
  const handleNotificationClick = async () => {
    setLoading(true);
    setError(null);

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

  // Function to handle Practice Session navigation
  const handlePracticeSession = () => {
    navigate("/abacus_question");
  };

  // Function to handle Test Session navigation
  const handleTestSession = () => {
    navigate("/test_session");
  };

  const handleLogout = async () => {
    try {
      const accessToken = localStorage.getItem("access_token");
      const refreshToken = localStorage.getItem("refresh_token");

      if (!accessToken || !refreshToken) {
        window.location.href = "/login_page";
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
        window.location.href = "/login_page";
      }
    } catch (error) {
      window.location.href = "/Register_page";
    }
  };

  return (
    <div className="relative flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
      <h1 className="absolute top-6 text-xl sm:text-xl md:text-xl lg:text-4xl font-bold text-gray-900 text-center mb-6">
        Online Abacus Test
      </h1>

      {/* Notification Button with Notification Message Below */}
      <div className="absolute top-4 left-4">
        <button
          onClick={handleNotificationClick}
          className="bg-red-500 text-white px-4 py-2 rounded-lg shadow-md hover:bg-red-600"
        >
          🔔 Notifications
        </button>

        {/* Display Notification Message Below Button */}
        {loading && <p className="text-gray-700 mt-2">Loading notification...</p>}
        {error && <p className="text-red-500 mt-2">{error}</p>}
        {notification && (
          <div className="absolute top-full mt-2 w-72 bg-white p-3 rounded-lg shadow-md border border-gray-300">
            <p className="text-lg font-semibold">{notification.message}</p>
            <p className="text-sm text-gray-600">{notification.start_message}</p>
          </div>
        )}
      </div>

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
