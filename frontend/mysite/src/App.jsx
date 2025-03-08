import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Register from './components/Register_page';
import Login from './components/Login_page';
import Home from './components/Home';
import PracticePage from './components/abacus_question';
import TestQuestion from './components/test_session';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Register />} />
        <Route path="/Login_page" element={<Login />} />
        
        {/* Protected Routes */}
        <Route 
          path="/Home" 
          element={
            <ProtectedRoute>
              <Home />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/abacus_question" 
          element={
            <ProtectedRoute>
              <PracticePage />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/test_session" 
          element={
            <ProtectedRoute>
              <TestQuestion />
            </ProtectedRoute>
          } 
        />
      </Routes>
    </Router>
  );
}

export default App;
