import { useEffect, useRef, useState } from 'react'
import { sendChat } from './api'
import './App.css'

const SUGGESTIONS = [
  'What are your core AI skills?',
  'Tell me about your Infosys work',
  'Which certifications do you have?',
  'Describe your RAG / LangGraph experience',
]

const WELCOME =
  "Hi — I'm Pranay. Ask me about my AI engineering experience, skills, projects, or education."

export default function App() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: WELCOME },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const bottomRef = useRef(null)
  const textareaRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  async function ask(text) {
    const trimmed = text.trim()
    if (!trimmed || loading) return

    setError('')
    setInput('')
    const nextHistory = [...messages, { role: 'user', content: trimmed }]
    setMessages(nextHistory)
    setLoading(true)

    try {
      const historyForApi = nextHistory
        .filter((m) => m.role === 'user' || m.role === 'assistant')
        .slice(0, -1)
        .filter((m) => m.content !== WELCOME)

      const data = await sendChat(trimmed, historyForApi)
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: data.reply, sources: data.sources },
      ])
    } catch (err) {
      setError(err.message || 'Failed to reach the API')
      setMessages((prev) => [
        ...prev,
        {
          role: 'system',
          content: 'Sorry — I could not answer that just now. Please try again.',
        },
      ])
    } finally {
      setLoading(false)
      textareaRef.current?.focus()
    }
  }

  function onSubmit(e) {
    e.preventDefault()
    ask(input)
  }

  function onKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      ask(input)
    }
  }

  return (
    <div className="app">
      <header className="hero">
        <h1 className="brand">
          Pranay <span>Chandra</span>
        </h1>
        <p className="tagline">
          AI Engineer — Generative AI, Agentic systems, and production LLM platforms.
          Chat with my resume assistant.
        </p>
        <div className="meta">
          <span>Hyderabad</span>
          <a
            href="https://www.linkedin.com/in/pranaychandra-kunche-54877b219"
            target="_blank"
            rel="noreferrer"
          >
            LinkedIn
          </a>
          <a href="mailto:pranaychandrakunche@gmail.com">Email</a>
        </div>
      </header>

      <section className="chat-shell" aria-label="Resume chat">
        <div className="messages" role="log" aria-live="polite">
          {messages.map((m, i) => (
            <div key={`${m.role}-${i}`} className={`bubble ${m.role}`}>
              {m.content}
            </div>
          ))}
          {loading && (
            <div className="bubble assistant">
              <span className="typing" aria-label="Thinking">
                <i />
                <i />
                <i />
              </span>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {messages.length <= 1 && (
          <div className="suggestions">
            {SUGGESTIONS.map((s) => (
              <button key={s} type="button" disabled={loading} onClick={() => ask(s)}>
                {s}
              </button>
            ))}
          </div>
        )}

        {error && <div className="error">{error}</div>}

        <form className="composer" onSubmit={onSubmit}>
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKeyDown}
            placeholder="Ask about skills, experience, projects…"
            rows={2}
            disabled={loading}
            aria-label="Your question"
          />
          <button type="submit" disabled={loading || !input.trim()}>
            Send
          </button>
        </form>
      </section>
    </div>
  )
}
