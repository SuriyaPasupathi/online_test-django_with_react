import React, { useState, useEffect } from "react";
import axios from "axios";

const TestQuestion = () => {
    const [questions, setQuestions] = useState([]);
    const [answers, setAnswers] = useState({});
    const [incorrectAnswers, setIncorrectAnswers] = useState({});
    const [correctAnswers, setCorrectAnswers] = useState({});
    const [level, setLevel] = useState(1);
    const [section, setSection] = useState(1);
    const [testCompleted, setTestCompleted] = useState(false);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [totalQuestions, setTotalQuestions] = useState(0);
    const [totalIncorrect, setTotalIncorrect] = useState(0);
    const [testTimer, setTestTimer] = useState(null);
    const [isTestRunning, setIsTestRunning] = useState(false);
    const [finalScore, setFinalScore] = useState(0);

    useEffect(() => {
        fetchQuestions();
    }, [level, section]);

    useEffect(() => {
        if (testCompleted) {
            axios
                .post("http://localhost:8000/api/test_session/", {
                    score: totalQuestions - totalIncorrect,
                    total_questions: totalQuestions,
                }, {
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem("access_token")}`
                    }
                })
                .then((response) => {
                    console.log("Practice session recorded:", response.data);
                })
                .catch((error) => {
                    console.error("Error submitting practice session:", error);
                });
        }
    }, [testCompleted]);

    useEffect(() => {
        if (testTimer !== null && testTimer > 0) {
            const timerInterval = setInterval(() => {
                setTestTimer((prev) => {
                    if (prev <= 1) {
                        clearInterval(timerInterval);
                        handleSubmit();
                    }
                    return prev - 1;
                });
            }, 1000);
            return () => clearInterval(timerInterval);
        }
    }, [testTimer]);

    const fetchQuestions = () => {
        axios
            .get(`http://localhost:8000/api/random_questions/${level}/${section}/`)
            .then((response) => {
                setQuestions(response.data.questions);
                setAnswers({});
                setIncorrectAnswers({});
                setCorrectAnswers({});
                setCurrentQuestionIndex(0);

                if (level === 1 && section === 1) {
                    setTotalQuestions(0);
                    setTotalIncorrect(0);
                }
                setTotalQuestions((prev) => prev + response.data.questions.length);
                setTestTimer(response.data.time_limit);
                setIsTestRunning(true);
            })
            .catch((error) => console.error("Error fetching questions:", error));
    };

    const handleAnswerChange = (questionId, value) => {
        setAnswers((prev) => ({
            ...prev,
            [questionId]: value,
        }));
    };

    const handleSubmit = () => {
        axios
            .post(`http://localhost:8000/api/validate_answers/${level}/${section}/`, { answers })
            .then((response) => {
                const { incorrect_answers, correct_answers } = response.data;
                setIncorrectAnswers(incorrect_answers);
                setCorrectAnswers(correct_answers);

                const incorrectCount = Object.keys(incorrect_answers).length;
                setTotalIncorrect((prev) => prev + incorrectCount);

                if (level === 3 && section === 2) {
                    const finalScore = totalQuestions - (totalIncorrect + incorrectCount);
                    setFinalScore(finalScore);
                    setTestCompleted(true);
                    alert(`Your final score is: ${finalScore}/${totalQuestions}`);
                } else {
                    if (section === 2) {
                        setLevel(level + 1);
                        setSection(1);
                    } else {
                        setSection(2);
                    }
                }
            })
            .catch((error) => console.error("Error submitting answers:", error));
    };

    const handleBack = () => {
        setTestCompleted(false);
        setLevel(1);
        setSection(1);
        setTotalQuestions(0);
        setTotalIncorrect(0);
    };

    return (
        <div className="container mx-auto p-4">
            <h1 className="text-2xl font-bold mb-4 text-center">Abacus Test</h1>
            {!testCompleted ? (
                <div>
                    <h2 className="text-xl font-semibold text-center">
                        Level {level} - Section {section}
                    </h2>
                    {testTimer !== null && (
                        <div className="text-center text-red-600 font-bold">
                            Time Left: {Math.floor(testTimer / 60)}:{testTimer % 60 < 10 ? "0" : ""}{testTimer % 60} min
                        </div>
                    )}

                    {questions.length > 0 && (
                        <div className="p-4 border rounded shadow">
                            <p className="text-lg font-semibold">
                                {questions[currentQuestionIndex]?.question_text}
                            </p>
                            <input
                                type="text"
                                onChange={(e) =>
                                    handleAnswerChange(questions[currentQuestionIndex]?.id, e.target.value)
                                }
                                value={answers[questions[currentQuestionIndex]?.id] || ""}
                                className="border p-2 w-full mt-2 rounded"
                                placeholder="Enter your answer"
                            />
                        </div>
                    )}

                    <div className="mt-4 flex justify-center space-x-2">
                        {questions.map((_, index) => (
                            <button
                                key={index}
                                onClick={() => setCurrentQuestionIndex(index)}
                                className={`px-3 py-1 rounded ${
                                    currentQuestionIndex === index
                                        ? "bg-blue-700 text-white"
                                        : "bg-gray-300 text-black"
                                }`}
                            >
                                {index + 1}
                            </button>
                        ))}
                    </div>

                    {currentQuestionIndex === questions.length - 1 && (
                        <button
                            onClick={handleSubmit}
                            className="bg-blue-500 text-white px-4 py-2 rounded mt-4"
                        >
                            Submit Section {section}
                        </button>
                    )}
                </div>
            ) : (
                <div className="p-6 border rounded shadow bg-gray-100 text-center">
                    <h2 className="text-xl font-bold">Test Completed</h2>
                    <p className="text-lg text-green-600">
                        Final Score: {finalScore}/{totalQuestions}
                    </p>
                    <button
                        onClick={handleBack}
                        className="mt-4 bg-gray-500 text-white px-4 py-2 rounded"
                    >
                        Back
                    </button>
                </div>
            )}
        </div>
    );
};

export default TestQuestion;





















