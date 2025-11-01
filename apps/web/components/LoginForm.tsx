'use client'

import { useState } from 'react'
import { LogIn, Loader2 } from 'lucide-react'

interface LoginFormProps {
  onLogin: (token: string) => void
}

export default function LoginForm({ onLogin }: LoginFormProps) {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [tokenSent, setTokenSent] = useState(false)

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email.trim()) return

    setLoading(true)
    setError('')

    try {
      // Request magic link
      const response = await fetch(`${API_URL}/auth/magic-link`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      })

      if (!response.ok) {
        const errorText = await response.text()
        console.error('API Error:', response.status, errorText)
        throw new Error(`Failed to create magic link: ${response.status} ${errorText}`)
      }

      const data = await response.json()
      
      // For demo, use the token directly
      if (data.token) {
        // Verify and get access token
        const verifyResponse = await fetch(`${API_URL}/auth/verify?token=${data.token}`)
        if (verifyResponse.ok) {
          const authData = await verifyResponse.json()
          onLogin(authData.access_token)
        } else {
          const errorText = await verifyResponse.text()
          console.error('Verify Error:', verifyResponse.status, errorText)
          setTokenSent(true)
        }
      } else {
        setTokenSent(true)
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-xl p-8 w-full max-w-md">
      <div className="text-center mb-6">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
          <LogIn className="w-8 h-8 text-blue-600" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900">IT Helpdesk Copilot</h2>
        <p className="text-gray-600 mt-2">Sign in with your email</p>
      </div>

      {tokenSent ? (
        <div className="text-center">
          <p className="text-green-600 mb-4">
            Magic link sent! Check your email and click the link to sign in.
          </p>
          <button
            onClick={() => setTokenSent(false)}
            className="text-blue-600 hover:text-blue-700 text-sm"
          >
            Try again
          </button>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@company.com"
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white"
            />
          </div>

          {error && (
            <div className="text-red-600 text-sm">{error}</div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Signing in...
              </>
            ) : (
              <>
                <LogIn className="w-5 h-5" />
                Sign In
              </>
            )}
          </button>

          <p className="text-xs text-gray-500 text-center mt-4">
            For demo: Enter any email to get started
          </p>
        </form>
      )}
    </div>
  )
}

