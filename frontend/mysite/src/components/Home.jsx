import React from "react";
import { useNavigate } from "react-router-dom"; 

const Home = () => {
  const navigate = useNavigate(); // Initialize useNavigate hook for navigation

  // Function to handle the Practice Session navigation
  const handlePracticeSession = () => {
    navigate("/abacus_question"); // Navigate to the Practice Session page
  };

  // Function to handle Test Session navigation and check approval
  const handleTestSession = async () => {
    navigate("/test_session")
  }
  

  return (
    <div className="relative flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
      {/* Heading */}
      <h1 className="absolute top-6 text-xl sm:text-xl md:text-xl lg:text-4xl font-bold text-gray-900 text-center mb-6">
        Online Abacus Test
      </h1>

      {/* Notification Button (Top Left Corner) */}
      <button className="absolute top-4 left-4 bg-red-500 text-white px-4 py-2 rounded-lg shadow-md hover:bg-red-600">
        🔔 Notifications
      </button>

      {/* Image Container with Overlay Text */}
      <div className="relative w-full max-w-3xl px-2">
        <img
          src="https://media.istockphoto.com/id/968852086/photo/happy-teacher-and-kids-learning-to-count-on-abacus-at-preschool.jpg?s=612x612&w=0&k=20&c=KGJytQqvptIHtEFePsQhIqckbCoXyuDBHNLHINpOe5A="
          alt="Abacus Learning"
          className="rounded-lg shadow-lg w-full h-auto"
        />
        {/* Overlay Text Inside the Image with Black Color and No Wrap */}
        <p className="absolute bottom-4 left-1/2 transform -translate-x-1/2 text-black text-lg sm:text-xl md:text-2xl font-['Roboto'] italic px-4 py-2 whitespace-nowrap">
          You can learn something new every day
        </p>
      </div>

      {/* Bottom Right Buttons */}
      <div className="absolute bottom-4 right-4 flex flex-col sm:flex-row gap-4">
        <button
          onClick={handlePracticeSession} // Add the onClick handler
          className="bg-blue-500 text-white px-6 py-3 rounded-lg shadow-md hover:bg-blue-600"
        >
          Practice Session
        </button>
        <button 
          onClick={handleTestSession} // Add the onClick handler
          className="bg-green-500 text-white px-6 py-3 rounded-lg shadow-md hover:bg-green-600"
        >
          Test Session
        </button>
      </div>
    </div>
  );
};

export default Home;
