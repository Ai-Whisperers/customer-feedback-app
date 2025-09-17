#!/usr/bin/env python3
"""
Deployment verification script for Customer Feedback Analyzer v3.1.0
Checks all critical components before deployment.
"""

import os
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, List, Tuple

# Color codes for terminal output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'


class DeploymentVerifier:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.errors = []
        self.warnings = []
        self.successes = []

    def log_success(self, message: str):
        print(f"{GREEN}✓{RESET} {message}")
        self.successes.append(message)

    def log_warning(self, message: str):
        print(f"{YELLOW}⚠{RESET} {message}")
        self.warnings.append(message)

    def log_error(self, message: str):
        print(f"{RED}✗{RESET} {message}")
        self.errors.append(message)

    def check_file_exists(self, filepath: str, description: str) -> bool:
        """Check if a critical file exists."""
        path = self.root_dir / filepath
        if path.exists():
            self.log_success(f"{description}: {filepath}")
            return True
        else:
            self.log_error(f"Missing {description}: {filepath}")
            return False

    def check_render_yaml(self) -> bool:
        """Verify render.yaml configuration."""
        print(f"\n{BOLD}Checking render.yaml configuration...{RESET}")

        render_path = self.root_dir / "render.yaml"
        if not render_path.exists():
            self.log_error("render.yaml not found")
            return False

        try:
            with open(render_path, 'r') as f:
                config = yaml.safe_load(f)

            # Check services
            services = config.get('services', [])
            required_services = ['feedback-analyzer-redis', 'feedback-analyzer-api',
                               'feedback-analyzer-worker', 'feedback-analyzer-web']

            service_names = [s.get('name') for s in services if isinstance(s, dict)]

            for required in required_services:
                if required in service_names:
                    self.log_success(f"Service configured: {required}")
                else:
                    self.log_error(f"Missing service: {required}")

            # Check Redis is keyvalue type
            redis_service = next((s for s in services if s.get('name') == 'feedback-analyzer-redis'), None)
            if redis_service and redis_service.get('type') == 'keyvalue':
                self.log_success("Redis configured as keyvalue service")
            else:
                self.log_error("Redis not properly configured as keyvalue")

            return len(self.errors) == 0

        except Exception as e:
            self.log_error(f"Failed to parse render.yaml: {e}")
            return False

    def check_environment_variables(self) -> bool:
        """Check environment variable configuration."""
        print(f"\n{BOLD}Checking environment variables...{RESET}")

        # Check API config.py
        config_path = self.root_dir / "api" / "app" / "config.py"
        if config_path.exists():
            with open(config_path, 'r') as f:
                content = f.read()

            required_vars = [
                'FILE_MAX_MB',
                'ALLOWED_ORIGINS',
                'SECRET_KEY',
                'PORT',
                'OPENAI_API_KEY',
                'REDIS_URL'
            ]

            for var in required_vars:
                if var in content:
                    self.log_success(f"Config has {var}")
                else:
                    self.log_error(f"Missing {var} in config.py")
        else:
            self.log_error("api/app/config.py not found")

        return len(self.errors) == 0

    def check_dependencies(self) -> bool:
        """Check Python and Node dependencies."""
        print(f"\n{BOLD}Checking dependencies...{RESET}")

        # Check Python requirements
        req_path = self.root_dir / "api" / "requirements.txt"
        if req_path.exists():
            with open(req_path, 'r') as f:
                requirements = f.read()

            critical_packages = [
                'fastapi', 'uvicorn', 'openai', 'celery',
                'redis', 'pandas', 'transformers', 'structlog'
            ]

            for package in critical_packages:
                if package in requirements:
                    self.log_success(f"Python package: {package}")
                else:
                    self.log_error(f"Missing Python package: {package}")
        else:
            self.log_error("api/requirements.txt not found")

        # Check Node packages
        package_paths = [
            self.root_dir / "web" / "package.json",
            self.root_dir / "web" / "client" / "package.json"
        ]

        for package_path in package_paths:
            if package_path.exists():
                with open(package_path, 'r') as f:
                    package = json.load(f)

                deps = {**package.get('dependencies', {}),
                       **package.get('devDependencies', {})}

                if 'express' in deps or 'react' in deps:
                    self.log_success(f"Node packages found in {package_path.relative_to(self.root_dir)}")
            else:
                self.log_warning(f"Package.json not found: {package_path.relative_to(self.root_dir)}")

        return len(self.errors) == 0

    def check_build_scripts(self) -> bool:
        """Verify build scripts exist and are executable."""
        print(f"\n{BOLD}Checking build scripts...{RESET}")

        scripts = [
            ("api/build.sh", "API build script"),
            ("api/start.sh", "API start script"),
            ("api/build-worker.sh", "Worker build script"),
            ("api/start-worker.sh", "Worker start script"),
            ("web/build.sh", "Web build script"),
            ("web/start.sh", "Web start script")
        ]

        for script_path, description in scripts:
            full_path = self.root_dir / script_path
            if full_path.exists():
                with open(full_path, 'r') as f:
                    content = f.read()

                # Check for problematic cd commands
                if 'cd ' in content and 'cd ..' not in content:
                    self.log_warning(f"{description} contains cd commands")
                else:
                    self.log_success(f"{description} exists")

                # Check shebang
                if not content.startswith('#!/'):
                    self.log_warning(f"{description} missing shebang")
            else:
                self.log_error(f"Missing: {script_path}")

        return len(self.errors) == 0

    def check_api_routes(self) -> bool:
        """Verify API routes are properly configured."""
        print(f"\n{BOLD}Checking API routes...{RESET}")

        routes_dir = self.root_dir / "api" / "app" / "routes"
        if not routes_dir.exists():
            self.log_error("API routes directory not found")
            return False

        required_routes = ['health.py', 'upload.py', 'status.py', 'results.py', 'export.py']

        for route in required_routes:
            route_path = routes_dir / route
            if route_path.exists():
                self.log_success(f"Route module: {route}")
            else:
                self.log_error(f"Missing route: {route}")

        return len(self.errors) == 0

    def check_openai_integration(self) -> bool:
        """Verify OpenAI integration with structured outputs."""
        print(f"\n{BOLD}Checking OpenAI integration...{RESET}")

        # Check analyzer
        analyzer_path = self.root_dir / "api" / "app" / "adapters" / "openai" / "analyzer.py"
        if analyzer_path.exists():
            with open(analyzer_path, 'r') as f:
                content = f.read()

            if 'response_format' in content and 'json_schema' in content:
                self.log_success("OpenAI structured outputs configured")
            else:
                self.log_warning("OpenAI may not be using structured outputs")
        else:
            self.log_error("OpenAI analyzer not found")

        # Check schemas
        schema_path = self.root_dir / "api" / "app" / "schemas" / "ai_schemas.py"
        if schema_path.exists():
            self.log_success("AI schemas defined")
        else:
            self.log_error("AI schemas not found")

        return len(self.errors) == 0

    def check_celery_configuration(self) -> bool:
        """Verify Celery worker configuration."""
        print(f"\n{BOLD}Checking Celery configuration...{RESET}")

        celery_path = self.root_dir / "api" / "app" / "workers" / "celery_app.py"
        if celery_path.exists():
            with open(celery_path, 'r') as f:
                content = f.read()

            # Check for Redis Sentinel (should not be present)
            if 'master_name' in content:
                self.log_error("Redis Sentinel configuration still present")
            else:
                self.log_success("Redis Sentinel removed")

            # Check for cleanup task
            if 'cleanup-expired-tasks' in content:
                self.log_success("Cleanup task scheduled")
            else:
                self.log_warning("Cleanup task not scheduled")
        else:
            self.log_error("Celery app configuration not found")

        # Check tasks.py for cleanup implementation
        tasks_path = self.root_dir / "api" / "app" / "workers" / "tasks.py"
        if tasks_path.exists():
            with open(tasks_path, 'r') as f:
                content = f.read()

            if 'def cleanup_expired_tasks' in content:
                self.log_success("Cleanup task implemented")
            else:
                self.log_error("Cleanup task not implemented")
        else:
            self.log_error("Tasks module not found")

        return len(self.errors) == 0

    def check_frontend_build(self) -> bool:
        """Verify frontend build configuration."""
        print(f"\n{BOLD}Checking frontend configuration...{RESET}")

        # Check vite config
        vite_path = self.root_dir / "web" / "client" / "vite.config.ts"
        if vite_path.exists():
            self.log_success("Vite configuration found")
        else:
            self.log_error("Vite configuration missing")

        # Check TypeScript config
        tsconfig_path = self.root_dir / "web" / "client" / "tsconfig.json"
        if tsconfig_path.exists():
            self.log_success("TypeScript configuration found")
        else:
            self.log_error("TypeScript configuration missing")

        # Check BFF server
        server_path = self.root_dir / "web" / "server" / "server.ts"
        if server_path.exists():
            with open(server_path, 'r') as f:
                content = f.read()

            if 'createProxyMiddleware' in content:
                self.log_success("BFF proxy configured")
            else:
                self.log_error("BFF proxy not configured")
        else:
            self.log_error("BFF server not found")

        return len(self.errors) == 0

    def check_security(self) -> bool:
        """Check security configurations."""
        print(f"\n{BOLD}Checking security configurations...{RESET}")

        # Check for CORS removal in API
        main_path = self.root_dir / "api" / "app" / "main.py"
        if main_path.exists():
            with open(main_path, 'r') as f:
                content = f.read()

            if 'CORSMiddleware' not in content:
                self.log_success("CORS removed from API (using BFF pattern)")
            else:
                self.log_warning("CORS still present in API")

        # Check for SECRET_KEY in render.yaml
        render_path = self.root_dir / "render.yaml"
        with open(render_path, 'r') as f:
            content = f.read()

        if 'generateValue: true' in content and 'SECRET_KEY' in content:
            self.log_success("SECRET_KEY auto-generation configured")
        else:
            self.log_error("SECRET_KEY not properly configured")

        return len(self.errors) == 0

    def run_verification(self) -> bool:
        """Run all verification checks."""
        print(f"{BOLD}={'='*60}{RESET}")
        print(f"{BOLD}Customer Feedback Analyzer v3.1.0 - Deployment Verification{RESET}")
        print(f"{BOLD}={'='*60}{RESET}")

        checks = [
            self.check_render_yaml,
            self.check_environment_variables,
            self.check_dependencies,
            self.check_build_scripts,
            self.check_api_routes,
            self.check_openai_integration,
            self.check_celery_configuration,
            self.check_frontend_build,
            self.check_security
        ]

        for check in checks:
            check()

        # Summary
        print(f"\n{BOLD}{'='*60}{RESET}")
        print(f"{BOLD}Verification Summary{RESET}")
        print(f"{BOLD}{'='*60}{RESET}")

        print(f"{GREEN}✓ Successes: {len(self.successes)}{RESET}")
        print(f"{YELLOW}⚠ Warnings: {len(self.warnings)}{RESET}")
        print(f"{RED}✗ Errors: {len(self.errors)}{RESET}")

        if self.errors:
            print(f"\n{RED}{BOLD}DEPLOYMENT NOT READY{RESET}")
            print(f"\n{BOLD}Critical errors that must be fixed:{RESET}")
            for error in self.errors:
                print(f"  {RED}• {error}{RESET}")
        elif self.warnings:
            print(f"\n{YELLOW}{BOLD}DEPLOYMENT READY WITH WARNINGS{RESET}")
            print(f"\n{BOLD}Non-critical warnings to review:{RESET}")
            for warning in self.warnings:
                print(f"  {YELLOW}• {warning}{RESET}")
            print(f"\n{GREEN}System can be deployed but review warnings.{RESET}")
        else:
            print(f"\n{GREEN}{BOLD}DEPLOYMENT READY!{RESET}")
            print(f"{GREEN}All checks passed successfully.{RESET}")

        return len(self.errors) == 0


if __name__ == "__main__":
    verifier = DeploymentVerifier()
    success = verifier.run_verification()

    if not success:
        sys.exit(1)
    else:
        print(f"\n{GREEN}{BOLD}Ready to deploy to Render.com!{RESET}")
        print(f"\nNext steps:")
        print(f"  1. Commit any pending changes")
        print(f"  2. Push to GitHub: git push origin main")
        print(f"  3. Deploy on Render.com dashboard")
        print(f"  4. Set OPENAI_API_KEY in Render environment")
        print(f"  5. Monitor deployment logs")