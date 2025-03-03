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
    const [totalScore, setTotalScore] = useState(0);
    const token = localStorage.getItem("token");

    useEffect(() => {
        fetchQuestions();
    }, [level, section]);

    // Fetch Questions from Backend
    const fetchQuestions = () => {
        axios.get(`http://localhost:8000/api/random_questions/${level}/${section}/`, {
            headers: { 
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            }
        })
        .then((response) => {
            if (response.data.questions.length === 0) {
                alert("No new questions available.");
                return;
            }

            setQuestions(response.data.questions);
            setAnswers({});
            setIncorrectAnswers({});
            setCorrectAnswers({});
            setCurrentQuestionIndex(0);
            setTotalQuestions(response.data.questions.length);
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
        axios.post(`http://localhost:8000/api/validate_answers/${level}/${section}/`, { answers }, {
            headers: { 
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            }
        })
        .then((response) => {
            const { incorrect_answers, correct_answers } = response.data;
            setIncorrectAnswers((prev) => ({ ...prev, [section]: incorrect_answers }));
            setCorrectAnswers((prev) => ({ ...prev, [section]: correct_answers }));

            const incorrectCount = Object.keys(incorrect_answers).length;
            const sectionScore = totalQuestions - incorrectCount;

            setTotalIncorrect((prev) => prev + incorrectCount);
            setTotalScore((prev) => prev + sectionScore);

            if (level === 3 && section === 2) {
                // Show final score only after Level 3 Section 2
                setTestCompleted(true);
                alert(`Test Completed! Your final score: ${totalScore + sectionScore}/${totalQuestions * 6}`);
            } else {
                // Move to next section or next level
                if (section === 2) {
                    setLevel((prev) => prev + 1);
                    setSection(1);
                } else {
                    setSection(2);
                }
            }
        })
        .catch((error) => console.error("Error submitting answers:", error));
    };

    const handleBack = () => {
        setLevel(1);
        setSection(1);
        setTestCompleted(false);
        setIncorrectAnswers({});
        setCorrectAnswers({});
        setTotalIncorrect(0);
        setTotalQuestions(0);
        setTotalScore(0);
    };

    const isLastQuestion = currentQuestionIndex === questions.length - 1;

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

                    {/* Pagination Buttons */}
                    <div className="mt-4 flex justify-center space-x-2">
                        {questions.map((_, index) => (
                            <button
                                key={index}
                                onClick={() => setCurrentQuestionIndex(index)}
                                className={`px-3 py-1 rounded ${currentQuestionIndex === index ? "bg-blue-700 text-white" : "bg-gray-300 text-black"}`}
                            >
                                {index + 1}
                            </button>
                        ))}
                    </div>

                    {/* Show Submit Button ONLY on the Last Question */}
                    {isLastQuestion && (
                        <button onClick={handleSubmit} className="bg-blue-500 text-white px-4 py-2 rounded mt-4">
                            Submit Section {section}
                        </button>
                    )}
                </div>
            ) : (
                <div className="p-6 border rounded shadow bg-gray-100 text-center">
                    <h2 className="text-xl font-bold">Test Completed!</h2>
                    <p className="text-lg text-green-600">
                        Final Score: {totalScore}/{totalQuestions * 6}
                    </p>
                    {[1, 2, 3].map((lvl) => (
                        <div key={lvl} className="mt-4">
                            <h2 className="text-xl font-semibold">Level {lvl}</h2>
                            {[1, 2].map((sec) => (
                                <div key={sec}>
                                    <h3 className="text-lg font-medium">Section {sec}</h3>
                                    {incorrectAnswers[sec] && Object.keys(incorrectAnswers[sec]).length > 0 ? (
                                        Object.entries(incorrectAnswers[sec]).map(([questionId, userAnswer]) => (
                                            <div key={questionId} className="p-4 border rounded shadow">
                                                <p className="text-red-500">❌ Your Answer: {userAnswer}</p>
                                                <p className="text-green-500">✔ Correct Answer: {correctAnswers[sec]?.[questionId]}</p>
                                            </div>
                                        ))
                                    ) : (
                                        <p className="text-gray-600">All answers correct!</p>
                                    )}
                                </div>
                            ))}
                        </div>
                    ))}
                    <button onClick={handleBack} className="mt-4 bg-gray-500 text-white px-4 py-2 rounded">Restart Test</button>
                </div>
            )}
        </div>
    );
};

export default TestQuestion;
