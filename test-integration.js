/**
 * Integration test script to verify web -> api connection
 * Tests the complete flow from web BFF to API backend
 */

const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const path = require('path');

// Configuration
const WEB_URL = process.env.WEB_URL || 'http://localhost:3000';
const API_URL = process.env.API_URL || 'http://localhost:8000';
const USE_PROXY = process.env.USE_PROXY !== 'false'; // Default to true

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m'
};

// Test results storage
const results = {
  passed: [],
  failed: []
};

// Helper functions
function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function logTest(name, passed, details = '') {
  if (passed) {
    log(`  ✓ ${name}`, 'green');
    results.passed.push(name);
  } else {
    log(`  ✗ ${name}`, 'red');
    if (details) log(`    ${details}`, 'yellow');
    results.failed.push(name);
  }
}

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Test Functions
async function testDirectAPIHealth() {
  log('\n📍 Testing Direct API Connection', 'cyan');
  try {
    const response = await axios.get(`${API_URL}/health`);
    logTest('API /health endpoint', response.status === 200);
    logTest('API health response valid', response.data.status === 'healthy');
    return true;
  } catch (error) {
    logTest('API /health endpoint', false, error.message);
    return false;
  }
}

async function testWebBFFHealth() {
  log('\n📍 Testing Web BFF Server', 'cyan');
  try {
    const response = await axios.get(`${WEB_URL}/health`);
    logTest('Web /health endpoint', response.status === 200);
    logTest('Web health response valid', response.data.service === 'web-bff');
    return true;
  } catch (error) {
    logTest('Web /health endpoint', false, error.message);
    return false;
  }
}

async function testProxyToAPI() {
  log('\n📍 Testing Web Proxy to API', 'cyan');
  try {
    const response = await axios.get(`${WEB_URL}/api/health`);
    logTest('Proxy /api/health endpoint', response.status === 200);
    logTest('Proxy forwards to API correctly', response.data.status === 'healthy');
    return true;
  } catch (error) {
    logTest('Proxy /api/health endpoint', false, error.message);
    return false;
  }
}

async function testAPIEndpoints() {
  log('\n📍 Testing API Endpoints', 'cyan');
  const baseUrl = USE_PROXY ? `${WEB_URL}/api` : API_URL;

  // Test root endpoint
  try {
    const response = await axios.get(`${baseUrl}/`);
    logTest('API root endpoint', response.status === 200);
    logTest('API version info', response.data.version === '3.1.0');
  } catch (error) {
    logTest('API root endpoint', false, error.message);
  }

  // Test status endpoint (should return 404 without task_id)
  try {
    await axios.get(`${baseUrl}/status/invalid-task-id`);
    logTest('API /status endpoint', false, 'Should return 404');
  } catch (error) {
    logTest('API /status endpoint', error.response?.status === 404,
            `Expected 404, got ${error.response?.status}`);
  }
}

async function testFileUpload() {
  log('\n📍 Testing File Upload Flow', 'cyan');
  const baseUrl = USE_PROXY ? `${WEB_URL}/api` : API_URL;

  // Create a test CSV file
  const testCSV = `Nota,Comentario Final
10,Excelente servicio y atencion al cliente
8,Buen producto pero la entrega fue lenta
5,Regular experiencia necesita mejorar
3,Mal servicio y producto defectuoso`;

  const testFilePath = path.join(__dirname, 'test-feedback.csv');
  fs.writeFileSync(testFilePath, testCSV);

  try {
    const form = new FormData();
    form.append('file', fs.createReadStream(testFilePath));

    const response = await axios.post(`${baseUrl}/upload`, form, {
      headers: {
        ...form.getHeaders(),
      },
    });

    logTest('File upload endpoint', response.status === 200);
    logTest('Upload returns task_id', !!response.data.task_id);

    if (response.data.task_id) {
      // Test status checking
      await sleep(1000);
      const statusResponse = await axios.get(`${baseUrl}/status/${response.data.task_id}`);
      logTest('Status check endpoint', statusResponse.status === 200);
      logTest('Status returns valid data', !!statusResponse.data.status);
    }

  } catch (error) {
    logTest('File upload endpoint', false, error.message);
  } finally {
    // Clean up test file
    if (fs.existsSync(testFilePath)) {
      fs.unlinkSync(testFilePath);
    }
  }
}

async function testCORSHeaders() {
  log('\n📍 Testing CORS Configuration', 'cyan');

  // Test that API doesn't have CORS (it's private)
  try {
    const response = await axios.options(`${API_URL}/health`, {
      headers: {
        'Origin': 'http://example.com',
        'Access-Control-Request-Method': 'GET'
      }
    });
    logTest('API blocks CORS (private)',
            !response.headers['access-control-allow-origin']);
  } catch (error) {
    logTest('API blocks CORS (private)', true, 'No CORS headers (expected)');
  }

  // Test that web proxy handles requests (no CORS needed)
  try {
    const response = await axios.get(`${WEB_URL}/api/health`);
    logTest('Web proxy handles API calls', response.status === 200);
  } catch (error) {
    logTest('Web proxy handles API calls', false, error.message);
  }
}

async function checkEnvironmentVariables() {
  log('\n📍 Checking Environment Configuration', 'cyan');

  // Check if .env files exist
  const webEnvExists = fs.existsSync(path.join(__dirname, 'web', '.env'));
  const apiEnvExists = fs.existsSync(path.join(__dirname, 'api', '.env'));

  logTest('Web .env file exists', webEnvExists,
          !webEnvExists ? 'Copy web/.env.example to web/.env' : '');
  logTest('API .env file exists', apiEnvExists,
          !apiEnvExists ? 'Copy api/.env.example to api/.env' : '');

  // Check for required variables in environment
  if (process.env.OPENAI_API_KEY) {
    logTest('OPENAI_API_KEY configured', true);
  } else {
    logTest('OPENAI_API_KEY configured', false,
            'Set OPENAI_API_KEY in api/.env');
  }

  if (process.env.REDIS_URL || apiEnvExists) {
    logTest('Redis configuration present', true);
  } else {
    logTest('Redis configuration present', false,
            'Configure REDIS_URL in api/.env');
  }
}

// Main test runner
async function runTests() {
  log('\n========================================', 'blue');
  log('🧪 Customer Feedback App Integration Tests', 'blue');
  log('========================================', 'blue');

  log(`\nConfiguration:`, 'yellow');
  log(`  Web URL: ${WEB_URL}`);
  log(`  API URL: ${API_URL}`);
  log(`  Use Proxy: ${USE_PROXY}`);

  // Run all tests
  await checkEnvironmentVariables();

  const apiHealthy = await testDirectAPIHealth();
  const webHealthy = await testWebBFFHealth();

  if (apiHealthy && webHealthy) {
    await testProxyToAPI();
    await testAPIEndpoints();
    await testFileUpload();
    await testCORSHeaders();
  } else {
    log('\n⚠️  Skipping integration tests - services not healthy', 'yellow');
  }

  // Summary
  log('\n========================================', 'blue');
  log('📊 Test Results Summary', 'blue');
  log('========================================', 'blue');

  log(`\n✅ Passed: ${results.passed.length}`, 'green');
  log(`❌ Failed: ${results.failed.length}`, 'red');

  if (results.failed.length > 0) {
    log('\nFailed tests:', 'red');
    results.failed.forEach(test => log(`  - ${test}`, 'red'));

    log('\n💡 Troubleshooting tips:', 'yellow');
    log('  1. Ensure both services are running:');
    log('     - API: cd api && uvicorn app.main:app --reload');
    log('     - Web: cd web && npm run dev');
    log('  2. Check .env files are configured correctly');
    log('  3. Ensure Redis is running (for Celery tasks)');
    log('  4. Verify OPENAI_API_KEY is set in api/.env');
  } else {
    log('\n🎉 All tests passed! Services are properly connected.', 'green');
  }

  process.exit(results.failed.length > 0 ? 1 : 0);
}

// Run tests
runTests().catch(error => {
  log(`\n❌ Test runner failed: ${error.message}`, 'red');
  process.exit(1);
});