import { useState } from 'react'

export default function SimpleApp() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const sendMessage = async (e) => {
    e.preventDefault()
    if (!input.trim()) return

    const userMsg = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMsg }])
    setLoading(true)
    setError('')

    try {
      console.log('Sending to API:', userMsg)
      const response = await fetch('/api/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMsg })
      })

      console.log('Response status:', response.status)
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      const data = await response.json()
      console.log('Response data:', data)
      
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: data.content 
      }])
    } catch (err) {
      console.error('API Error:', err)
      setError(`Error: ${err.message}`)
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: `❌ Error: ${err.message}` 
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>Simple Private GPT Test</h1>
      
      {error && (
        <div style={{ 
          background: '#fee', 
          border: '1px solid #f88', 
          padding: '10px', 
          marginBottom: '10px' 
        }}>
          {error}
        </div>
      )}
      
      <div style={{ 
        border: '1px solid #ccc', 
        padding: '20px', 
        height: '400px', 
        overflowY: 'auto',
        marginBottom: '20px',
        background: '#f9f9f9'
      }}>
        {messages.length === 0 && (
          <p style={{ color: '#666' }}>No messages yet. Type something below!</p>
        )}
        {messages.map((msg, i) => (
          <div key={i} style={{ 
            marginBottom: '10px',
            padding: '10px',
            background: msg.role === 'user' ? '#e3f2fd' : '#fff',
            borderRadius: '5px'
          }}>
            <strong>{msg.role === 'user' ? 'You' : 'AI'}:</strong> {msg.content}
          </div>
        ))}
        {loading && (
          <div style={{ color: '#666' }}>AI is thinking...</div>
        )}
      </div>
      
      <form onSubmit={sendMessage} style={{ display: 'flex' }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          disabled={loading}
          style={{ 
            flex: 1, 
            padding: '10px',
            fontSize: '16px'
          }}
        />
        <button 
          type="submit" 
          disabled={loading || !input.trim()}
          style={{ 
            padding: '10px 20px',
            fontSize: '16px',
            marginLeft: '10px'
          }}
        >
          {loading ? 'Sending...' : 'Send'}
        </button>
      </form>
      
      <div style={{ marginTop: '20px', fontSize: '12px', color: '#666' }}>
        <p>API URL: /api/chat/</p>
        <p>Check browser console for detailed logs</p>
      </div>
    </div>
  )
}
