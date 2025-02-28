import React, { useState, useEffect } from "react";
import axios from "axios";

const TestQuestion = () => {
    const [questions, setQuestions] = useState([]);
    const [answers, setAnswers] = useState({});
    const [totalQuestions, setTotalQuestions] = useState(0);
    const [level, setLevel] = useState(1); // Start from Level 1
    const [section, setSection] = useState(1);
    const [testCompleted, setTestCompleted] = useState(false);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [timeRemaining, setTimeRemaining] = useState(0); // Timer state
    const [totalScore, setTotalScore] = useState(0); // Total score across levels

    useEffect(() => {
        fetchQuestions();
    }, [level, section]);

    useEffect(() => {
        if (timeRemaining > 0) {
            const timer = setInterval(() => {
                setTimeRemaining((prevTime) => prevTime - 1);
            }, 1000);
            return () => clearInterval(timer);
        }
    }, [timeRemaining]);

    // Fetch Questions from Backend
    const fetchQuestions = () => {
        axios.get(`http://localhost:8000/api/random_questions/${level}/${section}/`)
            .then((response) => {
                setQuestions(response.data.questions);
                setTotalQuestions(response.data.questions.length);
                setAnswers({});
                setCurrentQuestionIndex(0);
                setTimeRemaining(response.data.questions.length * 60); // 60 seconds per question
            })
            .catch((error) => console.error("Error fetching questions:", error));
    };

    // Handle Answer Change
    const handleAnswerChange = (questionId, value) => {
        setAnswers((prev) => ({
            ...prev,
            [questionId]: value,
        }));
    };

    // Submit Answers and Validate
    const handleSubmit = () => {
        axios.post(`http://localhost:8000/api/validate_answers/${level}/${section}/`, { answers })
            .then((response) => {
                const sectionScore = response.data.score;
                setTotalScore((prev) => prev + sectionScore);

                if (section === 1) {
                    setSection(2); // Move to Section 2
                } else {
                    if (level < 3) {
                        setLevel(level + 1);
                        setSection(1); // Reset to first section of next level
                    } else {
                        setTestCompleted(true); // Test Completed
                    }
                }
            })
            .catch((error) => console.error("Error submitting answers:", error));
    };

    const isLastQuestion = currentQuestionIndex === questions.length - 1;
    const formattedTimeRemaining = `${Math.floor(timeRemaining / 60)}:${timeRemaining % 60 < 10 ? "0" : ""}${timeRemaining % 60}`;

    return (
        <div className="container mx-auto p-4">
            <h1 className="text-2xl font-bold mb-4 text-center">Abacus Test</h1>
            {!testCompleted ? (
                <div className="space-y-4">
                    <h2 className="text-xl font-semibold text-center">Level {level} - Section {section}</h2>
                    <p className="text-lg text-green-600 text-center">Time Remaining: {formattedTimeRemaining}</p>

                    <div className="flex justify-center space-x-2 mb-4">
                        {questions.map((_, index) => (
                            <button
                                key={index}
                                onClick={() => setCurrentQuestionIndex(index)}
                                className={`px-3 py-1 rounded ${index === currentQuestionIndex ? 'bg-blue-600 text-white' : 'bg-gray-300'}`}
                            >
                                {index + 1}
                            </button>
                        ))}
                    </div>
                    
                    {questions.length > 0 && (
                        <div key={questions[currentQuestionIndex].id} className="p-4 border rounded shadow">
                            <p className="text-lg font-semibold">{questions[currentQuestionIndex].question_text}</p>
                            <input
                                type="text"
                                onChange={(e) => handleAnswerChange(questions[currentQuestionIndex].id, e.target.value)}
                                value={answers[questions[currentQuestionIndex].id] || ""}
                                className="border p-2 w-full mt-2 rounded"
                                placeholder="Enter your answer"
                            />
                        </div>
                    )}
                    
                    {isLastQuestion && Object.keys(answers).length === questions.length && (
                        <button 
                            onClick={handleSubmit} 
                            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition"
                        >
                            Submit Section {section}
                        </button>
                    )}
                </div>
            ) : (
                <div className="p-6 border rounded shadow bg-gray-100 text-center">
                    <h2 className="text-xl font-bold">Test Completed</h2>
                    <p className="text-lg text-green-600">Total Score: {totalScore}</p>
                </div>
            )}
        </div>
    );
};

export default TestQuestion;
