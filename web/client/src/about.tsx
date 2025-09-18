import './index.css';
import { bootstrapApp } from '@/utils/bootstrap';
import { AboutPage } from '@/pages/AboutPage';

// Bootstrap the about page application
bootstrapApp({
  pageName: 'About',
  component: AboutPage,
  rootElementId: 'root',
  enableDebugLogs: process.env.NODE_ENV === 'development'
});