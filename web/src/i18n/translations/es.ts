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
    title: 'Analizador de Feedback',
    subtitle: 'Sube tu archivo y obtén insights instantáneos',
    upload: {
      title: 'Subir Archivo',
      description: 'Arrastra y suelta tu archivo CSV o XLSX aquí',
      browse: 'o haz clic para seleccionar',
      formats: 'Formatos soportados: .csv, .xlsx, .xls',
      maxSize: 'Tamaño máximo: 20 MB',
      processing: 'Procesando archivo...',
      success: 'Archivo subido exitosamente',
      error: 'Error al subir archivo',
    },
    requirements: {
      title: 'Requisitos del Archivo',
      column1: 'Columna "Nota" (0-10)',
      column2: 'Columna "Comentario Final" (texto)',
      optional: 'Columna "NPS" (opcional)',
    },
    analysis: {
      inProgress: 'Análisis en progreso...',
      processing: 'Procesando {{current}} de {{total}} filas',
      completed: 'Análisis completado',
      failed: 'El análisis falló',
      estimatedTime: 'Tiempo estimado: {{time}}',
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
    title: 'Acerca del Proyecto',
    version: 'Versión',
    description: 'Analizador de Feedback de Clientes impulsado por IA para empresas B2B',
    features: 'Características',
    documentation: 'Documentación',
    support: 'Soporte',
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
