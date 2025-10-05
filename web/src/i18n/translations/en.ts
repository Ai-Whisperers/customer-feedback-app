/**
 * English Translations (en)
 * Customer Feedback Analyzer - B2B Enterprise
 */

export const en = {
  // Common
  common: {
    loading: 'Loading...',
    error: 'Error',
    success: 'Success',
    cancel: 'Cancel',
    confirm: 'Confirm',
    save: 'Save',
    delete: 'Delete',
    edit: 'Edit',
    close: 'Close',
    back: 'Back',
    next: 'Next',
    previous: 'Previous',
    search: 'Search',
    filter: 'Filter',
    export: 'Export',
    import: 'Import',
    download: 'Download',
    upload: 'Upload',
  },

  // Navigation
  nav: {
    home: 'Home',
    analyzer: 'Analyzer',
    results: 'Results',
    about: 'About',
    documentation: 'Documentation',
    settings: 'Settings',
  },

  // Landing Page
  landing: {
    title: 'AI-Powered Customer Feedback Analyzer',
    subtitle: 'Analyze customer feedback with advanced AI',
    description: 'Automatically extract emotions, pain points, churn risk, and NPS',
    cta: {
      getStarted: 'Get Started',
      learnMore: 'Learn More',
      tryDemo: 'Try Demo',
      readyTitle: 'Ready to Get Started?',
      readyDescription: 'Upload your customer feedback data and get instant AI-powered insights',
      startFree: 'Start Free Analysis',
    },
    features: {
      title: 'Features',
      aiPowered: 'AI-Powered Analysis',
      aiPoweredDesc: 'Uses GPT-4 to extract emotions, pain points, and churn risk from comments',
      emotions: 'Emotion Analysis',
      emotionsDesc: 'Detect 7 main emotions in each comment',
      nps: 'NPS Calculation',
      npsDesc: 'Automatically calculate Net Promoter Score',
      painPoints: 'Pain Points',
      painPointsDesc: 'Identify issues and areas for improvement',
    },
    stats: {
      emotions: 'Emotions Analyzed',
      batchSize: 'Comments/Batch',
      processingTime: 'Processing Time',
      languages: 'Languages',
    },
  },

  // Analyzer Page
  analyzer: {
    title: 'AI-Powered Comment Analyzer',
    subtitle: 'Discover valuable insights from your customers through advanced emotion analysis, churn risk, and pain points',
    upload: {
      title: 'Upload File',
      description: 'Drag and drop your CSV or XLSX file here',
      browse: 'or click to browse',
      formats: 'Supported formats: .csv, .xlsx, .xls',
      maxSize: 'Max size: 20 MB',
      uploading: 'Uploading file...',
      processing: 'Processing file...',
      success: 'File uploaded successfully',
      error: 'Error uploading file',
      errorRetry: 'Error uploading file. Please try again.',
    },
    requirements: {
      title: 'File Requirements',
      column1: '"Nota" column (0-10)',
      column2: '"Comentario Final" column (text)',
      optional: '"NPS" column (optional)',
    },
    analysis: {
      inProgress: 'Processing...',
      processing: 'Processing {{current}} of {{total}} rows',
      completed: 'Analysis completed',
      failed: 'Analysis failed. Please check your file and try again.',
      stalled: 'Analysis has stalled. The process may be taking longer than expected. Please try with a smaller file.',
      statusError: 'Error retrieving analysis status.',
      estimatedTime: 'Estimated time: {{time}}',
    },
    actions: {
      analyzeAnother: 'Analyze Another File',
      tryAgain: 'Try Again',
    },
    error: {
      title: 'An Error Occurred',
    },
    footer: {
      poweredBy: 'Powered by OpenAI GPT-4 - Spanish & English Analysis',
    },
  },

  // Results Page
  results: {
    title: 'Analysis Results',
    subtitle: 'AI-generated insights',
    summary: {
      title: 'Summary',
      totalComments: 'Total Comments',
      averageScore: 'Average Score',
      npsScore: 'NPS Score',
      churnRisk: 'Churn Risk',
    },
    emotions: {
      title: 'Emotion Distribution',
      chartTitle: 'Emotion Analysis',
      satisfaction: 'Satisfaction',
      frustration: 'Frustration',
      anger: 'Anger',
      trust: 'Trust',
      disappointment: 'Disappointment',
      confusion: 'Confusion',
      anticipation: 'Anticipation',
    },
    painPoints: {
      title: 'Top Pain Points',
      noData: 'No pain points found in comments',
      frequency: 'Frequency',
      impact: 'Impact',
      category: 'Category',
    },
    nps: {
      title: 'NPS Distribution',
      score: 'NPS Score',
      promoters: 'Promoters',
      passives: 'Passives',
      detractors: 'Detractors',
    },
    churnRisk: {
      title: 'Churn Risk',
      averageRisk: 'Average Risk',
      levels: {
        veryLow: 'Very Low',
        low: 'Low',
        medium: 'Medium',
        high: 'High',
        veryHigh: 'Very High',
      },
    },
    export: {
      title: 'Export Results',
      csv: 'Export CSV',
      xlsx: 'Export Excel',
      pdf: 'Export PDF',
      success: 'Results exported successfully',
      error: 'Error exporting results',
    },
  },

  // Errors
  errors: {
    generic: 'An unexpected error occurred',
    fileUpload: 'Error uploading file',
    fileTooLarge: 'File is too large (max. 20 MB)',
    invalidFormat: 'Invalid file format',
    missingColumns: 'Required columns are missing',
    networkError: 'Connection error. Please try again',
    timeout: 'Request timed out',
    unauthorized: 'Unauthorized',
    forbidden: 'Access denied',
    notFound: 'Not found',
    serverError: 'Server error',
  },

  // Settings
  settings: {
    title: 'Settings',
    appearance: {
      title: 'Appearance',
      theme: 'Theme',
      themeLight: 'Light',
      themeDark: 'Dark',
      themeSystem: 'System',
      language: 'Language',
      languageEs: 'Español',
      languageEn: 'English',
    },
    accessibility: {
      title: 'Accessibility',
      fontSize: 'Font Size',
      highContrast: 'High Contrast',
      animations: 'Animations',
      animationsNone: 'None',
      animationsReduced: 'Reduced',
      animationsNormal: 'Normal',
    },
  },

  // About
  about: {
    title: 'About the Feedback Analyzer',
    subtitle: 'Advanced AI analysis for customer insights',
    version: 'Version',
    description: 'AI-powered Customer Feedback Analyzer for B2B enterprises',
    features: 'Features',
    documentation: 'Documentation',
    support: 'Support',
    overview: {
      title: 'Project Overview',
      paragraph1: 'Customer AI Driven Feedback Analyzer is a cutting-edge application designed to transform customer feedback into actionable business insights using advanced artificial intelligence.',
      paragraph2: 'Our system processes customer feedback in Spanish and English, extracting emotions, identifying pain points, calculating churn risk, and determining NPS scores to help businesses better understand their customers.',
    },
    techStack: {
      title: 'Technical Architecture',
      frontend: 'Frontend Stack',
      backend: 'Backend Stack',
      frontendItems: {
        react: 'React + TypeScript for type-safe development',
        tailwind: 'Tailwind CSS with glassmorphism design',
        plotly: 'Plotly.js for interactive data visualization',
        bff: 'Node.js BFF proxy for API communication',
      },
      backendItems: {
        fastapi: 'FastAPI for high-performance REST APIs',
        celery: 'Celery for distributed task processing',
        redis: 'Redis for caching and message brokering',
        openai: 'OpenAI GPT-4 for intelligent analysis',
      },
    },
    howItWorks: {
      title: 'How It Works',
      step1: {
        title: 'Upload Your Data',
        description: 'Upload CSV or Excel files with customer feedback and ratings. Files must include \'Nota\' (0-10) and \'Comentario Final\' columns.',
      },
      step2: {
        title: 'AI Processing',
        description: 'Our system processes feedback in batches using OpenAI\'s GPT-4, extracting 7 different emotions, identifying pain points, and calculating churn risk scores.',
      },
      step3: {
        title: 'Visualize Insights',
        description: 'View interactive charts showing emotion distributions, NPS breakdowns, churn risk analysis, and pain point frequencies.',
      },
      step4: {
        title: 'Export Results',
        description: 'Download complete analysis results in CSV or Excel format for further processing or integration with your business intelligence tools.',
      },
    },
    performance: {
      title: 'Performance Metrics',
      metric1: '850-1200 rows',
      metric1Desc: '5-10 seconds processing',
      metric2: '1800 rows',
      metric2Desc: '~18 seconds processing',
      metric3: '3000 rows',
      metric3Desc: '~30 seconds processing',
    },
    cta: {
      tryAnalyzer: 'Try the Analyzer',
      backHome: 'Back to Home',
    },
  },

  // Notifications
  notifications: {
    success: 'Operation successful',
    error: 'Operation error',
    warning: 'Warning',
    info: 'Information',
  },
} as const;

// Type for translation keys (same structure as Spanish)
export type TranslationKeys = typeof en;
