function AnswerBox({ answer }) {
  if (!answer) {
    return null
  }
  return (
    <div className="answer-box" aria-live="polite">
      <h3>Answer</h3>
      <p>{answer}</p>
    </div>
  )
}
export default AnswerBox