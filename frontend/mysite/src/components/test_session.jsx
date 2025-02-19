import React, { useState, useEffect, useRef } from "react";
import axios from "axios";

const TestQuestion = () => {
    const [questions, setQuestions] = useState([]);
    const [answers, setAnswers] = useState({});
    const [sectionScore, setSectionScore] = useState(null); // Track score for each section
    const [totalLevelScore, setTotalLevelScore] = useState(0); // Track cumulative score for each level
    const [incorrectAnswers, setIncorrectAnswers] = useState([]);
    const [correctAnswers, setCorrectAnswers] = useState({});
    const [level, setLevel] = useState(1);
    const [section, setSection] = useState(1);
    const [testCompleted, setTestCompleted] = useState(false);
    const [testAvailable, setTestAvailable] = useState(false);
    const [notificationMessage, setNotificationMessage] = useState("");
    const [startTime, setStartTime] = useState("");
    const [timeRemaining, setTimeRemaining] = useState(0);
    const timerRef = useRef(null); // Reference for interval

    useEffect(() => {
        fetchNotification();
    }, []);

    useEffect(() => {
        if (testAvailable) {
            fetchQuestions();
        }
    }, [testAvailable, level, section]);

    useEffect(() => {
        if (timeRemaining > 0) {
            if (timerRef.current) clearInterval(timerRef.current);

            timerRef.current = setInterval(() => {
                setTimeRemaining((prevTime) => {
                    if (prevTime <= 1) {
                        clearInterval(timerRef.current);
                        handleSubmit(); // Auto-submit on timeout
                        return 0;
                    }
                    return prevTime - 1;
                });
            }, 1000);

            return () => clearInterval(timerRef.current);
        }
    }, [timeRemaining]);

    const fetchNotification = () => {
        axios.get(`http://localhost:8000/api/test_notification/`)
            .then(response => {
                const { message, start_time, start_message, time_remaining_seconds } = response.data;
                setNotificationMessage(message);
                setStartTime(start_time);
                setTimeRemaining(time_remaining_seconds);

                if (start_message === "Test is now available!") {
                    setTestAvailable(true);
                }
            })
            .catch(error => console.error("Error fetching test notification:", error));
    };

    const fetchQuestions = () => {
        axios.get(`http://localhost:8000/api/random_question/${level}/${section}/`)
            .then(response => setQuestions(response.data))
            .catch(error => console.error("Error fetching questions:", error));
    };

    const handleAnswerChange = (questionId, value) => {
        setAnswers(prevAnswers => ({
            ...prevAnswers,
            [questionId]: value
        }));
    };

    const handleSubmit = () => {
        axios.post(
            `http://localhost:8000/api/validate_answers/${level}/${section}/`,
            { answers },
            { headers: { "Content-Type": "application/json" } }
        )
        .then((response) => {
            const { score, incorrect_answers, correct_answers, move_to_next_section, move_to_next_level } = response.data;
            
            setSectionScore(score); // Set section score
            setTotalLevelScore(prev => prev + score); // Update total score for level
            setIncorrectAnswers(incorrect_answers);
            setCorrectAnswers(correct_answers);

            if (move_to_next_section) {
                setTimeout(() => setSection(prev => prev + 1), 2000);
            } else if (move_to_next_level) {
                setTimeout(() => {
                    setLevel(prev => prev + 1);
                    setSection(1);
                }, 3000);
            } else if (level === 3 && section === 3) {
                setTestCompleted(true); // Mark test as completed after level 3, section 3
            }
        })
        .catch((error) => console.error("Error submitting answers:", error.response?.data || error));
    };

    const formatTime = (seconds) => {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}:${remainingSeconds < 10 ? '0' : ''}${remainingSeconds}`;
    };

    return (
        <div className="container mx-auto p-4">
            <h1 className="text-2xl font-bold mb-4 text-center">Abacus Test</h1>

            <div className="text-center">
                {testAvailable ? (
                    <p className="text-green-600 text-lg font-semibold">Test is now available!</p>
                ) : (
                    <p className="text-red-600 text-lg font-semibold">{notificationMessage}</p>
                )}
                {testAvailable && (
                    <>
                        <p>Start time: {new Date(startTime).toLocaleString()}</p>
                        <p>Time Remaining: {formatTime(timeRemaining)}</p>
                    </>
                )}
            </div>

            {testAvailable && (
                <>
                    {testCompleted ? (
                        <div className="p-6 border rounded shadow bg-gray-100 text-center">
                            <h2 className="text-xl font-bold">Test Completed</h2>
                            <p className="text-lg text-green-600">Final Score for Level {level}: {totalLevelScore}</p>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            <h2 className="text-xl font-semibold text-center">Level {level} - Section {section}</h2>
                            {questions.map((question) => (
                                <div key={question.id} className="p-4 border rounded shadow">
                                    <p className="text-lg font-semibold">{question.question_text}</p>
                                    <input
                                        type="text"
                                        onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                                        value={answers[question.id] || ""}
                                        className="border p-2 w-full mt-2 rounded"
                                        placeholder="Enter your answer"
                                    />
                                </div>
                            ))}
                            <button
                                onClick={handleSubmit}
                                className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition"
                            >
                                Submit {section === 1 ? "Section 1" : "Section 2"}
                            </button>

                            {sectionScore !== null && (
                                <div className="mt-4 p-4 border rounded shadow bg-gray-100 text-center">
                                    <p className="text-lg font-semibold">Section Score: {sectionScore}</p>
                                    <p className="text-lg font-semibold">Total Score for Level {level}: {totalLevelScore}</p>
                                </div>
                            )}
                        </div>
                    )}
                </>
            )}
        </div>
    );
};

export default TestQuestion;
