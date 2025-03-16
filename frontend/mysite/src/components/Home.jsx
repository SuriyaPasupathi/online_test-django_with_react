import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

const Home = () => {
  const navigate = useNavigate();
  const [notification, setNotification] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showNotification, setShowNotification] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      navigate("/Login_page");
    }
  }, [navigate]);

  const handleNotificationClick = async () => {
    setLoading(true);
    setError(null);
    setShowNotification(!showNotification);

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

  const handlePracticeSession = () => navigate("/abacus_question");
  const handleTestSession = () => navigate("/test_session");
  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    navigate("/Login_page");
  };

  return (
    <div className="relative flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4 text-center">
      <h1 className="absolute top-4 sm:top-6 text-xl sm:text-2xl md:text-4xl font-bold text-gray-900 px-2">
        Online Abacus Test
      </h1>

      <button
        onClick={handleNotificationClick}
        className="absolute top-16 sm:top-4 left-4 bg-red-500 text-white px-3 py-1.5 sm:px-4 sm:py-2 rounded-lg shadow-md hover:bg-red-600 transition text-sm sm:text-base"
      >
        🔔 Notifications
      </button>

      {loading && <p className="text-gray-700 mt-4">Loading notification...</p>}
      {error && <p className="text-red-500 mt-4">{error}</p>}
      {showNotification && notification && (
        <div className="absolute top-24 sm:top-16 left-2 sm:left-4 bg-white p-3 sm:p-4 rounded-lg shadow-md max-w-[90vw] sm:max-w-md">
          <p className="text-base sm:text-lg font-semibold">{notification.message}</p>
          <p className="text-xs sm:text-sm text-gray-600">
            Test Date: {notification.formatted_date} | Time: {notification.formatted_time}
          </p>
        </div>
      )}

      <button
        onClick={handleLogout}
        className="absolute top-16 sm:top-4 right-4 bg-gray-800 text-white px-3 py-1.5 sm:px-4 sm:py-2 rounded-lg shadow-md hover:bg-gray-900 transition text-sm sm:text-base"
      >
        Logout
      </button>

      <div className="relative w-full max-w-3xl px-2 mt-28 sm:mt-20">
        <img
          src="https://media.istockphoto.com/id/968852086/photo/happy-teacher-and-kids-learning-to-count-on-abacus-at-preschool.jpg?s=612x612&w=0&k=20&c=KGJytQqvptIHtEFePsQhIqckbCoXyuDBHNLHINpOe5A="
          alt="Abacus Learning"
          className="rounded-lg shadow-lg w-full h-auto object-cover aspect-video"
        />
        <p className="absolute bottom-4 left-1/2 transform -translate-x-1/2 text-black text-base sm:text-lg md:text-2xl font-['Roboto'] italic px-2 sm:px-4 py-1 sm:py-2 bg-white/75 rounded-lg w-[90%] sm:w-auto">
          You can learn something new every day
        </p>
      </div>

      <div className="fixed bottom-4 right-0 left-0 sm:left-auto sm:right-4 flex flex-row justify-center sm:flex-row gap-2 sm:gap-4 px-4">
        <button
          onClick={handlePracticeSession}
          className="flex-1 sm:flex-initial bg-blue-500 text-white px-4 sm:px-6 py-2 sm:py-3 rounded-lg shadow-md hover:bg-blue-600 transition text-sm sm:text-base"
        >
          Practice Session
        </button>
        <button
          onClick={handleTestSession}
          className="flex-1 sm:flex-initial bg-green-500 text-white px-4 sm:px-6 py-2 sm:py-3 rounded-lg shadow-md hover:bg-green-600 transition text-sm sm:text-base"
        >
          Test Session
        </button>
      </div>
    </div>
  );
};

export default Home;
