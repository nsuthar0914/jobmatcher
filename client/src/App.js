import React from 'react';
import { Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import HomePage from './pages/HomePage';
import JobOpeningPage from './pages/JobOpeningPage';
import JobSeekerPage from './pages/JobSeekerPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/job-seeker" element={<JobSeekerPage />} />
        <Route path="/job-opening" element={<JobOpeningPage />} />
      </Routes>
    </Router>
  );
}

export default App;
