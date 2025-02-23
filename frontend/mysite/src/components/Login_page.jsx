import React, { useState } from 'react';

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [errorMessage, setErrorMessage] = useState('');
    const [loading, setLoading] = useState(false);

    const handleLogin = async (event) => {
        event.preventDefault();
        setLoading(true);
        setErrorMessage('');

        try {
            // Make the POST request to the backend for login
            const response = await fetch('http://127.0.0.1:8000/api/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password }),
            });

            const data = await response.json();

            if (response.status === 200 && data.access_token) {
                // Store the access and refresh tokens in localStorage for future use
                localStorage.setItem('access_token', data.access_token);
                localStorage.setItem('refresh_token', data.refresh_token);

                // Redirect the user to the home page after a successful login
                window.location.href = '/Home';
            } else {
                // Display error message if login fails
                setErrorMessage(data.message || 'Invalid credentials.');
            }
        } catch (error) {
            // Catch any errors and display them
            setErrorMessage('Something went wrong. Please try again.');
        } finally {
            // Stop loading spinner
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-200">
            <div className="w-full max-w-md bg-white p-8 rounded-lg shadow-xl border border-gray-300">
                <h2 className="text-3xl font-bold text-center text-gray-800 mb-8">
                    Login to Your Account
                </h2>
                <form onSubmit={handleLogin}>
                    <div className="mb-6">
                        <label htmlFor="username" className="block text-lg text-gray-600">
                            Username
                        </label>
                        <input
                            type="text"
                            id="username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            className="w-full p-4 mt-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="Enter your username"
                            required
                        />
                    </div>
                    <div className="mb-6">
                        <label htmlFor="password" className="block text-lg text-gray-600">
                            Password
                        </label>
                        <input
                            type="password"
                            id="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full p-4 mt-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="Enter your password"
                            required
                        />
                    </div>
                    {errorMessage && (
                        <p className="text-red-500 text-sm mb-4 text-center">{errorMessage}</p>
                    )}
                    <button
                        type="submit"
                        className="w-full p-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none transition duration-200"
                        disabled={loading}
                    >
                        {loading ? 'Logging in...' : 'Login'}
                    </button>
                </form>
                <div className="flex justify-center mt-6">
                    <p className="text-sm text-gray-600">
                        Don't have an account?{' '}
                        <a href="/signup" className="text-blue-500 hover:text-blue-600">
                            Sign up
                        </a>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Login;
