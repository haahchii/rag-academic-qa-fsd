function Navbar({ backendStatus }) {
  return (
    <nav className="navbar">
      <h2>📚 RAG Academic QA</h2>

      <div>
        <span>AI-Powered Learning</span>
        <p>Backend: {backendStatus}</p>
      </div>
    </nav>
  )
}

export default Navbar