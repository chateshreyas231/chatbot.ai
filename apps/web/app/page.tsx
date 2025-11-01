'use client'

import { useState, useEffect } from 'react'
import { MessageSquare } from 'lucide-react'
import ChatWidget from '@/components/ChatWidget'
import LoginForm from '@/components/LoginForm'

export default function Home() {
  const [token, setToken] = useState<string | null>('demo-token') // Demo token - no auth required
  const [user, setUser] = useState<any>({ email: 'guest@user.com', name: 'Guest User' })

  useEffect(() => {
    // No authentication required - set guest user
    setUser({ email: 'guest@user.com', name: 'Guest User' })
  }, [])

  const handleLogin = (authToken: string) => {
    setToken(authToken)
    setUser({ email: 'guest@user.com', name: 'Guest User' })
  }

  const handleLogout = () => {
    // No logout needed for demo
  }

  // Skip authentication for now - allow direct access
  // if (!token) {
  //   return (
  //     <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
  //       <LoginForm onLogin={handleLogin} />
  //     </div>
  //   )
  // }

  return (
    <div className="min-h-screen bg-white relative overflow-hidden">
      {/* Animated background - Subtle white theme */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {/* Animated gradient orbs - subtle and soft */}
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-blue-100 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob"></div>
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-purple-100 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-2000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-indigo-100 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-4000"></div>
        
        {/* Floating particles */}
        <div className="absolute top-20 left-10 w-2 h-2 bg-blue-200 rounded-full opacity-40 animate-float"></div>
        <div className="absolute top-40 right-20 w-3 h-3 bg-purple-200 rounded-full opacity-30 animate-float animation-delay-1000"></div>
        <div className="absolute bottom-32 left-1/4 w-2 h-2 bg-indigo-200 rounded-full opacity-40 animate-float animation-delay-2000"></div>
        <div className="absolute bottom-20 right-1/3 w-3 h-3 bg-blue-200 rounded-full opacity-30 animate-float animation-delay-3000"></div>
      </div>
      
      {/* Header - Clean white theme */}
      <header className="relative bg-white/80 backdrop-blur-sm border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-50 rounded-lg">
                <MessageSquare className="w-6 h-6 text-blue-600" />
              </div>
              <h1 className="text-2xl font-bold text-gray-900">IT Helpdesk Copilot</h1>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-600 bg-gray-50 px-3 py-1 rounded-full">{user?.email}</span>
            </div>
          </div>
        </div>
      </header>
      
      {/* Main content */}
      <main className="relative max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <ChatWidget token={token || 'demo-token'} />
      </main>
    </div>
  )
}

