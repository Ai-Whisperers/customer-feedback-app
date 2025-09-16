# Project Configuration Files

This directory contains project-wide configuration files.

**Note:** Professional standards - zero emojis throughout the codebase.

## Files in this directory:

- `markdownlint.json` - Markdown linting rules for documentation
- Additional linting and formatting configurations

## Files that must remain in project root:

- `.pre-commit-config.yaml` - Must be in root for pre-commit to work
- `.gitignore` - Git configuration
- `.env.example` - Environment variable template

## Related configuration files:

- `api/.flake8` - Python linting configuration
- `api/pyproject.toml` - Python project configuration
- `web/.eslintrc.js` - JavaScript/TypeScript linting
- `web/tsconfig.json` - TypeScript configuration
- `web/tailwind.config.js` - Tailwind CSS configuration

## Enforcement tools:

- `tools/check-no-emojis.py` - Critical emoji detection script
- `docs/PROJECT_RULES.md` - Central project rules documentation