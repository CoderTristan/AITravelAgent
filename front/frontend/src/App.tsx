import { useState, useEffect } from 'react'
import ChatInterface from './ChatInterface'

export default function App() {
  const [token, setToken] = useState<string | null>(localStorage.getItem('app_token'))

  useEffect(() => {
  const params = new URLSearchParams(window.location.hash.slice(1))

  const token = params.get("token")

  if (token) {
    localStorage.setItem("app_token", token)
    setToken(token)
    window.history.replaceState({}, "", "/")
  }
}, [])

  const handleLogin = () => {
    window.location.href = "http://localhost:8000/api/auth/login"
  }

  if (!token) {
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-slate-950 text-slate-100 font-sans">
        <div className="bg-slate-900 border border-slate-800 p-8 rounded-2xl max-w-md w-full text-center shadow-xl">
          <h1 className="text-2xl font-bold mb-2 text-slate-200">Qwen Weather Assistant</h1>
          <p className="text-slate-400 text-sm mb-6">Please sign in with your Google account to access the secure chat.</p>
          <button 
            onClick={handleLogin}
            className="w-full bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold py-2.5 px-4 rounded-xl text-sm transition cursor-pointer"
          >
            Sign in with Google
          </button>
        </div>
      </div>
    )
  }

  return <ChatInterface token={token} setToken={setToken} />
}