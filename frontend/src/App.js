import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = 'http://localhost:5000';

function App() {
  const [question, setQuestion] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const chatContainerRef = useRef(null);

  // Load chat history on component mount
  useEffect(() => {
    loadChatHistory();
  }, []);

  // Auto-scroll to bottom when new messages are added
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [chatHistory]);

  const loadChatHistory = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/history`);
      setChatHistory(response.data.history || []);
    } catch (err) {
      console.error('Error loading chat history:', err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!question.trim()) {
      setError('Please enter a question');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API_BASE_URL}/ask`, {
        question: question.trim()
      });

      // Add new Q&A to chat history
      const newEntry = {
        timestamp: new Date().toISOString(),
        question: question.trim(),
        answer: response.data.answer,
        confidence: response.data.confidence
      };

      setChatHistory(prevHistory => [...prevHistory, newEntry]);
      setQuestion('');
    } catch (err) {
      console.error('Error asking question:', err);
      if (err.response && err.response.data && err.response.data.error) {
        setError(err.response.data.error);
      } else {
        setError('Failed to get response. Make sure the backend server is running.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const clearHistory = () => {
    setChatHistory([]);
  };

  return (
    <div className="App">
      <div className="chat-container">
        <header className="chat-header">
          <h1>🤖 Professional AI Assistant</h1>
          <p>Ask me about productivity, remote work, career development, and more!</p>
        </header>

        <div className="chat-history" ref={chatContainerRef}>
          {chatHistory.length === 0 ? (
            <div className="welcome-message">
              <h3>Welcome! Ask me anything about:</h3>
              <ul>
                <li>Task prioritization and time management</li>
                <li>Remote work best practices</li>
                <li>Career development and networking</li>
                <li>Startup funding and business planning</li>
                <li>Professional communication</li>
              </ul>
            </div>
          ) : (
            chatHistory.map((entry, index) => (
              <div key={index} className="chat-entry">
                <div className="question">
                  <div className="message-header">
                    <span className="sender">You</span>
                    <span className="timestamp">{formatTimestamp(entry.timestamp)}</span>
                  </div>
                  <div className="message-content">{entry.question}</div>
                </div>
                <div className="answer">
                  <div className="message-header">
                    <span className="sender">AI Assistant</span>
                    {entry.confidence && (
                      <span className="confidence">
                        Confidence: {(entry.confidence * 100).toFixed(0)}%
                      </span>
                    )}
                  </div>
                  <div className="message-content">{entry.answer}</div>
                </div>
              </div>
            ))
          )}
        </div>

        <form onSubmit={handleSubmit} className="input-form">
          {error && <div className="error-message">{error}</div>}
          
          <div className="input-container">
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask a professional question..."
              disabled={loading}
              rows={2}
              className="question-input"
            />
            <button 
              type="submit" 
              disabled={loading || !question.trim()}
              className="send-button"
            >
              {loading ? '⏳' : '📤'}
            </button>
          </div>
          
          {chatHistory.length > 0 && (
            <button 
              type="button" 
              onClick={clearHistory}
              className="clear-button"
            >
              Clear History
            </button>
          )}
        </form>
      </div>
    </div>
  );
}

export default App;