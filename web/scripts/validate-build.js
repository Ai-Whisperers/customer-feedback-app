#!/usr/bin/env node

/**
 * Build Validation Script
 * Ensures the build output is complete and valid before deployment
 */

const fs = require('fs');
const path = require('path');

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m'
};

// Configuration
const BUILD_DIR = path.join(__dirname, '../dist/client-build');
const REQUIRED_FILES = [
  'index.html',
  'about.html',
  'analyzer.html',
  'vite.svg'
];

const REQUIRED_PATTERNS = [
  { pattern: /assets\/main-.*\.js/, description: 'Main entry bundle' },
  { pattern: /assets\/about-.*\.js/, description: 'About page bundle' },
  { pattern: /assets\/analyzer-.*\.js/, description: 'Analyzer page bundle' },
  { pattern: /assets\/(vendor-react|react-vendor|react-dom)-.*\.js/, description: 'React vendor bundle' },
  { pattern: /assets\/(ErrorBoundary|bootstrap)-.*\.css/, description: 'Application styles' }
];

const MAX_FILE_SIZES = {
  'index.html': 5 * 1024, // 5KB max for HTML files
  'about.html': 5 * 1024,
  'analyzer.html': 5 * 1024,
  'plotly-core': 5 * 1024 * 1024 // 5MB max for plotly
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function validateFileExists(filePath) {
  return fs.existsSync(filePath);
}

function validateFileSize(filePath, maxSize) {
  const stats = fs.statSync(filePath);
  return stats.size <= maxSize;
}

function validateNoModulePreload(htmlFile) {
  const content = fs.readFileSync(htmlFile, 'utf8');
  const hasPlotlyPreload = content.includes('modulepreload') && content.includes('plotly');
  return !hasPlotlyPreload;
}

function getFilesInDir(dir) {
  try {
    const files = [];
    const items = fs.readdirSync(dir, { withFileTypes: true });

    for (const item of items) {
      if (item.isDirectory()) {
        files.push(...getFilesInDir(path.join(dir, item.name)));
      } else {
        files.push(path.join(dir, item.name));
      }
    }

    return files;
  } catch (error) {
    return [];
  }
}

function validateBuild() {
  log('\n🔍 Starting build validation...', 'blue');

  let errors = 0;
  let warnings = 0;

  // Check if build directory exists
  if (!fs.existsSync(BUILD_DIR)) {
    log(`❌ Build directory not found: ${BUILD_DIR}`, 'red');
    return false;
  }

  log(`✅ Build directory found: ${BUILD_DIR}`, 'green');

  // Check required files
  log('\n📋 Checking required files...', 'blue');
  for (const file of REQUIRED_FILES) {
    const filePath = path.join(BUILD_DIR, file);
    if (validateFileExists(filePath)) {
      log(`  ✅ ${file}`, 'green');

      // Check file size if applicable
      if (MAX_FILE_SIZES[file]) {
        if (!validateFileSize(filePath, MAX_FILE_SIZES[file])) {
          log(`  ⚠️  ${file} exceeds maximum size`, 'yellow');
          warnings++;
        }
      }

      // Check for modulepreload in HTML files
      if (file.endsWith('.html')) {
        if (validateNoModulePreload(filePath)) {
          log(`    ✅ No plotly modulepreload found`, 'green');
        } else {
          log(`    ❌ Contains plotly modulepreload!`, 'red');
          errors++;
        }
      }
    } else {
      log(`  ❌ ${file} - NOT FOUND`, 'red');
      errors++;
    }
  }

  // Check required patterns
  log('\n📦 Checking bundled assets...', 'blue');
  const allFiles = getFilesInDir(BUILD_DIR);
  const fileNames = allFiles.map(f => path.relative(BUILD_DIR, f).replace(/\\/g, '/'));

  for (const { pattern, description } of REQUIRED_PATTERNS) {
    const found = fileNames.some(file => pattern.test(file));
    if (found) {
      log(`  ✅ ${description}`, 'green');
    } else {
      log(`  ❌ ${description} - NOT FOUND`, 'red');
      errors++;
    }
  }

  // Check for plotly bundle size
  const plotlyFile = fileNames.find(f => f.includes('plotly-core'));
  if (plotlyFile) {
    const plotlyPath = path.join(BUILD_DIR, plotlyFile);
    const stats = fs.statSync(plotlyPath);
    const sizeMB = (stats.size / (1024 * 1024)).toFixed(2);

    if (stats.size > MAX_FILE_SIZES['plotly-core']) {
      log(`  ⚠️  Plotly bundle is ${sizeMB}MB (exceeds 5MB limit)`, 'yellow');
      warnings++;
    } else {
      log(`  ✅ Plotly bundle size: ${sizeMB}MB`, 'green');
    }
  }

  // Summary
  log('\n📊 Validation Summary', 'blue');
  log('━━━━━━━━━━━━━━━━━━━━', 'blue');

  if (errors === 0 && warnings === 0) {
    log('✅ Build validation PASSED!', 'green');
    log('All checks completed successfully.\n', 'green');
    return true;
  } else if (errors === 0) {
    log(`⚠️  Build validation PASSED with ${warnings} warning(s)`, 'yellow');
    log('Build is valid but has some issues that should be reviewed.\n', 'yellow');
    return true;
  } else {
    log(`❌ Build validation FAILED!`, 'red');
    log(`Found ${errors} error(s) and ${warnings} warning(s)\n`, 'red');
    return false;
  }
}

// Run validation
const isValid = validateBuild();
process.exit(isValid ? 0 : 1);