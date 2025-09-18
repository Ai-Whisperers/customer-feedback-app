import './index.css';
import { bootstrapApp } from '@/utils/bootstrap';
import { LandingPage } from '@/pages/LandingPage';

// Bootstrap the landing page application
bootstrapApp({
  pageName: 'Landing',
  component: LandingPage,
  rootElementId: 'root',
  enableDebugLogs: process.env.NODE_ENV === 'development'
});