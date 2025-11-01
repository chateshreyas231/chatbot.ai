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

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const userMessage: Message = {
      role: 'user',
      text: input,
    }
    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          sessionId: sessionId,
          message: input,
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
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage: Message = {
        role: 'assistant',
        text: 'Sorry, I encountered an error. Please try again.',
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
    <div className="flex flex-col h-[calc(100vh-200px)] bg-white rounded-lg shadow-lg">
      {/* Chat Header */}
      <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-t-lg">
        <div className="flex items-center gap-2">
          <MessageSquare className="w-5 h-5" />
          <h2 className="text-lg font-semibold">IT Helpdesk Assistant</h2>
        </div>
        <p className="text-sm text-blue-100 mt-1">
          Ask questions, create tickets, check status, or get help with password resets
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-12">
            <MessageSquare className="w-12 h-12 mx-auto mb-4 text-gray-400" />
            <p className="text-lg font-medium mb-2">Welcome to IT Helpdesk Copilot</p>
            <p className="text-sm">Try asking:</p>
            <ul className="mt-2 space-y-1 text-sm">
              <li>• "How do I set up MFA?"</li>
              <li>• "Open a ticket for VPN issue"</li>
              <li>• "What's the status of INC0012345?"</li>
              <li>• "Reset my password"</li>
            </ul>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg px-4 py-2 ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              <p className="whitespace-pre-wrap">{message.text}</p>
              
              {message.toolCalls && message.toolCalls.length > 0 && (
                <div className="mt-2 pt-2 border-t border-gray-300">
                  {message.toolCalls.map((call, i) => (
                    <div key={i} className="flex items-center gap-2 text-xs">
                      <Ticket className="w-3 h-3" />
                      <span>Ticket {call.id} created</span>
                    </div>
                  ))}
                </div>
              )}

              {message.sources && message.sources.length > 0 && (
                <div className="mt-2 pt-2 border-t border-gray-300">
                  <div className="flex items-center gap-2 text-xs text-gray-600">
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
            <div className="bg-gray-100 rounded-lg px-4 py-2">
              <Loader2 className="w-5 h-5 animate-spin text-gray-600" />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="px-6 py-4 border-t border-gray-200">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loading}
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {loading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
            Send
          </button>
        </div>
      </div>
    </div>
  )
}

