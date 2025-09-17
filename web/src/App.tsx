import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { LandingPage } from './app/LandingPage';
import { AboutPage } from './app/AboutPage';
import { AnalyzerPage } from './app/AnalyzerPage';

export const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/analyzer" element={<AnalyzerPage />} />
      </Routes>
    </Router>
  );
};