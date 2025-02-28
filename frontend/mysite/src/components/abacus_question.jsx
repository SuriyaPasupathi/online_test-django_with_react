import React, { useState, useEffect } from "react";
import axios from "axios";

const PracticePage = () => {
    const [questions, setQuestions] = useState([]);
    const [answers, setAnswers] = useState({});
    const [incorrectAnswers, setIncorrectAnswers] = useState({});
    const [lastCorrectAnswers, setLastCorrectAnswers] = useState({}); // changed from correctAnswers to lastCorrectAnswers
    const [level, setLevel] = useState(null);
    const [section, setSection] = useState(1);
    const [testCompleted, setTestCompleted] = useState(false);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [totalScore, setTotalScore] = useState(0);
    const [totalQuestions, setTotalQuestions] = useState(0);

    useEffect(() => {
        if (level !== null) {
            fetchQuestions();
        }
    }, [level, section]);

    const fetchQuestions = () => {
        axios.get(`http://localhost:8000/api/questions/${level}/${section}/`)
            .then((response) => {
                setQuestions(response.data.questions);
                setAnswers({});
                setIncorrectAnswers((prev) => ({ ...prev, [section]: {} }));
                setLastCorrectAnswers((prev) => ({ ...prev, [section]: {} })); // reset lastCorrectAnswers
                setCurrentQuestionIndex(0);
                setTotalQuestions((prev) => prev + response.data.questions.length); // Track total questions
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
        axios.post(`http://localhost:8000/api/submit_answers/${level}/${section}/`, { answers })
            .then((response) => {
                const { incorrect_answers, correct_answers } = response.data;
                setIncorrectAnswers((prev) => ({ ...prev, [section]: incorrect_answers }));
                setLastCorrectAnswers((prev) => ({ ...prev, [section]: correct_answers })); // save last correct answers

                const correctCount = Object.keys(correct_answers).length;
                setTotalScore((prev) => prev + correctCount); // Update total correct count

                if (section === 2) {
                    const token = localStorage.getItem("access_token");
                    if (!token) {
                        window.location.href = '/login';
                        return;
                    }

                    axios.post("http://localhost:8000/api/practice_session/", 
                        { score: totalScore + correctCount, total_questions: totalQuestions }, 
                        { headers: { "Authorization": `Bearer ${token}`, "Content-Type": "application/json" } }
                    )
                    .then(() => {
                        setTestCompleted(true);
                        alert(`Your total score is: ${totalScore + correctCount}/${totalQuestions}`);
                    })
                    .catch((error) => console.error("Error updating practice session:", error));
                } else {
                    setSection(2); // Move to Section 2
                }
            })
            .catch((error) => console.error("Error submitting answers:", error));
    };

    const handleLevelChange = (selectedLevel) => {
        setLevel(selectedLevel);
        setSection(1);
        setTestCompleted(false);
        setIncorrectAnswers({});
        setLastCorrectAnswers({}); // reset lastCorrectAnswers
        setTotalScore(0);
        setTotalQuestions(0);
    };

    const handleBack = () => {
        setLevel(null);
        setTestCompleted(false);
        setSection(1);
    };

    const handlePaginationClick = (index) => {
        setCurrentQuestionIndex(index);
    };

    return (
        <div className="container mx-auto p-4">
            <h1 className="text-2xl font-bold mb-4 text-center">Abacus Test</h1>
            {level === null ? (
                <div className="mb-4 text-center">
                    {[1, 2, 3].map((lvl) => (
                        <button key={lvl} onClick={() => handleLevelChange(lvl)} className="bg-blue-500 text-white px-4 py-2 rounded mr-2">
                            Level {lvl}
                        </button>
                    ))}
                </div>
            ) : !testCompleted ? (
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
                    <div className="flex justify-center mt-4">
                        {questions.map((_, index) => (
                            <button
                                key={index}
                                onClick={() => handlePaginationClick(index)}
                                className={`px-4 py-2 rounded mx-1 ${currentQuestionIndex === index ? 'bg-blue-500 text-white' : 'bg-gray-300'}`}
                            >
                                {index + 1}
                            </button>
                        ))}
                    </div>

                    {Object.keys(answers).length === questions.length && (
                        <button onClick={handleSubmit} className="bg-blue-500 text-white px-4 py-2 rounded mt-4">
                            Submit Section {section}
                        </button>
                    )}
                </div>
            ) : (
                <div className="p-6 border rounded shadow bg-gray-100 text-center">
                    <h2 className="text-xl font-bold">Level {level} Completed</h2>
                    <p className="text-lg text-green-600">Total Correct Answers: {totalScore}/{totalQuestions}</p>
                    {[1, 2].map((sec) => (
                        <div key={sec} className="mt-4">
                            <h2 className="text-xl font-semibold">Section {sec} Incorrect Answers</h2>
                            {Object.keys(incorrectAnswers[sec] || {}).length > 0 ? (
                                Object.entries(incorrectAnswers[sec]).map(([questionId, userAnswer]) => (
                                    <div key={questionId} className="p-4 border rounded shadow">
                                        <p className="text-red-500">❌ Your Answer: {userAnswer}</p>
                                        <p className="text-green-500">✔ Correct Answer: {lastCorrectAnswers[sec]?.[questionId]}</p> {/* Display last correct answer */}
                                    </div>
                                ))
                            ) : <p className="text-gray-600">No incorrect answers!</p>}
                        </div>
                    ))}
                    <button onClick={handleBack} className="mt-4 bg-gray-500 text-white px-4 py-2 rounded">Back</button>
                </div>
            )}
        </div>
    );
};

export default PracticePage;