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
    title: 'Feedback Analyzer',
    subtitle: 'Upload your file and get instant insights',
    upload: {
      title: 'Upload File',
      description: 'Drag and drop your CSV or XLSX file here',
      browse: 'or click to browse',
      formats: 'Supported formats: .csv, .xlsx, .xls',
      maxSize: 'Max size: 20 MB',
      processing: 'Processing file...',
      success: 'File uploaded successfully',
      error: 'Error uploading file',
    },
    requirements: {
      title: 'File Requirements',
      column1: '"Nota" column (0-10)',
      column2: '"Comentario Final" column (text)',
      optional: '"NPS" column (optional)',
    },
    analysis: {
      inProgress: 'Analysis in progress...',
      processing: 'Processing {{current}} of {{total}} rows',
      completed: 'Analysis completed',
      failed: 'Analysis failed',
      estimatedTime: 'Estimated time: {{time}}',
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
      title: 'Emotion Analysis',
      satisfaction: 'Satisfaction',
      frustration: 'Frustration',
      anger: 'Anger',
      trust: 'Trust',
      disappointment: 'Disappointment',
      confusion: 'Confusion',
      anticipation: 'Anticipation',
    },
    painPoints: {
      title: 'Pain Points',
      frequency: 'Frequency',
      impact: 'Impact',
      category: 'Category',
    },
    nps: {
      title: 'NPS Distribution',
      promoters: 'Promoters',
      passives: 'Passives',
      detractors: 'Detractors',
      score: 'Score',
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
    title: 'About the Project',
    version: 'Version',
    description: 'AI-powered Customer Feedback Analyzer for B2B enterprises',
    features: 'Features',
    documentation: 'Documentation',
    support: 'Support',
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
