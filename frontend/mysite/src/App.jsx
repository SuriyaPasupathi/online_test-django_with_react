import React from "react";
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Register from "./components/Register_page";
import Login from "./components/Login_page";
import Home from "./components/Home";
import PracticePage from "./components/abacus_question";
import TestQuestion from "./components/test_session";




function App() {
  return (
    <div>
      <Router>
      <Routes>
        <Route path="/" element={< Register/>} />
        <Route path="Login_page" element={< Login/>} />
        <Route path="Home" element={< Home/>} />
        <Route path="abacus_question" element={< PracticePage/>} />
        <Route path="test_session" element={< TestQuestion/>} />
     

     </Routes>
     </Router>
    </div>
  );
}

export default App;
