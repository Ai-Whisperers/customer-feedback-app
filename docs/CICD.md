# CI/CD Configuration

## GitHub Actions Workflow

The project uses GitHub Actions for automated testing and deployment to Render.

### Dependency Management

**Important:** Dependencies are installed from the root directory, not from individual service directories.

```bash
# Correct approach (used in production and CI/CD)
npm ci  # From root directory
cd web && npm run type-check  # Execute from web/

# Incorrect approach
cd web && npm install  # Would miss root-level dependencies
```

### Workflow Structure

1. **Test Job:**
   - Install Node.js dependencies from root (monorepo workspace)
   - Run frontend type checking and linting from web/
   - Install Python dependencies in api/
   - Run backend tests

2. **Deploy Job:**
   - Triggers on push to main branch
   - Calls Render deployment API

### Service Build Scripts

Each service has its own build scripts that handle the complex dependency structure:

- `web/build.sh` - Navigates to root for dependencies, builds from web/
- `api/build.sh` - Handles Python dependencies
- `render.yaml` - Orchestrates all services in production

### Package Structure

```
/ (root)
├── package.json         # Workspace configuration
├── package-lock.json    # Locked dependencies
├── web/
│   ├── package.json     # Web-specific scripts
│   └── build.sh        # Production build script
└── api/
    ├── requirements.txt # Python dependencies
    └── build.sh        # Production build script
```