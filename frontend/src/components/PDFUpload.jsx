function PDFUpload({ file, onFileChange }) {
  return (
    <section className="card">
      <h2>📄 Upload your document</h2>
      <p>Select an academic PDF to get started.</p>

      <label className="upload-box">
        <span className="upload-icon">⬆</span>
        <span>Click here to upload a PDF</span>
        <span className="file-hint">PDF files only</span>

        <input
          type="file"
          accept=".pdf,application/pdf"
          onChange={onFileChange}
        />
      </label>

      {file && (
        <p className="file-name">
          ✅ Selected: {file.name}
        </p>
      )}
    </section>
  )
}

export default PDFUpload