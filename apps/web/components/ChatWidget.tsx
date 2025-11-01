'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Loader2, MessageSquare, FileText, Ticket } from 'lucide-react'

interface Message {
  id?: string
  role: 'user' | 'assistant'
  text: string
  toolCalls?: any[]
  sources?: any[]
  createdAt?: string
}

interface ChatWidgetProps {
  token: string
}

export default function ChatWidget({ token }: ChatWidgetProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  
  // Debug: Log API URL
  useEffect(() => {
    console.log('API URL:', API_URL)
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || loading) return

    // Save input before clearing it
    const messageText = input.trim()
    
    const userMessage: Message = {
      role: 'user',
      text: messageText,
    }
    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // No auth header needed - authentication removed
        },
        body: JSON.stringify({
          sessionId: sessionId,
          message: messageText, // Use saved message text
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to send message')
      }

      const data = await response.json()
      
      if (!sessionId && data.sessionId) {
        setSessionId(data.sessionId)
      }

      const assistantMessage: Message = {
        role: 'assistant',
        text: data.answer,
        toolCalls: data.toolCalls,
        sources: data.sources,
      }
      setMessages((prev) => [...prev, assistantMessage])
    } catch (error: any) {
      console.error('Error sending message:', error)
      // Show more detailed error for debugging
      const errorDetails = error?.message || 'Unknown error'
      console.error('Error details:', errorDetails)
      const errorMessage: Message = {
        role: 'assistant',
        text: `Sorry, I encountered an error: ${errorDetails}. Please try again. If the problem persists, check if the backend is running on port 8000.`,
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-200px)] bg-white rounded-lg shadow-lg border border-gray-200 overflow-hidden">
      {/* Chat Header - Clean white theme */}
      <div className="px-6 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 border-b border-blue-700">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-white/20 rounded-lg">
            <MessageSquare className="w-5 h-5 text-white" />
          </div>
          <h2 className="text-lg font-semibold text-white">IT Helpdesk Assistant</h2>
        </div>
        <p className="text-sm text-blue-100 mt-1">
          Ask questions, get help with IT issues, or search the knowledge base
        </p>
      </div>

      {/* Messages - White background */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-white">
        {messages.length === 0 && (
          <div className="text-center mt-12">
            <div className="inline-flex items-center justify-center w-16 h-16 mb-4 bg-blue-50 rounded-full border border-blue-100">
              <MessageSquare className="w-8 h-8 text-blue-600" />
            </div>
            <p className="text-lg font-medium mb-2 text-gray-900">Welcome to IT Helpdesk Copilot</p>
            <p className="text-sm text-gray-600 mb-4">Try asking:</p>
            <div className="space-y-2 max-w-md mx-auto">
              <div className="bg-gray-50 rounded-lg px-4 py-2 border border-gray-200 text-sm text-gray-700">
                • "How do I set up MFA?"
              </div>
              <div className="bg-gray-50 rounded-lg px-4 py-2 border border-gray-200 text-sm text-gray-700">
                • "What movies are about action?"
              </div>
              <div className="bg-gray-50 rounded-lg px-4 py-2 border border-gray-200 text-sm text-gray-700">
                • "Open a ticket for VPN issue"
              </div>
            </div>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg px-4 py-3 border ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white border-blue-700 shadow-sm'
                  : 'bg-gray-50 text-gray-900 border-gray-200 shadow-sm'
              }`}
            >
              <p className="whitespace-pre-wrap leading-relaxed">{message.text}</p>
              
              {message.toolCalls && message.toolCalls.length > 0 && (
                <div className={`mt-2 pt-2 border-t ${message.role === 'user' ? 'border-blue-400/30' : 'border-gray-300'}`}>
                  {message.toolCalls.map((call, i) => (
                    <div key={i} className={`flex items-center gap-2 text-xs ${message.role === 'user' ? 'text-blue-100' : 'text-gray-600'}`}>
                      <Ticket className="w-3 h-3" />
                      <span>Ticket {call.id} created</span>
                    </div>
                  ))}
                </div>
              )}

              {message.sources && message.sources.length > 0 && (
                <div className={`mt-2 pt-2 border-t ${message.role === 'user' ? 'border-blue-400/30' : 'border-gray-300'}`}>
                  <div className={`flex items-center gap-2 text-xs ${message.role === 'user' ? 'text-blue-100' : 'text-gray-600'}`}>
                    <FileText className="w-3 h-3" />
                    <span>{message.sources.length} source(s)</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-50 rounded-lg px-4 py-3 border border-gray-200 shadow-sm">
              <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input - Clean white theme */}
      <div className="px-6 py-4 bg-white border-t border-gray-200">
        <div className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            className="flex-1 px-4 py-3 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900 placeholder:text-gray-400 shadow-sm transition-all"
            disabled={loading}
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || loading}
            className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-sm hover:shadow-md transition-all"
          >
            {loading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <>
                <Send className="w-5 h-5" />
                <span className="hidden sm:inline">Send</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}

