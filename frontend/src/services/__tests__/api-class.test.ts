/**
 * Test suite for the AtomicAgentAPI class.
 * Tests API service functionality, error handling, and configuration.
 */

import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest'
import { AtomicAgentAPI } from '../api'

// Mock fetch globally
const mockFetch = vi.fn()
global.fetch = mockFetch

// Mock window.location
Object.defineProperty(window, 'location', {
  value: {
    href: 'http://localhost:5173',
    pathname: '/',
    protocol: 'http:',
    host: 'localhost:5173'
  },
  writable: true
})

// Mock import.meta.env
vi.stubGlobal('import.meta', {
  env: {
    DEV: true,
    VITE_API_URL: undefined
  }
})

describe('AtomicAgentAPI', () => {
  let api: AtomicAgentAPI

  beforeEach(() => {
    vi.clearAllMocks()
    // Reset console.log mock if needed
    vi.spyOn(console, 'log').mockImplementation(() => {})
    api = new AtomicAgentAPI()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('constructor', () => {
    it('initializes with correct base URL in development mode', () => {
      expect(api['baseUrl']).toBe('/api')
    })

    it('handles environment variable configuration', () => {
      // In development mode, should use /api
      expect(api['baseUrl']).toBe('/api')
    })

    it('constructs API instance without errors', () => {
      const testApi = new AtomicAgentAPI()
      expect(testApi).toBeInstanceOf(AtomicAgentAPI)
      expect(typeof testApi['baseUrl']).toBe('string')
    })
  })

  describe('conductResearch', () => {
    it('makes successful research request', async () => {
      const mockResponse = {
        final_answer: 'AI is a branch of computer science that aims to create intelligent machines.',
        sources: [
          {
            url: 'https://example.com/ai-definition',
            title: 'What is Artificial Intelligence?',
            content: 'AI involves creating systems that can perform tasks requiring human intelligence...'
          }
        ],
        research_loops_executed: 2,
        total_queries: 4
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: 'OK',
        json: async () => mockResponse
      })

      const request = {
        question: 'What is artificial intelligence?',
        initial_search_query_count: 3,
        max_research_loops: 2,
        reasoning_model: 'gemini-2.0-flash-exp'
      }

      const result = await api.conductResearch(request)

      expect(mockFetch).toHaveBeenCalledWith('/api/research', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(request)
      })

      expect(result).toEqual(mockResponse)
    })

    it('handles API errors correctly', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error'
      })

      const request = {
        question: 'Test question',
        initial_search_query_count: 1,
        max_research_loops: 1
      }

      await expect(api.conductResearch(request)).rejects.toThrow(
        'Research failed: 500 Internal Server Error'
      )
    })

    it('handles network errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'))

      const request = {
        question: 'Test question'
      }

      await expect(api.conductResearch(request)).rejects.toThrow('Network error')
    })

    it('handles JSON parsing errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: 'OK',
        json: async () => {
          throw new Error('Invalid JSON')
        }
      })

      const request = {
        question: 'Test question'
      }

      await expect(api.conductResearch(request)).rejects.toThrow('Invalid JSON')
    })

    it('logs request and response information', async () => {
      const consoleSpy = vi.spyOn(console, 'log')
      
      const mockResponse = { final_answer: 'Test response', sources: [], research_loops_executed: 1, total_queries: 1 }
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: 'OK',
        json: async () => mockResponse
      })

      const request = {
        question: 'Test question'
      }

      await api.conductResearch(request)

      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('🔍 API Request:'),
        expect.any(Object)
      )
      
      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('📡 API Response:'),
        expect.any(Object)
      )
      
      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('✅ API Success:'),
        mockResponse
      )
    })
  })

  describe('healthCheck', () => {
    it('makes health check request successfully', async () => {
      const mockHealthResponse = {
        status: 'healthy',
        service: 'atomic-research-agent'
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockHealthResponse
      })

      const result = await api.healthCheck()

      expect(mockFetch).toHaveBeenCalledWith('/api/health')
      expect(result).toEqual(mockHealthResponse)
    })

    it('handles health check errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Health check failed'))

      await expect(api.healthCheck()).rejects.toThrow('Health check failed')
    })
  })

  describe('error handling', () => {
    it('logs errors to console', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      
      mockFetch.mockRejectedValueOnce(new Error('Test error'))

      const request = {
        question: 'Test question'
      }

      try {
        await api.conductResearch(request)
      } catch (error) {
        // Expected to throw
      }

      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('❌ API Error:'),
        expect.any(Error)
      )
    })
  })

  describe('URL construction', () => {
    it('constructs correct API URLs', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: 'OK',
        json: async () => ({ final_answer: 'test', sources: [], research_loops_executed: 1, total_queries: 1 })
      })

      await api.conductResearch({ question: 'test' })

      expect(mockFetch).toHaveBeenCalledWith(
        '/api/research',
        expect.any(Object)
      )
    })

    it('creates instance with valid base URL', () => {
      const testApi = new AtomicAgentAPI()
      expect(testApi['baseUrl']).toBeDefined()
      expect(typeof testApi['baseUrl']).toBe('string')
    })
  })
})