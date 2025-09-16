# PROJECT RULES - CUSTOMER FEEDBACK ANALYZER

## CRITICAL RULES (NEVER TO BE BROKEN)

### RULE #1: ZERO EMOJIS POLICY

**STATUS: ENFORCED BY AUTOMATION**

- **NO EMOJIS ALLOWED** anywhere in the codebase
- This includes: code files, documentation, comments, strings, commit messages
- **Enforcement mechanisms:**
  - Pre-commit hooks (`.pre-commit-config.yaml`)
  - Python flake8 configuration (`.flake8`)
  - TypeScript ESLint rules (`.eslintrc.js`)
  - Custom checker script (`tools/check-no-emojis.py`)
  - Automated CI checks

**Rationale:**
- Professional code standards
- Cross-platform compatibility
- Clear communication without ambiguity
- Consistent project aesthetics
- Accessibility for all developers

**Alternatives to emojis:**
- Use descriptive text: "ERROR:" instead of cross marks
- Use icons from icon libraries in UI
- Use markdown formatting: `**CRITICAL**` instead of warning symbols
- Use clear status indicators: "PASSED" instead of check marks

### RULE #2: Architecture Constraints

- Entry points ≤ 150 lines of code
- Individual files ≤ 250 lines of code
- Anti-overengineering principle
- Modular and predictable design

### RULE #3: Language Policy

- **Code comments and logs:** Always in English
- **Public documentation:** Spanish
- **Internal documentation:** English
- **Error messages:** Spanish (user-facing)

### RULE #4: No User State

- No user accounts or authentication
- Tasks identified by UUID only
- Results expire automatically (24h TTL)
- Stateless architecture

## DEVELOPMENT STANDARDS

### Code Quality

```bash
# These commands MUST pass before any commit
python tools/check-no-emojis.py --check-all  # CRITICAL
pre-commit run --all-files
cd api && black . && flake8 . && mypy .
cd web && npm run lint && npm run type-check
```

### File Organization

```
- api/              # Python backend (FastAPI + Celery)
- web/              # TypeScript frontend (React + BFF)
- docs/             # Public documentation (Spanish)
- local-reports/    # Internal docs (English)
- tools/            # Project automation scripts
```

### Naming Conventions

- **Files:** snake_case for Python, kebab-case for configs, PascalCase for React components
- **Variables:** camelCase in TypeScript, snake_case in Python
- **Constants:** UPPER_SNAKE_CASE
- **Classes:** PascalCase

### Git Workflow

- **Branch naming:** `feature/description`, `fix/issue-description`, `docs/update-topic`
- **Commit messages:** Descriptive, no emojis, English
- **PR requirements:** All checks must pass, including emoji validation

## TECHNOLOGY CONSTRAINTS

### Dependencies

- **Python:** >=3.11, FastAPI, Celery, OpenAI SDK
- **Node.js:** >=18, React 18, TypeScript, Tailwind CSS
- **External:** Redis, OpenAI API (gpt-4o-mini)

### Performance Requirements

- **File upload:** Max 20MB
- **Processing time:** <10s for 1200 comments
- **Concurrent tasks:** Max 10 per instance
- **Memory usage:** <500MB per task

### Security Requirements

- No CORS (BFF proxy pattern)
- Validate file types and sizes
- No secrets in code
- TTL-based cleanup
- No PII logging

## MONITORING & COMPLIANCE

### Automated Checks

1. **Emoji Policy Enforcement** (CRITICAL)
   - Pre-commit hook runs `check-no-emojis.py`
   - CI pipeline validates all files
   - Blocks any emoji introduction

2. **Code Quality**
   - Python: black, flake8, mypy
   - TypeScript: ESLint, TypeScript compiler
   - Documentation: markdownlint

3. **Security**
   - detect-secrets for credential scanning
   - Dependency vulnerability scanning

### Manual Reviews

- Architecture decisions documented
- Performance impact assessed
- Security implications evaluated
- Documentation updated

## EMERGENCY PROCEDURES

### Rule Violation Response

1. **Emoji Detection:**
   - IMMEDIATE: Block commit/PR
   - Run: `python tools/check-no-emojis.py --check-all`
   - Remove all detected emojis
   - Use text alternatives

2. **Performance Degradation:**
   - Check OpenAI rate limits
   - Review batch sizes
   - Monitor Redis memory usage

3. **Security Issues:**
   - Rotate API keys immediately
   - Review logs for data exposure
   - Update security configurations

## CONTACT & ESCALATION

For questions about project rules:
1. Check this document first
2. Review configuration files
3. Run automated validators
4. Consult project architecture documentation

**Remember: These rules exist to maintain code quality, security, and professional standards. They are enforced automatically and should never be bypassed.**