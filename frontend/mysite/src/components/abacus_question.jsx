import React, { useState, useEffect } from "react";
import axios from "axios";

const PracticePage = () => {
    const [questions, setQuestions] = useState([]);
    const [answers, setAnswers] = useState({});
    const [incorrectAnswers, setIncorrectAnswers] = useState({});
    const [correctAnswers, setCorrectAnswers] = useState({});
    const [totalQuestions, setTotalQuestions] = useState(0);
    const [level, setLevel] = useState(null);
    const [section, setSection] = useState(1);
    const [testCompleted, setTestCompleted] = useState(false);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);

    useEffect(() => {
        if (level !== null) {
            fetchQuestions();
        }
    }, [level, section]);

    const fetchQuestions = () => {
        axios.get(`http://localhost:8000/api/questions/${level}/${section}/`)
            .then((response) => {
                setQuestions(response.data.questions);
                setTotalQuestions((prev) => prev + response.data.questions.length);
                setAnswers({});
                setIncorrectAnswers((prev) => ({ ...prev, [section]: {} }));
                setCorrectAnswers((prev) => ({ ...prev, [section]: {} }));
                setCurrentQuestionIndex(0);
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
        // Submit the answers first
        axios.post(`http://localhost:8000/api/submit_answers/${level}/${section}/`, { answers }, {
            headers: { "Content-Type": "application/json" },
        })
        .then((response) => {
            const incorrect = response.data.incorrect_answers;
            const correct = response.data.correct_answers;
    
            // Update the state with incorrect and correct answers
            setIncorrectAnswers((prev) => ({
                ...prev,
                [section]: incorrect
            }));
    
            setCorrectAnswers((prev) => ({
                ...prev,
                [section]: correct
            }));
    
            // Calculate the score
            const incorrectCount = Object.keys(incorrect).length;
            const totalQuestions = questions.length;
            const score = totalQuestions - incorrectCount; // Calculate score
    
            if (section === 2) {
                // Check if token exists
                const token = localStorage.getItem("access_token"); // Make sure to use the correct key
    
                if (!token) {
                    console.error("Token is missing! Please log in again.");
                    window.location.href = '/login'; // Redirect to login if no token
                    return;
                }
    
                // Send the score to the practice session API
                axios.post("http://localhost:8000/api/practice-session/", { score: score }, {
                    headers: { 
                        "Authorization": `Bearer ${token}`, // Add Bearer token in the request header
                        "Content-Type": "application/json"
                    }
                })
                .then(() => {
                    console.log("Practice session updated with session count!");
                    setTestCompleted(true); // Mark the test as completed
                })
                .catch((error) => {
                    console.error("Error updating practice session:", error);
                });
            } else {
                // Move to the next section
                setSection(2); // Assuming section 2 is the next step
            }
        })
        .catch((error) => {
            console.error("Error submitting answers:", error);
        });
    };
    const handleLevelChange = (selectedLevel) => {
        setLevel(selectedLevel);
        setSection(1);
        setTestCompleted(false);
        setTotalQuestions(0);
        setIncorrectAnswers({});
        setCorrectAnswers({});
    };

    const handleBack = () => {
        setLevel(null);
        setTestCompleted(false);
        setTotalQuestions(0);
        setSection(1);
        setIncorrectAnswers({});
        setCorrectAnswers({});
    };

    // Calculate correct answers count
    const correctCount = totalQuestions - Object.values(incorrectAnswers).reduce((sum, sec) => sum + Object.keys(sec).length, 0);

    return (
        <div className="container mx-auto p-4">
            <h1 className="text-2xl font-bold mb-4 text-center">Abacus Test</h1>

            {level === null ? (
                <div className="mb-4 text-center">
                    {[1, 2, 3].map((lvl) => (
                        <button 
                            key={lvl} 
                            onClick={() => handleLevelChange(lvl)} 
                            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 mr-2"
                        >
                            Level {lvl}
                        </button>
                    ))}
                </div>
            ) : !testCompleted ? (
                <div className="space-y-4">
                    <h2 className="text-xl font-semibold text-center">Level {level} - Section {section}</h2>
                    
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
                    
                    {Object.keys(answers).length === questions.length && (
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
                    <h2 className="text-xl font-bold">Level {level} Completed</h2>

                    <p className="text-lg text-green-600">
                        Correct Answers: {correctCount} / {totalQuestions}
                    </p>

                    {[1, 2].map((sec) => (
                        <div key={sec} className="mt-4">
                            <h2 className="text-xl font-semibold">Section {sec} Incorrect Answers</h2>
                            {incorrectAnswers[sec] && Object.keys(incorrectAnswers[sec]).length > 0 ? (
                                Object.entries(incorrectAnswers[sec]).map(([questionId, userAnswer]) => (
                                    <div key={questionId} className="p-4 border rounded shadow">
                                        <p className="text-red-500">❌ Your Answer: {userAnswer}</p>
                                        <p className="text-green-500">✔ Correct Answer: {correctAnswers[sec][questionId]}</p>
                                    </div>
                                ))
                            ) : <p className="text-gray-600">No incorrect answers!</p>}
                        </div>
                    ))}
                    
                    <button 
                        onClick={handleBack} 
                        className="mt-4 bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
                    >
                        Back
                    </button>
                </div>
            )}
        </div>
    );
};

export default PracticePage;












