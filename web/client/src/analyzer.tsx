import './index.css';
import { bootstrapApp } from '@/utils/bootstrap';
import { AnalyzerPage } from '@/pages/AnalyzerPage';

// Bootstrap the analyzer page application
bootstrapApp({
  pageName: 'Analyzer',
  component: AnalyzerPage,
  rootElementId: 'root',
  enableDebugLogs: process.env.NODE_ENV === 'development'
});