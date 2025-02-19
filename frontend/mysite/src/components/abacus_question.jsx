import React, { useState, useEffect } from "react";
import axios from "axios";

const PracticePage = () => {
    const [questions, setQuestions] = useState([]);
    const [answers, setAnswers] = useState({});
    const [score, setScore] = useState(null);
    const [incorrectAnswers, setIncorrectAnswers] = useState([]);
    const [correctAnswers, setCorrectAnswers] = useState({});
    const [sectionScore, setSectionScore] = useState(null);
    const [totalScore, setTotalScore] = useState(0);
    const [level, setLevel] = useState(1);
    const [section, setSection] = useState(1);
    const [testCompleted, setTestCompleted] = useState(false);
    const [practiceCount, setPracticeCount] = useState(0);

    const token = localStorage.getItem("access_token"); // Only retrieve the token once

    useEffect(() => {
        // Fetch questions when the level or section changes
        fetchQuestions();
    }, [level, section]);

    useEffect(() => {
        // Check if the token exists before making the request
        if (token) {
            const data = {};  // Your practice session data (e.g., session details)

            // Make the POST request using axios
            axios.post(
                'http://localhost:8000/api/practice-session/', 
                data, 
                {
                    headers: { Authorization: `Bearer ${token}` }, // Attach token to header
                }
            )
            .then((response) => {
                console.log('Practice session started:', response.data);
            })
            .catch((error) => {
                console.error("Error tracking practice session:", error.response ? error.response.data : error);
                alert(`Error: ${error.response ? error.response.data : error}`);
            });
        } else {
            console.error("No token found in localStorage.");
        }
    }, [token]); // Effect runs when `token` changes or on component mount

    const fetchQuestions = () => {
        axios.get(`http://localhost:8000/api/questions/${level}/${section}/`)
            .then((response) => {
                setQuestions(response.data.questions);
                setAnswers({});
                setScore(null);
                setIncorrectAnswers([]);
                setCorrectAnswers({});
            })
            .catch((error) => {
                console.error("Error fetching questions:", error);
            });
    };

    const handleAnswerChange = (questionId, value) => {
        setAnswers((prevAnswers) => ({
            ...prevAnswers,
            [questionId]: value,
        }));
    };

    const handleSubmit = () => {
        axios.post(`http://localhost:8000/api/submit_answers/${level}/${section}/`, {
            answers: answers,
            total_score: totalScore,
        }, {
            headers: {
                "Content-Type": "application/json",
            },
        })
        .then((response) => {
            setScore(response.data.score);
            setIncorrectAnswers(response.data.incorrect_answers);
            setCorrectAnswers(response.data.correct_answers);

            if (response.data.move_to_next_section) {
                setSectionScore(response.data.score);
                setTimeout(() => setSection(2), 2000); // Move to Section 2
            } else if (response.data.move_to_next_level) {
                setTotalScore(response.data.total_score);
                setTestCompleted(true);

                // Prevent moving to level 4
                if (level < 3) {
                    setTimeout(() => {
                        setLevel(level + 1); // Move to next level
                        setSection(1); // Start from Section 1 in the next level
                        setTestCompleted(false);
                    }, 3000); // Move to next level after showing total score
                }
            }
        })
        .catch((error) => {
            console.error("Error submitting answers:", error);
        });
    };

    return (
        <div className="container mx-auto p-4">
            <h1 className="text-2xl font-bold mb-4 text-center">Abacus Test</h1>
            <p className="text-center text-lg font-semibold">You've practiced {practiceCount} times.</p>

            {testCompleted ? (
                <div className="p-6 border rounded shadow bg-gray-100 text-center">
                    <h2 className="text-xl font-bold">Level {level - 1} Completed</h2>
                    <p className="text-lg text-green-600">Total Score: {totalScore} / 20</p>
                    <p className="text-blue-500">Moving to Level {level}...</p>
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

                    {score !== null && (
                        <div className="mt-4 p-4 border rounded shadow bg-gray-100">
                            <p className="text-lg font-bold">Your Score: {score}</p>

                            {incorrectAnswers.length > 0 && (
                                <div>
                                    <p className="text-red-500 font-semibold">Incorrect Answers:</p>
                                    <ul className="list-disc list-inside">
                                        {incorrectAnswers.map((questionId, index) => (
                                            <li key={index} className="text-red-500">
                                                Q{questionId} - Correct: {correctAnswers[questionId]}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default PracticePage;
