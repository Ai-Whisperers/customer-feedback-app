/**
 * Main application component with React Router
 * Customer AI Driven Feedback Analyzer v3.1.0
 */

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { LandingPage } from '@/pages/LandingPage';
import { AboutPage } from '@/pages/AboutPage';
import { AnalyzerPage } from '@/pages/AnalyzerPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/analyzer" element={<AnalyzerPage />} />
      </Routes>
    </Router>
  );
}

export default App;