# Dependency Guide

This comprehensive guide details every dependency, version requirement, and configuration needed to recreate the AI-powered web research application's complete technology stack.

## 📋 Overview

The application uses a modern full-stack architecture with carefully selected dependencies optimized for AI research workflows, performance, and maintainability.

### Technology Stack Summary
- **Backend**: Python 3.11+ with FastAPI, Atomic Agents, and Google Generative AI
- **Frontend**: React 19, TypeScript 5.7, Vite 6.3, Tailwind CSS 4.1
- **Infrastructure**: Docker, PostgreSQL 16, Redis 6
- **Build Tools**: UV (Python), npm (Node.js), Vite (Frontend bundling)

## 🐍 Python Backend Dependencies

### Core Dependencies (Required)

#### `pyproject.toml` Configuration

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

dependencies = [
    # AI Agent Framework
    "atomic-agents>=1.0.24",           # Core agent orchestration framework
    
    # AI/ML Libraries
    "instructor>=1.3.7",               # Structured outputs from LLMs
    "google-genai>=0.1.0",            # Google Gemini API integration
    
    # Web Framework
    "fastapi>=0.104.0",               # Modern async web framework
    "uvicorn[standard]>=0.24.0",      # ASGI server with extras
    
    # Data Validation & Serialization
    "pydantic>=2.0.0",                # Data validation using type hints
    
    # HTTP Client & Utilities
    "httpx>=0.25.0",                  # Async HTTP client
    "python-dotenv>=1.0.1",           # Environment variable loading
    "jsonref>=1.1.0",                 # JSON reference resolution
]
```

### Development Dependencies

```toml
[project.optional-dependencies]
dev = [
    "mypy>=1.11.1",                   # Static type checking
    "ruff>=0.6.1",                    # Fast Python linter and formatter
]

[dependency-groups]
dev = [
    "pytest>=8.3.5",                 # Testing framework
    "pytest-asyncio>=0.23.0",        # Async testing support
    "pytest-mock>=3.12.0",           # Mocking utilities
]
```

### Detailed Dependency Explanations

#### AI & Research Dependencies

1. **atomic-agents (>=1.0.24)**
   - **Purpose**: Core framework for building AI agents
   - **Why this version**: Includes latest bug fixes and performance improvements
   - **Key features**: Agent orchestration, state management, tool integration
   - **Import pattern**: `from atomic_agents.lib.base.base_agent import BaseAgent`

2. **google-genai (>=0.1.0)**
   - **Purpose**: Official Google Gemini API client
   - **Features**: Text generation, embedding, safety settings
   - **Configuration**: Requires `GEMINI_API_KEY` environment variable
   - **Usage**: Research query generation, content analysis, answer synthesis

3. **instructor (>=1.3.7)**
   - **Purpose**: Structured outputs from language models
   - **Benefits**: Type-safe AI responses, Pydantic integration
   - **Pattern**: `@instructor.patch` decorator for API clients

#### Web Framework Dependencies

4. **fastapi (>=0.104.0)**
   - **Purpose**: Modern, fast web framework
   - **Features**: Auto-generated OpenAPI docs, async support, dependency injection
   - **Why chosen**: Excellent performance, built-in validation, developer experience

5. **uvicorn[standard] (>=0.24.0)**
   - **Purpose**: ASGI server for serving FastAPI applications
   - **Standard extras**: Includes `websockets`, `httptools`, `uvloop` for performance
   - **Configuration**: `--reload` for development, production-optimized settings

6. **pydantic (>=2.0.0)**
   - **Purpose**: Data validation using Python type annotations
   - **Integration**: Deep integration with FastAPI for request/response validation
   - **Features**: JSON Schema generation, custom validators, performance optimizations

#### Networking & Utilities

7. **httpx (>=0.25.0)**
   - **Purpose**: Modern HTTP client with async support
   - **Advantages**: Better performance than `requests`, async/await support
   - **Usage**: Search provider API calls, external service integration

8. **python-dotenv (>=1.0.1)**
   - **Purpose**: Load environment variables from `.env` files
   - **Development convenience**: Consistent environment setup across team

9. **jsonref (>=1.1.0)**
   - **Purpose**: JSON reference resolution for complex schemas
   - **Usage**: OpenAPI schema generation, configuration management

### Installation Commands

```bash
# Development setup with UV (recommended)
cd backend
curl -LsSf https://astral.sh/uv/install.sh | sh
uv pip install -e .
uv pip install -e ".[dev]"

# Alternative: Standard pip installation
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
pip install -e ".[dev]"

# Install specific dependency groups
pip install -e ".[dev]"  # Development dependencies
```

## ⚛️ Frontend Dependencies

### Core Dependencies (Required)

#### `package.json` Configuration

```json
{
  "name": "frontend",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  
  "dependencies": {
    // React Core
    "react": "^19.0.0",                    // Latest React with concurrent features
    "react-dom": "^19.0.0",               // React DOM bindings
    "react-router-dom": "^7.5.3",         // Client-side routing
    
    // UI Framework (Radix UI primitives)
    "@radix-ui/react-collapsible": "^1.1.12",  // Collapsible component
    "@radix-ui/react-scroll-area": "^1.2.8",   // Custom scrollbars
    "@radix-ui/react-select": "^2.2.4",        // Select dropdown
    "@radix-ui/react-slot": "^1.2.2",          // Slot component for composition
    "@radix-ui/react-tabs": "^1.1.11",         // Tab component
    "@radix-ui/react-tooltip": "^1.2.8",       // Tooltip component
    
    // Styling & CSS
    "@tailwindcss/vite": "^4.1.5",        // Vite integration for Tailwind
    "tailwindcss": "^4.1.5",              // Utility-first CSS framework
    "class-variance-authority": "^0.7.1",  // CSS-in-JS utility variants
    "clsx": "^2.1.1",                     // Conditional className utility
    "tailwind-merge": "^3.2.0",           // Merge Tailwind classes intelligently
    
    // Content & Rendering
    "react-markdown": "^9.0.3",           // Markdown rendering
    "remark-gfm": "^4.0.1",              // GitHub Flavored Markdown
    "remark-math": "^6.0.0",             // Math expressions in markdown
    "rehype-katex": "^7.0.1",            // KaTeX math rendering
    "katex": "^0.16.22",                 // Math typesetting
    
    // Icons & Assets
    "lucide-react": "^0.508.0"           // Lucide icon library
  }
}
```

### Development Dependencies

```json
{
  "devDependencies": {
    // TypeScript
    "typescript": "~5.7.2",              // TypeScript compiler
    "@types/node": "^22.15.17",          // Node.js type definitions
    "@types/react": "^19.1.2",           // React type definitions
    "@types/react-dom": "^19.1.3",       // React DOM type definitions
    "typescript-eslint": "^8.26.1",       // TypeScript ESLint integration
    
    // Build Tools
    "vite": "^6.3.4",                    // Next-gen frontend build tool
    "@vitejs/plugin-react-swc": "^3.9.0", // React SWC plugin for Vite
    
    // Code Quality
    "eslint": "^9.22.0",                 // JavaScript/TypeScript linting
    "@eslint/js": "^9.22.0",             // ESLint JavaScript configs
    "eslint-plugin-react-hooks": "^5.2.0", // React hooks linting
    "eslint-plugin-react-refresh": "^0.4.19", // React refresh linting
    "globals": "^16.0.0",                // Global variables for linting
    
    // Testing
    "vitest": "^3.2.4",                  // Fast unit testing framework
    "@testing-library/react": "^16.3.0",  // React testing utilities
    "@testing-library/jest-dom": "^6.7.0", // Additional jest matchers
    "jsdom": "^26.1.0",                  // DOM implementation for testing
    
    // Styling Dev Tools
    "tw-animate-css": "^1.2.9"           // Tailwind animation utilities
  }
}
```

### Detailed Frontend Dependency Explanations

#### React Ecosystem

1. **React 19 & React DOM 19**
   - **Features**: Concurrent features, automatic batching, Suspense improvements
   - **Benefits**: Better performance, improved developer experience
   - **Breaking changes**: Requires TypeScript 4.7+, new JSX transform

2. **React Router DOM (^7.5.3)**
   - **Purpose**: Client-side routing with data loading
   - **Features**: Nested routes, data loading, error boundaries
   - **Pattern**: `createBrowserRouter` for type-safe routing

#### UI Component Library (Radix UI)

3. **Radix UI Components**
   - **Philosophy**: Unstyled, accessible components as primitives
   - **Benefits**: Full control over styling, excellent accessibility
   - **Components used**: Collapsible, ScrollArea, Select, Slot, Tabs, Tooltip
   - **Integration**: Combined with Tailwind CSS for custom design system

#### Styling System

4. **Tailwind CSS 4.1**
   - **Purpose**: Utility-first CSS framework
   - **New in v4**: Oxide engine, improved performance, new features
   - **Integration**: `@tailwindcss/vite` for seamless Vite integration

5. **CSS Utilities**
   - **class-variance-authority**: Type-safe variant generation for components
   - **clsx**: Lightweight conditional className utility
   - **tailwind-merge**: Intelligently merges Tailwind classes

#### Content Rendering

6. **Markdown Processing Pipeline**
   ```
   Markdown → remark-gfm → remark-math → rehype-katex → Rendered HTML
   ```
   - **react-markdown**: Core markdown rendering
   - **remark-gfm**: GitHub Flavored Markdown (tables, task lists, etc.)
   - **remark-math**: Mathematical expressions ($x^2$, $$\frac{1}{2}$$)
   - **rehype-katex + katex**: Beautiful math rendering

#### Development Tools

7. **Vite 6.3 Build System**
   - **Features**: Lightning-fast HMR, optimized builds, plugin ecosystem
   - **SWC Plugin**: `@vitejs/plugin-react-swc` for faster compilation
   - **Benefits**: 10x faster than Webpack, excellent TypeScript support

8. **TypeScript 5.7**
   - **Features**: Better type inference, improved performance
   - **Configuration**: Strict mode enabled for better code quality
   - **Integration**: Deep integration with React 19 types

9. **Testing Framework**
   - **Vitest**: Jest-compatible API with Vite integration
   - **React Testing Library**: Component testing utilities
   - **jsdom**: DOM implementation for Node.js testing environment

### Installation Commands

```bash
# Install all dependencies
cd frontend
npm install

# Install specific categories
npm install react react-dom                    # Core React
npm install @radix-ui/react-select             # UI components
npm install tailwindcss @tailwindcss/vite      # Styling
npm install -D vitest @testing-library/react   # Testing tools
npm install -D typescript @types/react         # TypeScript support
```

## 🏗️ Build Tools & Infrastructure

### Python Build Tools

#### UV Package Manager (Recommended)

```bash
# Installation
curl -LsSf https://astral.sh/uv/install.sh | sh

# Usage
uv pip install package-name         # Install package
uv pip install -e .                # Install in editable mode
uv pip install -c constraints.txt  # Install with constraints
uv pip list                        # List installed packages
uv pip freeze > requirements.txt   # Export requirements
```

**Why UV?**
- **Speed**: 10-100x faster than pip
- **Reliability**: Better dependency resolution
- **Compatibility**: Drop-in pip replacement

#### Alternative: Standard Pip

```bash
# Virtual environment setup
python -m venv venv
source venv/bin/activate  # Unix/Mac
venv\Scripts\activate     # Windows

# Installation
pip install -e .
pip install -e ".[dev]"
```

### Node.js Build Tools

#### Package Manager Comparison

| Manager | Speed | Features | Recommendation |
|---------|--------|----------|----------------|
| **npm** | Good | Standard, included with Node | ✅ **Recommended** (used in project) |
| **yarn** | Fast | Workspaces, zero-installs | ✅ Compatible |
| **pnpm** | Fastest | Efficient storage | ✅ Compatible |

#### Vite Configuration

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

export default defineConfig({
  plugins: [
    react(),                          // React SWC plugin
    tailwindcss(),                    // Tailwind CSS integration
  ],
  base: "/app/",                      // Production base path
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),  // Path aliases
    }
  },
  server: {
    host: process.env.FRONTEND_HOST || "localhost",
    port: parseInt(process.env.FRONTEND_PORT || "5173"),
    strictPort: false,
    proxy: {
      "/api": {
        target: process.env.VITE_API_TARGET || "http://localhost:2024",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      }
    }
  },
  build: {
    outDir: 'dist',                   // Build output directory
    sourcemap: true,                  // Generate source maps
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'ui-vendor': ['@radix-ui/react-select', '@radix-ui/react-collapsible'],
        }
      }
    }
  }
})
```

## 🐳 Infrastructure Dependencies

### Docker

#### Requirements
- **Docker Engine**: 24.0+ (latest stable)
- **Docker Compose**: 2.0+ (included with Docker Desktop)
- **Platform**: Linux, macOS, Windows with WSL2

#### Base Images Used

```dockerfile
# Multi-stage build base images
FROM node:20-alpine AS frontend-builder    # Alpine for minimal size
FROM langchain/langgraph-api:3.11         # LangGraph API runtime
```

**Image Explanations:**
- **node:20-alpine**: Minimal Node.js 20 runtime for frontend builds
- **langchain/langgraph-api:3.11**: Pre-configured Python 3.11 environment with LangGraph

### Database Dependencies

#### PostgreSQL 16
```yaml
# docker-compose.yml
services:
  langgraph-postgres:
    image: docker.io/postgres:16
    environment:
      POSTGRES_DB: postgres
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 30s
      timeout: 10s
      retries: 3
```

**Features Used:**
- JSON/JSONB support for research data storage
- Full-text search capabilities
- ACID compliance for data integrity
- Connection pooling support

#### Redis 6
```yaml
services:
  langgraph-redis:
    image: docker.io/redis:6
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3
```

**Use Cases:**
- Session management
- Search result caching
- Request-scoped data storage
- Rate limiting counters

## 🔧 Development Dependencies

### Code Quality Tools

#### Python Linting & Formatting

```toml
# pyproject.toml
[tool.ruff]
lint.select = [
    "E",      # pycodestyle errors
    "F",      # pyflakes
    "I",      # isort imports
    "D",      # pydocstyle documentation
    "D401",   # First line imperative mood
    "T201",   # print statements
    "UP",     # pyupgrade
]

lint.ignore = [
    "UP006", "UP007", "UP035",  # typing compatibility
    "D417",   # Missing argument descriptions
    "E501",   # Line too long
]

[tool.ruff.lint.pydocstyle]
convention = "google"  # Google docstring style
```

#### TypeScript & ESLint

```javascript
// eslint.config.js
import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import tseslint from 'typescript-eslint'

export default tseslint.config(
  { ignores: ['dist'] },
  {
    extends: [js.configs.recommended, ...tseslint.configs.recommended],
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
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
    },
  },
)
```

### Testing Dependencies

#### Python Testing Stack
- **pytest**: Primary testing framework
- **pytest-asyncio**: Async test support
- **pytest-mock**: Mocking utilities
- **pytest-cov**: Coverage reporting

#### Frontend Testing Stack
- **Vitest**: Fast unit testing
- **@testing-library/react**: React component testing
- **@testing-library/jest-dom**: Extended matchers
- **jsdom**: DOM environment simulation

## 📦 Version Management

### Python Version Requirements

```toml
requires-python = ">=3.11,<4.0"
```

**Why Python 3.11+:**
- Improved error messages and debugging
- Better async/await performance
- Enhanced type hints support
- Pattern matching (structural pattern matching)

### Node.js Version Requirements

```json
{
  "engines": {
    "node": ">=20.0.0",
    "npm": ">=9.0.0"
  }
}
```

**Why Node.js 20+:**
- Native ES modules support
- Improved TypeScript integration
- Better performance characteristics
- Long-term support (LTS) version

## 🔄 Dependency Updates

### Update Strategies

#### Python Dependencies
```bash
# Check for outdated packages
uv pip list --outdated

# Update specific package
uv pip install --upgrade package-name

# Update all packages (cautious approach)
uv pip install --upgrade -r requirements.txt
```

#### Frontend Dependencies
```bash
# Check outdated packages
npm outdated

# Update specific package
npm update package-name

# Update all packages (major versions)
npx npm-check-updates -u && npm install
```

### Security Updates

#### Automated Security Scanning
```bash
# Python security scanning
pip-audit

# Node.js security scanning
npm audit
npm audit fix  # Automatic fixes
```

## 🚨 Common Dependency Issues

### Python Issues

1. **Import Path Issues**
   - **Solution**: Set `PYTHONPATH=./backend/src`
   - **Makefile**: Already configured in development commands

2. **UV Installation Issues**
   - **Fallback**: Use standard pip installation
   - **Alternative**: Use pipx to install UV globally

3. **Google GenAI Authentication**
   - **Requirement**: `GEMINI_API_KEY` environment variable
   - **Testing**: Verify API key with health check endpoint

### Frontend Issues

1. **Node.js Version Mismatch**
   - **Solution**: Use nvm or n to manage Node.js versions
   - **Commands**: `nvm use 20` or `n 20`

2. **Vite Build Issues**
   - **Common cause**: Incorrect base path configuration
   - **Solution**: Verify `base: "/app/"` in vite.config.ts

3. **TypeScript Compilation Errors**
   - **Solution**: Update @types packages
   - **Command**: `npm update @types/react @types/react-dom`

This comprehensive dependency guide ensures exact replication of the technology stack and provides solutions for common issues that may arise during setup and development.