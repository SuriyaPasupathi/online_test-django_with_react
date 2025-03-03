import React, { useState, useEffect } from "react";
import axios from "axios";

const TestQuestion = () => {
    const [questions, setQuestions] = useState([]);
    const [answers, setAnswers] = useState({});
    const [level, setLevel] = useState(1);
    const [section, setSection] = useState(1);
    const [testCompleted, setTestCompleted] = useState(false);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [totalQuestions, setTotalQuestions] = useState(0);
    const [totalIncorrect, setTotalIncorrect] = useState(0);
    const [finalScore, setFinalScore] = useState(0);

    useEffect(() => {
        if (level !== null) {
            fetchQuestions();
        }
    }, [level, section]);

    useEffect(() => {
        if (testCompleted && level === 3) {
            const calculatedScore = totalQuestions - totalIncorrect;
            setFinalScore(calculatedScore);
            axios.post("http://localhost:8000/api/test_session/", {
                score: calculatedScore,
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

    const fetchQuestions = () => {
        axios.get(`http://localhost:8000/api/random_questions/${level}/${section}/`)
            .then((response) => {
                setQuestions(response.data.questions);
                setAnswers({});
                setCurrentQuestionIndex(0);
                setTotalQuestions((prev) => prev + response.data.questions.length);
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
        axios.post(`http://localhost:8000/api/validate_answers/${level}/${section}/`, { answers })
            .then((response) => {
                const incorrectCount = Object.keys(response.data.incorrect_answers).length;
                setTotalIncorrect(prev => prev + incorrectCount);

                if (section === 2) {
                    if (level === 3) {
                        setTestCompleted(true);
                        alert(`Your final score is: ${totalQuestions - totalIncorrect}/${totalQuestions}`);
                    } else {
                        setLevel(level + 1);
                        setSection(1);
                    }
                } else {
                    setSection(2);
                }
            })
            .catch((error) => console.error("Error submitting answers:", error));
    };

    return (
        <div className="container mx-auto p-4">
            <h1 className="text-2xl font-bold mb-4 text-center">Abacus Test</h1>
            {!testCompleted ? (
                <div>
                    <h2 className="text-xl font-semibold text-center">Level {level} - Section {section}</h2>
                    {questions.length > 0 && (
                        <div className="p-4 border rounded shadow">
                            <p className="text-lg font-semibold">{questions[currentQuestionIndex]?.question_text}</p>
                            <input
                                type="text"
                                onChange={(e) => handleAnswerChange(questions[currentQuestionIndex]?.id, e.target.value)}
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
                                    currentQuestionIndex === index ? "bg-blue-700 text-white" : "bg-gray-300 text-black"
                                }`}
                            >
                                {index + 1}
                            </button>
                        ))}
                    </div>

                    {currentQuestionIndex === questions.length - 1 && (
                        <button onClick={handleSubmit} className="bg-blue-500 text-white px-4 py-2 rounded mt-4">
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
                </div>
            )}
        </div>
    );
};

export default TestQuestion;






