# Render Deployment Settings Guide
## Customer Feedback Analyzer v3.1.0

### Web Service Configuration (customer-feedback-app)

#### Build Settings
- **Build Command**: `cd web && npm install && npm run build:render`
- **Start Command**: `cd web && npm run start:prod`
- **Pre-Deploy Command**: ❌ Not needed (leave empty)
  - Build process handles all compilation
  - No database migrations required
  - Static assets compiled during build

#### Edge Caching
- **Enable Edge Caching**: ✅ YES (Recommended)
- **Reason**: Improves performance significantly
- **Implementation**: Already configured in `web/server/server.ts`
  ```javascript
  // Static assets cached for 1 day
  res.setHeader('Cache-Control', 'public, max-age=86400');
  ```

#### How to Enable Edge Caching in Render Dashboard:
1. Go to your Web Service (customer-feedback-app)
2. Navigate to Settings → Edge Caching
3. Toggle "Enable Edge Caching" to ON
4. Save changes

#### Benefits of Edge Caching:
- Faster load times for static assets (JS, CSS, images)
- Reduced server load
- Better user experience
- Automatic cache invalidation on new deployments

### Cache Headers Configuration (Already Implemented)
The BFF server (`web/server/server.ts`) already includes optimal cache headers:
- **Static Assets** (.js, .css, .png, .jpg, etc.): 1 day cache
- **HTML Files**: No cache (always fresh)
- **API Responses**: Not cached (dynamic content)

### API Service (customer-feedback-api)
- **Pre-Deploy Command**: Not applicable (background service)
- **Edge Caching**: Not applicable (private service)

### Worker Service (celery-worker)
- **Pre-Deploy Command**: Not applicable (background worker)
- **Edge Caching**: Not applicable (background worker)

### Summary
✅ **Edge Caching**: Enable for web service
❌ **Pre-Deploy Command**: Not needed
✅ **Cache Headers**: Already optimized in code

---
Generated: 2025-09-17