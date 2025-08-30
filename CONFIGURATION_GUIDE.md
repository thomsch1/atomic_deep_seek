# Configuration Guide

This comprehensive guide provides exact templates and configurations for all setup files, environment variables, build tools, and infrastructure components needed to recreate the AI-powered web research application.

## 🏗️ Project Structure Configuration

### Root Directory Files

#### `.gitignore`
**Purpose**: Git ignore patterns for both backend and frontend  
**Template**:
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
lerna-debug.log*
.pnpm-debug.log*

# Runtime data
pids/
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/
*.lcov
.nyc_output/

# ESLint cache
.eslintcache

# Microbundle cache
.rpt2_cache/
.rts2_cache_cjs/
.rts2_cache_es/
.rts2_cache_umd/

# Optional npm cache directory
.npm

# Optional REPL history
.node_repl_history

# Output of 'npm pack'
*.tgz

# Yarn Integrity file
.yarn-integrity

# dotenv environment variables file
.env.test
.env.production

# parcel-bundler cache (https://parceljs.org/)
.cache
.parcel-cache

# Next.js build output
.next
out

# Nuxt.js build / generate output
.nuxt
dist

# Vite build output
dist/
dist-ssr/
*.local

# Rollup build output
build/

# Storybook build outputs
.out
.storybook-out

# Temporary folders
tmp/
temp/

# Editor directories and files
.idea/
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?

# Database
*.db
*.sqlite
*.sqlite3

# Docker
.dockerignore

# AI/ML
models/
*.pkl
*.model
*.h5
*.weights

# Research data (if any)
data/
research_cache/
search_results/
```

#### `README.md` (Project Root)
**Purpose**: Main project documentation  
**Template**: *(Already exists - see existing README.md)*

#### `requirements.txt` (Project Root)
**Purpose**: Top-level Python requirements for easy setup  
**Template**:
```txt
# Main project requirements
-e ./backend

# Optional: Direct dependencies for quick reference
atomic-agents>=1.0.24
instructor>=1.3.7
google-genai>=0.1.0
python-dotenv>=1.0.1
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.0.0
httpx>=0.25.0
jsonref>=1.1.0

# Development dependencies (optional)
pytest>=8.3.5
pytest-asyncio>=0.23.0
pytest-mock>=3.12.0
mypy>=1.11.1
ruff>=0.6.1
```

## 🐍 Backend Configuration

### Python Project Configuration

#### `backend/pyproject.toml`
**Purpose**: Complete Python project configuration with all tools  
**Template**:
```toml
[project]
name = "agent"
version = "0.0.1"
description = "Backend for the Atomic Agent research system"
authors = [
    { name = "Philipp Schmid", email = "schmidphilipp1995@gmail.com" },
]
readme = "README.md"
license = { text = "MIT" }
requires-python = ">=3.11,<4.0"
keywords = ["ai", "research", "agents", "fastapi", "gemini"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
]

dependencies = [
    # Core AI Agent Framework
    "atomic-agents>=1.0.24",           # Agent orchestration
    
    # AI/ML Libraries
    "instructor>=1.3.7",               # Structured LLM outputs
    "google-genai>=0.1.0",            # Google Gemini API
    
    # Web Framework
    "fastapi>=0.104.0",               # Modern web framework
    "uvicorn[standard]>=0.24.0",      # ASGI server
    
    # Data & Validation
    "pydantic>=2.0.0",                # Data validation
    "httpx>=0.25.0",                  # HTTP client
    "python-dotenv>=1.0.1",           # Environment variables
    "jsonref>=1.1.0",                 # JSON references
    
    # Search Providers (optional)
    "duckduckgo-search>=6.3.0",      # DuckDuckGo search
    "googlesearch-python>=1.2.4",    # Google search (backup)
    
    # Utilities
    "beautifulsoup4>=4.12.0",        # HTML parsing
    "requests>=2.31.0",              # HTTP requests (fallback)
    "lxml>=4.9.0",                   # XML/HTML parsing
]

[project.optional-dependencies]
# Development dependencies
dev = [
    "mypy>=1.11.1",                   # Static type checking
    "ruff>=0.6.1",                    # Linting and formatting
    "black>=24.0.0",                  # Code formatting (backup)
    "isort>=5.13.0",                  # Import sorting (backup)
]

# Testing dependencies
test = [
    "pytest>=8.3.5",                 # Testing framework
    "pytest-asyncio>=0.23.0",        # Async testing
    "pytest-mock>=3.12.0",           # Mocking utilities
    "pytest-cov>=6.0.0",             # Coverage reporting
    "httpx-mock>=0.12.0",            # HTTP client mocking
    "respx>=0.21.1",                 # HTTP request mocking
]

# Production dependencies
prod = [
    "gunicorn>=22.0.0",              # WSGI server (if needed)
    "prometheus-client>=0.20.0",     # Metrics (optional)
]

# All dependencies
all = ["agent[dev,test,prod]"]

[project.urls]
Homepage = "https://github.com/your-username/atomic-deep-seek"
Repository = "https://github.com/your-username/atomic-deep-seek.git"
Documentation = "https://github.com/your-username/atomic-deep-seek/docs"
Issues = "https://github.com/your-username/atomic-deep-seek/issues"

[build-system]
requires = ["setuptools>=73.0.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
"*" = ["*.txt", "*.md", "*.yml", "*.yaml"]

# Ruff configuration (linting and formatting)
[tool.ruff]
target-version = "py311"
line-length = 100
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # pyflakes
    "I",      # isort
    "D",      # pydocstyle
    "D401",   # First line should be in imperative mood
    "T201",   # print statements (avoid in production)
    "UP",     # pyupgrade
    "N",      # pep8-naming
    "C90",    # mccabe complexity
    "B",      # flake8-bugbear
    "S",      # flake8-bandit (security)
    "A",      # flake8-builtins
    "COM",    # flake8-commas
    "PT",     # flake8-pytest-style
]

ignore = [
    "UP006",  # Use `list` instead of `List` for type annotations
    "UP007",  # Use `X | Y` instead of `Union[X, Y]`
    "UP035",  # Import from `typing_extensions`
    "D417",   # Missing argument descriptions in the docstring
    "E501",   # Line too long (handled by formatter)
    "S101",   # Use of assert detected
    "B008",   # Do not perform function calls in argument defaults
    "D100",   # Missing docstring in public module
    "D104",   # Missing docstring in public package
]

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["D", "UP", "S", "PT011"]  # Relax rules for tests
"examples/*" = ["D", "T201"]           # Allow prints in examples
"scripts/*" = ["T201"]                 # Allow prints in scripts

[tool.ruff.lint.pydocstyle]
convention = "google"

[tool.ruff.lint.isort]
known-first-party = ["agent"]
split-on-trailing-comma = true
combine-as-imports = true

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-string-normalization = false
line-ending = "auto"

# MyPy configuration (type checking)
[tool.mypy]
python_version = "3.11"
check_untyped_defs = true
disallow_any_generics = true
disallow_untyped_calls = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_return_any = true
warn_unreachable = true
strict_equality = true

[[tool.mypy.overrides]]
module = [
    "atomic_agents.*",
    "google.genai.*",
    "instructor.*",
    "duckduckgo_search.*",
]
ignore_missing_imports = true

# Pytest configuration
[tool.pytest.ini_options]
minversion = "8.0"
addopts = [
    "-ra",
    "--strict-markers",
    "--disable-warnings",
    "--tb=short",
    "-v",
]
testpaths = ["tests", "src/agent/test"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
    "api: marks tests that require API keys",
]
asyncio_mode = "auto"

# Coverage configuration
[tool.coverage.run]
source = ["src/agent"]
omit = [
    "*/test*",
    "*/tests/*",
    "*/__pycache__/*",
    "*/venv/*",
    "*/env/*",
]

[tool.coverage.report]
show_missing = true
skip_covered = false
fail_under = 70  # Minimum coverage percentage

[tool.coverage.html]
directory = "htmlcov"

# Dependency groups (alternative to optional-dependencies)
[dependency-groups]
dev = [
    "pytest>=8.3.5",
    "pytest-asyncio>=0.23.0", 
    "pytest-mock>=3.12.0",
    "pytest-cov>=6.0.0",
    "mypy>=1.11.1",
    "ruff>=0.6.1",
    "httpx-mock>=0.12.0",
    "respx>=0.21.1",
]
```

### Environment Configuration

#### `backend/.env` (Template)
**Purpose**: Environment variables for all configurations  
**Template**:
```bash
# =============================================================================
# AI Research Backend Configuration
# =============================================================================

# -----------------------------------------------------------------------------
# REQUIRED: AI Model Configuration
# -----------------------------------------------------------------------------
GEMINI_API_KEY=your_gemini_api_key_here

# -----------------------------------------------------------------------------
# OPTIONAL: AI Observability and Monitoring
# -----------------------------------------------------------------------------
LANGSMITH_API_KEY=your_langsmith_key_for_tracing
LANGSMITH_PROJECT=atomic-research-agent
LANGSMITH_ENDPOINT=https://api.smith.langchain.com

# -----------------------------------------------------------------------------
# SEARCH PROVIDER CONFIGURATION (Optional but Recommended)
# -----------------------------------------------------------------------------

# Google Custom Search (Primary)
GOOGLE_CSE_ID=your_custom_search_engine_id
GOOGLE_API_KEY=your_google_api_key

# SearchAPI.io (Commercial Alternative)
SEARCHAPI_KEY=your_searchapi_io_key

# DuckDuckGo (No key required - privacy focused)
# DUCKDUCKGO_API_KEY=optional_if_available

# Bing Search (Microsoft)
BING_SEARCH_KEY=your_bing_search_key

# -----------------------------------------------------------------------------
# SERVER CONFIGURATION
# -----------------------------------------------------------------------------
SERVER_HOST=localhost
SERVER_PORT=2024
SERVER_WORKERS=1

# Python Path (for imports)
PYTHONPATH=./backend/src

# -----------------------------------------------------------------------------
# DEVELOPMENT SETTINGS
# -----------------------------------------------------------------------------
NODE_ENV=development
DEBUG=true
LOG_LEVEL=INFO

# Hot reloading
AUTO_RELOAD=true
RELOAD_DIRS=./src

# -----------------------------------------------------------------------------
# RESEARCH CONFIGURATION
# -----------------------------------------------------------------------------

# Default Research Parameters
DEFAULT_INITIAL_QUERIES=3
DEFAULT_MAX_LOOPS=2
DEFAULT_QUALITY_THRESHOLD=0.5

# Search Configuration
SEARCH_TIMEOUT=30
MAX_SOURCES_PER_QUERY=20
SEARCH_RETRY_COUNT=3

# AI Model Configuration
DEFAULT_REASONING_MODEL=gemini-1.5-flash
TEMPERATURE=0.1
MAX_TOKENS=4096

# -----------------------------------------------------------------------------
# CACHING CONFIGURATION
# -----------------------------------------------------------------------------
ENABLE_CACHING=true
CACHE_TTL=3600
CACHE_TYPE=memory  # memory, redis, file

# Redis Configuration (if using Redis cache)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# -----------------------------------------------------------------------------
# DATABASE CONFIGURATION (for production)
# -----------------------------------------------------------------------------
DATABASE_URL=postgresql://user:password@localhost:5432/research_db
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10

# -----------------------------------------------------------------------------
# SECURITY CONFIGURATION
# -----------------------------------------------------------------------------
SECRET_KEY=your_secret_key_here_change_in_production
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
ALLOWED_HOSTS=localhost,127.0.0.1

# Rate limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=100

# -----------------------------------------------------------------------------
# LOGGING CONFIGURATION
# -----------------------------------------------------------------------------
LOG_FORMAT=json  # json, text
LOG_FILE=./logs/research.log
LOG_ROTATION=daily
LOG_RETENTION_DAYS=30

# Disable specific logs in development
DISABLE_UVICORN_LOGS=false
DISABLE_HTTPX_LOGS=true

# -----------------------------------------------------------------------------
# PERFORMANCE OPTIMIZATION
# -----------------------------------------------------------------------------
THREAD_POOL_SIZE=10
HTTP_CLIENT_TIMEOUT=30
HTTP_CLIENT_RETRIES=3

# Memory limits
MAX_MEMORY_MB=2048
GC_THRESHOLD=100

# -----------------------------------------------------------------------------
# FEATURE FLAGS
# -----------------------------------------------------------------------------
ENABLE_PERFORMANCE_PROFILING=true
ENABLE_DETAILED_LOGGING=false
ENABLE_METRICS=false
ENABLE_HEALTH_CHECKS=true

# -----------------------------------------------------------------------------
# EXTERNAL SERVICES
# -----------------------------------------------------------------------------

# Webhook URLs (optional)
WEBHOOK_URL_SUCCESS=
WEBHOOK_URL_ERROR=

# Email notifications (optional)
SMTP_HOST=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
EMAIL_FROM=noreply@yourdomain.com
EMAIL_TO=admin@yourdomain.com

# -----------------------------------------------------------------------------
# DEVELOPMENT TOOLS
# -----------------------------------------------------------------------------

# FastAPI Configuration
FASTAPI_DEBUG=true
FASTAPI_DOCS_URL=/docs
FASTAPI_REDOC_URL=/redoc
FASTAPI_OPENAPI_URL=/openapi.json

# Testing Configuration
TEST_DATABASE_URL=sqlite:///test.db
TEST_TIMEOUT=30

# -----------------------------------------------------------------------------
# PRODUCTION OVERRIDES
# -----------------------------------------------------------------------------
# Uncomment and modify for production deployment

# NODE_ENV=production
# DEBUG=false
# LOG_LEVEL=WARNING
# AUTO_RELOAD=false
# RATE_LIMIT_REQUESTS_PER_MINUTE=1000
# CORS_ORIGINS=https://yourdomain.com
# ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com
```

#### `backend/.env.example`
**Purpose**: Template for users to copy and configure  
**Template**:
```bash
# Copy this file to .env and configure your settings

# REQUIRED: Get your Gemini API key from https://ai.google.dev/
GEMINI_API_KEY=your_gemini_api_key_here

# OPTIONAL: For AI observability (https://smith.langchain.com/)
LANGSMITH_API_KEY=your_langsmith_key_for_tracing

# OPTIONAL: Search providers for better results
GOOGLE_CSE_ID=your_custom_search_engine_id
GOOGLE_API_KEY=your_google_api_key
SEARCHAPI_KEY=your_searchapi_io_key

# Server Configuration (defaults usually fine)
SERVER_HOST=localhost
SERVER_PORT=2024

# Development Settings
NODE_ENV=development
LOG_LEVEL=INFO
```

#### `backend/CLAUDE.md`
**Purpose**: Backend-specific Claude Code instructions  
**Template**:
```markdown
# Backend Development Instructions

This file contains specific instructions for Claude Code when working with the backend.

## Must-Follow Workflows

### Testing Requirements
If a test fails, you MUST NOT simplify the test without permission. Tests are designed to ensure correctness and should be fixed by correcting the implementation, not by reducing test requirements.

### Code Quality Standards
- All Python code must pass `ruff check .` linting
- Type hints are required for all public functions
- Docstrings required for all classes and public methods (Google style)
- Error handling must be comprehensive

### Development Workflow
1. Run `ruff check . --fix` before committing
2. Ensure all tests pass with `pytest`
3. Verify type checking with `mypy src/agent`
4. Test API endpoints with the health check

### Environment Setup
- Always set `PYTHONPATH=./backend/src` in development
- Required environment variable: `GEMINI_API_KEY`
- Use `python -m agent.app` or `uvicorn agent.app:app --reload` to run

### API Development
- All endpoints must include proper error handling
- Use Pydantic models for request/response validation
- Include comprehensive OpenAPI documentation
- Implement proper logging for debugging

### Agent Development
- All agents must inherit from `BaseResearchAgent`
- Implement proper input/output schemas with Pydantic
- Include error handling and logging
- Follow the established agent patterns

### Search Provider Integration
- All search providers must implement `BaseSearchProvider`
- Include proper error handling and retries
- Support quality scoring and source classification
- Implement timeout and rate limiting

### Testing Guidelines
- Unit tests for all agent classes
- Integration tests for API endpoints
- Mock external API calls in tests
- Maintain test coverage above 70%
```

## ⚛️ Frontend Configuration

### React Project Configuration

#### `frontend/package.json`
**Purpose**: Complete Node.js project configuration  
**Template**:
```json
{
  "name": "frontend",
  "private": true,
  "version": "0.0.1",
  "type": "module",
  "description": "Frontend for the AI-powered web research application",
  "keywords": ["react", "typescript", "vite", "research", "ai"],
  "author": "Your Name <your.email@example.com>",
  "license": "MIT",
  "homepage": "./",
  
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview",
    "lint": "eslint .",
    "lint:fix": "eslint . --fix",
    "type-check": "tsc --noEmit",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest run --coverage",
    "test:watch": "vitest --watch",
    "clean": "rm -rf dist node_modules",
    "analyze": "vite build --mode analyze"
  },
  
  "dependencies": {
    "@radix-ui/react-collapsible": "^1.1.12",
    "@radix-ui/react-scroll-area": "^1.2.8", 
    "@radix-ui/react-select": "^2.2.4",
    "@radix-ui/react-slot": "^1.2.2",
    "@radix-ui/react-tabs": "^1.1.11",
    "@radix-ui/react-tooltip": "^1.2.8",
    "@tailwindcss/vite": "^4.1.5",
    "class-variance-authority": "^0.7.1",
    "clsx": "^2.1.1",
    "katex": "^0.16.22",
    "lucide-react": "^0.508.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "react-markdown": "^9.0.3",
    "react-router-dom": "^7.5.3",
    "rehype-katex": "^7.0.1",
    "remark-gfm": "^4.0.1",
    "remark-math": "^6.0.0", 
    "tailwind-merge": "^3.2.0",
    "tailwindcss": "^4.1.5"
  },
  
  "devDependencies": {
    "@eslint/js": "^9.22.0",
    "@testing-library/jest-dom": "^6.7.0",
    "@testing-library/react": "^16.3.0",
    "@testing-library/user-event": "^14.5.2",
    "@types/katex": "^0.16.7",
    "@types/node": "^22.15.17",
    "@types/react": "^19.1.2",
    "@types/react-dom": "^19.1.3",
    "@vitejs/plugin-react-swc": "^3.9.0",
    "@vitest/coverage-v8": "^3.2.4",
    "@vitest/ui": "^3.2.4",
    "eslint": "^9.22.0",
    "eslint-plugin-react-hooks": "^5.2.0",
    "eslint-plugin-react-refresh": "^0.4.19",
    "globals": "^16.0.0",
    "jsdom": "^26.1.0",
    "rollup-plugin-analyzer": "^4.0.0",
    "tw-animate-css": "^1.2.9",
    "typescript": "~5.7.2",
    "typescript-eslint": "^8.26.1",
    "vite": "^6.3.4",
    "vite-plugin-pwa": "^0.21.1",
    "vitest": "^3.2.4"
  },
  
  "engines": {
    "node": ">=20.0.0",
    "npm": ">=9.0.0"
  },
  
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}
```

### TypeScript Configuration

#### `frontend/tsconfig.json`
**Purpose**: TypeScript compiler configuration  
**Template**:
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    
    /* Bundler mode */
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "isolatedModules": true,
    "moduleDetection": "force",
    "noEmit": true,
    "jsx": "react-jsx",
    
    /* Linting */
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "noImplicitReturns": true,
    "noImplicitOverride": true,
    "exactOptionalPropertyTypes": true,
    
    /* Path mapping */
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@/components/*": ["./src/components/*"],
      "@/services/*": ["./src/services/*"],
      "@/lib/*": ["./src/lib/*"],
      "@/types/*": ["./src/types/*"]
    },
    
    /* Additional checks */
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "allowSyntheticDefaultImports": true,
    "esModuleInterop": true,
    
    /* Type definitions */
    "types": ["vite/client", "node", "jsdom"]
  },
  
  "include": [
    "src/**/*.ts",
    "src/**/*.tsx", 
    "src/**/*.js",
    "src/**/*.jsx",
    "vite.config.ts",
    "vitest.config.ts"
  ],
  
  "exclude": [
    "node_modules",
    "dist",
    "build",
    "coverage",
    "*.config.js"
  ],
  
  "references": [
    { "path": "./tsconfig.node.json" }
  ]
}
```

#### `frontend/tsconfig.node.json`
**Purpose**: Node.js specific TypeScript configuration  
**Template**:
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2023"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "noEmit": true,
    "isolatedModules": true,
    "types": ["node"]
  },
  "include": [
    "vite.config.ts",
    "vitest.config.ts",
    "tailwind.config.js"
  ]
}
```

### Build Tool Configuration

#### `frontend/vite.config.ts`
**Purpose**: Vite build and development configuration  
**Template**:
```typescript
import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react-swc'
import tailwindcss from '@tailwindcss/vite'
import { VitePWA } from 'vite-plugin-pwa'
import path from 'path'

export default defineConfig(({ command, mode }) => {
  // Load environment variables
  const env = loadEnv(mode, process.cwd(), '')
  
  return {
    plugins: [
      react(),
      tailwindcss(),
      // PWA plugin for production builds
      VitePWA({
        registerType: 'autoUpdate',
        workbox: {
          globPatterns: ['**/*.{js,css,html,ico,png,svg}']
        }
      })
    ],
    
    // Base path for production deployment
    base: command === 'build' ? '/app/' : '/',
    
    // Path resolution
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
        '@/components': path.resolve(__dirname, './src/components'),
        '@/services': path.resolve(__dirname, './src/services'),
        '@/lib': path.resolve(__dirname, './src/lib'),
        '@/types': path.resolve(__dirname, './src/types'),
      }
    },
    
    // Development server configuration
    server: {
      host: env.FRONTEND_HOST || 'localhost',
      port: parseInt(env.FRONTEND_PORT || '5173'),
      strictPort: false,
      open: true,
      cors: true,
      
      // API proxy configuration
      proxy: {
        '/api': {
          target: env.VITE_API_TARGET || 'http://localhost:2024',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
          timeout: 30000,
        }
      }
    },
    
    // Build configuration
    build: {
      outDir: 'dist',
      assetsDir: 'assets',
      sourcemap: mode === 'development',
      minify: 'terser',
      target: 'es2020',
      
      // Rollup options for optimization
      rollupOptions: {
        output: {
          // Manual chunk splitting for better caching
          manualChunks: {
            'react-vendor': ['react', 'react-dom'],
            'router-vendor': ['react-router-dom'],
            'ui-vendor': [
              '@radix-ui/react-select',
              '@radix-ui/react-collapsible',
              '@radix-ui/react-tabs',
              '@radix-ui/react-tooltip',
              '@radix-ui/react-scroll-area',
              '@radix-ui/react-slot'
            ],
            'markdown-vendor': [
              'react-markdown',
              'remark-gfm',
              'remark-math',
              'rehype-katex',
              'katex'
            ],
            'utils-vendor': [
              'clsx',
              'tailwind-merge',
              'class-variance-authority',
              'lucide-react'
            ]
          }
        }
      },
      
      // Terser options for minification
      terserOptions: {
        compress: {
          drop_console: mode === 'production',
          drop_debugger: mode === 'production',
        }
      },
      
      // Chunk size warning limit
      chunkSizeWarningLimit: 1000,
    },
    
    // Preview configuration
    preview: {
      port: 4173,
      strictPort: true,
      host: true
    },
    
    // Environment variables
    define: {
      __DEV__: mode === 'development',
      __PROD__: mode === 'production',
      __VERSION__: JSON.stringify(process.env.npm_package_version || '0.0.1')
    },
    
    // CSS configuration
    css: {
      devSourcemap: true,
      preprocessorOptions: {
        scss: {
          additionalData: '@import "@/styles/variables.scss";'
        }
      }
    },
    
    // Optimization
    optimizeDeps: {
      include: [
        'react',
        'react-dom',
        'react-router-dom',
        '@radix-ui/react-select',
        'lucide-react'
      ],
      exclude: ['@vite/client', '@vite/env']
    }
  }
})
```

### Styling Configuration

#### `frontend/tailwind.config.js`
**Purpose**: Tailwind CSS configuration with custom theme  
**Template**:
```javascript
import animate from 'tailwindcss/plugin'

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  
  theme: {
    extend: {
      // Color system based on CSS variables
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        
        // Custom colors for research application
        success: {
          DEFAULT: "hsl(142 76% 36%)",
          foreground: "hsl(138 76% 97%)",
        },
        warning: {
          DEFAULT: "hsl(32 95% 44%)",
          foreground: "hsl(48 96% 89%)",
        },
        info: {
          DEFAULT: "hsl(204 94% 94%)",
          foreground: "hsl(213 94% 18%)",
        },
      },
      
      // Border radius system
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      
      // Typography
      fontFamily: {
        sans: [
          "Inter",
          "ui-sans-serif", 
          "system-ui",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "Roboto",
          "Helvetica Neue",
          "Arial",
          "Noto Sans",
          "sans-serif"
        ],
        mono: [
          "Fira Code",
          "ui-monospace",
          "SFMono-Regular",
          "Monaco",
          "Consolas",
          "Liberation Mono",
          "Menlo",
          "monospace"
        ],
      },
      
      // Spacing scale
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      
      // Animation and transitions
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-in': 'slideIn 0.3s ease-out',
        'bounce-gentle': 'bounceGentle 2s infinite',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'shimmer': 'shimmer 2s linear infinite',
      },
      
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideIn: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        bounceGentle: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-5px)' },
        },
        shimmer: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        },
      },
      
      // Box shadows
      boxShadow: {
        'soft': '0 2px 8px rgba(0, 0, 0, 0.1)',
        'medium': '0 4px 16px rgba(0, 0, 0, 0.12)',
        'hard': '0 8px 32px rgba(0, 0, 0, 0.16)',
      },
      
      // Typography scale
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem', { lineHeight: '1.5rem' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
        '5xl': ['3rem', { lineHeight: '1' }],
        '6xl': ['3.75rem', { lineHeight: '1' }],
      },
      
      // Screen breakpoints
      screens: {
        'xs': '475px',
        'sm': '640px',
        'md': '768px',
        'lg': '1024px',
        'xl': '1280px',
        '2xl': '1536px',
      },
    },
  },
  
  plugins: [
    animate,
    
    // Custom plugin for research-specific utilities
    function({ addUtilities, theme }) {
      const newUtilities = {
        '.text-balance': {
          'text-wrap': 'balance',
        },
        '.bg-grid': {
          'background-image': `url("data:image/svg+xml,%3csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3e%3cg fill='none' fill-rule='evenodd'%3e%3cg fill='%23${theme('colors.muted.DEFAULT').replace('#', '')}' fill-opacity='0.1'%3e%3ccircle cx='7' cy='7' r='1'/%3e%3c/g%3e%3c/g%3e%3c/svg%3e")`,
        },
        '.research-gradient': {
          'background': 'linear-gradient(135deg, hsl(var(--primary)) 0%, hsl(var(--accent)) 100%)',
        },
      }
      addUtilities(newUtilities)
    },
    
    // Container queries plugin
    require('@tailwindcss/container-queries'),
  ],
}
```

### Code Quality Configuration

#### `frontend/eslint.config.js`
**Purpose**: ESLint configuration for TypeScript and React  
**Template**:
```javascript
import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import tseslint from 'typescript-eslint'

export default tseslint.config(
  { ignores: ['dist', 'coverage', 'node_modules'] },
  {
    extends: [js.configs.recommended, ...tseslint.configs.recommended],
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
      parserOptions: {
        ecmaVersion: 'latest',
        ecmaFeatures: { jsx: true },
        sourceType: 'module',
      },
    },
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      'react-refresh/only-export-components': [
        'warn',
        { allowConstantExport: true },
      ],
      
      // TypeScript specific rules
      '@typescript-eslint/no-unused-vars': [
        'error',
        { 
          argsIgnorePattern: '^_',
          varsIgnorePattern: '^_',
          caughtErrorsIgnorePattern: '^_' 
        }
      ],
      '@typescript-eslint/explicit-function-return-type': 'off',
      '@typescript-eslint/explicit-module-boundary-types': 'off',
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/prefer-const': 'error',
      '@typescript-eslint/no-var-requires': 'error',
      
      // General JavaScript/TypeScript rules
      'no-console': ['warn', { allow: ['warn', 'error'] }],
      'no-debugger': 'error',
      'no-duplicate-imports': 'error',
      'no-unused-expressions': 'error',
      'prefer-const': 'error',
      'no-var': 'error',
      
      // Import/export rules
      'sort-imports': ['error', {
        'ignoreCase': false,
        'ignoreDeclarationSort': true,
        'ignoreMemberSort': false,
        'memberSyntaxSortOrder': ['none', 'all', 'multiple', 'single'],
        'allowSeparatedGroups': true
      }],
      
      // Styling and formatting
      'comma-dangle': ['error', 'always-multiline'],
      'quotes': ['error', 'single', { avoidEscape: true }],
      'semi': ['error', 'never'],
    },
    settings: {
      react: {
        version: 'detect',
      },
    },
  },
)
```

### Testing Configuration

#### `frontend/vitest.config.ts`
**Purpose**: Vitest testing framework configuration  
**Template**:
```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react-swc'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  
  test: {
    // Test environment
    environment: 'jsdom',
    globals: true,
    
    // Setup files
    setupFiles: ['./src/test-setup.ts'],
    
    // Coverage configuration
    coverage: {
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test-setup.ts',
        'src/**/*.d.ts',
        'src/**/*.test.{ts,tsx}',
        'src/**/*.spec.{ts,tsx}',
        'dist/',
        'coverage/',
      ],
      thresholds: {
        global: {
          branches: 70,
          functions: 70,
          lines: 70,
          statements: 70,
        },
      },
    },
    
    // Test file patterns
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
    exclude: ['node_modules/', 'dist/', 'coverage/'],
    
    // Test timeout
    testTimeout: 10000,
    hookTimeout: 10000,
    
    // Reporter configuration
    reporter: ['verbose', 'json', 'html'],
    outputFile: {
      json: './coverage/test-results.json',
      html: './coverage/test-results.html',
    },
    
    // Mock configuration
    clearMocks: true,
    restoreMocks: true,
    
    // Watch mode
    watch: false,
    
    // Parallel execution
    pool: 'threads',
    poolOptions: {
      threads: {
        singleThread: false,
        minThreads: 1,
        maxThreads: 4,
      },
    },
  },
  
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@/components': path.resolve(__dirname, './src/components'),
      '@/services': path.resolve(__dirname, './src/services'),
      '@/lib': path.resolve(__dirname, './src/lib'),
      '@/types': path.resolve(__dirname, './src/types'),
    }
  },
})
```

## 🐳 Infrastructure Configuration

### Docker Configuration

#### `Dockerfile`
**Purpose**: Multi-stage production build  
**Template**: *(See existing Dockerfile - already comprehensive)*

#### `docker-compose.yml`
**Purpose**: Full-stack development and production deployment  
**Template**:
```yaml
version: '3.8'

services:
  # Redis for caching and session management
  langgraph-redis:
    image: docker.io/redis:6-alpine
    container_name: research-redis
    restart: unless-stopped
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"  # Expose for development
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - research-network

  # PostgreSQL for persistent data storage
  langgraph-postgres:
    image: docker.io/postgres:16-alpine
    container_name: research-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: postgres
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_INITDB_ARGS: "--encoding=UTF-8 --lc-collate=C --lc-ctype=C"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql:ro
    ports:
      - "5432:5432"  # Expose for development
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - research-network

  # Main application container
  langgraph-api:
    image: gemini-fullstack-langgraph
    container_name: research-api
    restart: unless-stopped
    build:
      context: .
      dockerfile: Dockerfile
      args:
        - BUILD_ENV=production
    ports:
      - "8123:8000"
    environment:
      # Required
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      
      # Optional
      - LANGSMITH_API_KEY=${LANGSMITH_API_KEY}
      - GOOGLE_CSE_ID=${GOOGLE_CSE_ID}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - SEARCHAPI_KEY=${SEARCHAPI_KEY}
      
      # Database connections
      - POSTGRES_URI=postgresql://postgres:postgres@langgraph-postgres:5432/postgres
      - REDIS_URI=redis://langgraph-redis:6379
      
      # Application configuration
      - NODE_ENV=production
      - SERVER_HOST=0.0.0.0
      - SERVER_PORT=8000
      - LOG_LEVEL=INFO
      - PYTHONPATH=/deps/backend/src
      
      # Performance optimization
      - UVICORN_WORKERS=1
      - UVICORN_WORKER_CLASS=uvicorn.workers.UvicornWorker
    depends_on:
      langgraph-redis:
        condition: service_healthy
      langgraph-postgres:
        condition: service_healthy
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - research-network
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local

networks:
  research-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### Development Scripts

#### `scripts/setup-dev.sh`
**Purpose**: Development environment setup script  
**Template**:
```bash
#!/bin/bash

# Development Environment Setup Script
# This script sets up the complete development environment

set -e  # Exit on any error

echo "🚀 Setting up AI Research Application Development Environment"
echo "============================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on supported OS
check_os() {
    print_status "Checking operating system..."
    
    case "$(uname -s)" in
        Linux*)     OS=Linux;;
        Darwin*)    OS=Mac;;
        CYGWIN*)    OS=Cygwin;;
        MINGW*)     OS=MinGw;;
        *)          OS="UNKNOWN:$(uname -s)"
    esac
    
    print_success "Operating System: $OS"
}

# Check Python version
check_python() {
    print_status "Checking Python installation..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
        
        if [ "$PYTHON_MAJOR" -eq "3" ] && [ "$PYTHON_MINOR" -ge "11" ]; then
            print_success "Python $PYTHON_VERSION found"
        else
            print_error "Python 3.11+ required. Found: $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 not found. Please install Python 3.11+"
        exit 1
    fi
}

# Check Node.js version
check_node() {
    print_status "Checking Node.js installation..."
    
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version | cut -d'v' -f2)
        NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1)
        
        if [ "$NODE_MAJOR" -ge "20" ]; then
            print_success "Node.js $NODE_VERSION found"
        else
            print_error "Node.js 20+ required. Found: $NODE_VERSION"
            exit 1
        fi
    else
        print_error "Node.js not found. Please install Node.js 20+"
        exit 1
    fi
}

# Install UV (Python package manager)
install_uv() {
    print_status "Installing UV Python package manager..."
    
    if command -v uv &> /dev/null; then
        print_success "UV already installed"
    else
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.local/bin:$PATH"
        print_success "UV installed successfully"
    fi
}

# Setup backend
setup_backend() {
    print_status "Setting up backend environment..."
    
    cd backend
    
    # Install dependencies with UV
    if command -v uv &> /dev/null; then
        print_status "Installing backend dependencies with UV..."
        uv pip install -e .
        uv pip install -e ".[dev]"
    else
        print_status "Installing backend dependencies with pip..."
        python3 -m venv venv
        source venv/bin/activate
        pip install -e .
        pip install -e ".[dev]"
    fi
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        print_status "Creating .env file from template..."
        cp .env.example .env
        print_warning "Please configure your API keys in backend/.env"
    fi
    
    cd ..
    print_success "Backend setup completed"
}

# Setup frontend
setup_frontend() {
    print_status "Setting up frontend environment..."
    
    cd frontend
    
    # Install dependencies
    print_status "Installing frontend dependencies..."
    npm install
    
    cd ..
    print_success "Frontend setup completed"
}

# Create directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p logs
    mkdir -p data
    mkdir -p scripts
    
    print_success "Directories created"
}

# Verify installation
verify_installation() {
    print_status "Verifying installation..."
    
    # Test backend
    cd backend
    if python3 -c "import agent.app; print('Backend imports successful')" 2>/dev/null; then
        print_success "Backend verification passed"
    else
        print_warning "Backend verification failed - check dependencies"
    fi
    cd ..
    
    # Test frontend
    cd frontend
    if npm run type-check > /dev/null 2>&1; then
        print_success "Frontend verification passed"
    else
        print_warning "Frontend verification failed - check TypeScript setup"
    fi
    cd ..
}

# Main setup process
main() {
    echo "Starting setup process..."
    
    check_os
    check_python
    check_node
    install_uv
    create_directories
    setup_backend
    setup_frontend
    verify_installation
    
    echo ""
    echo "============================================================="
    print_success "🎉 Development environment setup completed!"
    echo ""
    print_status "Next steps:"
    echo "1. Configure your API keys in backend/.env"
    echo "2. Run 'make dev' to start both services"
    echo "3. Visit http://localhost:5173 to access the application"
    echo ""
    print_warning "Don't forget to set GEMINI_API_KEY in backend/.env"
}

# Run main function
main "$@"
```

This comprehensive configuration guide provides exact templates and settings for every configuration file needed to recreate the AI-powered web research application with proper tooling, optimization, and development workflow support.