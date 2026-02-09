import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Login from './pages/Login';
import Registration from './pages/Registration';
import CompanyDashboard from './pages/CompanyDashboard';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home/>} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Registration />} />
        <Route path="/" element={<Home />} />
        <Route path="/company/:id" element={<CompanyDashboard/>} />
      </Routes>
    </Router>
  );
}

export default App;