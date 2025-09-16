module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  extends: [
    'eslint:recommended',
    '@typescript-eslint/recommended',
    'plugin:react-hooks/recommended',
  ],
  ignorePatterns: ['dist', '.eslintrc.js'],
  parser: '@typescript-eslint/parser',
  plugins: ['react-refresh'],
  rules: {
    'react-refresh/only-export-components': [
      'warn',
      { allowConstantExport: true },
    ],
    // CRITICAL: No emojis allowed in any part of the codebase
    'no-irregular-whitespace': 'error',
    'no-emoji': 'error', // Custom rule - will need plugin
  },
  overrides: [
    {
      files: ['**/*.ts', '**/*.tsx', '**/*.js', '**/*.jsx'],
      rules: {
        // Enforce no emoji unicode ranges in strings and comments
        'no-control-regex': 'error',
        'no-emoji-in-code': 'error', // Custom rule
      }
    }
  ]
};