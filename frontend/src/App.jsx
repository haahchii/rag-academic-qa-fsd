import { useState, useEffect } from 'react'
import './App.css'
import Navbar from './components/Navbar'
import PDFUpload from './components/PDFUpload'
import AnswerBox from './components/AnswerBox'

function App() {
  const [file, setFile] = useState(null)
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [loading, setLoading] = useState(false)
  const [backendStatus, setBackendStatus] = useState('Checking connection...')

  useEffect(() => {
  fetch('http://127.0.0.1:8000/health')
    .then((response) => {
      if (!response.ok) {
        throw new Error('Backend unavailable')
      }
      return response.json()
    })
    .then((data) => {
      setBackendStatus(data.status === 'healthy' ? 'Connected' : 'Unavailable')
    })
    .catch(() => {
      setBackendStatus('Disconnected')
    })
  }, [])
  
  function handleFileChange(event) {
    const selectedFile = event.target.files[0]

    if (!selectedFile) return

    if (selectedFile.type !== 'application/pdf') {
      setFile(null)
      setAnswer('Please select a valid PDF file.')
      return
    }

    setFile(selectedFile)
    setAnswer('')
  }

  async function handleAsk() {
    if (!file) {
      setAnswer('Please upload a PDF first.')
      return
    }

    if (!question.trim()) {
      setAnswer('Please enter a question.')
      return
    }

    setLoading(true)
    setAnswer('Reading your PDF and generating an answer...')

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('question', question)

      const response = await fetch('http://127.0.0.1:8000/ask', {
        method: 'POST',
        body: formData
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to generate an answer.')
      }

      if(!data.answer) {
        throw new Error('No answer was generated. Please try again.')
      }

      setAnswer(data.answer || 'No answer was generated.')
    } catch (error) {
      if(!navigator.online) {
        setAnswer('You appear to be offline. Please check your internet connection.')
      } else {
      setAnswer(error.message || 'Something went wrong. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <Navbar backendStatus={backendStatus} />

      <main className="main-content">
        <section className="hero">
          <p className="tagline">YOUR PERSONAL STUDY ASSISTANT</p>
          <h1>Academic Question Answering</h1>
          <p className="subtitle">
            Upload your study materials and get answers to your questions.
          </p>
        </section>

        <PDFUpload
          file={file}
          onFileChange={handleFileChange}
        />

        <section className="card">
          <h2>💬 Ask a question</h2>
          <p>What would you like to learn from your document?</p>

          <textarea
            placeholder="Ask your Question here..."
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            rows="4"
          />

          <button onClick={handleAsk} disabled={loading}>
            {loading ? 'Processing...' : 'Get Answer →'}
          </button>

          <AnswerBox answer={answer} />
        </section>

        <footer>
          Powered by React, Python, SBERT, FAISS and Gemini
        </footer>
      </main>
    </div>
  )
}

export default App