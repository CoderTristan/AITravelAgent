import { useState, useEffect } from 'react'
import axios from 'axios'

interface Message {
  role: 'user' | 'assistant'
  text: string
}

interface ApiResponse {
  reply: string
}

interface ChatInterfaceProps {
  token: string
  setToken: (token: string | null) => void
}

export default function ChatInterface({ token, setToken }: ChatInterfaceProps) {
  const [input, setInput] = useState<string>('')
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState<boolean>(false)

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await axios.get('http://localhost:8000/api/history', {
          headers: { Authorization: `Bearer ${token}` }
        })
        
        const formattedHistory = res.data.history.map((msg: any) => ({
          role: msg.role,
          text: msg.content
        }))
        setMessages(formattedHistory)
      } catch (err: any) {
        if (err.response?.status === 401) {
          setToken(null)
          localStorage.removeItem('app_token')
        }
      }
    }
    fetchHistory()
  }, [token, setToken])

  const handleSubmit = async (e: React.SubmitEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMsg: Message = { role: 'user', text: input }
    setMessages((prev) => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const res = await axios.post<ApiResponse>('http://localhost:8000/api/chat', 
        { message: input },
        { headers: { Authorization: `Bearer ${token}` } }
      )
      const aiMsg: Message = { role: 'assistant', text: res.data.reply }
      setMessages((prev) => [...prev, aiMsg])
    } catch (err: any) {
      if (err.response?.status === 401) {
        setToken(null)
        localStorage.removeItem('app_token')
        return
      }
      setMessages((prev) => [
        ...prev, 
        { role: 'assistant', text: 'Error connecting to server.' }
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-screen bg-slate-950 text-slate-100 font-sans">
      {/* Top Header */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-slate-800/80 bg-slate-950/50 backdrop-blur-md">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-emerald-400 animate-pulse" />
          <h1 className="text-lg font-semibold text-slate-200 tracking-wide">
            Qwen Travel Assistant
          </h1>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-xs font-mono text-slate-500 bg-slate-900 border border-slate-800 px-2.5 py-1 rounded-full">
            qwen2.5:7b
          </span>
          <button 
            onClick={() => {
              setToken(null)
              localStorage.removeItem('app_token')
            }}
            className="text-xs text-slate-400 hover:text-white transition cursor-pointer"
          >
            Logout
          </button>
        </div>
      </header>

      {/* Main Chat Body */}
      <main className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-3xl mx-auto flex flex-col gap-6">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center min-h-[50vh] text-center my-auto">
              <h2 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-200 mb-3">
                Where to next?
              </h2>
              <p className="text-slate-400 text-sm max-w-md">
                Ask about current weather conditions, forecasts, or climate data anywhere around the globe.
              </p>
            </div>
          ) : (
            messages.map((m, idx) => (
              <div
                key={idx}
                className={`flex gap-3 text-sm leading-relaxed ${
                  m.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                <div
                  className={`px-5 py-3.5 rounded-2xl max-w-[80%] shadow-sm ${
                    m.role === 'user'
                      ? 'bg-emerald-600 text-white rounded-br-xs'
                      : 'bg-slate-900 border border-slate-800 text-slate-200 rounded-bl-xs'
                  }`}
                >
                  <p className="text-[11px] font-bold tracking-wider uppercase opacity-60 mb-1">
                    {m.role === 'user' ? 'You' : 'Qwen'}
                  </p>
                  <p className="whitespace-pre-wrap">{m.text}</p>
                </div>
              </div>
            ))
          )}

          {loading && (
            <div className="flex justify-start">
              <div className="bg-slate-900 border border-slate-800 text-slate-400 px-5 py-3.5 rounded-2xl rounded-bl-xs text-sm flex items-center gap-3">
                <span className="w-2 h-2 bg-emerald-400 rounded-full animate-ping" />
                Fetching data & thinking...
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Floating Bottom Input Bar */}
      <footer className="p-4 bg-slate-950/80 backdrop-blur-md">
        <div className="max-w-3xl mx-auto">
          <form
            onSubmit={handleSubmit}
            className="flex items-center gap-2 bg-slate-900 border border-slate-800 rounded-full px-4 py-2 focus-within:border-emerald-500/50 focus-within:ring-2 focus-within:ring-emerald-500/20 transition-all shadow-lg"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about weather in any city..."
              className="flex-1 bg-transparent px-2 py-1 text-sm text-slate-100 placeholder-slate-500 focus:outline-none"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="bg-emerald-500 hover:bg-emerald-400 disabled:bg-slate-800 disabled:text-slate-600 text-slate-950 font-semibold px-4 py-1.5 rounded-full text-xs transition cursor-pointer disabled:cursor-not-allowed flex items-center gap-1"
            >
              Send
            </button>
          </form>
          <p className="text-[11px] text-slate-600 text-center mt-2">
            Local Ollama tool calling via Open-Meteo API
          </p>
        </div>
      </footer>
    </div>
  )
}