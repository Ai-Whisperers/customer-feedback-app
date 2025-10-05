/**
 * Spanish Translations (es)
 * Customer Feedback Analyzer - B2B Enterprise
 */

export const es = {
  // Common
  common: {
    loading: 'Cargando...',
    error: 'Error',
    success: 'Éxito',
    cancel: 'Cancelar',
    confirm: 'Confirmar',
    save: 'Guardar',
    delete: 'Eliminar',
    edit: 'Editar',
    close: 'Cerrar',
    back: 'Volver',
    next: 'Siguiente',
    previous: 'Anterior',
    search: 'Buscar',
    filter: 'Filtrar',
    export: 'Exportar',
    import: 'Importar',
    download: 'Descargar',
    upload: 'Subir',
  },

  // Navigation
  nav: {
    home: 'Inicio',
    analyzer: 'Analizador',
    results: 'Resultados',
    about: 'Acerca de',
    documentation: 'Documentación',
    settings: 'Configuración',
  },

  // Landing Page
  landing: {
    title: 'Analizador de Feedback de Clientes con IA',
    subtitle: 'Analiza comentarios de clientes con IA avanzada',
    description: 'Extrae emociones, puntos de dolor, riesgo de abandono y NPS de manera automática',
    cta: {
      getStarted: 'Comenzar Análisis',
      learnMore: 'Saber Más',
      tryDemo: 'Probar Demo',
      readyTitle: '¿Listo para Comenzar?',
      readyDescription: 'Carga tus datos de comentarios de clientes y obtén insights instantáneos con IA',
      startFree: 'Iniciar Análisis Gratuito',
    },
    features: {
      title: 'Características',
      aiPowered: 'Análisis con IA',
      aiPoweredDesc: 'Usa GPT-4 para extraer emociones, puntos de dolor y riesgo de abandono de los comentarios',
      emotions: 'Análisis de Emociones',
      emotionsDesc: 'Detecta 7 emociones principales en cada comentario',
      nps: 'Cálculo NPS',
      npsDesc: 'Calcula automáticamente el Net Promoter Score',
      painPoints: 'Puntos de Dolor',
      painPointsDesc: 'Identifica problemas y áreas de mejora',
    },
    stats: {
      emotions: 'Emociones Analizadas',
      batchSize: 'Comentarios/Lote',
      processingTime: 'Tiempo de Procesamiento',
      languages: 'Idiomas',
    },
  },

  // Analyzer Page
  analyzer: {
    title: 'Analizador de Comentarios con IA',
    subtitle: 'Descubre insights valiosos de tus clientes mediante análisis avanzado de emociones, riesgo de abandono y puntos de dolor',
    upload: {
      title: 'Subir Archivo',
      description: 'Arrastra y suelta tu archivo CSV o XLSX aquí',
      browse: 'o haz clic para seleccionar',
      formats: 'Formatos soportados: .csv, .xlsx, .xls',
      maxSize: 'Tamaño máximo: 20 MB',
      uploading: 'Cargando archivo...',
      processing: 'Procesando archivo...',
      success: 'Archivo subido exitosamente',
      error: 'Error al subir archivo',
      errorRetry: 'Error al cargar el archivo. Por favor, intente nuevamente.',
    },
    requirements: {
      title: 'Requisitos del Archivo',
      column1: 'Columna "Nota" (0-10)',
      column2: 'Columna "Comentario Final" (texto)',
      optional: 'Columna "NPS" (opcional)',
    },
    analysis: {
      inProgress: 'Procesando...',
      processing: 'Procesando {{current}} de {{total}} filas',
      completed: 'Análisis completado',
      failed: 'El análisis falló. Por favor, verifique su archivo e intente nuevamente.',
      stalled: 'El análisis se ha detenido. El proceso puede estar tardando más de lo esperado. Por favor, intente con un archivo más pequeño.',
      statusError: 'Error al obtener el estado del análisis.',
      estimatedTime: 'Tiempo estimado: {{time}}',
    },
    actions: {
      analyzeAnother: 'Analizar Otro Archivo',
      tryAgain: 'Intentar Nuevamente',
    },
    error: {
      title: 'Ocurrió un Error',
    },
    footer: {
      poweredBy: 'Powered by OpenAI GPT-4 - Análisis en Español e Inglés',
    },
  },

  // Results Page
  results: {
    title: 'Resultados del Análisis',
    subtitle: 'Insights generados por IA',
    summary: {
      title: 'Resumen',
      totalComments: 'Total de Comentarios',
      averageScore: 'Puntuación Promedio',
      npsScore: 'Puntuación NPS',
      churnRisk: 'Riesgo de Abandono',
    },
    emotions: {
      title: 'Análisis de Emociones',
      satisfaction: 'Satisfacción',
      frustration: 'Frustración',
      anger: 'Enojo',
      trust: 'Confianza',
      disappointment: 'Decepción',
      confusion: 'Confusión',
      anticipation: 'Anticipación',
    },
    painPoints: {
      title: 'Puntos de Dolor',
      frequency: 'Frecuencia',
      impact: 'Impacto',
      category: 'Categoría',
    },
    nps: {
      title: 'Distribución NPS',
      promoters: 'Promotores',
      passives: 'Pasivos',
      detractors: 'Detractores',
      score: 'Puntuación',
    },
    export: {
      title: 'Exportar Resultados',
      csv: 'Exportar CSV',
      xlsx: 'Exportar Excel',
      pdf: 'Exportar PDF',
      success: 'Resultados exportados exitosamente',
      error: 'Error al exportar resultados',
    },
  },

  // Errors
  errors: {
    generic: 'Ocurrió un error inesperado',
    fileUpload: 'Error al subir el archivo',
    fileTooLarge: 'El archivo es demasiado grande (máx. 20 MB)',
    invalidFormat: 'Formato de archivo no válido',
    missingColumns: 'Faltan columnas requeridas',
    networkError: 'Error de conexión. Por favor, intenta de nuevo',
    timeout: 'La solicitud excedió el tiempo límite',
    unauthorized: 'No autorizado',
    forbidden: 'Acceso denegado',
    notFound: 'No encontrado',
    serverError: 'Error del servidor',
  },

  // Settings
  settings: {
    title: 'Configuración',
    appearance: {
      title: 'Apariencia',
      theme: 'Tema',
      themeLight: 'Claro',
      themeDark: 'Oscuro',
      themeSystem: 'Sistema',
      language: 'Idioma',
      languageEs: 'Español',
      languageEn: 'English',
    },
    accessibility: {
      title: 'Accesibilidad',
      fontSize: 'Tamaño de Fuente',
      highContrast: 'Alto Contraste',
      animations: 'Animaciones',
      animationsNone: 'Ninguna',
      animationsReduced: 'Reducidas',
      animationsNormal: 'Normales',
    },
  },

  // About
  about: {
    title: 'Acerca del Analizador de Comentarios',
    subtitle: 'Análisis avanzado con IA para insights de clientes',
    version: 'Versión',
    description: 'Analizador de Feedback de Clientes impulsado por IA para empresas B2B',
    features: 'Características',
    documentation: 'Documentación',
    support: 'Soporte',
    overview: {
      title: 'Descripción del Proyecto',
      paragraph1: 'Customer AI Driven Feedback Analyzer es una aplicación de vanguardia diseñada para transformar comentarios de clientes en insights de negocio accionables usando inteligencia artificial avanzada.',
      paragraph2: 'Nuestro sistema procesa comentarios de clientes en español e inglés, extrayendo emociones, identificando puntos de dolor, calculando riesgo de abandono y determinando puntajes NPS para ayudar a las empresas a entender mejor a sus clientes.',
    },
    techStack: {
      title: 'Arquitectura Técnica',
      frontend: 'Stack Frontend',
      backend: 'Stack Backend',
      frontendItems: {
        react: 'React + TypeScript para desarrollo seguro',
        tailwind: 'Tailwind CSS con diseño glassmorphism',
        plotly: 'Plotly.js para visualización interactiva de datos',
        bff: 'Node.js BFF proxy para comunicación con API',
      },
      backendItems: {
        fastapi: 'FastAPI para APIs REST de alto rendimiento',
        celery: 'Celery para procesamiento distribuido de tareas',
        redis: 'Redis para caché y message brokering',
        openai: 'OpenAI GPT-4 para análisis inteligente',
      },
    },
    howItWorks: {
      title: 'Cómo Funciona',
      step1: {
        title: 'Carga tus Datos',
        description: 'Carga archivos CSV o Excel con comentarios de clientes y calificaciones. Los archivos deben incluir columnas \'Nota\' (0-10) y \'Comentario Final\'.',
      },
      step2: {
        title: 'Procesamiento con IA',
        description: 'Nuestro sistema procesa comentarios en lotes usando GPT-4 de OpenAI, extrayendo 7 emociones diferentes, identificando puntos de dolor y calculando puntajes de riesgo de abandono.',
      },
      step3: {
        title: 'Visualizar Insights',
        description: 'Ve gráficos interactivos mostrando distribuciones de emociones, desgloses de NPS, análisis de riesgo de abandono y frecuencias de puntos de dolor.',
      },
      step4: {
        title: 'Exportar Resultados',
        description: 'Descarga resultados completos del análisis en formato CSV o Excel para procesamiento adicional o integración con tus herramientas de inteligencia de negocio.',
      },
    },
    performance: {
      title: 'Métricas de Rendimiento',
      metric1: '850-1200 filas',
      metric1Desc: '5-10 segundos de procesamiento',
      metric2: '1800 filas',
      metric2Desc: '~18 segundos de procesamiento',
      metric3: '3000 filas',
      metric3Desc: '~30 segundos de procesamiento',
    },
    cta: {
      tryAnalyzer: 'Probar el Analizador',
      backHome: 'Volver al Inicio',
    },
  },

  // Notifications
  notifications: {
    success: 'Operación exitosa',
    error: 'Error en la operación',
    warning: 'Advertencia',
    info: 'Información',
  },
} as const;

// Type for translation keys (dot notation)
export type TranslationKeys = typeof es;
