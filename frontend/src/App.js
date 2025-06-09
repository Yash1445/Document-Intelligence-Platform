import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = 'http://localhost:8000/api';

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState(null);
  const [uploadFile, setUploadFile] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);
  const [statistics, setStatistics] = useState(null);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_BASE_URL}/documents/`);
      if (response.data.status === 'success') {
        setDocuments(response.data.documents);
        setStatistics(response.data.statistics);
      } else {
        setError('Failed to fetch documents');
      }
    } catch (err) {
      setError(err.response?.data?.message || err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    event.preventDefault();
    if (!uploadFile) {
      setError('Please select a file');
      return;
    }

    setLoading(true);
    setError(null);
    
    const formData = new FormData();
    formData.append('file', uploadFile);

    try {
      const response = await axios.post(`${API_BASE_URL}/documents/upload/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.status === 'success') {
        setUploadFile(null);
        await fetchDocuments(); // Refresh the list
        setCurrentPage('dashboard');
        
        // Show success message
        const processingResult = response.data.processing_result;
        if (processingResult.status === 'success') {
          alert(`Document uploaded and processed successfully! Created ${processingResult.chunks_created} chunks.`);
        } else {
          alert('Document uploaded but processing failed. Please try again.');
        }
      } else {
        setError(response.data.message);
      }
    } catch (err) {
      setError(err.response?.data?.message || err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAskQuestion = async (event) => {
    event.preventDefault();
    if (!selectedDocument || !question.trim()) {
      setError('Please select a document and enter a question');
      return;
    }

    setLoading(true);
    setError(null);
    setAnswer(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/ask/`, {
        document_id: selectedDocument.id,
        question: question.trim(),
        num_chunks: 3
      });

      if (response.data.status === 'success') {
        setAnswer(response.data);
        // Refresh chat history
        fetchChatHistory(selectedDocument.id);
      } else {
        setError(response.data.message);
      }
    } catch (err) {
      setError(err.response?.data?.message || err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchChatHistory = async (documentId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/documents/${documentId}/chat-history/`);
      if (response.data.status === 'success') {
        setChatHistory(response.data.chat_history);
      }
    } catch (err) {
      console.error('Failed to fetch chat history:', err);
    }
  };

  const handleDeleteDocument = async (documentId) => {
    if (!window.confirm('Are you sure you want to delete this document? This action cannot be undone.')) {
      return;
    }

    setLoading(true);
    try {
      const response = await axios.delete(`${API_BASE_URL}/documents/${documentId}/delete/`);
      if (response.data.status === 'success') {
        await fetchDocuments(); // Refresh the list
        if (selectedDocument?.id === documentId) {
          setSelectedDocument(null);
          setCurrentPage('dashboard');
        }
        alert('Document deleted successfully');
      } else {
        setError(response.data.message);
      }
    } catch (err) {
      setError(err.response?.data?.message || err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatFileSize = (bytes) => {
    const sizes = ['B', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 B';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString() + ' ' + 
           new Date(dateString).toLocaleTimeString();
  };

  return (
    <div className="app">
      <header className="header">
        <div className="container">
          <h1>🔍 Document Intelligence Platform</h1>
          <nav className="nav">
            <button
              onClick={() => setCurrentPage('dashboard')}
              className={currentPage === 'dashboard' ? 'nav-button active' : 'nav-button'}
            >
              📊 Dashboard
            </button>
            <button
              onClick={() => setCurrentPage('upload')}
              className={currentPage === 'upload' ? 'nav-button active' : 'nav-button'}
            >
              📤 Upload
            </button>
          </nav>
        </div>
      </header>

      <main className="main">
        <div className="container">
          {loading && (
            <div className="loading-overlay">
              <div className="loading-content">
                <div className="spinner"></div>
                <span>Processing...</span>
              </div>
            </div>
          )}

          {error && (
            <div className="error-message">
              <span>❌ {error}</span>
              <button onClick={() => setError(null)} className="close-button">×</button>
            </div>
          )}

          {currentPage === 'dashboard' && (
            <div className="page">
              <div className="page-header">
                <h2>📚 Document Library</h2>
                <div className="header-actions">
                  {statistics && (
                    <div className="stats-summary">
                      <span className="stat">📄 {statistics.total_documents} Total</span>
                      <span className="stat">✅ {statistics.completed} Completed</span>
                      <span className="stat">⏳ {statistics.processing} Processing</span>
                      {statistics.failed > 0 && <span className="stat">❌ {statistics.failed} Failed</span>}
                    </div>
                  )}
                  <button onClick={() => setCurrentPage('upload')} className="button primary">
                    📤 Upload Document
                  </button>
                </div>
              </div>

              {documents.length === 0 ? (
                <div className="empty-state">
                  <div className="empty-icon">📭</div>
                  <div>No documents uploaded yet</div>
                  <p>Upload your first document to get started with AI-powered document analysis</p>
                  <button onClick={() => setCurrentPage('upload')} className="button primary">
                    📤 Upload Your First Document
                  </button>
                </div>
              ) : (
                <div className="document-grid">
                  {documents.map((doc) => (
                    <div key={doc.id} className="document-card">
                      <div className="document-header">
                        <h3>{doc.title}</h3>
                        <button 
                          onClick={() => handleDeleteDocument(doc.id)}
                          className="delete-btn"
                          title="Delete document"
                        >
                          🗑️
                        </button>
                      </div>
                      <div className="document-info">
                        <p><strong>Type:</strong> {doc.document_type.toUpperCase()}</p>
                        <p><strong>Size:</strong> {doc.file_size_display || formatFileSize(doc.file_size)}</p>
                        <p><strong>Status:</strong> <span className={`status ${doc.processing_status}`}>
                          {doc.processing_status === 'completed' && '✅'}
                          {doc.processing_status === 'processing' && '⏳'}
                          {doc.processing_status === 'pending' && '⏸️'}
                          {doc.processing_status === 'failed' && '❌'}
                          {' ' + doc.processing_status}
                        </span></p>
                        <p><strong>Uploaded:</strong> {formatDate(doc.uploaded_at)}</p>
                        {doc.pages_count && <p><strong>Pages:</strong> {doc.pages_count}</p>}
                      </div>
                      <button
                        onClick={() => {
                          setSelectedDocument(doc);
                          setCurrentPage('qa');
                          fetchChatHistory(doc.id);
                        }}
                        disabled={doc.processing_status !== 'completed'}
                        className="button primary full-width"
                      >
                        {doc.processing_status === 'completed' ? '💬 Ask Questions' : '⏳ Processing...'}
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {currentPage === 'upload' && (
            <div className="page">
              <div className="page-header">
                <h2>📤 Upload Document</h2>
                <button onClick={() => setCurrentPage('dashboard')} className="button secondary">
                  ← Back to Library
                </button>
              </div>

              <div className="upload-form">
                <form onSubmit={handleFileUpload}>
                  <div className="form-group">
                    <label>📄 Select Document</label>
                    <input
                      type="file"
                      accept=".txt,.pdf,.docx,.md"
                      onChange={(e) => setUploadFile(e.target.files[0])}
                      className="file-input"
                    />
                    <p className="help-text">
                      📋 <strong>Supported formats:</strong> TXT, PDF, DOCX, MD
                      <br />
                      📏 <strong>Maximum size:</strong> 10MB
                      <br />
                      ⚡ <strong>Currently optimized for:</strong> TXT files
                    </p>
                  </div>

                  {uploadFile && (
                    <div className="file-preview">
                      <h4>📋 File Preview:</h4>
                      <p><strong>Name:</strong> {uploadFile.name}</p>
                      <p><strong>Size:</strong> {formatFileSize(uploadFile.size)}</p>
                      <p><strong>Type:</strong> {uploadFile.type || 'Unknown'}</p>
                    </div>
                  )}

                  <button
                    type="submit"
                    disabled={loading || !uploadFile}
                    className="button primary full-width"
                  >
                    {loading ? '⏳ Uploading & Processing...' : '🚀 Upload & Process Document'}
                  </button>
                </form>
              </div>
            </div>
          )}

          {currentPage === 'qa' && (
            <div className="page">
              <div className="page-header">
                <h2>💬 Q&A: {selectedDocument?.title}</h2>
                <button onClick={() => setCurrentPage('dashboard')} className="button secondary">
                  ← Back to Library
                </button>
              </div>

              <div className="qa-grid">
                <div className="qa-section">
                  <h3>❓ Ask a Question</h3>
                  <form onSubmit={handleAskQuestion}>
                    <textarea
                      value={question}
                      onChange={(e) => setQuestion(e.target.value)}
                      placeholder="Enter your question about the document..."
                      rows="4"
                      className="form-input"
                    />
                    <button
                      type="submit"
                      disabled={loading || !question.trim()}
                      className="button primary full-width"
                    >
                      {loading ? '🤔 Thinking...' : '🔍 Ask Question'}
                    </button>
                  </form>

                  {chatHistory.length > 0 && (
                    <div className="chat-history">
                      <h4>📜 Recent Questions</h4>
                      <div className="chat-list">
                        {chatHistory.slice(0, 5).map((chat, index) => (
                          <div key={index} className="chat-item" onClick={() => setQuestion(chat.question)}>
                            <p className="chat-question">Q: {chat.question}</p>
                            <p className="chat-meta">
                              Confidence: {(chat.confidence_score * 100).toFixed(1)}% • 
                              {formatDate(chat.created_at)}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                <div className="qa-section">
                  <h3>💡 Answer</h3>
                  {answer ? (
                    <div>
                      <div className="answer-content">
                        <p>{answer.answer}</p>
                      </div>
                      <div className="answer-meta">
                        <p>🎯 <strong>Confidence:</strong> {(answer.confidence * 100).toFixed(1)}%</p>
                        <p>⏱️ <strong>Response Time:</strong> {answer.response_time?.toFixed(2)}s</p>
                      </div>
                      {answer.sources && answer.sources.length > 0 && (
                        <div className="sources">
                          <h4>📚 Sources:</h4>
                          {answer.sources.map((source, index) => (
                            <div key={index} className="source-item">
                              <p><strong>📄 Chunk {source.chunk_id + 1}</strong></p>
                              <p>🎯 Similarity: {(source.similarity * 100).toFixed(1)}%</p>
                              {source.semantic_score && (
                                <p>🧠 Semantic: {(source.semantic_score * 100).toFixed(1)}% | 
                                   🔤 Keyword: {(source.keyword_score * 100).toFixed(1)}%</p>
                              )}
                              <p className="source-content">{source.content}</p>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="empty-answer">
                      <div className="empty-icon">💭</div>
                      <p>Ask a question to see the answer here</p>
                      <p className="help-text">
                        Try asking about:<br />
                        • "What are the main features?"<br />
                        • "How does this work?"<br />
                        • "What are the benefits?"
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;