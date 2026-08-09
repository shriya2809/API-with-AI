import { useState } from "react";
import axios from "axios";
import { BounceLoader } from "react-spinners";

const api = axios.create({
  baseURL: "http://localhost:8000"
});

function QuestionForm() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState([]); // [{ question, answer }]

  const handleSubmit = async (e) => {
    e.preventDefault();
    setAnswer('');
    setIsLoading(true);
    const currentQuestion = question;

    try {
      const res = await fetch('http://localhost:8000/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: currentQuestion, chat_history: chatHistory }),
      });

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let fullAnswer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const chunks = buffer.split('\n\n');
        buffer = chunks.pop(); // last piece may be incomplete, hold it for the next read

        for (const chunk of chunks) {
          if (!chunk.startsWith('data: ')) continue;
          const raw = chunk.slice(6);
          if (raw === '[DONE]') continue;
          fullAnswer += JSON.parse(raw);
          setAnswer(fullAnswer); // re-render with each new token
        }
      }

      setChatHistory((prev) => [...prev, { question: currentQuestion, answer: fullAnswer }]);
    } catch (err) {
      console.error("Chat error:", err);
      setAnswer("Error getting response.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleIndexing = async (e) => {
    e.preventDefault();
    setAnswer('');
    setIsLoading(true);
    try {
      const response = await api.post('/indexing', null, { params: { url: question } });
      // Fixed: /indexing returns response.data.response
      setAnswer(response.data.response || response.data.message || "Successfully indexed!");
    } catch (err) {
      console.error("Indexing error:", err);
      setAnswer(err.response?.data?.error || "Failed to index URL. Ensure it starts with http:// or https://");
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = () => {
    setChatHistory([]);
    setAnswer('');
    setQuestion('');
  };

  return (
    <div className="main-container">
      <form className="form">
        <input 
          className="form-input" 
          type="text" 
          value={question} 
          onChange={(e) => setQuestion(e.target.value)} 
          placeholder="Ask a question or enter a URL..."
        />
        <div className="buttons-container">
          <button className="form-button" type="submit" onClick={handleSubmit}>Q&A</button>
          <button className="form-button" type="button" style={{backgroundColor: 'red'}} onClick={handleIndexing}>Index</button>
          <button className="form-button" type="button" onClick={handleNewChat}>New Chat</button>
        </div>
      </form>
      {isLoading && (
        <div className="loader-container">
          <BounceLoader color="#3498db" />
        </div>
      )}
      <div>
        <h2>Response:</h2>
        <p>{answer}</p>
      </div>
    </div>
  );
}

export default QuestionForm;